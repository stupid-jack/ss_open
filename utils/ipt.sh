#-------------------------------------------------------------------------------
iptables example

You have to build iptables with connection tracking and REDIRECT target.

# Create new chain
root# iptables -t nat -N REDSOCKS

# Ignore LANs and some other reserved addresses.
# See Wikipedia and RFC5735 for full list of reserved networks.
root# iptables -t nat -A REDSOCKS -d 0.0.0.0/8 -j RETURN
root# iptables -t nat -A REDSOCKS -d 10.0.0.0/8 -j RETURN
root# iptables -t nat -A REDSOCKS -d 127.0.0.0/8 -j RETURN
root# iptables -t nat -A REDSOCKS -d 169.254.0.0/16 -j RETURN
root# iptables -t nat -A REDSOCKS -d 172.16.0.0/12 -j RETURN
root# iptables -t nat -A REDSOCKS -d 192.168.0.0/16 -j RETURN
root# iptables -t nat -A REDSOCKS -d 224.0.0.0/4 -j RETURN
root# iptables -t nat -A REDSOCKS -d 240.0.0.0/4 -j RETURN

# Anything else should be redirected to port 12345
root# iptables -t nat -A REDSOCKS -p tcp -j REDIRECT --to-ports 12345

# Any tcp connection made by `luser' should be redirected.
root# iptables -t nat -A OUTPUT -p tcp -m owner --uid-owner luser -j REDSOCKS

# You can also control that in more precise way using `gid-owner` from
# iptables.
root# groupadd socksified
root# usermod --append --groups socksified luser
root# iptables -t nat -A OUTPUT -p tcp -m owner --gid-owner socksified -j REDSOCKS

# Now you can launch your specific application with GID `socksified` and it
# will be... socksified. See following commands (numbers may vary).
# Note: you may have to relogin to apply `usermod` changes.
luser$ id
uid=1000(luser) gid=1000(luser) groups=1000(luser),1001(socksified)
luser$ sg socksified -c id
uid=1000(luser) gid=1001(socksified) groups=1000(luser),1001(socksified)
luser$ sg socksified -c "firefox"

# If you want to configure socksifying router, you should look at
# doc/iptables-packet-flow.png and doc/iptables-packet-flow-ng.png and
# wikipedia/File:Netfilter-packet-flow.svg
# Note, you should have proper `local_ip' value to get external packets with
# redsocks, default 127.0.0.1 will not go. See iptables(8) manpage regarding
# REDIRECT target for details.
# Depending on your network configuration iptables conf. may be as easy as:
root# iptables -t nat -A PREROUTING --in-interface eth_int -p tcp -j REDSOCKS

#-------------------------------------------------------------------------------
"In my case proxy is located on the 10.100.100.100 IP address, SOCKS is on port 1080/tcp, HTTP and HTTPS on 8080/tcp so my redsocks.conf looks like this"

base {
daemon = on;
//log = stderr;
redirector = iptables;
}

redsocks {
local_ip = 0.0.0.0;
local_port = 12345;
ip = 10.100.100.100;
port = 1080;
type = socks5;
}

redsocks {
local_ip = 0.0.0.0;
local_port = 12346;
ip = 10.100.100.100;
port = 8080;
type = http-relay;
}

redsocks {
local_ip = 0.0.0.0;
local_port = 12347;
ip = 10.100.100.100;
port = 8080;
type = http-connect;
}

At this point, we have a service which can handle TCP streams and redirect to the appropriate kind of proxy based on the port number (e.g., 12345 means SOCKS proxy). Nothing magic, right?

The little magic starting here: we have to create some iptables rules to catch network connections, and if it is going towards the public internet redirect them to our recently started redsoks service and finally to the appropriate proxy service.

There are several special addresses that shouldn't be handled by the proxy. First, we have to create exceptions for them, otherwise we won't be able to reach the proxy itself. A new firewall chain, REDSOCKS, will help to separate proxy related rules inside of iptables.

# Create new chain
iptables -t nat -N REDSOCKS

# Ignore LANs and some other reserved addresses
iptables -t nat -A REDSOCKS -d 0.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 10.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 127.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 169.254.0.0/16 -j RETURN
iptables -t nat -A REDSOCKS -d 172.16.0.0/12 -j RETURN
iptables -t nat -A REDSOCKS -d 192.168.0.0/16 -j RETURN
iptables -t nat -A REDSOCKS -d 224.0.0.0/4 -j RETURN
iptables -t nat -A REDSOCKS -d 240.0.0.0/4 -j RETURN

With the following rules iptables can distinguish the traffic type and choose the right proxy. HTTP traffic comes on 80/tcp port and is redirected to the gateway's 12346 port, secure HTTP comes on 443/tcp and is redirected to the 12347 port, and all others to the 12345 port, which actually means the SOCKS proxy. SOCKS proxy is not an application aware proxy as HTTP(S), it can only allow or refuse connections without any further inspection like virus scanning and caching. This is the reason why, for example, SSH connections will be possible.

# All other TCP connections must be redirected to redsocks ports
iptables -t nat -A REDSOCKS -p tcp -m tcp --dport 443 -j REDIRECT --to-ports 12347
iptables -t nat -A REDSOCKS -p tcp -m tcp --dport 80 -j REDIRECT --to-ports 12346
iptables -t nat -A REDSOCKS -p tcp -m tcp -j REDIRECT --to-ports 12345

However, in the above network diagram I didn't mentioned (sorry :) ) I have an OpenVPN service as well, so the following two rules will handle not just the endpoints' traffic but the VPN's too.

# if it cames in on em2 or tun0 (internal network or VPN), and it is TCP, send it to REDSOCKS
iptables -t nat -A PREROUTING -i em2 -p tcp -j REDSOCKS
iptables -t nat -A PREROUTING -i tun0 -p tcp -j REDSOCKS

In general it is useful to handle connections initiated on the gateway in a same way:

# if it is locally originated it also send to REDSOCKS
iptables -t nat -A OUTPUT -p tcp -j REDSOCKS

Thats all. We have successfully hidden our corporate proxy, at least while we use only TCP connections. Other protocols will be discussed in an other post.

Just a side note: it is absolutely correct that tracapath shows something different then you expect at first.

#-------------------------------------------------------------------------------

The first thing to do is do enable IP forwarding. This is done either by using:

# echo "1" > /proc/sys/net/ipv4/ip_forward

or

# sysctl net.ipv4.ip_forward=1

Then, we will add a rule telling to forward the traffic on port 1111 to ip 2.2.2.2 on port 1111:

# iptables -t nat -A PREROUTING -p tcp --dport 1111 -j DNAT --to-destination 2.2.2.2:1111

and finally, we ask IPtables to masquerade:

iptables -t nat -A POSTROUTING -j MASQUERADE

Optionally, you could only redirect the traffic from a specific source/network with, for a host only:

# iptables -t nat -A PREROUTING -s 192.168.1.1 -p tcp --dport 1111 -j DNAT --to-destination 2.2.2.2:1111

or for a whole network

# iptables -t nat -A PREROUTING -s 192.168.1.0/24 -p tcp --dport 1111 -j DNAT --to-destination 2.2.2.2:1111

that’s it, now the traffic to port 1111 will be redirected to IP 2.2.2.2 .

If you go on host 2.2.2.2, you should see a lot of traffic coming from the host doing the redirection.


#-------------------------------------------------------------------------------
1、 redsocks和iptables规则在一个机器上

iptables -t nat -N REDSOCKS
iptables -t nat -A REDSOCKS -d 0.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 10.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 127.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 169.254.0.0/16 -j RETURN
iptables -t nat -A REDSOCKS -d 172.16.0.0/12 -j RETURN
iptables -t nat -A REDSOCKS -d 192.168.0.0/16 -j RETURN
iptables -t nat -A REDSOCKS -d 224.0.0.0/4 -j RETURN
iptables -t nat -A REDSOCKS -d 240.0.0.0/4 -j RETURN
iptables -t nat -A REDSOCKS -p tcp -j REDIRECT --to-port 12345

iptables -t nat -A OUTPUT -p tcp -j REDSOCKS

2、redsocks和iptables规则不在一个机器上。redsocks和socks5 proxy在一起.

iptables -t nat -N REDSOCKS
iptables -t nat -A REDSOCKS -d 0.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 10.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 127.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 169.254.0.0/16 -j RETURN
iptables -t nat -A REDSOCKS -d 172.16.0.0/12 -j RETURN
iptables -t nat -A REDSOCKS -d 192.168.0.0/16 -j RETURN
iptables -t nat -A REDSOCKS -d 224.0.0.0/4 -j RETURN
iptables -t nat -A REDSOCKS -d 240.0.0.0/4 -j RETURN
iptables -t nat -A REDSOCKS -p tcp  -j DNAT --to-destination 103.38.42.95:10005
iptables -t nat -I REDSOCKS -p tcp -d 103.38.42.95 -j RETURN



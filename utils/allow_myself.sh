#!/bin/bash

[ -f "~/.bashrc" ] && . ~/.bashrc
iptables_bin="/sbin/iptables"


url="http://x.x.x.x/ip.html"

wget $url -O /tmp/ip.html >/dev/null 2>&1
if [ $? -ne 0 ];then
    echo -e "Maybe some error.. Network or apache on the server? Please Check it out ... :)"
    exit 1
fi

if [ $(cat /tmp/ip.html|wc -l) -eq 0 ];then
    echo -e "IP is empty And I will just EXIT"
    exit 1
fi

function any_cidr_to_8_or_16_or_24_or_32()
{
    if [ -z $1 ];then
        echo -e "No [ip] give me in function [any_cidr_to_8_or_16_or_24]. Exiting..."
        exit 1
    else
        whole_ip="$1"
        N1=$(echo -e "$whole_ip"|egrep '/'|wc -l)
        if [ $N1 -ne 1 ];then
            return
        else
            ip=$(echo -e "$whole_ip"|awk -F'/' '{print $1}')
            N2=$(echo -e "$ip"|egrep "([0-9]{1,3}\.){3}[0-9]{1,3}"|wc -l)
            if [ $N2 -ne 1 ];then
                return
            fi
            ip1=$(echo -e "$ip"|awk -F'.' '{print $1}')
            ip2=$(echo -e "$ip"|awk -F'.' '{print $2}')
            ip3=$(echo -e "$ip"|awk -F'.' '{print $3}')
            ip4=$(echo -e "$ip"|awk -F'.' '{print $4}')
            cidr=$(echo -e "$whole_ip"|awk -F'/' '{print $2}')
            if [ $cidr -gt 32 -o $cidr -lt 8 ];then
                echo -e "cidr is not right. Exiting..."
                exit 1
            fi
            if [ $cidr -ge 8 -a $cidr -le 15 ];then
                last_ip="$ip1.0.0.0/$cidr"
            elif [ $cidr -ge 16 -a $cidr -le 23 ];then
                last_ip="$ip1.$ip2.0.0/$cidr"
            elif [ $cidr -ge 24 -a $cidr -le 31 ];then
                last_ip="$ip1.$ip2.$ip3.0/$cidr"
            elif [ $cidr -eq 32 ];then
                last_ip="$ip/$cidr"
            fi
            echo -e "$last_ip"
        fi
    fi
}

while read line
do
    N1=$(echo -e "$line"|egrep '/'|wc -l)
    if [ $N1 -eq 1 ];then
        line=$(any_cidr_to_8_or_16_or_24_or_32 $line)
    fi
    N=$($iptables_bin -t filter -L INPUT -vn|egrep -w "$line"|egrep "ACCEPT"|wc -l)
    if [ $N -ge 1 ];then
        echo -e "Already allowed IP $line"
    else
        echo -e "Added IP $line to allow"
        $iptables_bin -t filter -I INPUT -s $line -j ACCEPT
    fi
done < /tmp/ip.html
rm /tmp/ip.html 2>/dev/null

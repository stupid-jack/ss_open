#!/bin/bash

#这个脚本的作用是取代添加更多的block china ip的规则

allow_ip="/bin/ss/utils/allow_ip.sh"
iptables_bin=$(which iptables)

if [ -z $iptables_bin ];then
    iptables_bin="/sbin/iptables"
fi

#echo -e "$iptables_bin"
N1=$($iptables_bin -L INPUT -vn|egrep policy|egrep DROP|wc -l)

if [ $N1 -ne 1 ];then
    $iptables_bin -P INPUT DROP
fi

N2=$($iptables_bin -L INPUT -vn|egrep ESTABLISHED|egrep ACCEPT|wc -l)
if [ $N2 -lt 1 ];then
    $iptables_bin -I INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
fi

N3=$($iptables_bin -L INPUT -vn|egrep  ACCEPT|egrep lo|wc -l)
if [ $N3 -lt 1 ];then
    $iptables_bin -I INPUT -i lo -j ACCEPT
fi

#the_ip=$(nslookup aws1.publicvm.com|egrep Address|egrep -v '#53'|egrep -o "([0-9]{1,3}\.){3}[0-9]{1,3}"|head -1)
#$allow_ip $the_ip

#mv /usr/local/accept_ips /usr/local/accept_ips_`date +%F_%H:%M:%S`
iptables -L -vn > /usr/local/accept_ips

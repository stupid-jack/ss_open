#!/bin/bash

if [ $# -ne 1 ];then
    echo -e "Usage:\n\t$0 \"IP\""
    exit 1
fi

ip="$1"
log="/data/logs/ss/allow_ip.log"

N=$(iptables -t filter -L INPUT -vn|egrep -w "$ip"|egrep "ACCEPT"|wc -l)
if [ $N -ge 1 ];then
    echo -e "IP Address [ $ip ] Already allowed..."
else
    iptables -t filter  -A INPUT -s $ip -j ACCEPT
    if [ $? -eq 0 ];then
        echo -e "allowed [ $ip ]"
        echo -e "[`date +%F_%H:%M:%S`] allowed ip [$ip]" >> $log
    fi
fi

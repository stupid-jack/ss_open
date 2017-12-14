#!/bin/bash

[ -f "~/.bashrc" ] && . ~/.bashrc
iptables_bin=$(which iptables)


if [ $# -ne 1 ];then
    echo -e "Usage:\n\t$0 ip_address"
    exit 1
fi

ip_address="$1"
N=$($iptables_bin -L INPUT -vn|egrep $ip_address|egrep ACCEPT|wc -l)
if [ $N -ge 1 ];then
    echo -e "Deleting [$ip_address] from INPUT ACCEPT"
    $iptables_bin -D INPUT -s $ip_address -j ACCEPT
    if [ $? -eq 0 ];then
        echo -e "Deleted successfully"
    fi
else
    echo -e "Maybe wrong ip_address [$ip_address] or not match any rules in INPUT"
    exit 2
fi

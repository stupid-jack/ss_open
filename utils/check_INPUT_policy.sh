#!/bin/bash


iptables_bin="/sbin/iptables"

N=$($iptables_bin -L INPUT -vn|egrep policy|egrep DROP|wc -l)
if [ $N -ne 1 ];then
    $iptables_bin -P INPUT DROP
fi

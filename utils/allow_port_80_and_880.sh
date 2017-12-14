#!/bin/bash

#iptables -L INPUT -vn|egrep
N_80=$(iptables -L INPUT -vn|egrep dpt:80|egrep ACCEPT|wc -l)
N_880=$(iptables -L INPUT -vn|egrep dpt:880|egrep ACCEPT|wc -l)

if [ $N_80 -ge 1 ];then
        echo -e "Already allowed port 80 from anywhere"
else
        iptables -I INPUT 1 -p tcp --dport 80 -j ACCEPT
        echo -e "Allowed port 80 from anywhere"
fi

if [ $N_880 -ge 1 ];then
        echo -e "Already allowed port 880 from anywhere"
else
        iptables -I INPUT 1 -p tcp --dport 880 -j ACCEPT
        echo -e "Allowed port 880 from anywhere"
fi

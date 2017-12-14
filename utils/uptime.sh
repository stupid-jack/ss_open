#!/bin/bash


cwd_path=$(cd `dirname $0` && pwd)
cd $cwd_path
N=5

if [ -f "/etc/os-release" ];then
    egrep -q -i ubuntu /etc/os-release
    if [ $? -eq 0 ];then
        bc -v >/dev/null 2>&1
        if [ $? -ne 0 ];then
            echo -e "install bc anyway"
            apt-get install -y bc >/dev/null 2>&1
        fi
    fi
fi

up=$(uptime|awk -F':' '{print $NF}'|column  -t|sed 's/,/ /g'|column  -t|awk '{print $1}'|column  -t)

load=$(echo -e "($up - $N)/1 > 0" | bc)

if [ $load -eq 1 ];then
    echo -e "I need to warn my boss"
    if [ -f "alarm.py" ];then
        python alarm.py "老大，服务器负载过高。[$up]"
        echo -e "Sent to my boss"
    fi
else
    echo -e "Everything is ok"
fi


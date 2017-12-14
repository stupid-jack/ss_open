#!/bin/bash

. ~/.bashrc

restart_log_path="/data/logs/ss/restart_ss_client.log"
ss_client_log_path="/data/logs/ss/ss_client.log"

N5=`ps -e faux|egrep  "python /data/ss_client/shadowsocks/local.py -q -q"|egrep -v grep|wc -l`
echo -e "ss_client/local.py number is $N5"
if [ $N5 -lt 1 ];then
        echo -e "[`date +%F_%H:%M:%S`]  restart ss_client/local.py" >> $restart_log_path
        cd /data/ss_client/shadowsocks && python /data/ss_client/shadowsocks/local.py -q -q >> $ss_client_log_path 2>&1 &
fi


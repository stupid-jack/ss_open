#!/bin/bash

. ~/.bashrc

restart_log_path="/data/logs/ss/restart_server.log"
ss_log_path="/data/logs/ss/ss.log"
ss_no_change_log_path="/data/logs/ss/ss_no_change.log"
ss_hub_log_path="/data/logs/ss/ss_hub.log"

N2=`ps -e faux|egrep  "python /data/ss/shadowsocks/server.py -q -q"|egrep -v grep|wc -l`
echo -e "ss/server.py number is $N2"
if [ $N2 -lt 1 ];then
        echo -e "[`date +%F_%H:%M:%S`]  restart ss/server.py" >>  $restart_log_path
        python /data/ss/shadowsocks/server.py -q -q >> $ss_log_path 2>&1 &
fi

N3=`ps -e faux|egrep  "python /data/ss_no_change/shadowsocks/server.py -q -q"|egrep -v grep|wc -l`
echo -e "ss_no_change/server.py number is $N3"
if [ $N3 -lt 1 ];then
        echo -e "[`date +%F_%H:%M:%S`]  restart ss_no_change/server.py" >> $restart_log_path
        python /data/ss_no_change/shadowsocks/server.py -q -q >> $ss_no_change_log_path 2>&1 &
fi

N4=`ps -e faux|egrep  "python /data/ss_hub/shadowsocks/server.py -q -q"|egrep -v grep|wc -l`
echo -e "ss_hub/server.py number is $N4"
if [ $N4 -lt 1 ];then
        echo -e "[`date +%F_%H:%M:%S`]  restart ss_hub/server.py" >> $restart_log_path
        cd /data/ss_hub/shadowsocks && python /data/ss_hub/shadowsocks/server.py -q -q >> $ss_hub_log_path 2>&1 &
fi

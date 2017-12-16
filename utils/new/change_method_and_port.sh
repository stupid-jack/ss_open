#!/bin/bash

cwd_path=$(cd `dirname $0` && pwd)
cd $cwd_path

log_path="/data/logs/ss_client/change_method_and_port.log"

python change_method_and_port.py ip >> $log_path 2>&1
echo -e "`date +%F_%T`\n\n" >> $log_path

size=$(du -shm $log_path|cut -f1)
if [ $size -gt 30 ];then
    echo -e "[`date +%F_%T`]  clear once for log size > 30M" > $log_path
fi


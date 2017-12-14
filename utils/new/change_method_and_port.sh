#!/bin/bash

cwd_path=$(cd `dirname $0` && pwd)
cd $cwd_path

log_path="/data/logs/ss_client/change_method_and_port.log"

python change_method_and_port.py ip >> $log_path 2>&1
echo -e "`date +%F_%T`\n\n" >> $log_path


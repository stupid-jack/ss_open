#!/bin/bash

log_path="/data/logs/ss/delete_all_ACCEPT_ip.log"

iptables-save |egrep ACCEPT|egrep "([0-9]{1,3}\.){3}[0-9]{1,3}/32"|sed 's|-A|iptables -D|' > /tmp/delete_all_ACCEPT_ip.sh
echo -e "--------------------------------------- `date +%F_%T` ----------------------------" >> $log_path
iptables-save |egrep ACCEPT|egrep "([0-9]{1,3}\.){3}[0-9]{1,3}/32"|sed 's|-A|iptables -D|' >> $log_path
bash /tmp/delete_all_ACCEPT_ip.sh
echo -e "" >> $log_path
rm /tmp/delete_all_ACCEPT_ip.sh


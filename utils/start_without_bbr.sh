#!/bin/bash

cwd=$(cd `dirname $0` && pwd)
cd $cwd

apt-get install python git vim -y
vim ./Encrypt_or_Decrypt_my_data.py
python ./Encrypt_or_Decrypt_my_data.py -d new/1.sh.locked
if [ $? -ne 0 ];then
    echo -e "Sorry..Input password wrong..Please run me again."
    exit 2
fi
bash new/1.sh server
#echo -e "\niptables -P INPUT ACCEPT\n" >> /etc/rc.local
#bash new/bbr.sh

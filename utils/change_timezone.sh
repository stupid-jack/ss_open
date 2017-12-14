#!/bin/bash

if [ $# -ne 1 ];then
    echo -e "Usage:\n\t$0 \"timezone\"  "
    exit 2
else
    timezone_to_change="$1"
fi

ubuntu_check=$(cat /etc/os-release|egrep -i ubuntu|wc -l)
if [ $ubuntu_check -lt 1 ];then
    echo -e "Only ubuntu supported"
    exit 2
fi


echo -e "--------------------------- all timezones -----------------------------------"
timedatectl list-timezones > /tmp/all_timezones
cat /tmp/all_timezones
echo -e "-----------------------------------------------------------------------------"

timedatectl set-timezone $timezone_to_change

echo -e "After change...-----------------------"
timedatectl

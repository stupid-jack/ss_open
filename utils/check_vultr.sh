#!/bin/bash

cwd=$(cd `dirname $0` && pwd)
cd $cwd

N2=5
N3=0.5

if [ -f "vultr.txt" ];then
    while read line
    do
        N=$(echo -e "$line"|column -t|wc |awk '{print $3}')
        if [ $N -gt 1 ];then
            location=$(echo -e "$line"|awk -F'|' '{print $1}'|column -t)
            url=$(echo -e "$line"|awk -F'|' '{print $2}'|column -t)
            echo -e "$location ---- $url"
            ping -c $N2 -i $N3 $url|egrep icmp_seq
            echo
        fi
    done < vultr.txt
fi


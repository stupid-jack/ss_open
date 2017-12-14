#!/bin/bash

cwd=$(cd `dirname $0` && pwd)
cd $cwd

iotop_bin=""
iotop_bin=$(which iotop 2>/dev/null)
if [ "$iotop_bin" = "" ];then
    echo -e "Sorry. No iotop command found"
    echo -e "Now I install iotop by apt-get"
    apt-get install -y iotop >/dev/null 2>&1
    exit 12
fi

echo -e "1、动态查看IO数据 (大多数时候你应该选择这个)"
echo -e "2、结果写入文件，待会查看"
read -p "input your choice: " co2
if [ "$co2" == "1" ];then
    $iotop_bin -a -o -P
elif [ "$co2" == "2" ];then
    if [ ! -d "check_disk_io" ];then
        mkdir -p check_disk_io
    fi
    log_file="${cwd}/check_disk_io/`date +%F`_check_disk_io.log"
    num=0
    echo -e "Please wait for a while.. About 30 seconds.."
    while [ $num -lt 30 ]
    do
        echo $num
        num=$((num+1))
        echo -e "----------" >> $log_file
        $iotop_bin -b -n 1 -P -t -o -k >> $log_file
        echo -e "" >> $log_file
        sleep 0.5
        #if [ $num -ge 20 ];then
        #   break
        #fi
    done
    echo -e "=======================================" >> $log_file
    echo -e "please check the file [$log_file] to see the result"
else
    echo -e "sorry...Only 1 or 2 .. not others."
    exit 2
fi


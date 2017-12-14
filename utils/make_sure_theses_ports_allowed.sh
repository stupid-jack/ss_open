#!/bin/bash


cwd=`cd $(dirname $0) && pwd`
cd $cwd

iptables_bin=""
iptables_bin="`which iptables`"
if [ "$iptables_bin" == "" ];then
    echo -e "Sorry. No iptables command found. "
    exit 13
fi

if [ $# -gt 1 ];then
    echo -e "Usage:\n\t$0 path_to_file"
    exit 1
elif [ $# -eq 1 ];then
    path_file="$1"
    if [ ! -f "$path_file" ];then
        echo -e "Sorry.. path_file not exists [$path_file]"
        exit 12
    fi
else
    if [ -f "ports_to_allow" ];then
        path_file="./ports_to_allow"
    else
        echo -e "Sorry. no ports_to_allow found here..."
        exit 12
    fi
fi

function check_this_one()
{
    proto="$1"
    port="$2"
    N_DROP=$($iptables_bin -L  INPUT -nv --line-numbers|egrep -v "INPUT"|egrep -v "num"|egrep "$proto"|egrep "$port"|egrep "DROP"|wc -l)
    N_ACCEPT=$($iptables_bin -L  INPUT -nv --line-numbers|egrep -v "INPUT"|egrep -v "num"|egrep "$proto"|egrep "$port"|egrep "ACCEPT"|wc -l)
    if [ $N_DROP -gt 0 ];then
        N_DROP_numbers=$($iptables_bin -L  INPUT -nv --line-numbers|egrep -v "INPUT"|egrep -v "num"|egrep "$proto"|egrep "$port"|egrep "DROP"|awk '{print $1}'|sort -n -r)
        for i in $N_DROP_numbers
        do
            $iptables_bin -D INPUT $i
        done
    fi
    if [ $N_ACCEPT -eq 0 ];then
        $iptables_bin -A INPUT -p $proto --dport $port -j ACCEPT
    fi
}

all_tcp_ports=$(egrep  "^tcp" $path_file |awk '{print $2}'|sed 's/,/ /g')
all_udp_ports=$(egrep  "^udp" $path_file |awk '{print $2}'|sed 's/,/ /g')

for i in $all_tcp_ports
do
    check_this_one "tcp" "$i"
done
for i in $all_udp_ports
do
    check_this_one "udp" "$i"
done

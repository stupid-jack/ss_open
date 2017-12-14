#!/bin/bash

if [ -f "/etc/sysctl.conf" ];then
    N1=$(cat /etc/sysctl.conf|egrep "added by jack for optimize tcp"|wc -l)
    if [ $N1 == 1 ];then
        echo -e "Already added to sysctl.conf .. Exit Now."
        exit 2
    fi
    cat >> /etc/sysctl.conf << EOF
#########################################################
#added by jack for optimize tcp for this linux machine

net.core.wmem_max = 12582912
net.core.rmem_max = 12582912
net.ipv4.tcp_rmem = 10240 87380 12582912
net.ipv4.tcp_wmem = 10240 87380 12582912
net.ipv4.ip_local_port_range = 18000    65535
net.ipv4.netfilter.ip_conntrack_tcp_timeout_time_wait = 1
net.ipv4.tcp_window_scaling = 1
net.ipv4.tcp_max_syn_backlog = 3240000
net.core.somaxconn = 3240000
net.ipv4.tcp_max_tw_buckets = 1440000
net.ipv4.tcp_congestion_control = hybla
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 15
net.ipv4.tcp_syn_retries = 2
net.ipv4.tcp_synack_retries = 2
net.ipv4.tcp_tw_recycle = 1

#########################################################
EOF
    echo -e "Now ecex sysctl -p to make sure working"
    sysctl -p >/dev/null 2>&1
    echo -e "\n[After change. Please check one item.]\n"
    sysctl -a 2>/dev/null|egrep "net.ipv4.tcp_tw_reuse"
fi


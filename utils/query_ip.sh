#!/bin/bash

which curl >/dev/null 2>&1
if [ $? -ne 0 ];then
    echo -e "no curl find EXIT now."
    exit 2
fi

ValidIpAddressRegex="^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
ValidHostnameRegex="^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$"

function get_all_ips()
{
    local domain="$1"
    which dig >/dev/null 2>&1
    if [ $? -eq 0 ];then
        all_ips=$(dig "$domain"|egrep "$domain"|egrep -v "^\;"|egrep -i cname|wc -l)
        if [ $all_ips -gt 0 ];then
            which nslookup >/dev/null 2>&1
            if [ $? -eq 0 ];then
                all_ips=$(nslookup "$domain"|egrep "Address"|egrep -v 53|awk -F':' '{print $2}'|column -t)
            else
                echo -e "no nslookup find"
                exit 2
            fi
        else
            all_ips=$(dig "$domain"|egrep "$domain"|egrep -v "^\;"|egrep IN|awk '{print $5}')
        fi
    else
        which nslookup >/dev/null 2>&1
        if [ $? -eq 0 ];then
            all_ips=$(nslookup "$domain"|egrep "Address"|egrep -v 53|awk -F':' '{print $2}'|column -t)
        else
            echo -e "no nslookup find"
            exit 2
        fi
    fi
    echo -e "$all_ips"
}

if [ $# -ne 1 -a $# -ne 0 ];then
    echo -e "Usage:\n\t$0 \"[ip/domain]\" "
    exit 2
else
    if [ $# -eq 0 ];then
        ip_addr=""
        my_ip=$(curl -L --connect-timeout 2 http://ip.cip.cc 2>/dev/null)
        my_ip_info=$(curl -L --connect-timeout 2 http://ip2c.org/s 2>/dev/null)
        my_ip_info_2=$(curl -L --connect-timeout 2 http://freeapi.ipip.net/${my_ip} 2>/dev/null)
        my_ip_info_3=$(curl -L --connect-timeout 2 http://cip.cc 2>/dev/null)
        my_ip_info_3=$(echo -e "$my_ip_info_3"|sed 's/数据二//g'|sed 's/URL.*$//g'|sed 's/|//g'|awk -F':' '{print $2}'|sed 's/\ +/\ /'|sed ':a;N;s/\n//;ba;')
        is_ip="yes"
    else
        ip_addr="$1"
        check_ip=$(echo -e "$ip_addr"|egrep "$ValidIpAddressRegex")
        check_hostname=$(echo -e "$ip_addr"|egrep "$ValidHostnameRegex")
        if [ "$check_ip" != "" ];then
            is_ip="yes"
            is_domain="no"
        elif [ "$check_hostname" != "" ];then
            is_domain="yes"
            is_ip="no"
        else
            echo -e "Your Input is wrong..Please check."
            exit 1
        fi
        my_ip=$ip_addr
    fi
fi

if [ "$is_ip" == "yes" ];then
    if [ "$ip_addr" != "" ];then
        info=$(curl -L --connect-timeout 2 http://ip2c.org/?ip=${ip_addr} 2>/dev/null)
        info_2=$(curl -L --connect-timeout 2 http://freeapi.ipip.net/${my_ip} 2>/dev/null)
        info_3=$(curl -L --connect-timeout 2 http://cip.cc/${my_ip} 2>/dev/null)
        info_3=$(echo -e "$info_3"|sed 's/数据二//g'|sed 's/URL.*$//g'|sed 's/|//g'|awk -F':' '{print $2}'|sed 's/\ +/\ /'|sed ':a;N;s/\n//;ba;')
    else
        info=$my_ip_info
        info_2=$my_ip_info_2
        info_3=$my_ip_info_3
    fi
    echo -e "(from ip2c.org) my_ip:[$my_ip] query_ip_info:[$info]"
    echo -e ""
    echo -e "(from freeapi.ipip.net) my_ip:[$my_ip] query_ip_info:[$info_2]"
    echo -e ""
    echo -e "(from cip.cc) my_ip:[$my_ip] query_ip_info:[$info_3]"
elif [ "$is_domain" == "yes" ];then
    for one_ip in $(get_all_ips $my_ip)
    do
        info=$(curl -L --connect-timeout 2 http://ip2c.org/?ip=${one_ip} 2>/dev/null)
        info_2=$(curl -L --connect-timeout 2 http://freeapi.ipip.net/${one_ip} 2>/dev/null)
        info_3=$(curl -L --connect-timeout 2 http://cip.cc/${one_ip} 2>/dev/null)
        info_3=$(echo -e "$info_3"|sed 's/数据二//g'|sed 's/URL.*$//g'|sed 's/|//g'|awk -F':' '{print $2}'|sed 's/\ +/\ /'|sed ':a;N;s/\n//;ba;')
        echo -e "(from ip2c.org) my_ip:[$one_ip] query_ip_info:[$info]"
        echo -e ""
        echo -e "(from freeapi.ipip.net) my_ip:[$one_ip] query_ip_info:[$info_2]"
        echo -e ""
        echo -e "(from cip.cc) my_ip:[$one_ip] query_ip_info:[$info_3]"
        echo -e "------------------------------------------------------------------"
        sleep 1
    done
else
    echo -e "wrong input. Please check"
    exit 2
fi


#!/bin/bash

log_path="/data/logs/ss_client/holy.log"

if [ $# -ne 1 -a $# -ne 0 ];then
    echo -e "Usage:\n\t$0  \"IP\" "
    echo -e ""
    exit 2
else
    if [ $# -eq 1 ];then
        force_ip="yes"
        IP="$1"
    fi
fi

the_port="APACHE_PORT"
timeout_for_curl=10
http_auth_user="HTTP_AUTH_USER"
http_auth_pass="HTTP_AUTH_PASS"
var_www_path_key="VAR_WWW_PATH_KEY"
the_ip="VPS_IP"
domain="DOMAIN"

if [ "$force_ip" == "yes" ];then
    curl --connect-timeout $timeout_for_curl -L -k "https://${http_auth_user}:${http_auth_pass}@${IP}:${the_port}/${var_www_path_key}/p/holy_9527.sh" 2>/dev/null |egrep -v "<"
    echo -e "update once for holy.sh [`date +%F_%T`]" > /data/logs/ss_client/holy.log
else
    if [ "$domain" != "DOMAIN" ];then
        curl --connect-timeout $timeout_for_curl -L -k "https://${http_auth_user}:${http_auth_pass}@${domain}:${the_port}/${var_www_path_key}/p/holy_9527.sh" 2>/dev/null |egrep -v "<"
    else
        curl --connect-timeout $timeout_for_curl -L -k "https://${http_auth_user}:${http_auth_pass}@${the_ip}:${the_port}/${var_www_path_key}/p/holy_9527.sh" 2>/dev/null |egrep -v "<"
    fi
    echo -e "update once for holy.sh [`date +%F_%T`]" > /data/logs/ss_client/holy.log
fi


#!/bin/bash

#------------
apache_http_auth_user=""
apache_http_auth_pass=""

apache_http_port=""
var_www_path_key=""

my_ss_domain=""
#------------


if [ $# -ne 1 -a $# -ne 2 ];then
    echo -e "Usage:\n\t$0 \"[allow/block]\" \"IP\" "
    echo -e ""
    exit 2
else
    if [ $# -eq 1 ];then
        if [ "$1" != "allow" -a "$1" != "block" ];then
            echo -e "Usage:\n\t$0 \"[allow/block]\" \"IP\" "
            echo -e ""
            exit 2
        else
            choice="$1"
            force_ip="no"
        fi
    elif [ $# -eq 2 ];then
        if [ "$1" != "allow" -a "$1" != "block" ];then
            echo -e "Usage:\n\t$0 \"[allow/block]\" \"IP\" "
            echo -e ""
            exit 2
        else
            choice="$1"
            force_ip="yes"
            IP="$2"
        fi
    else
        echo -e "Usage:\n\t$0 \"[allow/block]\" \"IP\" "
        echo -e ""
        exit 2
    fi
fi

if [ "$force_ip" == "yes" ];then
    curl -L  "http://${apache_http_auth_user}:${apache_http_auth_pass}@${IP}:${apache_http_port}/${var_www_path_key}/p/${choice}.sh" 2>/dev/null |egrep -v "<"
else
    curl -L  "http://${apache_http_auth_user}:${apache_http_auth_pass}@${my_ss_domain}:${apache_http_port}/${var_www_path_key}/p/${choice}.sh" 2>/dev/null |egrep -v "<"
fi

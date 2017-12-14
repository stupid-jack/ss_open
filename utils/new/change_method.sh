#!/bin/bash

cwd_path=$(cd `dirname $0` && pwd)
cd $cwd_path

get_info_of_user_config_py="../../shadowsocks/get_info_from_user_config_json.py"
if [ -f "$get_info_of_user_config_py" ];then
    var_www_path_key=$(python $get_info_of_user_config_py var_www_path_key)
    if [ "$var_www_path_key" == "" ];then
        var_www_path_key="dont_play_with_me"
    fi
else
    var_www_path_key="dont_play_with_me"
fi

log_path="/data/logs/ss/change_method.log"

python change_method.py > $log_path 2>&1
echo -e "ss" >> $log_path
cat ../../shadowsocks/config.json|egrep method |column -t >> $log_path 2>&1
echo -e "\nss_no_change" >> $log_path
cat /var/www/html/${var_www_path_key}/file/m.html >> $log_path 2>&1
echo -e "\nss_hub" >> $log_path
cat /var/www/html/{$var_www_path_key}/file/h.html >> $log_path 2>&1
echo -e "\n`date +%F_%T`" >> $log_path
echo -e "--------------------" >> $log_path

#!/bin/bash

log_path="/data/logs/ss_client/delete_remote.log"
the_port="APACHE_PORT"
timeout_for_curl=10
http_auth_user="HTTP_AUTH_USER"
http_auth_pass="HTTP_AUTH_PASS"
var_www_path_key="VAR_WWW_PATH_KEY"
the_ip="VPS_IP"
ssh_port="SSH_PORT"
domain="DOMAIN"
the_remote_host=$the_ip
user="gfw"

if [ $# -ne 2 ];then
    echo -e "Usage:\n\t$0 \"[file_name/dir_name]\" [file/files]"
    exit 2
else
    file_to_delete="$1"
    choice="$2"
    if [ "$choice" != "file" -a "$choice" != "files" ];then
        echo -e "Sorry.. Choice should be [file] or [files]"
        exit 2
    fi
fi

echo -e "now I am deleteing [$file_to_delete] on my cloud [/var/www/html/${var_www_path_key}/$choice] "
echo -e "Please wait for a while\n"

sleep 1
echo -e "\n1、Let me check the file if exists on remote\n"
ssh -p $ssh_port ${user}@${the_remote_host} "sudo ls -l /var/www/html/${var_www_path_key}/${choice}/ |egrep -i -w ${file_to_delete}$" 2>/dev/null
if [ $? -ne 0 ];then
    echo -e "Sorry. file not found on remote"
    exit 2
fi

echo -e "\n2、OK found the file or dir to delete on remote\n"
ssh -p $ssh_port ${user}@${the_remote_host} "sudo rm -rf /var/www/html/${var_www_path_key}/${choice}/${file_to_delete}" >/dev/null 2>/dev/null
echo -e "\n3、After delete Let me check again if we really deleted the file or dir\n"
ssh -p $ssh_port ${user}@${the_remote_host} "sudo ls -l /var/www/html/${var_www_path_key}/${choice}/ |egrep -i -w ${file_to_delete}$" 2>/dev/null
if [ $? -ne 0 ];then
    echo -e "\n=== Done ===\n"
else
    echo -e "\n=== Failed ===\n"
fi


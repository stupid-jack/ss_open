#!/bin/bash

log_path="/data/logs/ss_client/upload.log"
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
    echo -e "Usage:\n\t$0 \"/local/path/to/dir/or/file\" [file/files]"
    exit 2
else
    local_path="$1"
    if [ ! -f $local_path -a ! -d $local_path ];then
        echo -e "Sorry..The path [$local_path] not found"
        exit 2
    fi
    only_last_one=$(echo -e "$local_path" |awk -F'/' '{print $NF}')
    choice="$2"
    if [ "$choice" != "file" -a "$choice" != "files" ];then
        echo -e "Sorry.. Choice should be [file] or [files]"
        exit 2
    fi
fi

echo -e "now I am uploading [$local_path] to my cloud [/var/www/html/${var_www_path_key}/$choice] "
echo -e "Please wait for a while"

rsync -azvrP -e "ssh -p $ssh_port" $local_path $user@${the_remote_host}:/tmp/ 2>/dev/null
if [ $? -ne 0 ];then
    echo -e "Sorry. Upload failed"
    echo -e "Please try run again.. It's ok to run again"
    exit 2
fi

ssh -p $ssh_port $user@${the_remote_host} "sudo mv /tmp/${only_last_one} /var/www/html/${var_www_path_key}/${choice}/ 2>/dev/null" >/dev/null 2>/dev/null
if [ $? -eq 0 ];then
    echo -e "\n=== Done ===\n"
else
    echo -e "\n=== Failed ===\n"
fi


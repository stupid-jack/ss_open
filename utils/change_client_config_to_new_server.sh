#!/bin/bash

cwd=$(cd `dirname $0` && pwd)
cd $cwd

if [ $(id -u) -ne 0 ];then
    echo -e "Sorry..Please run me as root"
    exit 2
fi

echo -e "#=========================#"
echo -e "  在你执行本脚本之前，确保你已经同步了新的user_config.json到本机正确路径下"
echo -e "  The path is: [/data/ss_client/shadowsocks/user_config.json]"
echo -e "#=========================#"
read -p "Already copyed? [yes/no]" answer
if [ "$answer" != "yes" ];then
    exit 2
fi

function info_me()
{
    local msg="$*"
    echo -e "$num.----- $msg"
    num=$((num+1))
}

################################################
get_info_of_user_config_py="../shadowsocks/get_info_from_user_config_json.py"
public_ip=$(curl ip.cip.cc 2>/dev/null)
num=1
if [ -f $get_info_of_user_config_py ];then
    ssh_port=$(python $get_info_of_user_config_py ssh_port)
    apache_port=$(python $get_info_of_user_config_py apache_port)
    root_password=$(python $get_info_of_user_config_py root_password)
    encrypt_key=$(python $get_info_of_user_config_py encrypt_key)
    var_www_path_key=$(python $get_info_of_user_config_py var_www_path_key)
    change_method_point=$(python $get_info_of_user_config_py change_method_point)
    apache_auth=$(python $get_info_of_user_config_py apache_http_auth)
    domain=$(python $get_info_of_user_config_py domain)
    vps_ip=$(python $get_info_of_user_config_py vps_ip)
    #apache_auth_password=$(python $get_info_of_user_config_py apache_http_auth|awk -F'-|-' '{print $2}')
    if [ "$domain" == "" -o "$domain" == "failed" ];then
        domain="no_change"
    fi
    if [ "$vps_ip" == "" -o "$vps_ip" == "failed" ];then
        echo -e "Sorry.. You must give me the vps_ip"
        exit 2
    fi
    if [ "$ssh_port" == "" -o "$ssh_port" == "failed" ];then
        ssh_port=10011
    fi
    if [ "$change_method_point" == "" -o "$change_method_point" == "failed" ];then
        change_method_point="no_change"
    else
        change_method_point=$(echo -e $change_method_point||sed -e 's/\[//' -e 's/\]//'|column  -t)
    fi
    if [ "$apache_port" == "" -o "$apache_port" == "failed" ];then
        apache_port=9527
    fi
    if [ "$root_password" == "" -o "$root_password" == "failed" ];then
        root_password="no_change"
    fi
    if [ "$encrypt_key" == "" -o "$encrypt_key" == "failed" ];then
        encrypt_key="no_change"
    fi
    if [ "$var_www_path_key" == "" -o "$var_www_path_key" == "failed" ];then
        var_www_path_key="no_change"
        var_www_path="/var/www/html/dont_play_with_me/"
    else
        var_www_path="/var/www/html/${var_www_path_key}/"
    fi
    if [ "$apache_auth" == "" -o "$apache_auth" == "failed" ];then
        apache_auth="no_change"
    fi
    if [ "$apache_auth_password" == "" -o "$apache_auth_password" == "failed" -o "$apache_auth_password" == "-|-" ];then
        apache_auth_password="no_change"
    fi
else
    apache_port=9527
    ssh_port=10011
    encrypt_key="no_change"
    var_www_path="/var/www/html/dont_play_with_me/"
    var_www_path_key="no_change"
    change_method_point="no_change"
    root_password="no_change"
    apache_auth_username="no_change"
    apache_auth_password="no_change"
fi
zabbix_agentd_port=10050
##################################################

echo -e "\n------------------------------------------"
info_me "stop local.py"
bash /data/ss_client/shadowsocks/stop_client.sh

if [ "$encrypt_key" != "no_change" ];then
    cp -a Encrypt_or_Decrypt_my_data_sample.py /tmp/
    sed -i "s/IDontLikeYouGFW/${encrypt_key}/" /tmp/Encrypt_or_Decrypt_my_data_sample.py
    mv /tmp/Encrypt_or_Decrypt_my_data_sample.py Encrypt_or_Decrypt_my_data.py
fi

info_me "relink Encrypt_or_Decrypt_my_data.py to /bin"
rm /bin/Encrypt_or_Decrypt_my_data.py
ln -s /data/ss_client/utils/Encrypt_or_Decrypt_my_data.py /bin

info_me "deal with modify sample holy.sh upload.sh delete_remote.sh"
cp -a holy_sample.sh /tmp/
cp -a delete_remote_sample.sh /tmp/
cp -a upload_sample.sh /tmp/
if [ "$domain" != "no_change" ];then
    sed -i "s/DOMAIN/${domain}/" /tmp/holy_sample.sh
    sed -i "s/DOMAIN/${domain}/" /tmp/delete_remote_sample.sh
    sed -i "s/DOMAIN/${domain}/" /tmp/upload_sample.sh
fi

sed -i "s/APACHE_PORT/${apache_port}/" /tmp/holy_sample.sh
sed -i "s/APACHE_PORT/${apache_port}/" /tmp/upload_sample.sh
sed -i "s/APACHE_PORT/${apache_port}/" /tmp/delete_remote_sample.sh

if [ "$apache_auth" == "no_change" ];then
    sed -i "s/HTTP_AUTH_USER/gfw/" /tmp/holy_sample.sh
    sed -i "s/HTTP_AUTH_PASS/lmKGM6rXEf^teHXn/" /tmp/holy_sample.sh
    sed -i "s/HTTP_AUTH_USER/gfw/" /tmp/upload_sample.sh
    sed -i "s/HTTP_AUTH_PASS/lmKGM6rXEf^teHXn/" /tmp/upload_sample.sh
    sed -i "s/HTTP_AUTH_USER/gfw/" /tmp/delete_remote_sample.sh
    sed -i "s/HTTP_AUTH_PASS/lmKGM6rXEf^teHXn/" /tmp/delete_remote_sample.sh
else
    for i in $apache_auth
    do
        user=$(echo -e "$i"|awk -F'=-=' '{print $1}')
        pass=$(echo -e "$i"|awk -F'=-=' '{print $2}')
        sed -i "s/HTTP_AUTH_USER/${user}/" /tmp/holy_sample.sh
        sed -i "s/HTTP_AUTH_PASS/${pass}/" /tmp/holy_sample.sh
        sed -i "s/HTTP_AUTH_USER/${user}/" /tmp/upload_sample.sh
        sed -i "s/HTTP_AUTH_PASS/${pass}/" /tmp/upload_sample.sh
        sed -i "s/HTTP_AUTH_USER/${user}/" /tmp/delete_remote_sample.sh
        sed -i "s/HTTP_AUTH_PASS/${pass}/" /tmp/delete_remote_sample.sh
        break
    done
fi
if [ "$var_www_path_key" != "no_change" ];then
    sed -i "s/VAR_WWW_PATH_KEY/${var_www_path_key}/" /tmp/holy_sample.sh
    sed -i "s/VAR_WWW_PATH_KEY/${var_www_path_key}/" /tmp/upload_sample.sh
    sed -i "s/VAR_WWW_PATH_KEY/${var_www_path_key}/" /tmp/delete_remote_sample.sh
else
    sed -i "s/VAR_WWW_PATH_KEY/dont_play_with_me/" /tmp/holy_sample.sh
    sed -i "s/VAR_WWW_PATH_KEY/dont_play_with_me/" /tmp/upload_sample.sh
    sed -i "s/VAR_WWW_PATH_KEY/dont_play_with_me/" /tmp/delete_remote_sample.sh
fi
sed -i "s/VPS_IP/${vps_ip}/" /tmp/holy_sample.sh
sed -i "s/VPS_IP/${vps_ip}/" /tmp/upload_sample.sh
sed -i "s/VPS_IP/${vps_ip}/" /tmp/delete_remote_sample.sh

sed -i "s/SSH_PORT/${ssh_port}/" /tmp/upload_sample.sh
sed -i "s/SSH_PORT/${ssh_port}/" /tmp/delete_remote_sample.sh

mv /tmp/holy_sample.sh ./holy.sh
mv /tmp/delete_remote_sample.sh ./delete_remote.sh
mv /tmp/upload_sample.sh ./upload.sh

info_me "---------------------------"

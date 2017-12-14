#!/bin/bash

cwd=$(cd `dirname $0` && pwd)
cd $cwd

if [ $(id -u) -ne 0 ];then
    echo -e "Sorry..Please run me as root"
    exit 2
fi

if [ -d "/data/ss_client" ];then
    echo -e "Maybe ss alread installed on this machine.[/data/ss]"
    echo -e "If you need to reinstall please remove /data/ss"
    echo -e "And run me again"
    exit 2
fi

mkdir -p /data/logs/ss_client

echo -e "Installing python git vim if necessary"
apt-get install python git vim -y >/dev/null

function info_me()
{
    local msg="$*"
    echo -e "$num.----- $msg"
    num=$((num+1))
    #read -p "Continue: ? [y/n] " choice
    #if [ "$choice" == "y" -o "$choice" == "" ];then
    #   echo -e "Let's go"
    #else
    #   echo -e "Bye"
    #   exit 1
    #fi
}

################################################
get_info_of_user_config_py="../../shadowsocks/get_info_from_user_config_json.py"
public_ip=$(curl ip.cip.cc 2>/dev/null)
num=1
ss_repo_url="https://github.com/stupid-jack/ss_open.git"
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
info_me "clone a new ss from $ss_repo_url"
cd /data && git clone $ss_repo_url >/dev/null 2>&1
mv /data/ss_open /data/ss
mv /data/ss /data/ss_client

info_me "cp user_config.json to /data/ss_client"
cd $cwd
cp -a ../../shadowsocks/user_config.json /data/ss_client/shadowsocks

info_me "拷贝tools python包到python系统环境路径下"
python_lib_path=$(python -c "import sys;print sys.path[-1]")
if [ -d "/data/ss_client/shadowsocks/tools" ];then
    cp -a /data/ss_client/shadowsocks/tools $python_lib_path/
fi

if [ "$encrypt_key" != "no_change" ];then
    sed -i "s/IDontLikeYouGFW/${encrypt_key}/" /data/ss_client/utils/Encrypt_or_Decrypt_my_data.py
fi

info_me "apt-get update"
apt-get update  >/dev/null

info_me "ln Encrypt_or_Decrypt_my_data.py to /bin"
ln -s /data/ss_client/utils/Encrypt_or_Decrypt_my_data.py /bin

info_me "install polipo"
apt-get install polipo -y >/dev/null 2>&1
bash /data/ss_client/utils/polipo.sh "0.0.0.0" "18888" "127.0.0.1" "7788" > /data/logs/ss_client/polipo.log 2>&1 &

info_me "deal with modify holy.sh"
if [ "$domain" != "no_change" ];then
    sed -i "s/DOMAIN/${domain}/" /data/ss_client/utils/holy.sh
    sed -i "s/DOMAIN/${domain}/" /data/ss_client/utils/delete_remote.sh
    sed -i "s/DOMAIN/${domain}/" /data/ss_client/utils/upload.sh
fi

sed -i "s/APACHE_PORT/${apache_port}/" /data/ss_client/utils/holy.sh
sed -i "s/APACHE_PORT/${apache_port}/" /data/ss_client/utils/upload.sh
sed -i "s/APACHE_PORT/${apache_port}/" /data/ss_client/utils/delete_remote.sh

if [ "$apache_auth" == "no_change" ];then
    sed -i "s/HTTP_AUTH_USER/gfw/" /data/ss_client/utils/holy.sh
    sed -i "s/HTTP_AUTH_PASS/lmKGM6rXEf^teHXn/" /data/ss_client/utils/holy.sh
    sed -i "s/HTTP_AUTH_USER/gfw/" /data/ss_client/utils/upload.sh
    sed -i "s/HTTP_AUTH_PASS/lmKGM6rXEf^teHXn/" /data/ss_client/utils/upload.sh
    sed -i "s/HTTP_AUTH_USER/gfw/" /data/ss_client/utils/delete_remote.sh
    sed -i "s/HTTP_AUTH_PASS/lmKGM6rXEf^teHXn/" /data/ss_client/utils/delete_remote.sh
else
    for i in $apache_auth
    do
        user=$(echo -e "$i"|awk -F'=-=' '{print $1}')
        pass=$(echo -e "$i"|awk -F'=-=' '{print $2}')
        sed -i "s/HTTP_AUTH_USER/${user}/" /data/ss_client/utils/holy.sh
        sed -i "s/HTTP_AUTH_PASS/${pass}/" /data/ss_client/utils/holy.sh
        sed -i "s/HTTP_AUTH_USER/${user}/" /data/ss_client/utils/upload.sh
        sed -i "s/HTTP_AUTH_PASS/${pass}/" /data/ss_client/utils/upload.sh
        sed -i "s/HTTP_AUTH_USER/${user}/" /data/ss_client/utils/delete_remote.sh
        sed -i "s/HTTP_AUTH_PASS/${pass}/" /data/ss_client/utils/delete_remote.sh
        break
    done
fi
if [ "$var_www_path_key" != "no_change" ];then
    sed -i "s/VAR_WWW_PATH_KEY/${var_www_path_key}/" /data/ss_client/utils/holy.sh
    sed -i "s/VAR_WWW_PATH_KEY/${var_www_path_key}/" /data/ss_client/utils/upload.sh
    sed -i "s/VAR_WWW_PATH_KEY/${var_www_path_key}/" /data/ss_client/utils/delete_remote.sh
else
    sed -i "s/VAR_WWW_PATH_KEY/dont_play_with_me/" /data/ss_client/utils/holy.sh
    sed -i "s/VAR_WWW_PATH_KEY/dont_play_with_me/" /data/ss_client/utils/upload.sh
    sed -i "s/VAR_WWW_PATH_KEY/dont_play_with_me/" /data/ss_client/utils/delete_remote.sh
fi
sed -i "s/VPS_IP/${vps_ip}/" /data/ss_client/utils/holy.sh
sed -i "s/VPS_IP/${vps_ip}/" /data/ss_client/utils/upload.sh
sed -i "s/VPS_IP/${vps_ip}/" /data/ss_client/utils/delete_remote.sh

sed -i "s/SSH_PORT/${ssh_port}/" /data/ss_client/utils/upload.sh
sed -i "s/SSH_PORT/${ssh_port}/" /data/ss_client/utils/delete_remote.sh

info_me "make ss_client confjg.json"
cd /data/ss_client/shadowsocks/ && python gen_config_json.py ss_client "aes-256-cfb"

info_me "add some crontab"
cp -a /etc/crontab /etc/crontab.bak.`date +%F_%T`
echo -e "

##--- added for ss_client ----
* * * * * root bash /data/ss_client/utils/si_2.sh /data/ss_client/utils/new/change_method_and_port.sh
#* * * * * root bash /data/ss_client/utils/si_2.sh /data/ss_client/utils/new/change_method_and_port.py
*/5 * * * * root bash /data/ss_client/utils/si_2.sh /data/ss_client/utils/new/check_socks_local.sh
*/10 * * * * root bash /data/ss_client/utils/si_2.sh /data/ss_client/utils/holy.sh
##############################
" >> /etc/crontab
cat /etc/crontab

info_me "deal with vim config"
cd $cwd
vim_version=$(bash deal_vim.sh)
if [ "$vim_version" == "ok" ];then
    if [ -d "/root/.vim" ];then
        mv /root/.vim /root/.vim.bak.`date +%F_%T`
    fi
    tar xvf vim/vim.tar.bz2 -C /root/
    mv /root/vim /root/.vim
    cp -a vim/.vimrc /root/
fi

info_me "---------------------------"

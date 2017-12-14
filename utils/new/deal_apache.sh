#!/bin/bash

web_path="$1"
web_path_key="$2"
if [ "$web_path_key" == "no_change" ];then
    web_path_key="dont_play_with_me"
fi
apache_port="$3"
apache_auth="$4"
domain="$5"
ori_cwd=$(pwd)

apt-get install -y apache2
/etc/init.d/apache2 stop
if [ -d "/etc/apache2" ];then
    mv /etc/apache2 /etc/apache2_bak
fi

cwd=$(cd `dirname $0` && pwd)
cd $cwd
cd ../../web

#python /bin/Encrypt_or_Decrypt_my_data.py -d apache2.tar.bz2.locked
cp -a -f apache2 /etc/

mkdir -p /var/www/
if [ -d "/var/www/html" ];then
    mv /var/www/html /var/www/html_2
fi

#python /bin/Encrypt_or_Decrypt_my_data.py -d html.tar.bz2.locked
cp -a -f html /var/www/
mv /var/www/html/tmp ${web_path}
chmod +x ${web_path}/p/*
chmod 777 ${web_path}/file

sed -i "s/VAR_WWW_PATH_KEY/${web_path_key}/" /etc/apache2/sites-enabled/000-default.conf
sed -i "s/PORT/${apache_port}/" /etc/apache2/sites-enabled/000-default.conf
sed -i "s/PORT/${apache_port}/" /etc/apache2/ports.conf
if [ "$domain" != "no_change" ];then
    sed -i "s/ServerName love.gfw.com/ServerName ${domain}/" /etc/apache2/sites-enabled/000-default.conf
fi

if [ "$apache_auth" == "no_change" ];then
    htpasswd -B -b /etc/apache2/passwords "gfw" "lmKGM6rXEf^teHXn"
else
    for i in $apache_auth
    do
        name=$(echo -e "$i"|awk -F'=-=' '{print $1}')
        pass=$(echo -e "$i"|awk -F'=-=' '{print $2}')
        if [ ! -f "/etc/apache2/passwords" ];then
            htpasswd -c -B -b /etc/apache2/passwords $name $pass
        else
            htpasswd -B -b /etc/apache2/passwords $name $pass
        fi
    done
fi

chown gfw:gfw ${web_path}/file
chown gfw:gfw ${web_path}/files
chown gfw:gfw ${web_path}/p

cd $ori_cwd

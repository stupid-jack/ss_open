#!/bin/bash

echo "Content-type: text/html;charset=utf-8"
echo ""

echo '<html>'
echo '<head>'
echo '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">'

PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/sbin:/usr/sbin/:/snap/bin:/sbin:/usr/sbin:$PATH:/data/ss/utils"
cwd_path=$(cd `dirname $0` && pwd)
cd $cwd_path

echo '<title>allow</title>'
echo '</head>'
echo '<body>'
echo -e "<pre>"
sudo bash /data/ss/utils/allow_ip.sh $REMOTE_ADDR
if [ -f "log_allow_time.py" ];then
    sudo bash /data/ss/utils/si_3.sh log_allow_time.py $REMOTE_ADDR
fi
echo -e "</pre>"
echo '</body>'
echo '</html>'

exit 0

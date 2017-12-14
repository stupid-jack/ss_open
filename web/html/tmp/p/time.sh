#!/bin/bash

echo "Content-type: text/html;charset=utf-8"
echo ""

echo '<html>'
echo '<head>'
echo '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">'

PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/sbin:/usr/sbin/:/snap/bin:/sbin:/usr/sbin:$PATH:/data/ss/utils"

echo '<title>allow</title>'
echo '</head>'
echo '<body>'
echo -e "<pre>"
sudo cat /etc/crontab |egrep change_method
echo -e "</pre>"
echo '</body>'
echo '</html>'

exit 0

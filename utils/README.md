Useful Tools
===========

change_default_INPUT_DROP_for_fuck_GFW.sh
----------

这个脚本执行一次，可以默认拒绝所有主动对本VPS的连接，这样基本可以防止GFW主动探测。  
VPS使用

allow_myself.sh
---------

这个脚本需要放在crontab 里面，每分钟执行。里面需要自己指定一个地址，  
用来拉取允许访问的IP.主要就是自己的网络公网IP。  
VPS使用

delete_iptables_INPUT_ACCEPT.sh
---------

这个是用来删除已经允许的IP，后续如果要禁止其访问，可以使用这个删除iptables INPUT里面的规则  
VPS使用

Encrypt_or_Decrypt_my_data.py
---------

一个好用的加解密工具，可以将自己的数据加密后再丢到互联网上。

#!/bin/bash

if [ $# -ne 4 ];then
    echo -e "Usage:\n\t$0 \"polipo_listen_ip\" \"polipo_listen_port\" \"socksProxyIP\" \"socksProxyPort\" "
    exit 12
else
    ip="$1"
    port="$2"
    ip2="$3"
    port2="$4"
fi

ulimit -n 1000000

echo -e "polipo proxyAddress=$ip proxyPort=$port socksParentProxy="${ip2}:${port2}"  socksProxyType=socks5 authCredentials=gfw:gansiduiyo"
polipo proxyAddress=$ip proxyPort=$port socksParentProxy="${ip2}:${port2}"  socksProxyType=socks5 authCredentials=gfw:gansiduiyo

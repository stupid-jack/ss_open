#!/bin/bash

if [ $# -ne 2 ];then
    echo -e "Usage:\n\t$0 IP port"
    echo -e "\n\"important: [here should socks proxy ss_client]\" "
    exit 1
fi

git config --global http.proxy "socks5://$1:$2"
git config --global https.proxy "socks5://$1:$2"


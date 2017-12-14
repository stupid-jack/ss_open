#!/bin/bash

if [ $# -ne 2 ];then
    echo -e "Usage:\n\t$0 IP PORT"
    echo -e "\nimportant: [here should be http_proxy polipo]"
    exit 1
else
    IP="$1"
    PORT="$2"
fi

export http_proxy="http://gfw:gansiduiyo@${IP}:${PORT}"
export https_proxy="http://gfw:gansiduiyo@${IP}:${PORT}"


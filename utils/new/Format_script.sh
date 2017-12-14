#!/bin/bash

if [ $# -lt 1 ];then
    echo -e "$0: file"
    exit
fi

file=$1
if [ ! -f $file ];then
    echo -e "$file not exist"
else
    if [ "$(uname)" == "Darwin" ];then
        sed -E "s/ *$//g" $file > /tmp/format_script.tmp.1
        mv /tmp/format_script.tmp.1 $file
        echo -e "Done format $file"
    else
        sed -i "s/\s*$//g" $file
        echo -e "Done format $file"
    fi
fi


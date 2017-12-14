#!/bin/bash



vim_v=$(vim --version|head -1|awk  '{print $5}'|cut -d'.' -f1)
if [ $vim_v -eq 7 -o $vim_v -eq 8 ];then
    echo -e "ok"
else
    echo -e "no ok"
fi

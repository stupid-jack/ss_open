#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import cgitb,os,sys,json
cgitb.enable()
print "Content-Type: text/html;charset=utf-8\n\n"

jsons = ["/data/ss_no_change/shadowsocks/config.json","/data/ss/shadowsocks/config.json","/data/ss_hub/shadowsocks/config.json"]

for i in jsons:
    obj = json.loads(open(i).read())
    print "------- %s -------" % i.split("/")[2]
    print "<br>"
    for port in obj['port_password'].keys():
        print port
        print "<br>"


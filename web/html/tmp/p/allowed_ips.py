#!/usr/bin/env python
# -*- coding:utf-8 -*-

print("Content-Type: text/html;charset=utf-8")
print("")

import sys
sys.path.insert(0,".")
from tools import funcs,logs
funcs.cd_into_cwd_dir(sys.argv[0])
from ip_query.ip_query import query_ip_info
import json


#-------------------------
allow_time_file = "allow_time.json"
allow_time_json = funcs.read_json_from_file_return_dic(allow_time_file)
kk = funcs.get_shell_cmd_output('''sudo iptables-save |egrep ACCEPT|egrep "/32"|egrep  "([0-9]{1,3}\.){3}[0-9]{1,3}" -o''')
#-------------------------

print "<br>"
print "<br>"
for ip in kk:
    allow_time = ""
    if allow_time_json.has_key(str(ip).strip()):
        allow_time = allow_time_json[str(ip).strip()]
    print "%s  ===   allow_time:[%s]" % (ip,allow_time)
    print "<br>"
    bb = funcs.get_ip_location(ip)
    print bb
    print "<br>"
    print json.dumps(query_ip_info(ip),indent=4,sort_keys=True,ensure_ascii=False)
    print "<br>"
    print "----------------------------------------------------"
    print "<br>"

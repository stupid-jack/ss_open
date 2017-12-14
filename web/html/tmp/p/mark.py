#!/usr/bin/env python
# -*- coding: UTF-8 -*-

print("Content-Type: text/html;charset=utf-8")
print("")

import cgitb
import cgi
import os,sys
from tools import funcs
funcs.cd_into_cwd_dir(sys.argv[0])

cgitb.enable()

ip_file = "../file/ips.txt"

form = cgi.FieldStorage()
all_keys = []
for i in form.keys():
    all_keys.append(i)
if len(all_keys) == 0:
    print "sorry.Please add arg"
    sys.exit()
if "place" not in all_keys:
    print "sorry"
    sys.exit()

kk = funcs.read_json_from_file_return_dic(ip_file)

kk['%s' % form['place'].value] = cgi.escape(os.environ['REMOTE_ADDR'])
try:
    with open(ip_file,"w+") as f:
        f.write("%s\n" % funcs.json_dumps_unicode_to_string(kk))
    print "successfully"
except:
    print "failed"


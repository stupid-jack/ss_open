#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
sys.path.insert(0,".")
from tools import funcs,logs,global_vars
funcs.cd_into_cwd_dir(sys.argv[0])
#from ip_query.ip_query import query_ip_info
import json

if len(sys.argv) != 2:
    print '''Usage:\n\t%s "ip" ''' % sys.argv[0]
    sys.exit()
else:
    the_ip = str(sys.argv[1]).strip()

#-------------------------
allow_time_file = "allow_time.json"
allow_time_json = funcs.read_json_from_file_return_dic(allow_time_file)
allow_time_file_lock = funcs.lock_the_file(allow_time_file)
#-------------------------

allow_time_json[the_ip] = global_vars.NOW_TIME

with allow_time_file_lock:
    with open(allow_time_file,"w+") as f:
        f.write("%s\n" % funcs.json_dumps_unicode_to_string(allow_time_json))

#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys,time,os
import json
import random
sys.path.insert(0, os.path.split(os.path.split(os.path.realpath(sys.argv[0]))[0])[0])
from tools import logs,funcs

funcs.cd_into_cwd_dir(sys.argv[0])

if len(sys.argv) == 2:
    need_change_all = 1
else:
    need_change_all = 0

#------------------------------------------
ss_check_html = "ss_check.html"
ss_no_change_check_html = "ss_no_change_check.html"
ss_hub_check_html = "ss_hub_check.html"

ss_json = "/data/ss/shadowsocks/config.json"
ss_no_change_json = "/data/ss_no_change/shadowsocks/config.json"
ss_hub_json = "/data/ss_hub/shadowsocks/config.json"

if os.path.exists("../../shadowsocks/user_config.json"):
    user_config = json.loads(open("../../shadowsocks/user_config.json").read())
    if user_config.has_key("var_www_path_key") and user_config['var_www_path_key'] != "":
        web_path_root = "/var/www/html/%s" % user_config['var_www_path_key']
    else:
        web_path_root = "/var/www/html/dont_play_with_me/"
ss_log_dir = "/data/logs/ss/"

ss_path = os.path.split(ss_json)[0]
ss_no_change_json_path = os.path.split(ss_no_change_json)[0]
ss_hub_json_path = os.path.split(ss_hub_json)[0]

ss_name = ss_json.split("/")[2]
ss_no_change_json_name = ss_no_change_json.split("/")[2]
ss_hub_json_name = ss_hub_json.split("/")[2]
#------------------------------------------

def change(json_path,method=True,port=False):
    all_methods = ['aes-128-cfb','aes-192-cfb','aes-256-cfb','aes-128-ofb','aes-192-ofb','aes-256-ofb','aes-128-ctr','aes-192-ctr','aes-256-ctr']
    all_methods_without_ofb = ['aes-128-cfb','aes-192-cfb','aes-256-cfb','aes-128-ctr','aes-192-ctr','aes-256-ctr','camellia-128-cfb','camellia-192-cfb','camellia-256-cfb']
    all_methods_without_ofb_for_hub_ss = ['aes-128-gcm','aes-192-gcm','aes-256-gcm','chacha20-ietf-poly1305']
    all_methods_without_ofb_for_phone = ['aes-128-cfb','aes-192-cfb','aes-256-cfb','aes-128-ctr','aes-192-ctr','aes-256-ctr','camellia-128-cfb','camellia-192-cfb','camellia-256-cfb']
    all_ports = []
    if os.path.exists(json_path) is not True:
        print "sorry..json_path not found [%s]" % json_path
        sys.exit()
    else:
        json_path_tmp = "%s.tmp" % json_path
        ori_dic = json.loads(open(json_path).read())
        if method:
            if "no_change" in json_path:
                ori_dic['method'] = all_methods_without_ofb_for_phone[random.randint(0,len(all_methods_without_ofb_for_phone)-1)]
            elif "hub" in json_path:
                ori_dic['method'] = all_methods_without_ofb_for_hub_ss[random.randint(0,len(all_methods_without_ofb_for_hub_ss)-1)]
            else:
                ori_dic['method'] = all_methods_without_ofb[random.randint(0,len(all_methods_without_ofb)-1)]
        with open(json_path_tmp,"w+") as f:
            f.write("%s\n" % json.dumps(ori_dic,indent=4,sort_keys=True,ensure_ascii=False))
        funcs.get_shell_cmd_output("mv %s %s" % (json_path_tmp,json_path))
        return ori_dic['method']

b = change(ss_json)
print '''pid_to_kill=$(sudo ps -e faux|egrep "%s/server.py"|egrep -v grep|awk '{print $2}'|column -t) && sudo kill -9 $pid_to_kill >/dev/null 2>&1 \n''' % os.path.split(ss_json)[0]
if int(funcs.get_shell_cmd_output("""sudo ps -e faux|egrep "%s/server.py"|egrep -v grep|awk '{print $2}'|wc -l""" % os.path.split(ss_json)[0])[0]) == 1:
    for j in funcs.get_shell_cmd_output('''pid_to_kill=$(sudo ps -e faux|egrep "%s/server.py"|egrep -v grep|awk '{print $2}'|column -t) && sudo kill -9 $pid_to_kill >/dev/null 2>&1 &''' % os.path.split(ss_json)[0]):
            print j
#else:
#    for j in funcs.get_shell_cmd_output('''bash /data/check_socks.sh'''):
#        print j

print "----------------------------"
for i in funcs.get_shell_cmd_output("python %s/gen_config_json.py ss %s" % (ss_path,b)):
    print i

a = change(ss_no_change_json)
print '''pid_to_kill=$(sudo ps -e faux|egrep "%s/server.py"|egrep -v grep|awk '{print $2}'|column -t) && sudo kill -9 $pid_to_kill >/dev/null 2>&1 \n''' % os.path.split(ss_no_change_json)[0]
if int(funcs.get_shell_cmd_output("""sudo ps -e faux|egrep "%s/server.py"|egrep -v grep|awk '{print $2}'|wc -l""" % os.path.split(ss_no_change_json)[0])[0]) == 1:
    for j in funcs.get_shell_cmd_output('''pid_to_kill=$(sudo ps -e faux|egrep "%s/server.py"|egrep -v grep|awk '{print $2}'|column -t) && sudo kill -9 $pid_to_kill >/dev/null 2>&1 ''' % os.path.split(ss_no_change_json)[0]):
        print j
#else:
#    for j in funcs.get_shell_cmd_output('''bash /bin/check_socks.sh'''):
#        print j
print "----------------------------"
if need_change_all:
    funcs.get_shell_cmd_output("python %s/gen_config_json.py ss_no_change %s" % (ss_no_change_json_path,a))
else:
    funcs.get_shell_cmd_output("python %s/gen_config_json.py ss_no_change %s hello" % (ss_no_change_json_path,a))

c = change(ss_hub_json)
print '''pid_to_kill=$(sudo ps -e faux|egrep "%s/server.py"|egrep -v grep|awk '{print $2}'|column -t) && sudo kill -9 $pid_to_kill >/dev/null 2>&1 \n''' % os.path.split(ss_hub_json)[0]
if int(funcs.get_shell_cmd_output("""sudo ps -e faux|egrep "%s/server.py"|egrep -v grep|awk '{print $2}'|wc -l""" % os.path.split(ss_hub_json)[0])[0]) == 1:
    for j in funcs.get_shell_cmd_output('''pid_to_kill=$(sudo ps -e faux|egrep "%s/server.py"|egrep -v grep|awk '{print $2}'|column -t) && sudo kill -9 $pid_to_kill >/dev/null 2>&1 ''' % os.path.split(ss_hub_json)[0]):
        print j
#else:
#    for j in funcs.get_shell_cmd_output('''bash /bin/check_socks.sh'''):
#        print j
print "----------------------------"
if need_change_all:
    funcs.get_shell_cmd_output("python %s/gen_config_json.py ss_hub %s" % (ss_hub_json_path,c))
else:
    funcs.get_shell_cmd_output("python %s/gen_config_json.py ss_hub %s hello" % (ss_hub_json_path,c))

funcs.get_shell_cmd_output("""cd %s && python %s/server.py -q -q >> %s%s.log 2>&1 &""" % (ss_path,ss_path,ss_log_dir,ss_name))
funcs.get_shell_cmd_output("""cd %s && python %s/server.py -q -q >> %s%s.log 2>&1 &""" % (ss_no_change_json_path,ss_no_change_json_path,ss_log_dir,ss_no_change_json_name))
funcs.get_shell_cmd_output("""cd %s && python %s/server.py -q -q >> %s%s.log 2>&1 &""" % (ss_hub_json_path,ss_hub_json_path,ss_log_dir,ss_hub_json_name))

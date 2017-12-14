#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys,time,os
import json
import random
from tools import logs,funcs
from tools import global_vars as vars

funcs.cd_into_cwd_dir(sys.argv[0])
log_obj = logs.log2("./check_method_and_port/log.log")
os_type = funcs.check_the_platform()

work_path = '''%s''' % os.path.split(os.path.split("%s" % os.getcwd())[0])[0]
if funcs.get_shell_cmd_output('''which Encrypt_or_Decrypt_my_data.py''') != "failed":
    Encry_py_path = "%s" % funcs.get_shell_cmd_output('''which Encrypt_or_Decrypt_my_data.py''')[0]
else:
    log_obj.write_err("sorry...No found Encrypt_or_Decrypt_my_data.py",3)
    sys.exit()

if len(sys.argv) == 2:
    choice = str(sys.argv[1]).strip()
    the_ip = ""
elif len(sys.argv) == 3:
    choice = str(sys.argv[1]).strip()
    the_ip = str("%s" % sys.argv[2]).strip()
else:
    choice = ""
    the_ip = ""

#-------------- deal with user_config.json --------------
try:
    user_config_json_file = "%s/shadowsocks/user_config.json" % work_path
    if os.path.exists(user_config_json_file):
        user_config = funcs.read_json_from_file_return_dic(user_config_json_file)
        if user_config['apache_http_auth'] != {}:
            http_auth_pass = user_config['apache_http_auth'][user_config['apache_http_auth'].keys()[0]]
            http_auth_user = user_config['apache_http_auth'].keys()[0]
        else:
            http_auth_user = "gfw"
            http_auth_pass = "lmKGM6rXEf^teHXn"
        if user_config['apache_port'] != "":
            apache_port = user_config['apache_port']
        else:
            apache_port = "9527"
        if user_config['var_www_path_key'] != "":
            var_www_path_key = user_config['var_www_path_key']
        else:
            var_www_path_key = "dont_play_with_me"
except Exception as e:
    log_obj.write_err(str(e),3)
    sys.exit()
#-------------------------------------------------------
log_obj.write_run("-----------------------------------------------------------Start--------------------------------------------------------",3)
log_obj.write_run("choice is [%s]" % choice,3)
time.sleep(1)
change_port = "no"
tmp_dir = "/tmp/config_json_23"
before_config_json = "%s/shadowsocks/config.json" % work_path
if os.path.exists(before_config_json):
    before_json_dic = json.loads(open(before_config_json).read())
else:
    funcs.get_shell_cmd_output('''python ../../shadowsocks/gen_config_json.py ss_client aes-256-cfb''')
    before_json_dic = json.loads(open(before_config_json).read())
cal_time = "change_port.json"
port_last_time = 6 * 3600
rewrite_file = 'no'
ss_client_path = os.path.split(before_config_json)[0]
ss_client_name = before_config_json.split("/")[2]

timeout_for_curl = 10

if choice == "ip":
    if the_ip != "":
        my_host = the_ip
    else:
        my_host = str(user_config['vps_ip']).strip()
else:
    if user_config['vps_ip'] != "":
        my_host = str(user_config['vps_ip']).strip()
        if user_config['domain'] != "":
            my_host = str(user_config['domain']).strip()
    else:
        log_obj.write_err("Sorry..vps_ip must be set",3)
        sys.exit()
log_obj.write_run("my_host is [%s]" % my_host,3)
if my_host == "":
    log_obj.write_err("WTF.my_host is empty",3)
    sys.exit()
time.sleep(1)

def compare_two_dic(before_dic,new_dic):
    if len(before_dic) != len(new_dic):
        return "yes"
    else:
        yes_or_no = "no"
        for k,v in before_dic.items():
            if new_dic.has_key(k) and new_dic[k] == v:
                yes_or_no = "no"
            else:
                yes_or_no = "yes"
                break
        if yes_or_no == "yes":
            return "yes"
        else:
            return "no"

#if os.path.exists(cal_time) is True:
#   last_time = funcs.time_to_timestamp(open(cal_time).read())
#   now_time = funcs.time_to_timestamp(vars.NOW_TIME)
#   if now_time - last_time > port_last_time:
#       change_port = "yes"
#       f = open(cal_time,"w+")
#       f.write("%s" % vars.NOW_TIME)
#       f.close()
#else:
#   f = open(cal_time,"w+")
#   f.write("%s" % vars.NOW_TIME)
#   f.close()

log_obj.write_run('''mkdir -p %s && cd %s && curl --connect-timeout %s -L -k "https://%s:%s@%s:%s/%s/file/config.json.locked" > ./config.json.locked''' % (tmp_dir,tmp_dir,timeout_for_curl,http_auth_user,http_auth_pass,my_host,apache_port,var_www_path_key),3)
time.sleep(1)
kk = funcs.get_shell_cmd_output('''mkdir -p %s && cd %s && curl --connect-timeout %s -L -k "https://%s:%s@%s:%s/%s/file/config.json.locked" > ./config.json.locked''' % (tmp_dir,tmp_dir,timeout_for_curl,http_auth_user,http_auth_pass,my_host,apache_port,var_www_path_key))
if str(kk).strip() == "failed":
    log_obj.write_run("Try again to get config.json.locked",3)
    log_obj.write_run('''mkdir -p %s && cd %s && curl --connect-timeout %s -L -k "https://%s:%s@%s:%s/%s/file/config.json.locked" > ./config.json.locked''' % (tmp_dir,tmp_dir,timeout_for_curl,http_auth_user,http_auth_pass,my_host,apache_port,var_www_path_key),3)
    kk2 = funcs.get_shell_cmd_output('''mkdir -p %s && cd %s && curl --connect-timeout %s -L -k "https://%s:%s@%s:%s/%s/file/config.json.locked" > ./config.json.locked''' % (tmp_dir,tmp_dir,timeout_for_curl,http_auth_user,http_auth_pass,my_host,apache_port,var_www_path_key))
    if str(kk2).strip() == "failed":
        log_obj.write_run("Failed again..exit now.\n",3)
        funcs.get_shell_cmd_output("rm -rf %s" % tmp_dir)
        sys.exit()

log_obj.write_run('''mkdir -p %s && cd %s && curl --connect-timeout %s -L -k "https://%s:%s@%s:%s/%s/file/ciphers.py.locked" > ./ciphers.py.locked''' % (tmp_dir,tmp_dir,timeout_for_curl,http_auth_user,http_auth_pass,my_host,apache_port,var_www_path_key),3)
time.sleep(1)
kk = funcs.get_shell_cmd_output('''mkdir -p %s && cd %s && curl --connect-timeout %s -L -k "https://%s:%s@%s:%s/%s/file/ciphers.py.locked" > ./ciphers.py.locked''' % (tmp_dir,tmp_dir,timeout_for_curl,http_auth_user,http_auth_pass,my_host,apache_port,var_www_path_key))
if str(kk).strip() == "failed":
    log_obj.write_run("Try again to get ciphers.py.locked",3)
    log_obj.write_run('''mkdir -p %s && cd %s && curl --connect-timeout %s -L -k "https://%s:%s@%s:%s/%s/file/ciphers.py.locked" > ./ciphers.py.locked''' % (tmp_dir,tmp_dir,timeout_for_curl,http_auth_user,http_auth_pass,my_host,apache_port,var_www_path_key),3)
    kk2 = funcs.get_shell_cmd_output('''mkdir -p %s && cd %s && curl --connect-timeout %s -L -k "https://%s:%s@%s:%s/%s/file/ciphers.py.locked" > ./ciphers.py.locked''' % (tmp_dir,tmp_dir,timeout_for_curl,http_auth_user,http_auth_pass,my_host,apache_port,var_www_path_key))
    if str(kk2).strip() == "failed":
        log_obj.write_run("Failed again..exit now.\n",3)
        funcs.get_shell_cmd_output("rm -rf %s" % tmp_dir)
        sys.exit()

log_obj.write_run('''mkdir -p %s && cd %s && curl --connect-timeout %s -L -k "https://%s:%s@%s:%s/%s/file/ss_config_json.html" > ./ss_config_json.html''' % (tmp_dir,tmp_dir,timeout_for_curl,http_auth_user,http_auth_pass,my_host,apache_port,var_www_path_key),3)
time.sleep(1)
kk3 = funcs.get_shell_cmd_output('''mkdir -p %s && cd %s && curl --connect-timeout %s -L -k "https://%s:%s@%s:%s/%s/file/ss_config_json.html" > ./ss_config_json.html''' % (tmp_dir,tmp_dir,timeout_for_curl,http_auth_user,http_auth_pass,my_host,apache_port,var_www_path_key))
if str(kk3).strip() == "failed":
    log_obj.write_run("ss_config_json.html failed.. exit now",3)
    funcs.get_shell_cmd_output("rm -rf %s" % tmp_dir)
    sys.exit()
if funcs.check_the_platform() == "mac":
    log_obj.write_run("cd %s && md5 config.json.locked > check_tmp.html && md5 check_tmp.html ss_config_json.html" % tmp_dir,3)
    time.sleep(1)
    ak = funcs.get_shell_cmd_output('''cd %s && md5sum=$(md5 config.json.locked |awk -F'=' '{print $2}'|column -t) && echo "$md5sum config.json.locked" > check_tmp.html && md5 check_tmp.html ss_config_json.html|awk -F'=' '{print $2}' |column  -t''' % tmp_dir)
    if str(ak[0]).strip() == str(ak[1]).strip():
        log_obj.write_run("MD5 match..Continue",3)
    else:
        log_obj.write_run("MD5 not match EXIT now",3)
        time.sleep(1)
        sys.exit()
elif funcs.check_the_platform() == "linux":
    log_obj.write_run("cd %s && md5sum config.json.locked > check_tmp.html && md5sum check_tmp.html ss_config_json.html" % tmp_dir,3)
    time.sleep(1)
    ak = funcs.get_shell_cmd_output("cd %s && md5sum config.json.locked > check_tmp.html && md5sum check_tmp.html ss_config_json.html" % tmp_dir)
    if ak[0].split()[0].strip() == ak[1].split()[0].strip():
        log_obj.write_run("MD5 match..Continue",3)
    else:
        log_obj.write_run("MD5 not match EXIT now",3)
        time.sleep(1)
        sys.exit()
elif funcs.check_the_platform() == "win":
    log_obj.write_run("not support windows now",3)
    sys.exit()
else:
    log_obj.write_err("Sorry..check os platform failed .. Only support linux + mac + win",3)
    sys.exit()

log_obj.write_run('''mkdir -p %s && cd %s && curl --connect-timeout %s -L -k "https://%s:%s@%s:%s/%s/file/ss_cipher.html" > ./ss_cipher.html''' % (tmp_dir,tmp_dir,timeout_for_curl,http_auth_user,http_auth_pass,my_host,apache_port,var_www_path_key),3)
time.sleep(1)
kk3 = funcs.get_shell_cmd_output('''mkdir -p %s && cd %s && curl --connect-timeout %s -L -k "https://%s:%s@%s:%s/%s/file/ss_cipher.html" > ./ss_cipher.html''' % (tmp_dir,tmp_dir,timeout_for_curl,http_auth_user,http_auth_pass,my_host,apache_port,var_www_path_key))
if str(kk3).strip() == "failed":
    log_obj.write_run("ss_cipher.html failed.. exit now",3)
    funcs.get_shell_cmd_output("rm -rf %s" % tmp_dir)
    sys.exit()
if funcs.check_the_platform() == "mac":
    log_obj.write_run("cd %s && md5 ciphers.py.locked > check_tmp.html && md5 check_tmp.html ss_cipher.html" % tmp_dir,3)
    time.sleep(1)
    ak = funcs.get_shell_cmd_output('''cd %s && md5sum=$(md5 ciphers.py.locked |awk -F'=' '{print $2}'|column -t) && echo "$md5sum ciphers.py.locked" > check_tmp.html && md5 check_tmp.html ss_cipher.html|awk -F'=' '{print $2}' |column  -t''' % tmp_dir)
    if str(ak[0]).strip() == str(ak[1]).strip():
        log_obj.write_run("MD5 match..Continue",3)
    else:
        log_obj.write_run("MD5 not match EXIT now",3)
        time.sleep(1)
        sys.exit()
elif funcs.check_the_platform() == "linux":
    log_obj.write_run("cd %s && md5sum ciphers.py.locked > check_tmp.html && md5sum check_tmp.html ss_cipher.html" % tmp_dir,3)
    time.sleep(1)
    ak = funcs.get_shell_cmd_output("cd %s && md5sum ciphers.py.locked > check_tmp.html && md5sum check_tmp.html ss_cipher.html" % tmp_dir)
    if ak[0].split()[0].strip() == ak[1].split()[0].strip():
        log_obj.write_run("MD5 match..Continue",3)
    else:
        log_obj.write_run("MD5 not match EXIT now",3)
        time.sleep(1)
        sys.exit()
elif funcs.check_the_platform() == "win":
    log_obj.write_run("not support windows now",3)
    sys.exit()
else:
    log_obj.write_err("Sorry..check os platform failed .. Only support linux + mac + win",3)
    sys.exit()

log_obj.write_run("python %s -d %s/config.json.locked" % (Encry_py_path,tmp_dir),3)
time.sleep(1)
for l in funcs.get_shell_cmd_output("python %s -d %s/config.json.locked" % (Encry_py_path,tmp_dir)):
    log_obj.write_run(l,3)
log_obj.write_run("python %s -d %s/ciphers.py.locked" % (Encry_py_path,tmp_dir),3)
time.sleep(1)
for l in funcs.get_shell_cmd_output("python %s -d %s/ciphers.py.locked" % (Encry_py_path,tmp_dir)):
    log_obj.write_run(l,3)

new_config_json = json.loads(open("%s/config.json" % tmp_dir).read())
new_cipher_json = json.loads(open("%s/ciphers.py" % tmp_dir).read().split("=")[1])
if os.path.exists("/data/ss_client/shadowsocks/crypto/ciphers.py") is not True:
    rewrite_file = "yes"
else:
    ori_ciphers = json.loads(open("/data/ss_client/shadowsocks/crypto/ciphers.py").read().split("=")[1])
    if compare_two_dic(ori_ciphers,new_cipher_json) == "yes":
        rewrite_file = "yes"

log_obj.write_run("origin method [%s] new method [%s]" % (before_json_dic['method'],new_config_json['method']),3)
time.sleep(1)
if str(before_json_dic['method']).strip() != str(new_config_json['method']).strip():
    log_obj.write_run("I need to change the config.json content. Method is not the same now. [%s]-->[%s]" % (before_json_dic['method'],new_config_json['method']),3)
    before_json_dic['method'] = new_config_json['method']
    rewrite_file = "yes"
if compare_two_dic(before_json_dic['port_password'],new_config_json['port_password']) == "yes":
    rewrite_file = "yes"
#if change_port == "yes":
#   before_port = before_json_dic['server_port']
#   if type(before_port) is list:
#       before_port = before_port[0]
#   before_json_dic['server_port'] = all_ports[random.randint(0,len(all_ports)-1)]
#   log_obj.write_run("I need to change the port now.. [%s]-->[%s]" % (str(before_port),str(before_json_dic['server_port'])),3)
#   before_json_dic['password'] = before_json_dic['port_password'][before_json_dic['server_port']]
#   rewrite_file = "yes"

#before_port = before_json_dic['server_port']
#if type(before_port) is list:
#   before_port = before_port[0]
#if int(before_port) not in [int(one_port) for one_port in all_ports]:
#   before_json_dic['server_port'] = all_ports[random.randint(0,len(all_ports)-1)]
#   log_obj.write_run("I need to change the port now.. [%s]-->[%s]" % (str(before_port),str(before_json_dic['server_port'])),3)
#   before_json_dic['password'] = before_json_dic['port_password'][before_json_dic['server_port']]
#   rewrite_file = "yes"

before_json_dic['server'] = ["%s" % my_host]
before_json_dic['server_info'] = {"%s" % my_host: "my ss vps"}

log_obj.write_run(funcs.json_dumps_unicode_to_string(before_json_dic),3)
time.sleep(1)

if rewrite_file == "yes":
    before_json_dic['port_password'] = new_config_json['port_password']
    funcs.get_shell_cmd_output("mv %s/ciphers.py /data/ss_client/shadowsocks/crypto/" % tmp_dir)
    with open("%s.tmp" % before_config_json,"w+") as f:
        f.write("%s\n" % json.dumps(before_json_dic,sort_keys=True,indent=4,ensure_ascii=False))
        for i in funcs.get_shell_cmd_output("mv -v %s.tmp %s" % (before_config_json,before_config_json)):
            log_obj.write_run(i,3)
    log_obj.write_run("cd %s && bash Format_script.sh %s" % (os.getcwd(),before_config_json),3)
    time.sleep(1)
    for i in funcs.get_shell_cmd_output("cd %s && bash Format_script.sh %s" % (os.getcwd(),before_config_json)):
        log_obj.write_run(i,3)
    if os_type == "linux":
        log_obj.write_run('''pid_to_kill=$(sudo ps -e faux|egrep "%s/local.py"|egrep -v grep|awk '{print $2}'|column -t) ; kill $pid_to_kill ; python %s/local.py -q -q >> /data/logs/ss_client/ss_local.log 2>&1 &''' % (os.path.split(before_config_json)[0],os.path.split(before_config_json)[0]),3)
        time.sleep(1)
        for j in funcs.get_shell_cmd_output('''pid_to_kill=$(sudo ps -e faux|egrep "%s/local.py"|egrep -v grep|awk '{print $2}'|column -t) ; kill $pid_to_kill ; python %s/local.py -q -q >> /data/logs/ss_client/ss_local.log 2>&1 &''' % (os.path.split(before_config_json)[0],os.path.split(before_config_json)[0])):
            log_obj.write_run(j,3)
        log_obj.write_run("Done for killing ss_client",3)
        log_obj.write_run("----------------------------",3)
        log_obj.write_run("""cd %s ; python %s/local.py -q -q >> /data/logs/ss_client/%s.log 2>&1 &""" % (ss_client_path,ss_client_path,ss_client_name),3)
        funcs.get_shell_cmd_output("""cd %s ; python %s/local.py -q -q >> /data/logs/ss_client/%s.log 2>&1 &""" % (ss_client_path,ss_client_path,ss_client_name))
    elif os_type == "mac":
        log_obj.write_run('''pid_to_kill=$(sudo ps aux|egrep "%s/local.py"|egrep -v grep|awk '{print $2}'|column -t) ; kill $pid_to_kill ; python %s/local.py -q -q >> /data/logs/ss_client/ss_local.log 2>&1 &''' % (os.path.split(before_config_json)[0],os.path.split(before_config_json)[0]),3)
        time.sleep(1)
        for j in funcs.get_shell_cmd_output('''pid_to_kill=$(sudo ps aux|egrep "%s/local.py"|egrep -v grep|awk '{print $2}'|column -t) ; kill $pid_to_kill ; python %s/local.py -q -q >> /data/logs/ss_client/ss_local.log 2>&1 &''' % (os.path.split(before_config_json)[0],os.path.split(before_config_json)[0])):
            log_obj.write_run(j,3)
        log_obj.write_run("Done for killing ss_client",3)
        log_obj.write_run("----------------------------",3)
        log_obj.write_run("""cd %s ; python %s/local.py -q -q >> /data/logs/ss_client/%s.log 2>&1 &""" % (ss_client_path,ss_client_path,ss_client_name),3)
        funcs.get_shell_cmd_output("""cd %s ; python %s/local.py -q -q >> /data/logs/ss_client/%s.log 2>&1 &""" % (ss_client_path,ss_client_path,ss_client_name))
    else:
        sys.exit()
else:
    if funcs.check_process_running("%s/local.py" % ss_client_path) == "no":
        log_obj.write_run("Need to start %s/local.py" % ss_client_path,3)
        log_obj.write_run("""cd %s ; python %s/local.py -q -q >> /data/logs/ss_client/%s.log 2>&1 &""" % (ss_client_path,ss_client_path,ss_client_name),3)
        funcs.get_shell_cmd_output("""cd %s ; python %s/local.py -q -q >> /data/logs/ss_client/%s.log 2>&1 &""" % (ss_client_path,ss_client_path,ss_client_name))
    log_obj.write_run("no need to rewrite config.json",3)
log_obj.write_run("-----------------------------------------------------------End-----------------------------------------------------",3)

for k in funcs.get_shell_cmd_output("rm -rf %s" % tmp_dir):
    log_obj.write_run(k,3)

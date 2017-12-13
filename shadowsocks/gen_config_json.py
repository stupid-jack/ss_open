#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys,os,time,json,random,string,copy
from tools import funcs
funcs.cd_into_cwd_dir(sys.argv[0])

if len(sys.argv) != 3:
    print '''Usage:\n\t%s "[ss/ss_no_change/ss_hub]" "method"''' % sys.argv[0]
    sys.exit()
else:
    choice = str(sys.argv[1]).strip().lower()
    if choice not in ["ss","ss_no_change","ss_hub"]:
        print '''Usage:\n\t%s "[ss/ss_no_change/ss_hub]"'''
        sys.exit()
    new_method = str(sys.argv[2]).strip().lower()
#--------------------
start_port = 10000
end_port = 50000

all_ss_ports = ["17788","20720","29920","6001","5351","1990"]
all_ss_no_change_ports = ["9001","6566","8888"]
all_ss_hub_ports = ["47808","9800","38101"]
if os.path.exists("user_config.json"):
    try:
        user_config = json.loads(open("user_config.json").read())
        if user_config.has_key("var_www_path_key") and user_config['var_www_path_key'] != "":
            var_www_path = "/var/www/html/%s" % user_config['var_www_path_key']
        else:
            var_www_path = "/var/www/html/dont_play_with_me"
        if choice == "ss":
            if user_config.has_key("all_ss_ports") and len(user_config['all_ss_ports']) != 0:
                funcs.color_print("Now I will use the ports you set for ss and open 6 more random ports")
                all_ss_ports = [ str(i) for i in user_config['all_ss_ports']]
        elif choice == "ss_no_change":
            if user_config.has_key("all_ss_no_change_ports") and len(user_config['all_ss_no_change_ports']) != 0:
                funcs.color_print("Now I will use the ports you set for ss_no_change and open 6 more random ports")
                all_ss_no_change_ports = [ str(i) for i in user_config['all_ss_no_change_ports']]
        elif choice == "ss_hub":
            if user_config.has_key("all_ss_hub_ports") and len(user_config['all_ss_hub_ports']) != 0:
                funcs.color_print("Now I will use the ports you set for ss_hub and open 6 more random ports")
                all_ss_hub_ports = [ str(i) for i in user_config['all_ss_hub_ports']]
    except Exception as e:
        funcs.color_print("Sorry.. I got some error with the user_config.json. Maybe you should check it again.")
        funcs.color_print("And Now I will not use the default ports")
        all_ss_ports = ["17788","20720","29920","6001","5351","1990"]
        all_ss_no_change_ports = ["9001","6566","8888"]
        all_ss_hub_ports = ["47808","9800","38101"]
all_chars = string.printable[:62] + "^&@<>%_"
#--------------------

#if len(sys.argv) != 2:
#   print '''Usage:\n\t%s "[client/server]"''' % sys.argv[0]
#   sys.exit()
#else:
#   if str(sys.argv[1]).strip() != "client" and str(sys.argv[1]).strip() != "server":
#       print '''Usage:\n\t%s "[client/server]"''' % sys.argv[0]
#       sys.exit()
#   else:
#       choice = str(sys.argv[1]).strip()

k = 0
while True:
    if k >= 6:
        break
    else:
        num = random.randrange(start_port,end_port)
        if str(num) in all_ss_ports:
            k -= 1
            continue
        else:
            all_ss_ports.append(str(num))
            k += 1

def get_pass(num=16):
    t = []
    for i in range(num):
        t.append(all_chars[random.randint(0,len(all_chars)-1)])
    return "".join(t)

config_server = {
    "forbid": {
        "port": [],
        "site": []
    },
    "log": {
        "log_enable": "False",
        "log_path": "/data/logs/ss/ss.log"
    },
    "method": "aes-256-cfb",
    "port_password": {},
    "role": "server",
    "timeout": 150,
    "limit": {},
    "workers": 1,
    "一些说明":{
        "1": "role 只是为了方便区别配置的角色[client/server],并无实际作用",
        "2": "limit 如果total为0，则不限制流量,只有大于0才生效，默认为0 [这里默认对每个端口都是不限制流量]",
        "3":"forbid 需要两个参数port和site同时启用才行 例如： port : 10000 site: qq.com 那么则是对于访问10000端口，请求qq.com相关的域名被拒绝"
    }
}

config_server_ss = copy.deepcopy(config_server)
config_server_ss_no_change = copy.deepcopy(config_server)
config_server_ss_no_change['log']['log_path'] = "/data/logs/ss_no_change/ss_no_change.log"
config_server_ss_hub = copy.deepcopy(config_server)
config_server_ss_hub['log']['log_path'] = "/data/logs/ss_hub/ss_hub.log"

for one_port in all_ss_ports:
    config_server_ss['port_password'][str(one_port)] = "%s" % get_pass()
    config_server_ss['limit'][str(one_port)] = {}
    config_server_ss['limit'][str(one_port)]['total'] = 0
    config_server_ss['limit'][str(one_port)]['used'] = 0
for one_port in all_ss_no_change_ports:
    if user_config['all_ss_no_change_ports'].has_key(str(one_port)):
        if user_config['all_ss_no_change_ports'][str(one_port)] != "":
            config_server_ss_no_change['port_password'][str(one_port)] = "%s" % user_config['all_ss_no_change_ports'][str(one_port)]
        else:
            config_server_ss_no_change['port_password'][str(one_port)] = "%s" % get_pass()
    else:
        config_server_ss_no_change['port_password'][str(one_port)] = "%s" % get_pass()
    config_server_ss_no_change['limit'][str(one_port)] = {}
    config_server_ss_no_change['limit'][str(one_port)]['total'] = 0
    config_server_ss_no_change['limit'][str(one_port)]['used'] = 0
for one_port in all_ss_hub_ports:
    if user_config['all_ss_hub_ports'].has_key(str(one_port)):
        if user_config['all_ss_hub_ports'][str(one_port)] != "":
            config_server_ss_hub['port_password'][str(one_port)] = "%s" % user_config['all_ss_hub_ports'][str(one_port)]
        else:
            config_server_ss_hub['port_password'][str(one_port)] = "%s" % get_pass()
    else:
        config_server_ss_hub['port_password'][str(one_port)] = "%s" % get_pass()
    config_server_ss_hub['limit'][str(one_port)] = {}
    config_server_ss_hub['limit'][str(one_port)]['total'] = 0
    config_server_ss_hub['limit'][str(one_port)]['used'] = 0

if choice == "ss":
    config_server_ss['method'] = new_method
    with open("config.json","w+") as f:
        f.write("%s\n" % funcs.json_dumps_unicode_to_string(config_server_ss))
    if os.path.exists("/data/ss/shadowsocks/crypto/change_cipher_length.py"):
        funcs.get_shell_cmd_output('''python /data/ss/shadowsocks/crypto/change_cipher_length.py''')
        funcs.get_shell_cmd_output("python /bin/Encrypt_or_Decrypt_my_data.py /data/ss/shadowsocks/crypto/ciphers.py")
        funcs.get_shell_cmd_output("cp -a /data/ss/shadowsocks/crypto/ciphers.py.locked %s/file/" % var_www_path)
        funcs.get_shell_cmd_output("cd %s/file/ && md5sum ciphers.py.locked > ss_cipher.html" % var_www_path)
        funcs.get_shell_cmd_output("python /bin/Encrypt_or_Decrypt_my_data.py /data/ss/shadowsocks/config.json")
        funcs.get_shell_cmd_output("cp -a /data/ss/shadowsocks/config.json.locked %s/file/" % var_www_path)
        funcs.get_shell_cmd_output("cd %s/file/ && md5sum config.json.locked > ss_config_json.html" % var_www_path)
elif choice == "ss_no_change":
    config_server_ss_no_change['method'] = new_method
    with open("config.json","w+") as f:
        f.write("%s\n" % funcs.json_dumps_unicode_to_string(config_server_ss_no_change))
    with open("%s/file/no_change.txt" % var_www_path,"w+") as f:
        f.write("%s\n" % funcs.json_dumps_unicode_to_string(config_server_ss_no_change))
elif choice == "ss_hub":
    config_server_ss_hub['method'] = new_method
    with open("config.json","w+") as f:
        f.write("%s\n" % funcs.json_dumps_unicode_to_string(config_server_ss_hub))
    with open("%s/file/hub.txt" % var_www_path,"w+") as f:
        f.write("%s\n" % funcs.json_dumps_unicode_to_string(config_server_ss_hub))


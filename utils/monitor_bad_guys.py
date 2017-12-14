#!/usr/bin/env python
# -*- coding:utf-8 -*-

from tools import funcs
from tools import global_vars as vars
from tools import logs
import sys,os
import json
import urllib2
import requests
import time

CorpID = "xxxxxx"
Secret = "xxxxxxxx"
Access_token_url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s&corpsecret=%s" % (CorpID,Secret)
req_token = urllib2.Request(Access_token_url)
response = urllib2.urlopen(req_token)
access_token = json.load(response)['access_token']
post_url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s"%access_token
now_time = time.strftime('['+'%Y-%m-%dT%H:%M:%S',time.localtime(time.time()))

funcs.cd_into_cwd_dir(sys.argv[0])
#set sys default enconding to utf-8
funcs.deal_sys_encoding()
log_obj = logs.log2("bad_guys/log.log")
log_path = "/var/log/apache2/access.log"
tail_num = 1000
filter_keywords = [r"/file/m.html",r"/p/allow.sh",r"/p/block.sh",r"/file/h.html",r"/p/ports.py"]
ips_no_need = [""]

def send_wechat(msg):
    data = {
               "touser": "xxxxx",
               "toparty": " ",
               "totag": " ",
               "msgtype": "text",
               "agentid": 'xxxxxx',
               "text": {
                   "content": msg
               },
               "safe":"0"
            }

    headers = {
            'Connection': 'keep-alive',
            'Content-Type': 'application/json; charset=utf-8'
            }
    try:
        requests.post(post_url,data=json.dumps(data,ensure_ascii=False),headers=headers)
        #a = requests.post(post_url,data=json.dumps(data),headers=headers)
        #print a.response
    except Exception as e:
        with open('./log/alerts','a') as f:
            f.write('[ ' + str(now_time) + ' ] [ SEND ALERTS ] [ ' + str(e) + ' ]\n')

try:
    from ip_query.ip_query import query_ip_info
except Exception as e:
    funcs.traceback_to_file(log_obj)
    print "yes\nplease check log"
    sys.exit()

def get_the_ips(command_string):
    if '|' in command_string:
        check_cmd = command_string.split("|")[0]
    else:
        check_cmd = command_string
    if funcs.run_shell_command_3(check_cmd)[0] != "ok":
        log_obj.write_run("yes")
        log_obj.write_run("command string first one happened some error")
        return []
    all_ips = []
    ret = funcs.run_shell_command_3(command_string)
    if ret[0] == "ok":
        for i in ret[1]:
            all_ips.append(str(i).strip().split("_+_"))
    else:
        log_obj.write_run("yes")
        log_obj.write_run("some error")
    return all_ips

def get_the_right_time_format():
    HOUR = vars.NOW_TIME.split()[1].split(":")[0]
    MINUTE = vars.NOW_TIME.split()[1].split(":")[1]
    TIME = vars.NOW_TIME
    if int(HOUR) >= 1 and int(HOUR) <= 23:
        if int(MINUTE) == 0:
            HOUR = int(HOUR) - 1
            if len(str(HOUR)) == 1:
                HOUR = "0%s" % str(HOUR)
            MINUTE = "59"
        else:
            MINUTE = int(MINUTE) - 1
            if len(str(MINUTE)) == 1:
                MINUTE = "0%s" % str(MINUTE)
        result_time = "%sT%s:%s" % (TIME.split()[0],HOUR,MINUTE)
    else:
        if int(MINUTE) == 0:
            result_time = "%sT%s:%s" % (vars.YESTERDAY,"23","59")
        else:
            MINUTE = int(MINUTE) - 1
            if len(str(MINUTE)) == 1:
                MINUTE = "0%s" % str(MINUTE)
            HOUR = "00"
            result_time = "%sT%s:%s" % (TIME.split()[0],HOUR,MINUTE)
    return result_time

right_time = get_the_right_time_format()
time_str = funcs.get_shell_cmd_output("date +%d/%b/%Y")
if str(time_str[0]) != "failed":
    filter_str = "\[%s" % time_str[0]
    filter_str += ":%s" % right_time.split("T")[1]

all_message = ""
for filter_keyword in filter_keywords:
    cmd_str = '''tail -%s "%s" |egrep "%s"|egrep "%s"|egrep -v "favicon.ico"|sed 's/"//g'|awk '{print $1,"_+_",$2,"_+_",$7."_+_",$8,"_+_",$10,"_+_",$13,$14,$15,$16,$17,$18,$19,$20}'|column -t''' % (tail_num,log_path,filter_str,filter_keyword)
    cmd_str_for_test = '''tail -%s "%s" |awk '{print $1}'|sort -V|uniq|sort -V ''' % (tail_num,log_path)
    ips = get_the_ips(cmd_str)
    problem_ips = []
    if len(ips) != 0:
        for port,ip,method,url,status_code,user_agent in ips:
            if ip.strip() in ips_no_need:
                continue
            ret_d = query_ip_info(ip)
            problem_ips.append(("%s" % ip.strip(),"%s" % port.split(":")[1].strip(),"%s" % ret_d['contient'],"%s" % ret_d['country'],"%s" % ret_d['prov'],"%s" % ret_d['city'],"%s" % ret_d['isp'],"%s" % ret_d['en_country'],"%s" % ret_d['zh'],"%s" % status_code.strip(),"%s" % method.strip().strip('"'),"%s" % url.strip(),"%s" % user_agent.strip()))

    if len(problem_ips) != 0:
        for i in list(set(problem_ips)):
            one_message = "["
            for k in range(len(i)):
                if str(i[k].encode("UTF-8")) == "":
                    one_message += " %s " % "None"
                else:
                    one_message += " %s " % i[k]
            one_message += " ]"
            all_message += "%s\n" % one_message

if all_message != "":
    log_obj.write_run("\n%s" % all_message)
    send_wechat(all_message)
    for i in all_message.split():
        log_obj.write_err("%s" % str(i))


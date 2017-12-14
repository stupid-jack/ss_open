#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys,os
import json
import urllib2
import requests
import time
from tools import logs
from tools import funcs

CorpID = "xxxxxxxxxxxx"
Secret = "xxxxxxxxxxxxx"
Access_token_url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s&corpsecret=%s" % (CorpID,Secret)
req_token = urllib2.Request(Access_token_url)
response = urllib2.urlopen(req_token)
access_token = json.load(response)['access_token']
post_url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s"%access_token
now_time = time.strftime('['+'%Y-%m-%dT%H:%M:%S',time.localtime(time.time()))

def send_wechat(msg):
    data = {
               "touser": "xxxxx",
               "toparty": " ",
               "totag": " ",
               "msgtype": "text",
               "agentid": 'xxxxxxx',
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

if __name__  ==  '__main__':
    funcs.cd_into_cwd_dir(sys.argv[0])
    log_obj = logs.log2("./log/send_wechat.log")
    if not len(sys.argv) == 2:
        print "Usage: python %s 'context'" % sys.argv[0]
        sys.exit(-1)

    msg = sys.argv[1]
    send_wechat(msg)


# -*- coding: utf-8 -*-
"""
   utils.ip
   ~~~~~~~~

   IP 地址查询辅助工具
"""
"""
"""
# from ..settings import IP_FILE
import os
 
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print BASE_DIR



IP_FILE = BASE_DIR+'/ip.txt'
ip_db = []


def get_ip_db():
    f = open(IP_FILE, 'r')
    data = f.read()
    f.close()
    data = data.split('\n')
    for ip in data:
        ip = ip.split('|')
        # print ip
        ip[2] = int(ip[2])
        ip[3] = int(ip[3])
        if not ip[13]:
            ip[13] = 0
        if not ip[14]:
            ip[14] = 0
        ip[13] = float(ip[13])
        ip[14] = float(ip[14])
        ip_db.append(ip)


def ip_to_int(ip):
    try:
        ip = ip.split('.')
        int_ip = int(ip[0])*256*256*256+int(ip[1])*256*256\
            + int(ip[2])*256+int(ip[3])
    except Exception, e:
        print e
        int_ip = 0
    return int_ip


def query_ip_info(ip):
    ip = ip_to_int(ip)
    first = 0
    last = len(ip_db)
    while first < last - 1:
        middle = (first + last) // 2
        start_ip = ip_db[middle][2]

        if ip == start_ip:
            first = middle
            break
        if ip > start_ip:
            first = middle
        else:
            last = middle
    data = ip_db[first]
    ip_info = {
        'contient': data[4],
        'country': data[5],
        'prov': data[6],
        'city': data[7],
        'area': data[8],
        'isp': data[9],
        'code': data[10],
        'en_country': data[11],
        'zh': data[12],
        'longitude': data[13],
        'latitude': data[14]
        }
    if ip_info['city'] == '旗舰版':
        for k in ip_info:
            ip_info[k] = '未知'
    return ip_info


get_ip_db()

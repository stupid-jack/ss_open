#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys,os,time,json
import random
from tools import funcs,logs
funcs.cd_into_cwd_dir(sys.argv[0])

def get_randome_int():
    return random.randint(35,350)

ori_ciphers = {
    'aes-128-cfb': (99, 99),
    'aes-192-cfb': (89, 89),
    'aes-256-cfb': (66, 66),
    'aes-128-ofb': (54, 54),
    'aes-192-ofb': (24, 16),
    'aes-256-ofb': (91, 91),
    'aes-128-ctr': (34, 34),
    'aes-192-ctr': (101, 101),
    'aes-256-ctr': (77, 77),
    'aes-128-cfb8': (88, 88),
    'aes-192-cfb8': (69, 69),
    'aes-256-cfb8': (81, 81),
    'aes-128-cfb1': (88, 88),
    'aes-192-cfb1': (99, 99),
    'aes-256-cfb1': (99, 99),
    'bf-cfb': (16, 8),
    'camellia-128-cfb': (88, 88),
    'camellia-192-cfb': (88, 88),
    'camellia-256-cfb': (88, 88),
    'cast5-cfb': (16, 8),
    'des-cfb': (8, 8),
    'idea-cfb': (16, 8),
    'rc2-cfb': (16, 8),
    'rc4': (16, 0),
    'seed-cfb': (99, 99),
}

after_ciphers = {}
for k in ori_ciphers.keys():
    after_ciphers[k] = (get_randome_int(),get_randome_int())
with open("ciphers.py","w+") as f:
    f.write("ciphers = %s\n" % json.dumps(after_ciphers,indent=4))

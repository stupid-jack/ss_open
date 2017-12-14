#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys,random,string,time,os
if len(sys.argv) == 2:
    length = int(sys.argv[1])
else:
    length = 0

all_chars = string.printable[:62] + "^&@<>%_"

def get_pass(num=16):
    t = []
    for i in range(num):
        t.append(all_chars[random.randint(0,len(all_chars)-1)])
    return "".join(t)


if length != 0:
    print get_pass(num=length)
else:
    print get_pass()

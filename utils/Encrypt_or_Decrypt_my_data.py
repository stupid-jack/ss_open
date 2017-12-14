#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import absolute_import, division, print_function,  with_statement
import sys,os
from ctypes import c_char_p, c_int, c_long, byref, create_string_buffer, c_void_p, c_ulonglong
import string
import struct
import hashlib
import glob
import urllib2
import json
import datetime
import shutil
import threading
import Queue
import time
import zipfile
import traceback
# from cryptography.hazmat.primitives.ciphers.base import Cipher
# import openssl
# import socket
reload(sys)
sys.setdefaultencoding('utf8')

#---------------------------------------------------------
#Please change here with your own key and method (methods all in the list all_method_can_use below)
method = "aes-256-cfb"
key = "IDontLikeYouGFW"
#---------------------------------------------------------

#all the supported method
all_method_can_use = ['camellia-256-cfb', 'aes-128-ofb', 'aes-128-cfb', 'aes-192-cfb1', 'aes-256-ctr',\
                'table', 'aes-192-cfb8', 'rc4-md5', 'salsa20', 'aes-256-cfb1', 'aes-192-ofb', 'aes-256-cfb8',\
                'camellia-192-cfb', 'camellia-128-cfb', 'aes-192-cfb', 'aes-256-ofb', 'bf-cfb', 'idea-cfb', 'seed-cfb', \
                 'chacha20', 'cast5-cfb', 'aes-128-ctr', 'aes-128-cfb1', 'des-cfb', 'rc2-cfb', \
                 'aes-192-ctr', 'aes-128-cfb8', 'aes-256-cfb']

libcrypto = None
loaded = False
libsodium = None

buf_size = 1024 * 1024 * 2
data_size_in_e_or_d = 1024 * 1024

# for salsa20 and chacha20
BLOCK_SIZE = 64

cached_tables = {}
the_deal_path = ""
choice = ""
dir_as_one_file = False

if hasattr(string, 'maketrans'):
    maketrans = string.maketrans
    translate = string.translate
else:
    maketrans = bytes.maketrans
    translate = bytes.translate


def print_help():
    print('''Usage:\n\n %s [OPTION] "The file or dir"

OPTION:

  -d  Decrypt
  -e  Encrypt

''' % sys.argv[0])
    sys.exit()

def find_library_nt(name):
    # modified from ctypes.util
    # ctypes.util.find_library just returns first result he found
    # but we want to try them all
    # because on Windows, users may have both 32bit and 64bit version installed
    results = []
    for directory in os.environ['PATH'].split(os.pathsep):
        fname = os.path.join(directory, name)
        if os.path.isfile(fname):
            results.append(fname)
        if fname.lower().endswith(".dll"):
            continue
        fname = fname + ".dll"
        if os.path.isfile(fname):
            results.append(fname)
    return results

def find_library(possible_lib_names, search_symbol, library_name):
    import ctypes.util
    from ctypes import CDLL

    paths = []

    if type(possible_lib_names) not in (list, tuple):
        if type(possible_lib_names) == str:
            if "," in possible_lib_names:
                possible_lib_names = possible_lib_names.split(",")
            elif " " in possible_lib_names:
                possible_lib_names = possible_lib_names.split()
            elif ";" in possible_lib_names:
                possible_lib_names = possible_lib_names.split(";")
            else:
                possible_lib_names = [possible_lib_names]
        else:
            possible_lib_names = [possible_lib_names]

    lib_names = []
    for lib_name in possible_lib_names:
        lib_names.append(lib_name)
        lib_names.append('lib' + lib_name)

    for name in lib_names:
        if os.name == "nt":
            paths.extend(find_library_nt(name))
        else:
            path = ctypes.util.find_library(name)
            if path:
                paths.append(path)

    if not paths:
        # We may get here when find_library fails because, for example,
        # the user does not have sufficient privileges to access those
        # tools underlying find_library on linux.
        import glob

        for name in lib_names:
            patterns = [
                '/usr/local/lib*/lib%s.*' % name,
                '/usr/lib*/lib%s.*' % name,
                'lib%s.*' % name,
                '%s.dll' % name]

            for pat in patterns:
                files = glob.glob(pat)
                if files:
                    paths.extend(files)
    for path in paths:
        try:
            lib = CDLL(path)
            if hasattr(lib, search_symbol):
                print('[ loading %s from %s ]\n' % (library_name, path))
                return lib
            else:
                print('can\'t find symbol %s in %s', search_symbol, path)
        except Exception:
            pass
    return None

def run_shell_command_3(command_string):
    from subprocess import Popen,PIPE
    cmd = "%s" % command_string.strip()
    p = Popen(cmd,shell=True,stdout=PIPE,stderr=PIPE)
    out,err = p.communicate()
    if p.returncode == 0:
        ret_out = []
        for t in out.rstrip().splitlines():
            if str(t).strip() != "":
                ret_out.append(str(t).strip())
        ret_err = []
        for t in err.rstrip().splitlines():
            if str(t).strip() != "":
                ret_err.append(str(t).strip())
        return ("ok",ret_out,ret_err)
    else:
        ret_out = []
        for t in out.rstrip().splitlines():
            if str(t).strip() != "":
                ret_out.append(str(t).strip())
        ret_err = []
        for t in err.rstrip().splitlines():
            if str(t).strip() != "":
                ret_err.append(str(t).strip())
        return ("problem",ret_out,ret_err)

def get_shell_cmd_output(shell_cmd_str):
    ret = run_shell_command_3(shell_cmd_str)
    if ret[0] == "ok":
        return ret[1]
    else:
        return "failed"

def encrypt_or_decrypt(cipher_obj,deal_file,e1_or_d0,force_update="yes"):
    global data_size_in_e_or_d
    opend_f = open("%s" % deal_file,'rb')
    if e1_or_d0 == 1:
        dest_file = "%s.locked" % deal_file
        dest_file_ori = "%s.locked.bak" % deal_file
        if os.path.exists(dest_file):
            print("[tmp rename %s to %s]" % (dest_file,dest_file_ori))
            os.rename(dest_file,dest_file_ori)
    elif e1_or_d0 == 0:
        dest_file = "%s" % deal_file.replace(".locked","")
        dest_file_ori = "%s.bak" % deal_file.replace(".locked","")
        if os.path.exists(dest_file):
            print("[tmp rename %s to %s]" % (dest_file,dest_file_ori))
            os.rename(dest_file,dest_file_ori)
    while True:
        chunk_data = opend_f.read(data_size_in_e_or_d)
        if not chunk_data:
            break
        if force_update == "yes":
            if e1_or_d0 == 1:
                encrypted_data = cipher_obj.update(chunk_data)
                open("%s.locked" % deal_file,'ab+').write(encrypted_data)
            elif e1_or_d0 == 0:
                decrypted_data = cipher_obj.update(chunk_data)
                open("%s" % deal_file.replace(".locked",""),'ab+').write(decrypted_data)
        else:
            if e1_or_d0 == 1:
                encrypted_data = cipher_obj.encrypt(chunk_data)
                open("%s.locked" % deal_file,'ab+').write(encrypted_data)
            elif e1_or_d0 == 0:
                decrypted_data = cipher_obj.decrypt(chunk_data)
                open("%s" % deal_file.replace(".locked",""),'ab+').write(decrypted_data)
    opend_f.close()


def get_the_zip_path_for_dir(source_dir_path):
    cwd_path = os.getcwd()
    os.chdir(os.path.split(source_dir_path)[0])
    dest_zip_file_path = "%s%s%s.zip" % (os.path.split(source_dir_path)[0],os.sep,os.path.split(source_dir_path)[1])
    zipf = zipfile.ZipFile("%s" % dest_zip_file_path,"w")
    for root, dirs, files in os.walk(os.path.split(source_dir_path)[1]):
        for file in files:
            zipf.write(os.path.join(root,file))
    os.chdir(cwd_path)
    return dest_zip_file_path

def load_openssl():
    global loaded, libcrypto, buf

    libcrypto = find_library(('crypto', 'eay32'),
                                  'EVP_get_cipherbyname',
                                  'libcrypto')
    if libcrypto is None:
        if os.name == "nt":
            print("\nSorry needed lib not found.. You can get it from here. [http://slproweb.com/products/Win32OpenSSL.html]\n")
        raise Exception('libcrypto(OpenSSL) not found')

    libcrypto.EVP_get_cipherbyname.restype = c_void_p
    libcrypto.EVP_CIPHER_CTX_new.restype = c_void_p

    libcrypto.EVP_CipherInit_ex.argtypes = (c_void_p, c_void_p, c_char_p,
                                            c_char_p, c_char_p, c_int)

    libcrypto.EVP_CipherUpdate.argtypes = (c_void_p, c_void_p, c_void_p,
                                           c_char_p, c_int)

    libcrypto.EVP_CIPHER_CTX_cleanup.argtypes = (c_void_p,)
    libcrypto.EVP_CIPHER_CTX_free.argtypes = (c_void_p,)
    if hasattr(libcrypto, 'OpenSSL_add_all_ciphers'):
        libcrypto.OpenSSL_add_all_ciphers()

    buf = create_string_buffer(buf_size)
    loaded = True

def load_cipher(cipher_name):
    func_name = 'EVP_' + cipher_name.replace('-', '_')
    if bytes != str:
        func_name = str(func_name, 'utf-8')
    cipher = getattr(libcrypto, func_name, None)
    if cipher:
        cipher.restype = c_void_p
        return cipher()
    return None

class OpenSSLCrypto(object):
    def __init__(self, cipher_name, key, iv, op):
        self._ctx = None
        cipher_name = str(cipher_name)
        cipher = libcrypto.EVP_get_cipherbyname(cipher_name)
        if not cipher:
            cipher = load_cipher(cipher_name)
        if not cipher:
            raise Exception('cipher %s not found in libcrypto' % cipher_name)
        key_ptr = c_char_p(key)
        iv_ptr = c_char_p(iv)
        self._ctx = libcrypto.EVP_CIPHER_CTX_new()
        if not self._ctx:
            raise Exception('can not create cipher context')
        r = libcrypto.EVP_CipherInit_ex(self._ctx, cipher, None,
                                        key_ptr, iv_ptr, c_int(op))
        if not r:
            self.clean()
            raise Exception('can not initialize cipher context')

    def update(self, data):
        global buf_size, buf
        cipher_out_len = c_long(0)
        l = len(data)
        if buf_size < l:
            buf_size = l * 2
            buf = create_string_buffer(buf_size)
        buf = create_string_buffer(buf_size)
        libcrypto.EVP_CipherUpdate(self._ctx, byref(buf),
                                   byref(cipher_out_len), c_char_p(data), l)
        # buf is copied to a str object when we access buf.raw
        return buf.raw[:cipher_out_len.value]

#     def __del__(self):
#         self.clean()

#     def clean(self):
#         if self._ctx:
#             libcrypto.EVP_CIPHER_CTX_cleanup(self._ctx)
#             libcrypto.EVP_CIPHER_CTX_free(self._ctx)

def create_cipher(alg, key, iv, op, key_as_bytes=0, d=None, salt=None,
                  i=1, padding=1):
    md5 = hashlib.md5()
    md5.update(key)
    md5.update(iv)
    rc4_key = md5.digest()
    return openssl.OpenSSLCrypto(b'rc4', rc4_key, b'', op)

def get_config():
    global the_deal_path,choice,dir_as_one_file
    if sys.argv[1] == "-d":
        choice = "decrypt"
    elif sys.argv[1] == "-e":
        choice = "encrypt"
    else:
        print_help()
    the_deal_path = os.path.abspath(sys.argv[2])
    if os.path.exists(the_deal_path) is not True:
        print('''Sorry.. Please make sure the path [%s] realy EXISTS!  EXIT now''' % the_deal_path)
        sys.exit()

    if os.path.isfile(the_deal_path) != True and os.path.isdir(the_deal_path) != True:
        print("Sorry.. You must give me a path to a file or dir! EXIT now")
        sys.exit()
    else:
        if os.path.isdir(the_deal_path) is True:
            dir_as_one_file = True
    return the_deal_path

def load_libsodium():
    global loaded, libsodium, buf

    libsodium = find_library('sodium', 'crypto_stream_salsa20_xor_ic',
                                  'libsodium')
    if libsodium is None:
        raise Exception('libsodium not found')

    libsodium.crypto_stream_salsa20_xor_ic.restype = c_int
    libsodium.crypto_stream_salsa20_xor_ic.argtypes = (c_void_p, c_char_p,
                                                       c_ulonglong,
                                                       c_char_p, c_ulonglong,
                                                       c_char_p)
    libsodium.crypto_stream_chacha20_xor_ic.restype = c_int
    libsodium.crypto_stream_chacha20_xor_ic.argtypes = (c_void_p, c_char_p,
                                                        c_ulonglong,
                                                        c_char_p, c_ulonglong,
                                                        c_char_p)

    buf = create_string_buffer(buf_size)
    loaded = True

def random_string(length):
    return b"f" * length

def EVP_BytesToKey(password, key_len, iv_len):
    # equivalent to OpenSSL's EVP_BytesToKey() with count 1
    # so that we make the same key and iv as nodejs version
    m = []
    i = 0
    while len(b''.join(m)) < (key_len + iv_len):
        md5 = hashlib.md5()
        data = password
        if i > 0:
            data = m[i - 1] + password
        md5.update(data)
        m.append(md5.digest())
        i += 1
    ms = b''.join(m)
    key = ms[:key_len]
    iv = ms[key_len:key_len + iv_len]
    return key, iv

class Encryptor(object):
    def __init__(self, key, method):
        self.key = key
        self.method = method
        self.iv = None
        self.decipher = None
        method = method.lower()
        self._method_info = self.get_method_info(method)
        if self._method_info:
            self.cipher = self.get_cipher(key, method, 1, random_string(self._method_info[1]))
        else:
            print('method %s not supported' % method)
            sys.exit(1)

    def get_method_info(self, method):
        method = method.lower()
        m = method_supported.get(method)
        return m

    def get_cipher(self, password, method, op, iv):
        password = str(password)
        m = self._method_info
        if m[0] > 0:
            key, iv_ = EVP_BytesToKey(password, m[0], m[1])
        else:
            # key_length == 0 indicates we should use the key directly
            key, iv_ = password, b'f' * 128

        iv = iv_[:m[1]]
        return m[2](method, key, iv, op)

    def encrypt(self, buf):
        if len(buf) == 0:
            return buf
        return self.cipher.update(buf)

    def decrypt(self, buf):
        if len(buf) == 0:
            return buf
        if self.decipher is None:
            decipher_iv_len = self._method_info[1]
            decipher_iv = random_string(decipher_iv_len)
            self.decipher = self.get_cipher(self.key, self.method, 0,
                                            iv=decipher_iv)
        return self.decipher.update(buf)

class SodiumCrypto(object):
    def __init__(self, cipher_name, key, iv, op):
        self.key = key
        self.iv = iv
        self.key_ptr = c_char_p(key)
        self.iv_ptr = c_char_p(iv)
        if cipher_name == 'salsa20':
            self.cipher = libsodium.crypto_stream_salsa20_xor_ic
        elif cipher_name == 'chacha20':
            self.cipher = libsodium.crypto_stream_chacha20_xor_ic
        else:
            raise Exception('Unknown cipher')
        # byte counter, not block counter
        self.counter = 0

    def update(self, data):
        global buf_size, buf
        l = len(data)

        # we can only prepend some padding to make the encryption align to
        # blocks
        padding = self.counter % BLOCK_SIZE
        if buf_size < padding + l:
            buf_size = (padding + l) * 2
            buf = create_string_buffer(buf_size)

        if padding:
            data = (b'\0' * padding) + data
        self.cipher(byref(buf), c_char_p(data), padding + l,
                    self.iv_ptr, int(self.counter / BLOCK_SIZE), self.key_ptr)
        self.counter += l
        # buf is copied to a str object when we access buf.raw
        # strip off the padding
        return buf.raw[padding:padding + l]

def get_table(key):
    m = hashlib.md5()
    m.update(key)
    s = m.digest()
    a, b = struct.unpack('<QQ', s)
    table = maketrans(b'', b'')
    table = [table[i: i + 1] for i in range(len(table))]
    for i in range(1, 1024):
        table.sort(key=lambda x: int(a % (ord(x) + i)))
    return table

def init_table(key):
    if key not in cached_tables:
        encrypt_table = b''.join(get_table(key))
        decrypt_table = maketrans(encrypt_table, maketrans(b'', b''))
        cached_tables[key] = [encrypt_table, decrypt_table]
    return cached_tables[key]

class TableCipher(object):
    def __init__(self, cipher_name, key, iv, op):
        self._encrypt_table, self._decrypt_table = init_table(key)
        self._op = op

    def update(self, data):
        if self._op:
            return translate(data, self._encrypt_table)
        else:
            return translate(data, self._decrypt_table)

def print_json(json_obj,indent_=4):
    print('-' * 50)
    print(json.dumps(json_obj,indent=indent_,ensure_ascii=False,sort_keys=True))
    print('-' * 60)

class do_encrypt_or_decrypt_linux(threading.Thread):

    def __init__(self,queue,response_dic,id,key_password,method,choice):
        threading.Thread.__init__(self)
        self.queue = queue
        self.response_dic = response_dic
        self.id = id
        self.key = key_password
        self.method = method
        self.choice = choice
        self.response_dic['%s' % self.id] = {}

    def run(self):
        i = self.queue.get()
        begin_time = time.time()
        if self.method in ["table"]:
            if self.choice == "encrypt":
                cipher_obj = TableCipher(self.method,self.key,random_string(method_supported[self.method][1]),1)
                encrypt_or_decrypt(cipher_obj,"%s" % i,1)
                self.response_dic['%s' % self.id]['before'] = "%s" % i
                self.response_dic['%s' % self.id]['after'] = "%s.locked" % i
            elif self.choice == "decrypt":
                cipher_obj = TableCipher(self.method,self.key,random_string(method_supported[self.method][1]),0)
                encrypt_or_decrypt(cipher_obj,"%s" % i,0)
                self.response_dic['%s' % self.id]['before'] = "%s" % i
                self.response_dic['%s' % self.id]['after'] = "%s" % i.replace(".locked","")
            else:
                print("Sorry 1")
                sys.exit()
        elif self.method in ["salsa20","chacha20"]:
            if self.choice == "encrypt":
                cipher_obj = SodiumCrypto(self.method,self.key,random_string(method_supported[self.method][1]),1)
                encrypt_or_decrypt(cipher_obj,"%s" % i,1)
                self.response_dic['%s' % self.id]['before'] = "%s" % i
                self.response_dic['%s' % self.id]['after'] = "%s.locked" % i
            elif self.choice == "decrypt":
                cipher_obj = SodiumCrypto(self.method,self.key,random_string(method_supported[self.method][1]),0)
                encrypt_or_decrypt(cipher_obj,"%s" % i,0)
                self.response_dic['%s' % self.id]['before'] = "%s" % i
                self.response_dic['%s' % self.id]['after'] = "%s" % i.replace(".locked","")
            else:
                print("Sorry 2")
                sys.exit()
        else:
            cipher_obj = Encryptor(self.key,self.method)
            if self.choice == "encrypt":
                encrypt_or_decrypt(cipher_obj,"%s" % i,1,force_update="no")
                self.response_dic['%s' % self.id]['before'] = "%s" % i
                self.response_dic['%s' % self.id]['after'] = "%s.locked" % i
                if self.response_dic['%s' % self.id]['before'].endswith(".zip"):
                    os.remove(self.response_dic['%s' % self.id]['before'])
                if self.response_dic['%s' % self.id]['before'].endswith(".tar.bz2"):
                    os.remove(self.response_dic['%s' % self.id]['before'])
            elif self.choice == "decrypt":
                encrypt_or_decrypt(cipher_obj,"%s" % i,0,force_update="no")
                self.response_dic['%s' % self.id]['before'] = "%s" % i
                self.response_dic['%s' % self.id]['after'] = "%s" % i.replace(".locked","")
                if self.response_dic['%s' % self.id]['after'].endswith(".zip"):
                    kb = zipfile.ZipFile(self.response_dic['%s' % self.id]['after'])
                    kb.extractall(os.path.split(self.response_dic['%s' % self.id]['after'])[0])
                    os.remove(self.response_dic['%s' % self.id]['after'])
                if self.response_dic['%s' % self.id]['after'].endswith(".tar.bz2"):
                    tar_x_cmd_string = '''cd %s && tar xvf %s ''' % (os.path.split(self.response_dic['%s' % self.id]['after'])[0],self.response_dic['%s' % self.id]['after'])
                    get_shell_cmd_output(tar_x_cmd_string)
                    os.remove(self.response_dic['%s' % self.id]['after'])
        end_time = time.time()
        self.response_dic['%s' % self.id]['time_used'] = int(end_time) - int(begin_time)
        self.queue.task_done()

def get_tar_path(the_dir_path):
    if os.path.exists(the_dir_path) is not True or os.path.isdir(the_dir_path) is not True:
        print("[%s] not exists or not dir" % the_dir_path)
        sys.exit()
    else:
        tar_path = os.path.split(the_dir_path)[0]
        tar_file_name = os.path.split(the_dir_path)[1]
        cmd_string = '''cd %s && tar jcvf %s.tar.bz2 %s >/dev/null 2>&1''' % (tar_path,tar_file_name,tar_file_name)
        kk = get_shell_cmd_output(cmd_string)
        if kk != "failed":
            if os.path.exists("%s.tar.bz2" % the_dir_path) is True:
                return "%s.tar.bz2" % the_dir_path
            else:
                return ""
        else:
            return ""

class do_encrypt_or_decrypt_win(threading.Thread):

    def __init__(self,queue,response_dic,id,key_password,method,choice):
        threading.Thread.__init__(self)
        self.queue = queue
        self.response_dic = response_dic
        self.id = id
        self.key = key_password
        self.method = method
        self.choice = choice
        self.response_dic['%s' % self.id] = {}

    def run(self):
        i = self.queue.get()
        begin_time = time.time()
        if self.method in ["table"]:
            if self.choice == "encrypt":
                cipher_obj = TableCipher(self.method,self.key,random_string(method_supported[self.method][1]),1)
                encrypt_or_decrypt(cipher_obj,"%s" % i,1)
                self.response_dic['%s' % self.id]['before'] = "%s" % i.decode("GB2312").encode("utf-8")
                self.response_dic['%s' % self.id]['after'] = "%s.locked" % i.decode("GB2312").encode("utf-8")
            elif self.choice == "decrypt":
                cipher_obj = TableCipher(self.method,self.key,random_string(method_supported[self.method][1]),0)
                encrypt_or_decrypt(cipher_obj,"%s" % i,0)
                self.response_dic['%s' % self.id]['before'] = "%s" % i.decode("GB2312").encode("utf-8")
                self.response_dic['%s' % self.id]['after'] = "%s" % i.replace(".locked","").decode("GB2312").encode("utf-8")
            else:
                print("Sorry 1")
                sys.exit()
        elif self.method in ["salsa20","chacha20"]:
            if self.choice == "encrypt":
                cipher_obj = SodiumCrypto(self.method,self.key,random_string(method_supported[self.method][1]),1)
                encrypt_or_decrypt(cipher_obj,"%s" % i,1)
                self.response_dic['%s' % self.id]['before'] = "%s" % i.decode("GB2312").encode("utf-8")
                self.response_dic['%s' % self.id]['after'] = "%s.locked" % i.decode("GB2312").encode("utf-8")
            elif self.choice == "decrypt":
                cipher_obj = SodiumCrypto(self.method,self.key,random_string(method_supported[self.method][1]),0)
                encrypt_or_decrypt(cipher_obj,"%s" % i,0)
                self.response_dic['%s' % self.id]['before'] = "%s" % i.decode("GB2312").encode("utf-8")
                self.response_dic['%s' % self.id]['after'] = "%s" % i.replace(".locked","").decode("GB2312").encode("utf-8")
            else:
                print("Sorry 2")
                sys.exit()
        else:
            cipher_obj = Encryptor(self.key,self.method)
            if self.choice == "encrypt":
                print(i.decode("GB2312").encode("utf-8"))
                encrypt_or_decrypt(cipher_obj,"%s" % i,1,force_update="no")
                self.response_dic['%s' % self.id]['before'] = "%s" % i.decode("GB2312").encode("utf-8")
                self.response_dic['%s' % self.id]['after'] = "%s.locked" % i.decode("GB2312").encode("utf-8")
                if self.response_dic['%s' % self.id]['before'].endswith(".zip"):
                    os.remove(self.response_dic['%s' % self.id]['before'])
            elif self.choice == "decrypt":
                encrypt_or_decrypt(cipher_obj,"%s" % i,0,force_update="no")
                self.response_dic['%s' % self.id]['before'] = "%s" % i.decode("GB2312").encode("utf-8")
                self.response_dic['%s' % self.id]['after'] = "%s" % i.replace(".locked","").decode("GB2312").encode("utf-8")
                if self.response_dic['%s' % self.id]['after'].endswith(".zip"):
                    kb = zipfile.ZipFile(self.response_dic['%s' % self.id]['after'])
                    kb.extractall(os.path.split(self.response_dic['%s' % self.id]['after'])[0])
                    os.remove(self.response_dic['%s' % self.id]['after'])
        end_time = time.time()
        self.response_dic['%s' % self.id]['time_used'] = int(end_time) - int(begin_time)
        self.queue.task_done()


method_supported = {
    'aes-128-cfb': (16, 16, OpenSSLCrypto),
    'aes-192-cfb': (24, 16, OpenSSLCrypto),
    'aes-256-cfb': (32, 16, OpenSSLCrypto),
    'aes-128-ofb': (16, 16, OpenSSLCrypto),
    'aes-192-ofb': (24, 16, OpenSSLCrypto),
    'aes-256-ofb': (32, 16, OpenSSLCrypto),
    'aes-128-ctr': (16, 16, OpenSSLCrypto),
    'aes-192-ctr': (24, 16, OpenSSLCrypto),
    'aes-256-ctr': (32, 16, OpenSSLCrypto),
    'aes-128-cfb8': (16, 16, OpenSSLCrypto),
    'aes-192-cfb8': (24, 16, OpenSSLCrypto),
    'aes-256-cfb8': (32, 16, OpenSSLCrypto),
    'aes-128-cfb1': (16, 16, OpenSSLCrypto),
    'aes-192-cfb1': (24, 16, OpenSSLCrypto),
    'aes-256-cfb1': (32, 16, OpenSSLCrypto),
    'bf-cfb': (16, 8, OpenSSLCrypto),
    'camellia-128-cfb': (16, 16, OpenSSLCrypto),
    'camellia-192-cfb': (24, 16, OpenSSLCrypto),
    'camellia-256-cfb': (32, 16, OpenSSLCrypto),
    'cast5-cfb': (16, 8, OpenSSLCrypto),
    'des-cfb': (8, 8, OpenSSLCrypto),
    'idea-cfb': (16, 8, OpenSSLCrypto),
    'rc2-cfb': (16, 8, OpenSSLCrypto),
    'rc4': (16, 0, OpenSSLCrypto),
    'seed-cfb': (16, 16, OpenSSLCrypto),
#     'rc4-md5': (16, 16, create_cipher),
    'salsa20': (32, 8, SodiumCrypto),
    'chacha20': (32, 8, SodiumCrypto),
    'table': (0, 0, TableCipher)
}

def run_cipher(cipher, decipher):
    from os import urandom
    import random
    import time

    BLOCK_SIZE = 16384
    rounds = 1 * 1024
    plain = urandom(BLOCK_SIZE * rounds)

    results = []
    pos = 0
    print('test start')
    start = time.time()
    while pos < len(plain):
        l = random.randint(100, 32768)
        c = cipher.update(plain[pos:pos + l])
        results.append(c)
        pos += l
    pos = 0
    c = b''.join(results)
    results = []
    while pos < len(plain):
        l = random.randint(100, 32768)
        results.append(decipher.update(c[pos:pos + l]))
        pos += l
    end = time.time()
    print('speed: %d bytes/s' % (BLOCK_SIZE * rounds / (end - start)))
    assert b''.join(results) == plain


def test_salsa20():
    cipher = SodiumCrypto('salsa20', b'k' * 32, b'i' * 16, 1)
    decipher = SodiumCrypto('salsa20', b'k' * 32, b'i' * 16, 0)

    run_cipher(cipher, decipher)


def test_chacha20():

    cipher = SodiumCrypto('chacha20', b'k' * 32, b'i' * 16, 1)
    decipher = SodiumCrypto('chacha20', b'k' * 32, b'i' * 16, 0)

    run_cipher(cipher, decipher)


if __name__ == '__main__':
    if len(sys.argv) not in [3,4]:
        print_help()

    #check the method if nt not support salsa20 and chacha20 on some win system; eg: win7
    if method in ['salsa20','chacha20'] and os.name == "nt":
        print("Sorry.. method [salsa20/chacha20] not supported on windows; eg: win7  Please change the method")
        sys.exit()

    the_deal_path_ori = get_config()
    my_queue = Queue.Queue()
    result_dic = {}
    result_dic['method'] = method
    try:
        if dir_as_one_file:
            if os.name == 'posix':
                the_deal_path = get_tar_path(the_deal_path)
                if the_deal_path == "":
                    the_deal_path = get_the_zip_path_for_dir(the_deal_path)
            elif os.name == 'nt':
                the_deal_path = get_the_zip_path_for_dir(the_deal_path)
            if the_deal_path != "":
                shutil.rmtree(the_deal_path_ori)
        if method in ["salsa20","chacha20"] and not loaded:
            load_libsodium()
        elif method not in ['table'] and not loaded:
            load_openssl()
        if os.path.isdir(the_deal_path):
            os.chdir(the_deal_path)
            if choice == "encrypt":
                all_encrypt_files = [f for f in glob.glob("*") if "locked" not in f and os.path.isfile(f)]
                for i in range(len(all_encrypt_files)):
                    if os.name == 'nt':
                        t = do_encrypt_or_decrypt_win(my_queue,result_dic,i,key,method,choice)
                    elif os.name == "posix":
                        t = do_encrypt_or_decrypt_linux(my_queue,result_dic,i,key,method,choice)
                    t.setDaemon(True)
                    t.start()
                result_dic['direction'] = 'encrypt'
                for one_file in all_encrypt_files:
                    my_queue.put(one_file)
            elif choice == "decrypt":
                all_decrypt_files = [f for f in glob.glob("*.locked")]
                for i in range(len(all_decrypt_files)):
                    if os.name == 'nt':
                        t = do_encrypt_or_decrypt_win(my_queue,result_dic,i,key,method,choice)
                    elif os.name == "posix":
                        t = do_encrypt_or_decrypt_linux(my_queue,result_dic,i,key,method,choice)
                    t.setDaemon(True)
                    t.start()
                result_dic['direction'] = 'decrypt'
                for one_file in all_decrypt_files:
                    my_queue.put(one_file)
            my_queue.join()
        elif os.path.isfile(the_deal_path):
            thread_num = 1
            if choice == "encrypt":
                if "locked" in the_deal_path:
                    raise Exception("The file has been locked.. %s" % the_deal_path)
                for i in range(thread_num):
                    if os.name == 'nt':
                        t = do_encrypt_or_decrypt_win(my_queue,result_dic,i,key,method,choice)
                    elif os.name == "posix":
                        t = do_encrypt_or_decrypt_linux(my_queue,result_dic,i,key,method,choice)
                    t.setDaemon(True)
                    t.start()
                result_dic['direction'] = 'encrypt'
                my_queue.put(the_deal_path)
            elif choice == "decrypt":
                for i in range(thread_num):
                    if os.name == 'nt':
                        t = do_encrypt_or_decrypt_win(my_queue,result_dic,i,key,method,choice)
                    elif os.name == "posix":
                        t = do_encrypt_or_decrypt_linux(my_queue,result_dic,i,key,method,choice)
                    t.setDaemon(True)
                    t.start()
                result_dic['direction'] = 'decrypt'
                my_queue.put(the_deal_path)
            my_queue.join()
        print_json(result_dic)
        open("%s%sencrypt_or_decrypt.log" % (os.path.split(os.path.abspath(__file__))[0],os.sep),'a+').write("%s\n-------------------------%s-----------------------\n\n" % (json.dumps(result_dic,indent=4,ensure_ascii=False,sort_keys=True),time.strftime("%Y-%m-%d %H:%M:%S")))
    except Exception as e:
        print("ERROR INFO: %s" % str(e))
        sys.exit()
    except:
        for i in str(traceback.format_exc()).splitlines():
            print(i)


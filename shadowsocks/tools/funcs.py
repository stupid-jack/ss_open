#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os,time,sys,datetime
import signal
import platform
import urllib
import urllib2
import json
import socket,codecs,re
import errno
import sys
import datetime
import smtplib
import mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from os.path import join, getsize
from collections import OrderedDict
import global_vars as vars
from decimal import *
import calendar

import socket
socket.setdefaulttimeout(15)
reload(sys)
sys.setdefaultencoding('utf8')

mailto_list=[""] #收件人列表
mail_host="smtp.gmail.com"  #设置服务器
mail_user=""    #用户名
mail_pass=""   #口令
mail_postfix="gmail.com"  #发件箱的后缀

class FileLock(object):
    """ A file locking mechanism that has context-manager support so
        you can use it in a ``with`` statement. This should be relatively cross
        compatible as it doesn't rely on ``msvcrt`` or ``fcntl`` for the locking.
    """

    class FileLockException(Exception):
        pass

    def __init__(self, protected_file_path, timeout=None, delay=1, lock_file_contents=None):
        """ Prepare the file locker. Specify the file to lock and optionally
            the maximum timeout and the delay between each attempt to lock.
        """
        self.is_locked = False
        self.lockfile = protected_file_path + ".lock"
        self.timeout = timeout
        self.delay = delay
        self._lock_file_contents = lock_file_contents
        if self._lock_file_contents is None:
            self._lock_file_contents = "Owning process args:\n"
            for arg in sys.argv:
                self._lock_file_contents += arg + "\n"

    def locked(self):
        """
        Returns True iff the file is owned by THIS FileLock instance.
        (Even if this returns false, the file could be owned by another FileLock instance, possibly in a different thread or process).
        """
        return self.is_locked

    def available(self):
        """
        Returns True iff the file is currently available to be locked.
        """
        return not os.path.exists(self.lockfile)

    def acquire(self, blocking=True):
        """ Acquire the lock, if possible. If the lock is in use, and `blocking` is False, return False.
            Otherwise, check again every `self.delay` seconds until it either gets the lock or
            exceeds `timeout` number of seconds, in which case it raises an exception.
        """
        start_time = time.time()
        wait_num = 0
        while True:
            try:
                # Attempt to create the lockfile.
                # These flags cause os.open to raise an OSError if the file already exists.
                fd = os.open( self.lockfile, os.O_CREAT | os.O_EXCL | os.O_RDWR )
                with os.fdopen( fd, 'a' ) as f:
                    # Print some info about the current process as debug info for anyone who bothers to look.
                    f.write( self._lock_file_contents )
                break;
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
                if self.timeout is not None and (time.time() - start_time) >= self.timeout:
                    raise FileLock.FileLockException("Timeout occurred.")
                if not blocking:
                    return False
                time.sleep(self.delay)
                wait_num += self.delay
                print "I have wait for the lock for %s seconds" % wait_num
        self.is_locked = True
        return True

    def release(self):
        """ Get rid of the lock by deleting the lockfile.
            When working in a `with` statement, this gets automatically
            called at the end.
        """
        self.is_locked = False
        os.unlink(self.lockfile)


    def __enter__(self):
        """ Activated when used in the with statement.
            Should automatically acquire a lock to be used in the with block.
        """
        self.acquire()
        return self


    def __exit__(self, type, value, traceback):
        """ Activated at the end of the with statement.
            It automatically releases the lock if it isn't locked.
        """
        self.release()


    def __del__(self):
        """ Make sure this ``FileLock`` instance doesn't leave a .lock file
            lying around.
        """
        if self.is_locked:
            self.release()

    def purge(self):
        """
        For debug purposes only.  Removes the lock file from the hard disk.
        """
        if os.path.exists(self.lockfile):
            self.release()
            return True
        return False

def lock_the_file(file_path,lock_file_con=None,lock_timeout=30):
    if os.path.exists(file_path) is True:
        if lock_file_con:
            lock_t = FileLock(file_path,lock_file_contents=lock_file_con,timeout=lock_timeout)
        else:
            lock_t = FileLock(file_path,timeout=lock_timeout)
        return lock_t
    else:
        return None

def lock_the_file_and_touch(file_path,lock_file_con=None,lock_timeout=30):
    if os.path.exists(file_path) is True:
        if lock_file_con:
            lock_t = FileLock(file_path,lock_file_contents=lock_file_con,timeout=lock_timeout)
        else:
            lock_t = FileLock(file_path,timeout=lock_timeout)
        return lock_t
    else:
        file_abs_path = get_file_abs_path(file_path)
        mk_dir_if_not_exist(file_abs_path)
        touch('''%s''' % file_abs_path)
        lock_t = FileLock(file_path,timeout=lock_timeout)
        return lock_t

def check_lock_num_and_delete(fl_obj,check_num=5,the_log_obj=None):
    check_file = fl_obj.lockfile
    check_lock_num_file = "%s.num" % check_file
    if os.path.exists(check_file) is True:
        if os.path.exists(check_lock_num_file) is True:
            N = int(open(check_lock_num_file).read())
            if N >= check_num:
                with open(check_lock_num_file,"w+") as f:
                    f.write("0\n")
                os.unlink(check_file)
                if the_log_obj:
                    the_log_obj.write_run("I need to delete the lock file [%s] cause now it's bigger than %s" % (check_file,check_num),2)
                    the_log_obj.write_run("""write 0 to check_lock_file [%s]""" % check_lock_num_file,2)
            else:
                N += 1
                with open(check_lock_num_file,"w+") as f:
                    f.write("%s\n" % N)
                if the_log_obj:
                    the_log_obj.write_run("no need to delete the lock file [%s]" % check_file,2)
                    the_log_obj.write_run("""write %s to check_lock_file [%s] """ % (N,check_lock_num_file),2)
        else:
            with open(check_lock_num_file,"w+") as f:
                f.write("0\n")
            if the_log_obj:
                the_log_obj.write_run("""write 0 to check_lock_file [%s] """ % check_lock_num_file,2)

def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv

def _decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value
    return rv

def json_loads_unicode_to_string(data):
    #return json.loads(data,object_hook=_decode_list)
    return json.loads(data,object_hook=_decode_dict)

def json_dumps_unicode_to_string(data):
    if type(data) is list:
        result = _decode_list(data)
    elif type(data) is dict:
        result = _decode_dict(data)
    else:
        result = data
    return json.dumps(result,indent=4,sort_keys=True,ensure_ascii=False)

def get_file_size(file_path):
    if os.path.exists(file_path) is not True:
        print "File not exists [%s]" % file_path
        sys.exit()
    return (os.path.getsize(file_path),"bytes")

def get_dir_size(dir):
    if os.path.exists(dir) is not True:
        print "Sorry. dir not found . [%s]" % dir
        sys.exit()
    size = 0L
    for root, dirs, files in os.walk(dir):
        size += sum([getsize(join(root, name)) for name in files])
    return (size,"bytes")

def mk_dir_if_not_exist(path):
    uid = os.getuid()
    gid = os.getgid()
    dir_path = os.path.split(path)[0]
    if dir_path in ["","."]:
        dir_path = os.path.split(path)[1]
    if os.path.exists(dir_path) is not True:
        os.makedirs(dir_path)
        os.chown(dir_path,uid,gid)

def touch(fname):
    if os.path.exists(fname):
        os.utime(fname, None)
    else:
        open(fname, 'a').close()

def touch2(fname, mode=0o666, dir_fd=None, **kwargs):
    flags = os.O_CREAT | os.O_APPEND
    with os.fdopen(os.open(fname, flags=flags, mode=mode, dir_fd=dir_fd)) as f:
        os.utime(f.fileno() if os.utime in os.supports_fd else fname,
            dir_fd=None if os.supports_fd else dir_fd, **kwargs)

def mk_dir(path):
    dir_path = path
    if os.path.exists(dir_path) is not True:
        os.makedirs(dir_path)

def encrypt_str_1(data):
    d1 = {'c': '[_2_]', 'e': '[_j_]', 'd': '[_4_]', 'g': '[_66_]', 'f': '[_&_]', 'h': '[_<_]', 'j': '[_g_]', 'm': '[_j_]', 'l': '[_33_]', 'o': '[_sx_]', 'n': '[_m_]', 'q': '[_o_]', 'p': '[_rr_]', 'u': '[_b_]', 'y': '[_nb_]', 'x': '[_kk_]','3':'[_$_]','5':'[_&_]'}
    data = str(data).strip()
    tmp_l = []
    for k in data:
        if str(k) in d1:
            tmp_l.append(d1[k])
            #data.replace(k,d1[k])
        else:
            tmp_l.append(k)
        #if str(k).lower() in d1 and str(k).lower() in d1:
        #   tmp_l.append("%s_" % d1[str(k).lower()])
        #elif str(k).lower() in d1 and str(k) in d1:
        #   tmp_l.append(d1[k])
    return "".join(tmp_l)

def decrypt_str_1(data):
    d1 = {'c': '[_2_]', 'e': '[_j_]', 'd': '[_4_]', 'g': '[_66_]', 'f': '[_&_]', 'h': '[_<_]', 'j': '[_g_]', 'm': '[_j_]', 'l': '[_33_]', 'o': '[_sx_]', 'n': '[_m_]', 'q': '[_o_]', 'p': '[_rr_]', 'u': '[_b_]', 'y': '[_nb_]', 'x': '[_kk_]','3':'[_$_]','5':'[_&_]'}
    d3 = {'sx': 'o', 'rr': 'p', 'g': 'j', '&': 'f', '33': 'l', 'nb': 'y', 'j': 'm', 'm': 'n', 'o': 'q', 'kk': 'x', '2': 'c', '4': 'd', '66': 'g', 'b': 'u', '<': 'h'}
    d4 = {'66_': 'g', '4_': 'd', '33_': 'l', 'j_': 'm', 'nb_': 'y', 'g_': 'j', '<_': 'h', '2_': 'c', 'kk_': 'x', '&_': 'f', 'o_': 'q', 'rr_': 'p', 'm_': 'n', 'b_': 'u', 'sx_': 'o'}
    data = str(data).strip()
    tmp_l = []
    for k,v in d1.items():
        if v in data:
            #print "oh year"
            data = data.replace(v,k)
    return data

def encrypt_str_2(data):
    data = str(data).strip()
    data = data[-1] + data[1:-1] + data[0]
    data = data[:2] + data[-5:-4] + data[3:-5] + data[2:3] + data[-4:]
    data = data + "ops"
    return data

def decrypt_str_2(data):
    data = str(data).strip()
    data = data[:-3]
    data = data[-1] + data[1:-1] + data[0]
    data = data[:2] + data[-5:-4] + data[3:-5] + data[2:3] + data[-4:]
    return data

def encrypt_str_3(data):
    a = {1:3,-3:-2,-5:-1}
    data = str(data).strip()
    data = list(data)
    for k,v in a.items():
        t = data[k]
        data[k] = data[v]
        data[v] = t
    for kk in range(len(data)):
        if data[kk].isupper():
            data[kk] = data[kk].lower()
            break
    return "".join(data)

def decrypt_str_3(data):
    a = {-1:-5,-2:-3,3:1}
    data = str(data).strip()
    data = list(data)
    for kk in range(len(data)):
        if data[kk].islower():
            data[kk] = data[kk].upper()
            break
    for k,v in a.items():
        t = data[k]
        data[k] = data[v]
        data[v] = t
    return "".join(data)

def t_to_l(t):
    new_list = []
    for i in t:
        new_list.append(list(i))
    for i in range(len(new_list)):
        for j in range(len(new_list[i])):
            new_list[i][j] = str(new_list[i][j])
    return new_list

def check_the_platform():
    if platform.system().lower() == "linux":
        return "linux"
    elif platform.system().lower() == "darwin":
        return "mac"
    elif platform.system().lower() == "windows":
        return "win"
    else:
        return "Unknown"

def get_monday_to_sunday():
    a = datetime.datetime.today()
    b = a.weekday()
    the_last = a + datetime.timedelta(6 - a.weekday())
    if b == 0:
        the_first = a
    else:
        the_first = get_the_one_date(b,"-")
    return (the_first,the_last)

def get_monday_to_sunday_with_everyday():
    ff = []
    for i in range(7):
        d = convert_datetime_to_string(get_monday_to_sunday()[0] + datetime.timedelta(days=i),default_list=False,only_date=True)
        ff.append(d)
    return ff

def get_this_month_first_day_to_last():
    date1 = datetime.datetime.now()
    y=date1.year
    m = date1.month
    month_start_dt = datetime.datetime(y,m,1)
    if m == 12:
        month_end_dt = datetime.datetime(y+1,1,1) - datetime.timedelta(days=1)
    else:
        month_end_dt = datetime.datetime(y,m+1,1) - datetime.timedelta(days=1)
    return (month_start_dt,month_end_dt)

def get_this_month_first_day_to_last_with_everyday():
    ff = []
    for i in range(31):
        d = convert_datetime_to_string(get_this_month_first_day_to_last()[0] + datetime.timedelta(days=i),default_list=False,only_date=True)
        if d == convert_datetime_to_string(get_this_month_first_day_to_last()[1],default_list=False,only_date=True):
            ff.append(d)
            break
        else:
            ff.append(d)
    return ff

def get_this_quarter_first_day_and_last_day():
    date1 = datetime.datetime.now()
    y=date1.year
    month = date1.month
    if month in (1,2,3):
        quarter_start_dt = datetime.datetime(y,1,1)
        quarter_end_dt = datetime.datetime(y,4,1) - datetime.timedelta(days=1)
    elif month in (4,5,6):
        quarter_start_dt = datetime.datetime(y,4,1)
        quarter_end_dt = datetime.datetime(y,7,1) - datetime.timedelta(days=1)
    elif month in (7,8,9):
        quarter_start_dt = datetime.datetime(y,7,1)
        quarter_end_dt = datetime.datetime(y,10,1) - datetime.timedelta(days=1)
    else:
        quarter_start_dt = datetime.datetime(y,10,1)
        quarter_end_dt = datetime.datetime(y+1,1,1) - datetime.timedelta(days=1)
    return (quarter_start_dt,quarter_end_dt)

def get_this_quarter_total_days_and_remain_days():
    date1 = datetime.datetime.now()
    a = get_this_quarter_first_day_and_last_day()
    quarter_days = (a[1] - a[0]).days + 1
    quarter_rem = (a[1] - date1).days
    return (quarter_days,quarter_rem)

def get_last_month_first_day_to_last():
    date1 = datetime.datetime.now()
    y=date1.year
    m = date1.month
    if m==1:
        start_date=datetime.datetime(y-1,12,1)
    else:
        start_date=datetime.datetime(y,m-1,1)
    end_date=datetime.datetime(y,m,1) - datetime.timedelta(days=1)
    return (start_date,end_date)

def convert_seconds_to_time(second):
    a = "{:0>8}".format(datetime.timedelta(seconds=second))
    return a

def get_last_monday_to_sunday():
    date1 = datetime.datetime.now()
    last_week_start_dt = date1-datetime.timedelta(days=date1.weekday()+7)
    last_week_end_dt = date1-datetime.timedelta(days=date1.weekday()+1)
    return (last_week_start_dt,last_week_end_dt)

def get_the_date_of_last(days,out_string=False):
    TODAY = datetime.datetime.today()
    date_list =[]
    for i in range(days,0,-1):
        NUM_DAY = datetime.timedelta(days=i)
        date_list.append(TODAY - NUM_DAY)
    if out_string == True:
        return convert_datetime_to_string(date_list)
    else:
        return date_list

def get_the_date_of_last_with_today(days,out_string=False):
    TODAY = datetime.datetime.today()
    date_list =[]
    for i in range(days):
        NUM_DAY = datetime.timedelta(days=i)
        date_list.insert(0,TODAY - NUM_DAY)
    if out_string == True:
        return convert_datetime_to_string(date_list)
    else:
        return date_list

def convert_datetime_to_string(datetime_obj_list,default_list=True,only_date=False):
    ret = []
    if default_list is not True:
        if only_date:
            return datetime_obj_list.strftime("%Y-%m-%d")
        else:
            return datetime_obj_list.strftime("%Y-%m-%d %H:%M:%S")
    for i in datetime_obj_list:
        if only_date:
            ret.append(i.strftime("%Y-%m-%d"))
        else:
            ret.append(i.strftime("%Y-%m-%d %H:%M:%S"))
    return ret

def get_the_one_date(num,choice):
    TODAY = datetime.datetime.today()
    if str(choice) == '-':
        NUM_DAY = datetime.timedelta(days=(int(num)))
        the_date = TODAY - NUM_DAY
        return the_date
    elif str(choice) == '+':
        NUM_DAY = datetime.timedelta(days=(int(num)))
        the_date = TODAY + NUM_DAY
        return the_date
    else:
        print "ERROR! from functions.get_the_one_date"
        sys.exit()

def get_the_24_hour_format_for_mysql_query():
    time_list_before = []
    time_list_after = []
    for i in range(24):
        time_list_before.append("%s:00:00" % i)
        time_list_after.append("%s:59:59" % i)
    return time_list_before,time_list_after

#open the ip data file and store all in list
if os.path.exists("/tmp/all_ip_with_location.txt") is True:
    f = open("/tmp/all_ip_with_location.txt","r")
    all_ip_location_list = f.read().splitlines()
    f.close()
else:
    all_ip_location_list = []

def check_ip_location_if_in_local_file(all_ip_info,check_ip):
    _all_ip = all_ip_info
    i = ""
    for i in _all_ip:
        if i.split(':')[0].strip() == check_ip.strip():
            return (10,i)
    return (8,i)

def get_match_substr_from_str(ori_string,re_compile_str):
    pattern = re.compile(r'%s' % re_compile_str)
    a = pattern.findall("%s" % ori_string)
    if len(a) != 0:
        return a
    else:
        return []


def get_ip_location(ip):
    re_ipaddress = re.compile(r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
    re_domain = re.compile(r'[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+\.?')
    if re_ipaddress.match(ip):
        url = "http://ip.taobao.com/service/getIpInfo.php?ip="
        #Use the file ip location
        #
        num_and_location = check_ip_location_if_in_local_file(all_ip_location_list,ip)
        if num_and_location[0] == 10:
            #print "File"
            return num_and_location[1].split(':')[1]
        #
        else:
            data = urllib.urlopen(url + ip).read()
            datadict=json.loads(data)
            for oneinfo in datadict:
                if "code" == oneinfo:
                    if datadict[oneinfo] == 0:
                        result = datadict["data"]["country"] + datadict["data"]["region"] + datadict["data"]["city"] + datadict["data"]["isp"]
                        ll = "%s" % ip.strip() + ":" + result
                        f = codecs.open("/tmp/all_ip_with_location.txt","a+","utf-8")
                        f.write("%s\n" % ll)
                        f.close()
                        #print "Net"
                        return datadict["data"]["country"] + datadict["data"]["region"] + datadict["data"]["city"] + datadict["data"]["isp"]
    else:
        raise SystemError,"The ip %s is wrong." % ip
        sys.exit()

def get_ip_from_domain(www):
    re_ipaddress = re.compile(r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
    re_domain = re.compile(r'[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+\.?')
    if re_domain.match(www):
        result = socket.getaddrinfo(www, None)
        ip_address = result[0][4][0]
        return ip_address
    else:
        raise SystemError,"The domain %s is wrong" % www
        sys.exit()

def get_the_time_now(sign):
    if sign == "begin":
        return datetime.datetime.now()
    elif sign == "end":
        return datetime.datetime.now()
    else:
        print "ERROR..Not the right sign...It should be begin OR end"
        sys.exit()

def caculate_the_seconds(begin,end):
    return end - begin

################################ send mail funcs #################################
#------------- 只有文字，可以发送中文
#
def send_mail_just_text(to_list,subject,content=None):
    if content == None:
        content = ""
    me="hello"+"<"+mail_user+"@"+mail_postfix+">"
    msg = MIMEText(content,_subtype='plain',_charset='UTF8')
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.starttls()
        server.login(mail_user,mail_pass)
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        return True
    except Exception, e:
        print str(e)
        return False

#------------  发送html格式的邮件
#
def send_mail_html(to_list,subject,content=None):  #to_list：收件人；subject：主题；content：邮件内容
    if content == None:
        content = ""
    me="hello"+"<"+mail_user+"@"+mail_postfix+">"   #这里的hello可以任意设置，收到信后，将按照设置显示
    msg = MIMEText(content,_subtype='html',_charset='UTF8')    #创建一个实例，这里设置为html格式邮件
    msg['Subject'] = subject    #设置主题
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    try:
        s = smtplib.SMTP()
        s.connect(mail_host)  #连接smtp服务器
        s.starttls()
        s.login(mail_user,mail_pass)  #登陆服务器
        s.sendmail(me, to_list, msg.as_string())  #发送邮件
        s.close()
        return True
    except Exception, e:
        print str(e)
        return False

# ------------- 可以发送附件，可以添加多个附件
#
def send_mail_with_att(to_list,subject,att=None):
    #创建一个带附件的实例
    msg = MIMEMultipart()

    if att != None:
        for i in att:
            if os.path.exists(i) != True:
                continue
            else:
                att_tmp = MIMEText(open(i,'rb').read(),'base64','utf8')
                att_tmp["Content-Type"] = 'application/octet-stream'
                att_tmp["Content-Disposition"] = 'attachment; filename="%s"' % os.path.split(i)[1] #这里的filename可以任意写，写什么名字，邮件中显示什么名字
                msg.attach(att_tmp)

    #msg['to'] = 'qq@qq.com'
    msg['to'] =";".join(to_list)
    msg['from'] = 'gg@gmail.com'
    msg['subject'] = subject
    #发送邮件
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.starttls()
        server.login(mail_user,mail_pass)#XXX为用户名，XXXXX为密码
        server.sendmail(msg['from'], msg['to'],msg.as_string())
        server.quit()
        print '发送成功'
    except Exception, e:
        print str(e)


# ------------- 图片附件，可以发送图片附件。但是附件名称不对
#
def send_mail_with_pic(to_list,subject,pic=None):
    msg = MIMEMultipart()
    msg['To'] = ';'.join(to_list)
    msg['From'] = 'gg@gmail.com'
    msg['Subject'] = '%s' % subject

    txt = MIMEText("发送给你一些图片，瞧瞧吧，亲~~",'plain','utf8')
    msg.attach(txt)

    if pic == None:
        pic = ""
    else:
        for i in pic:
            if os.path.exists(i) != True:
                continue
            else:
                file1 = "%s" % i
                image = MIMEImage(open(file1,'rb').read())
                image.add_header('Content-ID','<image1>')
                msg.attach(image)

    server = smtplib.SMTP()
    server.connect(mail_host)
    server.starttls()
    server.login(mail_user,mail_pass)
    server.sendmail(msg['From'],msg['To'],msg.as_string())
    server.quit()

#------- all type

def send_mail_with_all(to_list,subject,html_content=None,att=None):
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject

    # Create the body of the message (a plain-text and an HTML version).
    if html_content == None:
        html_content = ""
    text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.python.org"
    html = html_content

    # Record the MIME types of both parts - text/plain and text/html.
    #part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    msg.attach(part2)
    #构造附件
    if att == None:
        att = ""
    else:
        for i in att:
            if os.path.exists(i) != True:
                continue
            else:
                att_tmp = MIMEText(open(i, 'rb').read(), 'base64', 'utf-8')
                att_tmp["Content-Type"] = 'application/octet-stream'
                att_tmp["Content-Disposition"] = 'attachment; filename="%s"' % os.path.split(i)[1]
                msg.attach(att_tmp)

    ##加邮件头
    msg['to'] = 'qq@qq.com'
    msg['from'] = 'gg@gmail.com'
    #msg['subject'] = 'hello world'

    server = smtplib.SMTP()
    server.connect(mail_host)
    server.starttls()
    server.login(mail_user,mail_pass)#XXX为用户名，XXXXX为密码
    server.sendmail(msg['from'], msg['to'],msg.as_string())
    server.quit()


def split_list(list_tmp,N):
    new_list = []
    try:
        N = abs(int(float(N)))
    except:
        print "From functions.py func split_list: N should be int"
        sys.exit()
    N_1 = len(list_tmp) / N
    N_2 = len(list_tmp) % N
    for i in range(N_1):
        new_list.append(list_tmp[i*N:(i+1)*N])
    if N_2 != 0:
        new_list.append(list_tmp[N_1*N:])
    return new_list

def a_list_of_date(given_date,months_num):
    year = int(str(given_date).strip().split('-')[0])
    month = int(str(given_date).strip().split('-')[1])
    out_list = []
    date1 = datetime.datetime(year,month,1)
    for i in range(int(months_num)):
        date2 = date1 - datetime.timedelta(days=1)
        out_list.append(date2.strftime("%Y-%m"))
        date1 = datetime.datetime(int(out_list[-1].split('-')[0]),int(out_list[-1].split('-')[1]),1)
    return out_list


def run_shell_command(command_string):
    from subprocess import Popen,PIPE
    cmd = "%s" % command_string.strip()
    p = Popen(cmd,shell=True,stdout=PIPE,stderr=PIPE)
    out,err = p.communicate()
    return (p.returncode,out.rstrip(),err.rstrip())

def run_shell_command_2(command_string):
    from subprocess import Popen,PIPE
    cmd = "%s" % command_string.strip()
    p = Popen(cmd,shell=True,stdout=PIPE,stderr=PIPE)
    out,err = p.communicate()
    if p.returncode == 0:
        return ("ok",out.rstrip(),err.rstrip())
    else:
        return ("problem",out.rstrip(),err.rstrip())

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

def is_valid_ip(ip_string):
    try:
        parts = ip_string.split('.')
        return len(parts) == 4 and all(0 <= int(part) < 256 for part in parts)
    except ValueError:
        return False # one of the 'parts' not convertible to integer
    except (AttributeError, TypeError):
        return False # `ip` isn't even a string


def get_all_ip_from_string(string):
    ret = []
    import re
    ipPattern = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
    aab = re.findall(ipPattern,string)
    for ip in aab:
        if is_valid_ip(ip):
            ret.append(ip)
    return ret

def get_all_ip_from_string_with_uniq_result(string):
    ret = []
    import re
    ipPattern = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
    aab = re.findall(ipPattern,string)
    for ip in aab:
        if is_valid_ip(ip):
            ret.append(ip)
    return list(set(ret))

def print_json(json_obj,indent_=4):
    print "-" * 50
    print json.dumps(json_obj,indent=indent_,ensure_ascii=False,sort_keys=True)
    print "-" * 60

def print_json_with_sort_all_num_keys(data,indent_=4):
    tmp_dic = {}
    for k,v in data.items():
        tmp_dic[int(k)] = v
    print "-" * 50
    print json.dumps(tmp_dic,indent=indent_,ensure_ascii=False,sort_keys=True)
    print "-" * 60

def cd_into_cwd_dir(running_script):
    os.chdir(os.path.split(os.path.realpath(running_script))[0])

def multikeysort(dic, columns):
    comparers = [
        ((i(col[1:].strip()), -1) if col.startswith('-') else (i(col.strip()), 1))
        for col in columns
    ]
    def comparer(left, right):
        comparer_iter = (
            cmp(fn(left), fn(right)) * mult
            for fn, mult in comparers
        )
        return next((result for result in comparer_iter if result), 0)
    return sorted(dic.items, cmp=comparer)

def sort_dict_return_OrderedDict(ori_dic,sort_by="key"):
    try:
        new_dic = OrderedDict()
        import operator
        if sort_by == "key":
            sorted_x = sorted(ori_dic.items(), key=operator.itemgetter(0))
        else:
            sorted_x = sorted(ori_dic.items(), key=operator.itemgetter(1))
        for i in sorted_x:
            new_dic[i[0]] = i[1]
        return new_dic
    except:
        return ori_dic

def sort_dict_by_key_return_OrderedDict(ori_dic,reverse=False,key_is_num=False):
    try:
        new_dic = OrderedDict()
        import operator
        sorted_x = sorted(ori_dic.items(), key=operator.itemgetter(0))
        if reverse:
            sorted_x.reverse()
        for i in sorted_x:
            if key_is_num:
                new_dic[int(i[0])] = i[1]
            else:
                new_dic[i[0]] = i[1]
        return new_dic
    except:
        return ori_dic

def sort_dict_by_the_value_keystring(ori_dic,value_key):
    try:
        sorted_by_value_key = OrderedDict(sorted(ori_dic.items(), key=lambda kv: kv[1]["%s" % str(value_key).strip()],reverse=True))
        return sorted_by_value_key
    except:
        return ori_dic

def timestamp_to_time(the_timestamp):
    time = datetime.datetime.fromtimestamp(int("%s" % the_timestamp)).strftime('%Y-%m-%d %H:%M:%S')
    return str(time)

def time_to_timestamp(the_time):
    timestamp = time.mktime(datetime.datetime.strptime(the_time, '%Y-%m-%d %H:%M:%S').timetuple())
    #time = datetime.datetime.fromtimestamp(int("%s" % the_timestamp)).strftime('%Y-%m-%d %H:%M:%S')
    return int(timestamp)

def write_to_file_with_tmp_file(last_file,content,is_list=False):
    tmp_file = "%s.tmp" % last_file
    with open(tmp_file) as f:
        if is_list:
            for i in content:
                f.write("%s\n" % str(i).strip())
        else:
            f.write(content)
            f.write("\n")
    os.rename(tmp_file,last_file)

def hasNumbers(inputString):
    return any(char.isdigit() for char in str(inputString))

def allNumbers(inputString):
    return all(char.isdigit() for char in str(inputString))

def get_all_disk_of_this_machine():
    ret = run_shell_command("ls -al /dev/disk/by-id/ata*|awk -F'/' '{print $NF}'|sort -V")
    if ret[0] == 0:
        only_disk = []
        disk_with_part = []
        for disk in ret[1].split('\n'):
            if hasNumbers(disk):
                disk_with_part.append(disk)
            else:
                only_disk.append(disk)
        return (only_disk,disk_with_part)
    else:
        return ""

def human(num, power="Bi"):
    num = int(num)
    powers = ["Bi","Ki", "Mi", "Gi", "Ti"]
    while num >= 1000: #4 digits
        num /= 1024.0
        power = powers[powers.index(power)+1]
    return "%.1f %s" % (num, power)


def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split('(\d+)', text) ]

def insert_into_list(ori_list,match_string,insert_data):
    jk = ""
    for i in range(len(ori_list)):
        if str(ori_list[i]).startswith(str(match_string)):
            jk = i
            break
    if jk != "":
        ori_list.insert(jk,insert_data)
    return ori_list

def color_print(msg, color='red', exits=False):
    """
    Print colorful string.
    颜色打印字符或者退出
    """
    color_msg = {'blue': '\033[1;36m%s\033[0m',
                 'green': '\033[1;32m%s\033[0m',
                 'yellow': '\033[1;33m%s\033[0m',
                 'red': '\033[1;31m%s\033[0m',
                 'title': '\033[30;42m%s\033[0m',
                 'info': '\033[32m%s\033[0m'}
    msg = color_msg.get(color, 'red') % msg
    print msg
    if exits:
        time.sleep(2)
        sys.exit()
    return msg

def traceback_to_file(log_obj,debug=0):
    try:
        import traceback
        for i in str(traceback.format_exc()).splitlines():
            if debug == 1:
                log_obj.write_err(i,3)
            else:
                log_obj.write_err(i,2)
    except Exception as e:
        print "%s" % str(e)

def check_requests_version():
    try:
        import requests
        if int(requests.__version__.split(".")[1]) < 7:
            return "sorry\nrequests version too low"
        else:
            return "ok"
    except Exception as e:
        return "ERROR when import requests module."

def time_to_sec(time_str):
    if len(time_str.split(":")) == 2:
        h, m = time_str.split(':')
        s = ""
    elif len(time_str.split(":")) == 3:
        h, m, s = time_str.split(':')
    elif len(time_str.split(":")) == 1:
        h = time_str.split(":")[0]
        m = ""
        s = ""
    if str(h) == "":
        h = 0
    if str(m) == "":
        m = 0
    if str(s) == "":
        s = 0
    return int(h) * 3600 + int(m) * 60 + int(s)

def aggregate_dic_by_keystring(the_dic,N=6):
    new_dic = OrderedDict()
    #the_dic = _decode_dict(the_dic)
    for k,v in the_dic.items():
        if new_dic == {}:
            if allNumbers(v):
                new_dic[k] = v
            else:
                new_dic[k] = 1
            continue
        else:
            #new_dic = _decode_dict(new_dic)
            for k1,v1 in new_dic.items():
                if k.startswith(k1) or k1[:N] == k[:N] or k1.startswith(k) or k1 in k or k in k1:
                    join = "yes"
                    break
                else:
                    join = "no"
            if join == "yes":
                new_dic[k1] += 1
            else:
                if allNumbers(v):
                    new_dic[k] = v
                else:
                    new_dic[k] = 1
    return new_dic

def deal_sys_encoding():
    import sys
    if sys.getdefaultencoding() != "utf8":
        reload(sys)
        sys.setdefaultencoding("utf8")

def get_shell_cmd_output(shell_cmd_str):
    ret = run_shell_command_3(shell_cmd_str)
    if ret[0] == "ok":
        return ret[1]
    else:
        return "failed"

def read_json_from_file(file_path):
    if os.path.exists(file_path) is not True:
        return "{}"
    else:
        if os.path.getsize(file_path) == 0 or str(open(file_path).read().strip("\n")) == "{}":
            return "{}"
        else:
            return open(file_path).read().strip().strip("\n")

def read_json_from_file_return_dic(file_path):
    file_path = str(file_path).strip()
    if os.path.exists(file_path) is not True:
        return {}
    else:
        if os.path.getsize(file_path) == 0 or str(open(file_path).read().strip("\n")) == "{}":
            return {}
        else:
            return json.loads(open(file_path).read().strip().replace("\n",""),strict=False,object_hook=_decode_dict)

def get_file_abs_path_two_part(rel_path):
    try:
        abs_path,file_name = os.path.split(os.path.realpath(os.path.expandvars(os.path.expanduser(rel_path))))
        if file_name == "" or "." in file_name:
            return (abs_path,file_name)
        else:
            return ("%s%s%s" % (abs_path,os.sep,file_name),"")
    except Exception as e:
        return None

def get_file_abs_path(rel_path):
    try:
        abs_path,file_name = os.path.split(os.path.realpath(os.path.expandvars(os.path.expanduser(rel_path))))
        return "%s%s%s" % (abs_path,os.path.sep,file_name)
    except Exception as e:
        return None

def get_time_formated(choice,with_space=True,with_T=False):
    if with_T:
        if int(str(choice).lower().strip()) == 1:
            return "%sT%s" % (vars.CURR_DATE_1,vars.CURR_TIME_1)
        elif int(str(choice).lower().strip()) == 2:
            return "%sT%s" % (vars.CURR_DATE_1,vars.CURR_TIME_2)
        elif int(str(choice).lower().strip()) == 3:
            return "%sT%s" % (vars.CURR_DATE_1,vars.CURR_TIME_3)
        elif int(str(choice).lower().strip()) == 4:
            return "%sT%s" % (vars.CURR_DATE_1,vars.CURR_TIME_4)
        elif int(str(choice).lower().strip()) == 5:
            return "%sT%s" % (vars.CURR_DATE_2,vars.CURR_TIME_1)
        elif int(str(choice).lower().strip()) == 6:
            return "%sT%s" % (vars.CURR_DATE_2,vars.CURR_TIME_2)
        elif int(str(choice).lower().strip()) == 7:
            return "%sT%s" % (vars.CURR_DATE_2,vars.CURR_TIME_3)
        elif int(str(choice).lower().strip()) == 8:
            return "%sT%s" % (vars.CURR_DATE_2,vars.CURR_TIME_4)
        elif int(str(choice).lower().strip()) == 9:
            return "%sT%s" % (vars.CURR_DATE_3,vars.CURR_TIME_1)
        elif int(str(choice).lower().strip()) == 10:
            return "%sT%s" % (vars.CURR_DATE_3,vars.CURR_TIME_2)
        elif int(str(choice).lower().strip()) == 11:
            return "%sT%s" % (vars.CURR_DATE_3,vars.CURR_TIME_3)
        elif int(str(choice).lower().strip()) == 12:
            return "%sT%s" % (vars.CURR_DATE_3,vars.CURR_TIME_4)
        else:
            return None
    else:
        if with_space:
            if int(str(choice).lower().strip()) == 1:
                return "%s %s" % (vars.CURR_DATE_1,vars.CURR_TIME_1)
            elif int(str(choice).lower().strip()) == 2:
                return "%s %s" % (vars.CURR_DATE_1,vars.CURR_TIME_2)
            elif int(str(choice).lower().strip()) == 3:
                return "%s %s" % (vars.CURR_DATE_1,vars.CURR_TIME_3)
            elif int(str(choice).lower().strip()) == 4:
                return "%s %s" % (vars.CURR_DATE_1,vars.CURR_TIME_4)
            elif int(str(choice).lower().strip()) == 5:
                return "%s %s" % (vars.CURR_DATE_2,vars.CURR_TIME_1)
            elif int(str(choice).lower().strip()) == 6:
                return "%s %s" % (vars.CURR_DATE_2,vars.CURR_TIME_2)
            elif int(str(choice).lower().strip()) == 7:
                return "%s %s" % (vars.CURR_DATE_2,vars.CURR_TIME_3)
            elif int(str(choice).lower().strip()) == 8:
                return "%s %s" % (vars.CURR_DATE_2,vars.CURR_TIME_4)
            elif int(str(choice).lower().strip()) == 9:
                return "%s %s" % (vars.CURR_DATE_3,vars.CURR_TIME_1)
            elif int(str(choice).lower().strip()) == 10:
                return "%s %s" % (vars.CURR_DATE_3,vars.CURR_TIME_2)
            elif int(str(choice).lower().strip()) == 11:
                return "%s %s" % (vars.CURR_DATE_3,vars.CURR_TIME_3)
            elif int(str(choice).lower().strip()) == 12:
                return "%s %s" % (vars.CURR_DATE_3,vars.CURR_TIME_4)
            elif int(str(choice).lower().strip()) == 13:
                return "%s %s" % (vars.CURR_DATE_4,vars.CURR_TIME_1)
            elif int(str(choice).lower().strip()) == 14:
                return "%s %s" % (vars.CURR_DATE_4,vars.CURR_TIME_2)
            elif int(str(choice).lower().strip()) == 15:
                return "%s %s" % (vars.CURR_DATE_4,vars.CURR_TIME_3)
            elif int(str(choice).lower().strip()) == 16:
                return "%s %s" % (vars.CURR_DATE_4,vars.CURR_TIME_4)
            else:
                return None
        else:
            if int(str(choice).lower().strip()) == 1:
                return "%s%s" % (vars.CURR_DATE_1,vars.CURR_TIME_1)
            elif int(str(choice).lower().strip()) == 2:
                return "%s%s" % (vars.CURR_DATE_1,vars.CURR_TIME_2)
            elif int(str(choice).lower().strip()) == 3:
                return "%s%s" % (vars.CURR_DATE_1,vars.CURR_TIME_3)
            elif int(str(choice).lower().strip()) == 4:
                return "%s%s" % (vars.CURR_DATE_1,vars.CURR_TIME_4)
            elif int(str(choice).lower().strip()) == 5:
                return "%s%s" % (vars.CURR_DATE_2,vars.CURR_TIME_1)
            elif int(str(choice).lower().strip()) == 6:
                return "%s%s" % (vars.CURR_DATE_2,vars.CURR_TIME_2)
            elif int(str(choice).lower().strip()) == 7:
                return "%s%s" % (vars.CURR_DATE_2,vars.CURR_TIME_3)
            elif int(str(choice).lower().strip()) == 8:
                return "%s%s" % (vars.CURR_DATE_2,vars.CURR_TIME_4)
            elif int(str(choice).lower().strip()) == 9:
                return "%s%s" % (vars.CURR_DATE_3,vars.CURR_TIME_1)
            elif int(str(choice).lower().strip()) == 10:
                return "%s%s" % (vars.CURR_DATE_3,vars.CURR_TIME_2)
            elif int(str(choice).lower().strip()) == 11:
                return "%s%s" % (vars.CURR_DATE_3,vars.CURR_TIME_3)
            elif int(str(choice).lower().strip()) == 12:
                return "%s%s" % (vars.CURR_DATE_3,vars.CURR_TIME_4)
            else:
                return None

def get_time_formated_2(choice,with_space=True,with_T=False):
    if with_T:
        if int(str(choice).lower().strip()) == 11:
            return "%sT%s" % (vars.CURR_DATE_1,vars.CURR_TIME_1)
        elif int(str(choice).lower().strip()) == 12:
            return "%sT%s" % (vars.CURR_DATE_1,vars.CURR_TIME_2)
        elif int(str(choice).lower().strip()) == 13:
            return "%sT%s" % (vars.CURR_DATE_1,vars.CURR_TIME_3)
        elif int(str(choice).lower().strip()) == 14:
            return "%sT%s" % (vars.CURR_DATE_1,vars.CURR_TIME_4)
        elif int(str(choice).lower().strip()) == 21:
            return "%sT%s" % (vars.CURR_DATE_2,vars.CURR_TIME_1)
        elif int(str(choice).lower().strip()) == 22:
            return "%sT%s" % (vars.CURR_DATE_2,vars.CURR_TIME_2)
        elif int(str(choice).lower().strip()) == 23:
            return "%sT%s" % (vars.CURR_DATE_2,vars.CURR_TIME_3)
        elif int(str(choice).lower().strip()) == 24:
            return "%sT%s" % (vars.CURR_DATE_2,vars.CURR_TIME_4)
        elif int(str(choice).lower().strip()) == 31:
            return "%sT%s" % (vars.CURR_DATE_3,vars.CURR_TIME_1)
        elif int(str(choice).lower().strip()) == 32:
            return "%sT%s" % (vars.CURR_DATE_3,vars.CURR_TIME_2)
        elif int(str(choice).lower().strip()) == 33:
            return "%sT%s" % (vars.CURR_DATE_3,vars.CURR_TIME_3)
        elif int(str(choice).lower().strip()) == 34:
            return "%sT%s" % (vars.CURR_DATE_3,vars.CURR_TIME_4)
        else:
            return None
    else:
        if with_space:
            if int(str(choice).lower().strip()) == 11:
                return "%s %s" % (vars.CURR_DATE_1,vars.CURR_TIME_1)
            elif int(str(choice).lower().strip()) == 12:
                return "%s %s" % (vars.CURR_DATE_1,vars.CURR_TIME_2)
            elif int(str(choice).lower().strip()) == 13:
                return "%s %s" % (vars.CURR_DATE_1,vars.CURR_TIME_3)
            elif int(str(choice).lower().strip()) == 14:
                return "%s %s" % (vars.CURR_DATE_1,vars.CURR_TIME_4)
            elif int(str(choice).lower().strip()) == 21:
                return "%s %s" % (vars.CURR_DATE_2,vars.CURR_TIME_1)
            elif int(str(choice).lower().strip()) == 22:
                return "%s %s" % (vars.CURR_DATE_2,vars.CURR_TIME_2)
            elif int(str(choice).lower().strip()) == 23:
                return "%s %s" % (vars.CURR_DATE_2,vars.CURR_TIME_3)
            elif int(str(choice).lower().strip()) == 24:
                return "%s %s" % (vars.CURR_DATE_2,vars.CURR_TIME_4)
            elif int(str(choice).lower().strip()) == 31:
                return "%s %s" % (vars.CURR_DATE_3,vars.CURR_TIME_1)
            elif int(str(choice).lower().strip()) == 32:
                return "%s %s" % (vars.CURR_DATE_3,vars.CURR_TIME_2)
            elif int(str(choice).lower().strip()) == 33:
                return "%s %s" % (vars.CURR_DATE_3,vars.CURR_TIME_3)
            elif int(str(choice).lower().strip()) == 34:
                return "%s %s" % (vars.CURR_DATE_3,vars.CURR_TIME_4)
            elif int(str(choice).lower().strip()) == 41:
                return "%s %s" % (vars.CURR_DATE_4,vars.CURR_TIME_1)
            elif int(str(choice).lower().strip()) == 42:
                return "%s %s" % (vars.CURR_DATE_4,vars.CURR_TIME_2)
            elif int(str(choice).lower().strip()) == 43:
                return "%s %s" % (vars.CURR_DATE_4,vars.CURR_TIME_3)
            elif int(str(choice).lower().strip()) == 44:
                return "%s %s" % (vars.CURR_DATE_4,vars.CURR_TIME_4)
            else:
                return None
        else:
            if int(str(choice).lower().strip()) == 11:
                return "%s%s" % (vars.CURR_DATE_1,vars.CURR_TIME_1)
            elif int(str(choice).lower().strip()) == 12:
                return "%s%s" % (vars.CURR_DATE_1,vars.CURR_TIME_2)
            elif int(str(choice).lower().strip()) == 13:
                return "%s%s" % (vars.CURR_DATE_1,vars.CURR_TIME_3)
            elif int(str(choice).lower().strip()) == 14:
                return "%s%s" % (vars.CURR_DATE_1,vars.CURR_TIME_4)
            elif int(str(choice).lower().strip()) == 21:
                return "%s%s" % (vars.CURR_DATE_2,vars.CURR_TIME_1)
            elif int(str(choice).lower().strip()) == 22:
                return "%s%s" % (vars.CURR_DATE_2,vars.CURR_TIME_2)
            elif int(str(choice).lower().strip()) == 23:
                return "%s%s" % (vars.CURR_DATE_2,vars.CURR_TIME_3)
            elif int(str(choice).lower().strip()) == 24:
                return "%s%s" % (vars.CURR_DATE_2,vars.CURR_TIME_4)
            elif int(str(choice).lower().strip()) == 31:
                return "%s%s" % (vars.CURR_DATE_3,vars.CURR_TIME_1)
            elif int(str(choice).lower().strip()) == 32:
                return "%s%s" % (vars.CURR_DATE_3,vars.CURR_TIME_2)
            elif int(str(choice).lower().strip()) == 33:
                return "%s%s" % (vars.CURR_DATE_3,vars.CURR_TIME_3)
            elif int(str(choice).lower().strip()) == 34:
                return "%s%s" % (vars.CURR_DATE_3,vars.CURR_TIME_4)
            else:
                return None

def check_process_running(name):
    if check_the_platform() == "linux":
        cmd_string = '''ps -e faux|egrep -i -w "%s"|egrep -v grep|wc -l''' % name
        number = get_shell_cmd_output(cmd_string)
        if number[0] != "failed":
            if int(number[0]) > 0:
                return "yes"
            else:
                return "no"
        else:
            raise Exception("some error")
    elif check_the_platform() == "mac":
        cmd_string = '''ps aux|egrep -i -w "%s"|egrep -v grep|wc -l''' % name
        number = get_shell_cmd_output(cmd_string)
        if number[0] != "failed":
            if int(number[0]) > 0:
                return "yes"
            else:
                return "no"
        else:
            raise Exception("some error")

def cal_fu_li(money,rate,year):
    sum = 0
    rate = float(Decimal(rate) / 100)
    for i  in range(1,int(year)+1):
        sum = float(money) * float( 1 + rate)
        #print "%s -> %s [%s]" % (i,sum,float(1 + rate))
        money = sum
    return str(sum)

def get_the_day_of_week(the_datetime=None):
    if the_datetime:
        today = the_datetime
    else:
        today = datetime.datetime.today()
    day_num = today.isoweekday()
    day_name = calendar.day_name[today.weekday()]
    return ('''%s,%s''' % (day_num,day_name))

def get_string_between_list_two_keys(first_key,second_key,the_list,default_choice=1,sep_str=" "):
    '''
        可以获取到list中的一段数据，可以根据2个关键字来截取
    '''
    _ret_list = []
    _ret_list_2 = []
    the_list = _decode_list(the_list)
    begin = 0
    end = 0
    shit = 0
    all_string = ""
    for love in range(len(the_list)):
        if str(the_list[love]).startswith(first_key):
            begin = love + 1
            continue
        if str(the_list[love]).startswith(second_key):
            if begin == 0:
                continue
            end = love
            _ret_list_2.append((begin,end))
            begin = 0
            end = 0
    if default_choice == "all":
        for ak in _ret_list_2:
            t_1 = sep_str.join([str(ok) for ok in the_list[ak[0]:ak[1]]])
            all_string += t_1
            all_string += sep_str
    else:
        for i in range(int(default_choice)):
            first = _ret_list_2[i][0]
            second = _ret_list_2[i][1]
            t_2 = sep_str.join([str(ok) for ok in the_list[first:second]])
            all_string += t_2
            all_string += sep_str
    return all_string.lstrip(sep_str).rstrip(sep_str)

def get_string_between_list_two_keys_not_starts(first_key,second_key,the_list,default_choice=1,sep_str=" "):
    '''
        可以获取到list中的一段数据，可以根据2个关键字来截取，关键key可以不用是开头的^key
    '''
    _ret_list = []
    _ret_list_2 = []
    the_list = _decode_list(the_list)
    begin = 0
    end = 0
    shit = 0
    all_string = ""
    for love in range(len(the_list)):
        if first_key in str(the_list[love]):
            begin = love + 1
            continue
        if second_key in str(the_list[love]):
            if begin == 0:
                continue
            end = love
            _ret_list_2.append((begin,end))
            begin = 0
            end = 0
    if default_choice == "all":
        for ak in _ret_list_2:
            t_1 = sep_str.join([str(ok) for ok in the_list[ak[0]:ak[1]]])
            all_string += t_1
            all_string += sep_str
    else:
        for i in range(int(default_choice)):
            first = _ret_list_2[i][0]
            second = _ret_list_2[i][1]
            t_2 = sep_str.join([str(ok) for ok in the_list[first:second]])
            all_string += t_2
            all_string += sep_str
    return all_string.lstrip(sep_str).rstrip(sep_str)

def convert_timestring_to_time(time_string,choice=1):
    if choice == 1:
        return time.strptime("%s" % str(time_string).strip(),'%Y-%m-%d %H:%M:%S')
    elif choice == 2:
        return time.strptime("%s" % str(time_string).strip(),'%Y%m%d %H:%M:%S')
    elif choice == 3:
        return time.strptime("%s" % str(time_string).strip(),'%Y_%m_%d %H:%M:%S')
    elif choice == 4:
        return time.strptime("%s" % str(time_string).strip(),'%Y_%m_%d %H_%M_%S')
    elif choice == 5:
        return time.strptime("%s" % str(time_string).strip(),'%Y-%m-%d %H-%M-%S')
    elif choice == 6:
        return time.strptime("%s" % str(time_string).strip(),'%Y%m%d%H%M%S')

def is_time_between(start_time,end_time,the_time):
    start = convert_timestring_to_time(start_time)
    end = convert_timestring_to_time(end_time)
    t_time = convert_timestring_to_time(the_time)
    if start <= t_time <= end:
        return True
    else:
        return False

def get_the_right_time_format(num=1):
    HOUR = vars.NOW_TIME.split()[1].split(":")[0]
    MINUTE = vars.NOW_TIME.split()[1].split(":")[1]
    TIME = vars.NOW_TIME
    TIME_2 = "%s %s" % (vars.NOW_TIME_2.split()[0],vars.NOW_TIME_2.split()[1])
    TIME_3 = "%s" % get_time_formated_2(33)
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
        if int(num) == 1:
            result_time = "%sT%s:%s" % (TIME.split()[0],HOUR,MINUTE)
        elif int(num) == 2:
            result_time = "%s %s:%s" % (TIME_2,HOUR,MINUTE)
    else:
        if int(MINUTE) == 0:
            if int(num) == 1:
                result_time = "%sT%s:%s" % (vars.YESTERDAY,"23","59")
            elif int(num) == 2:
                result_time = "%s %s:%s" % (vars.YESTERDAY,"23","59")
        else:
            MINUTE = int(MINUTE) - 1
            if len(str(MINUTE)) == 1:
                MINUTE = "0%s" % str(MINUTE)
            HOUR = "00"
            if int(num) == 1:
                result_time = "%sT%s:%s" % (TIME.split()[0],HOUR,MINUTE)
            elif int(num) == 2:
                result_time = "%s %s:%s" % (TIME_2,HOUR,MINUTE)
    return result_time

def print_for_show(msg,choice=2):
    try:
        length = 2 ** int(choice)
        line = "-" * length
    except:
        length = 4
        line = "-" * length
    print line
    print str(msg).strip()
    print line + "\n"

def get_zabbix_check_file_path(file_name,the_log):
    try:
        ori_path = os.getcwd()
        import sys
        cd_into_cwd_dir(sys.argv[0])
        if os.path.exists("zabbix_check") is not True:
            mk_dir_if_not_exist("zabbix_check")
        if os.path.isdir("zabbix_check") is not True:
            get_shell_cmd_output("mv zabbix_check zabbix_check_bak")
            mk_dir_if_not_exist("zabbix_check")
        the_full_path = "%s%s%s%s%s" % (os.getcwd(),os.sep,"zabbix_check",os.sep,str(file_name).strip())
        os.chdir(ori_path)
        return the_full_path
    except:
        traceback_to_file(the_log)

def get_cpu_time():
    the_dic = {}
    cmd_line = """egrep -w "^cpu" /proc/stat |sed 's/cpu//'|column -t"""
    all_cpu_time   = [ int(k) for k in get_shell_cmd_output(cmd_line)[0].split()]
    the_dic["cpu_user"] = all_cpu_time[0]
    the_dic["cpu_nice"] = all_cpu_time[1]
    the_dic["cpu_sys"] = all_cpu_time[2]
    the_dic["cpu_idle"] = all_cpu_time[3]
    the_dic["cpu_iowait"] = all_cpu_time[4]
    the_dic["cpu_irq"] = all_cpu_time[5]
    the_dic["cpu_softirq"] = all_cpu_time[6]
    the_dic["cpu_steal"] = all_cpu_time[7]
    the_dic["cpu_guest"] = all_cpu_time[8]
    the_dic["cpu_guest_nice"] = all_cpu_time[9]
    return the_dic

def cal_cpu_percent(old_dic,new_dic):
    hell = {}
    sum = 0
    for k,v in new_dic.items():
        hell[k] = int(v) - int(old_dic[k])
    for i in hell:
        sum += int(hell[i])
    percent_1 = float("%0.5f" % (float(hell["cpu_user"] + hell["cpu_sys"] + hell["cpu_iowait"] + hell["cpu_nice"]) / sum ))
    percent_2 = float("%0.5f" % (float(sum - hell["cpu_idle"] - hell["cpu_iowait"]) / sum ))
    percent_3 = float("%0.5f" % (float(hell["cpu_user"] + hell["cpu_sys"] ) / float(hell["cpu_user"] + hell["cpu_sys"] + hell["cpu_idle"])))
    return (percent_1,percent_2,percent_3)

def walklevel(some_dir, level=1):
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        yield root, dirs, files
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]
#################################################################################

if __name__ == '__main__':
    print cal_fu_li(1,200,10)
    color_print("Hello",color="blue")
    color_print("Hello",color="red")
    color_print("Hello",color="yellow")
    color_print("Hello",color="green")
    color_print("Hello",color="title")
    color_print("Hello",color="info")


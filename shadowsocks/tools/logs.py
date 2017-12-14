#!/usr/bin/env python
# -*- coding:utf-8 -*-
#

try:
    import time,os,sys
    import global_vars as vars
    import funcs as my_func
    import shutil,glob,re
except ImportError,e:
    print "Hi,boss..I catch a exception:",e
    print "And we exit now"
    sys.exit()

class Logging_To_Print:
    CRITICAL = 50
    FATAL = CRITICAL
    ERROR = 40
    WARNING = 30
    WARN = WARNING
    INFO = 20
    DEBUG = 10
    NOTSET = 0

    def __init__(self, *args, **kwargs):
        self.level = self.__class__.INFO
        self.__set_error_color = lambda: None
        self.__set_warning_color = lambda: None
        self.__set_debug_color = lambda: None
        self.__reset_color = lambda: None
        if hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
            if os.name == 'nt':
                import ctypes
                SetConsoleTextAttribute = ctypes.windll.kernel32.SetConsoleTextAttribute
                GetStdHandle = ctypes.windll.kernel32.GetStdHandle
                self.__set_error_color = lambda: SetConsoleTextAttribute(GetStdHandle(-11), 0x04)
                self.__set_warning_color = lambda: SetConsoleTextAttribute(GetStdHandle(-11), 0x06)
                self.__set_debug_color = lambda: SetConsoleTextAttribute(GetStdHandle(-11), 0x002)
                self.__reset_color = lambda: SetConsoleTextAttribute(GetStdHandle(-11), 0x07)
            elif os.name == 'posix':
                self.__set_error_color = lambda: sys.stderr.write('\033[31m')
                self.__set_warning_color = lambda: sys.stderr.write('\033[33m')
                self.__set_debug_color = lambda: sys.stderr.write('\033[32m')
                self.__reset_color = lambda: sys.stderr.write('\033[0m')

    @classmethod
    def getLogger(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    def basicConfig(self, *args, **kwargs):
        self.level = int(kwargs.get('level', self.__class__.INFO))
        if self.level > self.__class__.DEBUG:
            self.debug = self.dummy
        #self.basicConfig(format='%(levelname)s - %(asctime)s %(message)s', datefmt='[%b %d %H:%M:%S]')

    def log(self, level, fmt, *args, **kwargs):
        sys.stderr.write('%s - [%s] %s\n' % (level, vars.NOW_TIME, fmt % args))

    def dummy(self, *args, **kwargs):
        pass

    def debug(self, fmt, *args, **kwargs):
        self.__set_debug_color()
        self.log('DEBUG', fmt, *args, **kwargs)
        self.__reset_color()

    def info(self, fmt, *args, **kwargs):
        self.log('INFO', fmt, *args)

    def warning(self, fmt, *args, **kwargs):
        self.__set_warning_color()
        self.log('WARNING', fmt, *args, **kwargs)
        self.__reset_color()

    def warn(self, fmt, *args, **kwargs):
        self.warning(fmt, *args, **kwargs)

    def error(self, fmt, *args, **kwargs):
        self.__set_error_color()
        self.log('ERROR', fmt, *args, **kwargs)
        self.__reset_color()

    def exception(self, fmt, *args, **kwargs):
        self.error(fmt, *args, **kwargs)
        sys.stderr.write(traceback.format_exc() + '\n')

    def critical(self, fmt, *args, **kwargs):
        self.__set_error_color()
        self.log('CRITICAL', fmt, *args, **kwargs)
        self.__reset_color()

class log2(object):
    def __init__(self,*logs,**args):
        '''
        logs.log("/only/one/log/path")
        '''

        self.rlog_path = ""
        self.elog_path = ""

        if len(logs) != 1:
            print "Sorry.. You must give one log path now OR you can set the default log_path in [global_vars.py]"
            sys.exit()
        else:
            if args.has_key("ram"):
                self.ram = 1
                ram_path = "%s" % self.find_the_tmpfs()[2]
                self.ram_log_full_path = "%s%s%s%s" % (ram_path,os.sep,"tmp_log_path",os.sep)
                my_func.mk_dir_if_not_exist(self.ram_log_full_path)
                self.rlog_ram = my_func.get_file_abs_path("%s%s%s" % (self.ram_log_full_path,os.sep,"r_log"))
                self.elog_ram = my_func.get_file_abs_path("%s%s%s" % (self.ram_log_full_path,os.sep,"e_log"))
            else:
                self.ram = 0
            if os.path.split(logs[0])[0] == "":
                self.rlog_path = my_func.get_file_abs_path(logs[0])
                self.elog_path = my_func.get_file_abs_path(logs[0])
            else:
                self.rlog_path = os.path.split(logs[0])[0]
                self.elog_path = os.path.split(logs[0])[0]
                self.rlog_path = my_func.get_file_abs_path(self.rlog_path)
                self.elog_path = my_func.get_file_abs_path(self.elog_path)
            if "." in os.path.split(self.rlog_path)[1]:
                self.rlog_path = os.path.split(self.rlog_path)[0]
            if "." in os.path.split(self.elog_path)[1]:
                self.elog_path = os.path.split(self.elog_path)[0]
            log_filename = os.path.split(logs[0])[1]
            if "." not in log_filename:
                log_filename = "%s.log" % log_filename
            self.rlog = "%s/log/%s/right_%s" % (self.rlog_path,vars.CURR_DATE_2,log_filename)
            self.elog = "%s/log/%s/error_%s" % (self.elog_path,vars.CURR_DATE_2,log_filename)
            my_func.mk_dir_if_not_exist(self.rlog)
            my_func.mk_dir_if_not_exist(self.elog)
            if os.path.exists(self.rlog) is not True:
                my_func.touch(self.rlog)
            if os.path.exists(self.elog) is not True:
                my_func.touch(self.elog)

    def write_run(self,MESSAGE,LEVEL=2):
        if not MESSAGE:
            return -1
        if not LEVEL:
            return -1
        if (LEVEL == 1):
            #print "Don't show log info 1"
            print MESSAGE
        elif (LEVEL == 2):
            #print "Don't show log info 2"
            NEW_MESSAGE = "[%s %s] %s\n" % (vars.CURR_DATE_1,vars.CURR_TIME_4,MESSAGE)
            if self.ram:
                with open(self.rlog_ram,'a+') as File_Object:
                    File_Object.write(NEW_MESSAGE)
                    File_Object.flush()
                    File_Object.close()
            else:
                with open(self.rlog,'a+') as File_Object:
                    File_Object.write(NEW_MESSAGE)
                    File_Object.flush()
                    File_Object.close()
        elif (LEVEL == 3):
            NEW_MESSAGE = "[%s %s] %s\n" % (vars.CURR_DATE_1,vars.CURR_TIME_4,MESSAGE)
            if self.ram:
                with open(self.rlog_ram,'a+') as File_Object:
                    File_Object.write(NEW_MESSAGE)
                    File_Object.flush()
                    File_Object.close()
            else:
                with open(self.rlog,'a+') as File_Object:
                    File_Object.write(NEW_MESSAGE)
                    File_Object.flush()
                    File_Object.close()
            print "[%s %s] %s" % (vars.CURR_DATE_1,vars.CURR_TIME_4,MESSAGE)
        else:
            print "Sorry.. Some ERROR..[You must give me 1 or 2 or 3]"
            sys.exit()

    def write_err(self,MESSAGE,LEVEL=2):
        if not MESSAGE:
            return -1
        if not LEVEL:
            return -1
        if (LEVEL == 1):
            #print "Don't show log info 1"
            print MESSAGE
        elif (LEVEL == 2):
            #print "Don't show log info 2"
            NEW_MESSAGE = "[%s %s] %s\n" % (vars.CURR_DATE_1,vars.CURR_TIME_4,MESSAGE)
            if self.ram:
                with open(self.elog_ram,'a+') as File_Object:
                    File_Object.write(NEW_MESSAGE)
                    File_Object.flush()
                    File_Object.close()
            else:
                with open(self.elog,'a+') as File_Object:
                    File_Object.write(NEW_MESSAGE)
                    File_Object.flush()
                    File_Object.close()
        elif (LEVEL == 3):
            NEW_MESSAGE = "[%s %s] %s\n" % (vars.CURR_DATE_1,vars.CURR_TIME_4,MESSAGE)
            if self.ram:
                with open(self.elog_ram,'a+') as File_Object:
                    File_Object.write(NEW_MESSAGE)
                    File_Object.flush()
                    File_Object.close()
            else:
                with open(self.elog,'a+') as File_Object:
                    File_Object.write(NEW_MESSAGE)
                    File_Object.flush()
                    File_Object.close()
            print "[%s %s] %s" % (vars.CURR_DATE_1,vars.CURR_TIME_4,MESSAGE)
        else:
            print "Sorry.. Some ERROR..[You must give me 1 or 2 or 3]"
            sys.exit()

    def get_log_full_path(self):
        rlog = my_func.get_file_abs_path(self.rlog)
        elog = my_func.get_file_abs_path(self.elog)
        return (rlog,elog)

    def flush_ram_log_to_disk(self):
        if os.path.exists(self.rlog_ram):
            rlog_content = open(self.rlog_ram).read()
            with open(self.rlog,'a+') as File_Object:
                File_Object.write(rlog_content)
                File_Object.flush()
                File_Object.close()
        if os.path.exists(self.elog_ram):
            elog_content = open(self.elog_ram).read()
            with open(self.elog,'a+') as File_Object:
                File_Object.write(elog_content)
                File_Object.flush()
                File_Object.close()
        if os.path.exists(self.ram_log_full_path):
            shutil.rmtree(self.ram_log_full_path)

    def find_the_tmpfs(self):
        cmd_string = """df -amT|column -t|egrep tmpfs|egrep -v "devtmpfs"|column -t|sort -k3 -n|tail -1|awk '{print $3,$6,$7}'"""
        ret = my_func.get_shell_cmd_output(cmd_string)
        if ret != "failed" and ret != []:
            return ret[0].split()

    def __del__(self):
        '''
        自动删除指定日期前的日志
        '''
        N = 30

        try:
            log_obj_root = "%s%s%s" % (self.rlog_path.split("log")[0],os.sep,"log")
            all_log_dirs = os.listdir(log_obj_root)
            all_log_dirs = [one_dir for one_dir in all_log_dirs if re.search(r"[0-9]{4}-[0-9]{2}-[0-9]{2}",one_dir)]
            all_log_dirs.sort()
            for one_dir in all_log_dirs[:-N]:
                the_full_path = "%s%s%s" % (log_obj_root,os.sep,one_dir)
                with open(self.rlog,'a+') as File_Object:
                    MESSAGE = "I need to delete old log dir [%s] for it's older than %s days" % (the_full_path,N)
                    NEW_MESSAGE = "[%s %s] %s\n" % (vars.CURR_DATE_1,vars.CURR_TIME_4,MESSAGE)
                    File_Object.write(NEW_MESSAGE)
                    File_Object.flush()
                    File_Object.close()
                shutil.rmtree(the_full_path)
        except Exception as e:
            with open(self.elog,'a+') as File_Object:
                MESSAGE = "Hey %s" % str(e)
                NEW_MESSAGE = "[%s %s] %s\n" % (vars.CURR_DATE_1,vars.CURR_TIME_4,MESSAGE)
                File_Object.write(NEW_MESSAGE)
                File_Object.flush()
                File_Object.close()

class log:
    def __init__(self,*logs):
        '''
        logs.log("/right_log_path","/error_log_path")
        '''

        self.rlog_path = ""
        self.elog_path = ""

        if len(logs) != 2:
            my_func.mk_dir(vars.LOG_PATH)
            self.rlog = "%s" % vars.RER_HTML_RLOG
            self.elog = "%s" % vars.RER_HTML_ELOG
            my_func.mk_dir_if_not_exist(self.rlog)
            my_func.mk_dir_if_not_exist(self.elog)
        else:
            self.rlog_path = os.path.split(logs[0])[0]
            self.elog_path = os.path.split(logs[1])[0]
            rlog_filename = os.path.split(logs[0])[1]
            elog_filename = os.path.split(logs[1])[1]
            self.rlog = "%s/log/%s/%s" % (self.rlog_path,vars.CURR_DATE_2,rlog_filename)
            self.elog = "%s/log/%s/%s" % (self.elog_path,vars.CURR_DATE_2,elog_filename)
            my_func.mk_dir_if_not_exist(self.rlog)
            my_func.mk_dir_if_not_exist(self.elog)

    def write_run(self,MESSAGE,LEVEL=3):
        if not MESSAGE:
            return -1
        if not LEVEL:
            return -1
        if (LEVEL == 1):
            #print "Don't show log info 1"
            print MESSAGE
        elif (LEVEL == 2):
            #print "Don't show log info 2"
            NEW_MESSAGE = "[%s %s] %s\n" % (vars.CURR_DATE_1,vars.CURR_TIME_4,MESSAGE)
            File_Object = open(self.rlog,'a+')
            File_Object.write(NEW_MESSAGE)
            File_Object.close()
        elif (LEVEL == 3):
            NEW_MESSAGE = "[%s %s] %s\n" % (vars.CURR_DATE_1,vars.CURR_TIME_4,MESSAGE)
            File_Object = open(self.rlog,'a+')
            File_Object.write(NEW_MESSAGE)
            File_Object.close()
            print "[%s %s] %s" % (vars.CURR_DATE_1,vars.CURR_TIME_4,MESSAGE)
        else:
            print "Sorry.. Some ERROR..[You must give me 1 or 2 or 3]"
            sys.exit()

    def write_err(self,MESSAGE,LEVEL=3):
        if not MESSAGE:
            return -1
        if not LEVEL:
            return -1
        if (LEVEL == 1):
            #print "Don't show log info 1"
            print MESSAGE
        elif (LEVEL == 2):
            #print "Don't show log info 2"
            NEW_MESSAGE = "[%s %s] %s\n" % (vars.CURR_DATE_1,vars.CURR_TIME_4,MESSAGE)
            File_Object = open(self.elog,'a+')
            File_Object.write(NEW_MESSAGE)
            File_Object.close()
        elif (LEVEL == 3):
            NEW_MESSAGE = "[%s %s] %s\n" % (vars.CURR_DATE_1,vars.CURR_TIME_4,MESSAGE)
            File_Object = open(self.elog,'a+')
            File_Object.write(NEW_MESSAGE)
            File_Object.close()
            print "[%s %s] %s" % (vars.CURR_DATE_1,vars.CURR_TIME_4,MESSAGE)
        else:
            print "Sorry.. Some ERROR..[You must give me 1 or 2 or 3]"
            sys.exit()

if __name__ == "__main__":
    pass

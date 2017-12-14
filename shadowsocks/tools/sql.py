#!/usr/bin/env python
# -*- coding:utf-8 -*-

#
#
#

try:
    import time
    import sys
    import funcs as funcs
    import MySQLdb,sys,os,time
    import global_vars as vars
except ImportError,e:
    print "I catch a exception for you:",e
    sys.exit()

class mysql:

    def __init__(self):
        self.host = ""
        self.port = ""
        self.user = ""
        self.password = ""
        self.db = ""
        self.this_conn = None
        self.this_cursor = None
        self.charset = "utf8"

    def sql_conn(self,*args,**zidian):
        #global this_cursor,this_conn
        if  len(args) == 3 and len(zidian) == 0:
            host = args[0]
            user = args[1]
            password = args[2]
            self.this_conn = MySQLdb.connect(host=host,user=user,passwd=password,charset=self.charset)
            self.this_cursor = self.this_conn.cursor()
        elif len(args) == 4 and len(zidian) == 0:
            host = args[0]
            user = args[1]
            password = args[2]
            port = args[3]
            self.this_conn = MySQLdb.connect(host=host,user=user,passwd=password,port=port,charset=self.charset)
            self.this_cursor = self.this_conn.cursor()
        elif len(args) == 5 and len(zidian) == 0:
            host = args[0]
            user = args[1]
            password = args[2]
            port = args[3]
            db = args[4]
            self.this_conn = MySQLdb.connect(host=host,user=user,passwd=password,port=port,db=db,charset=self.charset)
            self.this_cursor = self.this_conn.cursor()
        elif len(args) == 2 and len(zidian) == 0:
            host = args[0]
            user = args[1]
            self.this_conn = MySQLdb.connect(host=host,user=user,charset=self.charset)
            self.this_cursor = self.this_conn.cursor()
        elif len(args) == 0 and len(zidian) == 0:
            #this_conn = MySQLdb.connect(db=self.db,host=self.host,port=self.port,user=self.user,passwd=self.password)
            self.this_conn = MySQLdb.connect(db=self.db,host=self.host,port=self.port,user=self.user,passwd=self.password,use_unicode=True,charset='utf8')
            self.this_cursor = self.this_conn.cursor()
        elif len(zidian) == 4:
            host = zidian["host"]
            port = zidian["port"]
            user = zidian["user"]
            password = zidian["password"]
            self.this_conn = MySQLdb.connect(host=host,user=user,passwd=password,port=port,charset=self.charset)
            self.this_cursor = self.this_conn.cursor()
        elif len(zidian) == 3:
            host = zidian["host"]
            user = zidian["user"]
            password = zidian["password"]
            self.this_conn = MySQLdb.connect(host=host,user=user,passwd=password,charset=self.charset)
            self.this_cursor = self.this_conn.cursor()
        elif len(args) == 1 and len(zidian) == 0:
            db = args[0]
            self.this_conn = MySQLdb.connect(db=db,host=self.host,port=self.port,user=self.user,passwd=self.password,charset=self.charset)
            self.this_cursor = self.this_conn.cursor()

    def sql_exec(self,*sql):
        self.this_cursor.execute(sql[0])

    def sql_get_result_only_one_list(self):
        return_tmp = []
        return_things = self.this_cursor.fetchall()
        for every_line in return_things:
            return_tmp.append(list(every_line))
        return return_tmp

    def sql_get_result(self):
        return_things = self.this_cursor.fetchall()
        return return_things

    def sql_close(self):
        if self.this_conn:
            self.this_conn.commit()
            self.this_cursor.close()
            self.this_conn.close()


if __name__ == '__main__':
    new_conn = mysql()
    new_conn.sql_conn(vars.DEV_DB_HOST,vars.DEV_DB_USER,vars.DEV_DB_PASSWORD,vars.DEV_DB_PORT,vars.DEV_DB_NAME)
    b = '''show databases;'''
    new_conn.sql_exec(b)
    all_result = funs.t_to_l(new_conn.sql_get_result())
    print all_result
    sys.exit()
    new_conn.sql_exec('''select count(*) from deayou_borrow_tender;;''')
    result_2 = new_conn.sql_get_result()
    new_conn.sql_close()
    for i in range(len(all_result[0])):
        print i,all_result[0][i]
        if i == 11:
            print all_result[0][i].decode("GB2312").encode("UTF8")
        time.sleep(1)
        #realname = all_result[i].decode("GB2312").encode("UTF8")
        #print realname
    sys.exit()
    time.sleep(1)
    for i in all_result:
        print i
        time.sleep(0.04)
    #except Exception,e:
    #   print "Oh..No...I catch exception...%s" % e

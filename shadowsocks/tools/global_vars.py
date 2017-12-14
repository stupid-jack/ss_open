#!/usr/bin/env python
# -*- coding:utf-8 -*-

#global mysql_host,mysql_password,mysql_user,mysql_port,mysql_db
try:
    import time,os,sys,datetime
except ImportError,e:
    print "Hi,Boss..I catch a exception: ",e
    print "Exit now"
    sys.exit()


#---------------------------------------------------------
CURR_DATE_YEAR = time.strftime("%Y")
CURR_DATE_MONTH = time.strftime("%m")
CURR_DATE_DAY = time.strftime("%d")
CURR_DATE_MONTH_2 = time.strftime("%b")

CURR_DATE_1 = time.strftime("%Y_%m_%d")
CURR_DATE_2 = time.strftime("%Y-%m-%d")
CURR_DATE_3 = time.strftime("%Y%m%d")
CURR_DATE_4 = time.strftime("%Y.%m.%d")

CURR_TIME_1 = time.strftime("%H_%M_%S")
CURR_TIME_2 = time.strftime("%H-%M-%S")
CURR_TIME_3 = time.strftime("%H%M%S")
CURR_TIME_4 = time.strftime("%H:%M:%S")

NOW_TIME = "%s %s" % (CURR_DATE_2,CURR_TIME_4)
NOW_TIME_2 = "%s %s %s" % (CURR_DATE_MONTH_2,CURR_DATE_DAY,CURR_TIME_4)

TODAY = datetime.date.today()
ONEDAY = datetime.timedelta(days=1)
TWODAY = datetime.timedelta(days=2)
THREEDAY = datetime.timedelta(days=3)
YESTERDAY = TODAY - ONEDAY
YESTERDAY_OF_YESTERDAY = TODAY - TWODAY
YESTERDAY_OF_YESTERDAY_OF_YESTERDAY = TODAY - THREEDAY
TOMORROW = TODAY + ONEDAY
a = int(time.strftime("%w"))
b = int(time.strftime("%w")) + 6
delay_day_of_last_week_last = datetime.timedelta(days=a)
delay_day_of_last_week_first = datetime.timedelta(days=b)
LAST_WEEK_LAST_DAY = TODAY - delay_day_of_last_week_last
LAST_WEEK_FIRST_DAY = TODAY - delay_day_of_last_week_first

FIRST_DAY_OF_THIS_MONTH = "%s-%s-1" % (CURR_DATE_YEAR,CURR_DATE_MONTH)
LAST_DAY_OF_THIS_MONTH = "%s-%s-31" % (CURR_DATE_YEAR,CURR_DATE_MONTH)

BEGIN_OF_TODAY = "%s 00:00:00" % CURR_DATE_2
END_OF_TODAY = "%s 23:59:59" % CURR_DATE_2
BEGIN_OF_YESTERDAY = "%s 00:00:00" % YESTERDAY
END_OF_YESTERDAY = "%s 23:59:59" % YESTERDAY
BEGIN_OF_YESTERDAY_OF_YESTERDAY = "%s 00:00:00" % YESTERDAY_OF_YESTERDAY
END_OF_YESTERDAY_OF_YESTERDAY = "%s 23:59:59" % YESTERDAY_OF_YESTERDAY
BEGIN_OF_YESTERDAY_OF_YESTERDAY_OF_YESTERDAY = "%s 00:00:00" % YESTERDAY_OF_YESTERDAY_OF_YESTERDAY
END_OF_YESTERDAY_OF_YESTERDAY_OF_YESTERDAY = "%s 23:59:59" % YESTERDAY_OF_YESTERDAY_OF_YESTERDAY
NOW_HOUR = int(time.strftime("%H"))
start_date_of_hour_stat = "%s %s:00:00" % (CURR_DATE_2,NOW_HOUR)
end_date_of_hour_stat = "%s %s:59:59" % (CURR_DATE_2,NOW_HOUR)

#####################################################


if __name__ == '__main__' :
    #print start_date_of_hour_stat
    #print end_date_of_hour_stat
    #print FIRST_DAY_OF_THIS_MONTH
    #print LAST_DAY_OF_THIS_MONTH
    #print RER_HTML_RESULT_FILE_FOR_TIB
    print TOMORROW
    #print CURR_DATE_1,CURR_TIME_1,CURR_TIME_2,CURR_TIME_3,CURR_TIME_4
    #now_time = "%s %s " % (CURR_DATE_2,CURR_TIME_4)
    #print BEGIN_OF_TODAY
    #print NOW_HOUR
    #print YESTERDAY
    ##print RER_HTML_RESULT_FILE_YESTERDAY
    ##print RER_HTML_RESULT_FILE_TODAY
    #print NOW_TIME
    print TODAY

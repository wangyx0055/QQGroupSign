#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import threading
import logging
import libs.mail

import Config
from Sign import Sign
import Data

def DoTasker():
    lstUserData = Data.laodUserData()
    emails = []
    for d in lstUserData:
        sign = Sign(d[0], d[1])
        if sign.autosign() == False:
            #签到失败,删除Cookie,发送邮件提醒
            email = Data.getUserEmailData(d[0])
            if email != None and len(email)>0:
                emails.append(email)
            Data.removeUserData(d[0])
            Data.removeUserEmailData(d[0])
        #time.sleep(1)
    #print emails
    if len(emails)>0:
        email = libs.mail.Message(Config.smtp_user, emails, Config.mail_notify)
        try:
            conn = libs.mail.Connection(Config.smtp_server, 25 ,Config.smtp_user, Config.smtp_pass)
            conn.send_message(email)
        except:
            pass

#Data.updateUserData(123456789,'@Fr2YJJNqd')
#Data.updateUserEmailData(123456789,'123456789@qq.com')
#time.sleep(0.1)
#DoTasker()

def Loop():
    logging.info('Loop begining ...')
    while True:
        #0000
        min = int(time.strftime("%H%M"))
        if min == 0 or min == 1200:
            logging.info('DoTasker...')
            DoTasker()
            time.sleep(60)
        else:
            time.sleep(1)

def Run():
    thread = threading.Thread(target=Loop)
    thread.daemon = True
    logging.info('DoTasker...')
    thread.start()

#Run()
#while True:
#    time.sleep(1)

def test():
    Data.updateUserData(123456789, '@Fr2YJJNqd')
    #wait sql write
    time.sleep(0.1)
    DoTasker()
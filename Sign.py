#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import time
import logging
import re
import sys
import hashlib

reload(sys)
sys.setdefaultencoding('utf-8')

class Sign():

    def __init__(self, qq, skey):
        self.qq = qq
        self.uin = 'o0%s' % qq
        self.skey = skey
        self.g_tk = self.getToken_g_tk(self.skey)
        self.cookie = {'uin': self.uin, 'skey' : self.skey}

    def getToken_g_tk(self, skey):
        length = len(skey)
        hash = 5381
        for i in range(length):
            hash += (hash << 5) + ord(skey[i]);
        return hash & 0x7fffffff;

    def getGroupListId(self):
        try:
            ret = requests.get('http://qun.qzone.qq.com/cgi-bin/get_group_list?uin=%s&g_tk=%s'% (self.qq, self.g_tk), cookies = self.cookie, timeout = 10)
        except:
            return [], 'except'
        #strjs = ret.text[10:-3]
        #bug if has some control char
        #js = json.loads(strjs)
        #print js
        return re.findall('"groupid":(\d+)', ret.text), ret.text

    def autosign(self):
        lst, context = self.getGroupListId()
        if len(lst) == 0:
            logging.error('获取列表失败: %s context:%s' % (self.uin, context))
            #饼干应该过期了
            return False
        for id in lst:
            self.sign(id)
        return True

    def sign(self, groupid):
        data = {'gc': groupid, 'bkn' : self.g_tk}
        try:
            ret = requests.post('http://qiandao.qun.qq.com/cgi-bin/sign', data = data, cookies = self.cookie, timeout = 10)
        except:
            import traceback
            logging.error('sign fail uin=%s groupid=%s info=%s' % (self.uin, groupid, traceback.print_exc()))

#sign = Sign(123456789, '@23333333')
#print sign.getGroupListId()
#sign.autosign()


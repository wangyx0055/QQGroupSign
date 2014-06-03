#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import time
import logging
import re
import sys
import hashlib
from urllib import unquote

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

def hexchar2bin(_str):
    arr = ''
    length = len(_str)
    for i in range(0, length, 2):
        arr += chr(int(_str[i:i+2], 16))
    return arr

def uin2hex(_str):
    maxLength = 16
    _str = int(_str)
    strhex = hex(_str)[2:].upper()
    hexlen = len(strhex)
    for i in range(hexlen, maxLength):
        strhex = '0' + strhex
    arr = ''
    for j in range(0, maxLength, 2):
        arr += chr(int(strhex[j:j+2], 16))
    return arr

def get_token_p(password, uin, vcode):
    str1 = hexchar2bin(hashlib.md5(password).hexdigest().upper())
    str2 = hashlib.md5(str1 + uin).hexdigest().upper()
    return hashlib.md5(str2 + vcode.upper()).hexdigest().upper()

def get_vcode_cd(qq):
    try:
        #QQ群空间登录接口
        ret = requests.get('http://ui.ptlogin2.qq.com/cgi-bin/login?appid=549000912&style=12'\
                           '&s_url=http://qun.qzone.qq.com/group', timeout = 10)
        login_sig = re.findall('login_sig:"([^"]*)"', ret.text)[0]
        cookies = ret.cookies
        #获取验证码
        ref = 'http://ui.ptlogin2.qq.com/cgi-bin/login?appid=549000912&style=12&s_url=http://qun.qzone.qq.com/group'
        headers = {'Referer':ref}
        ret = requests.get('http://check.ptlogin2.qq.com/check?regmaster=&uin=%s' \
                           '&appid=549000912&js_ver=10080&js_type=1&login_sig=%s' \
                           '&u1=http%%3A%%2F%%2Fqun.qzone.qq.com%%2Fgroup' % (qq, login_sig), timeout = 10, cookies = cookies, headers = headers)
        #没有验证码返回!XXX
        return login_sig, re.findall('\'(\S*?)\'', ret.text)[1], ret.cookies
    except:
        return False

def get_captcha(qq, cd, cookies):
    url = 'http://captcha.qq.com/getimage?uin=%s&aid=549000912&cap_cd=%s'% (qq, cd)
    ret = requests.get(url, cookies=cookies)
    file = open('vcode.png', 'wb')
    file.write(ret.content)
    file.close()
    return raw_input("请输入code.png验证码:\n").upper(), ret.cookies

def login(qq, p, vcode, login_sig, cookies):
    utime = str(time.time())[:-3] + '000'
    url = 'http://ptlogin2.qq.com/login?u=%s&p=%s&verifycode=%s&aid=549000912' \
          '&u1=http%%3A%%2F%%2Fqun.qzone.qq.com%%2Fgroup&h=1&ptredirect=1&ptlang=2052&from_ui=1' \
          '&dumy=&low_login_enable=0&regmaster=&fp=loginerroralert&action=1-12-%s' \
          '&mibao_css=&t=1&g=1&js_ver=10080&js_type=1&login_sig=%s&pt_uistyle=12&pt_rsa=0&pt_3rd_aid=' % (qq, p, vcode, utime, login_sig)
    ref = 'http://ui.ptlogin2.qq.com/cgi-bin/login?appid=549000912&style=12&s_url=http://qun.qzone.qq.com/group'
    headers = {'Referer':ref}
    cookies['ptui_loginuin'] = str(qq)
    print cookies
    ret = requests.get(url, cookies = cookies, headers = headers)
    try:
        #print ret.status_code
        #print ret.cookies
        if not 'skey' in ret.cookies:
            login.error('登录失败:获取COOKIE失败')
            return False
        return ret.cookies
    except:
        return False

def autologin(qq, password, hand = False):
    login_sig, vocde_cd, cookies = get_vcode_cd(qq)
    if vocde_cd == False:
        return False

    #print vocde_cd
    if len(vocde_cd) == 4:
        #没验证码vocde_cd当验证码
        pass
    elif (hand == True):
        vocde_cd, cookies = get_captcha(qq, vocde_cd, cookies)
    else:
        return False

    p = get_token_p(password, uin2hex(qq), vocde_cd)
    print vocde_cd

    return login(qq, p, vocde_cd, login_sig, cookies)

#print get_token_p('qq310301913', uin2hex('310301913'), 'SVBW')

#print autologin(310301913, 'passwd', True)['skey']
#sign = Sign(310301913, '@KBObVn8mE')
#print sign.getGroupListId()
#sign.autosign()
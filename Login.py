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

class Login():

    def __init__(self, qq, password):
        self.qq = qq
        self.password = password

    def hexchar2bin(self, _str):
        arr = ''
        length = len(_str)
        for i in range(0, length, 2):
            arr += chr(int(_str[i:i+2], 16))
        return arr
    
    def uin2hex(self, _str):
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
    
    def get_token_p(self, password, uin, vcode):
        str1 = self.hexchar2bin(hashlib.md5(password).hexdigest().upper())
        str2 = hashlib.md5(str1 + uin).hexdigest().upper()
        return hashlib.md5(str2 + vcode.upper()).hexdigest().upper()
    
    def get_vcode_cd(self):
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
                               '&u1=http%%3A%%2F%%2Fqun.qzone.qq.com%%2Fgroup' % (self.qq, login_sig), timeout = 10, cookies = cookies, headers = headers)
            #没有验证码返回!XXX
            return login_sig, re.findall('\'(\S*?)\'', ret.text)[1], ret.cookies
        except:
            return False
    
    def get_captcha(self, cd, cookies):
        url = 'http://captcha.qq.com/getimage?uin=%s&aid=549000912&cap_cd=%s'% (self.qq, cd)
        ret = requests.get(url, cookies=cookies)
        file = open('vcode.png', 'wb')
        file.write(ret.content)
        file.close()
        return raw_input("请输入code.png验证码:\n").upper(), ret.cookies
    
    def login(self, qq, p, vcode, login_sig, cookies):
        utime = str(time.time())[:-3] + '000'
        url = 'http://ptlogin2.qq.com/login?u=%s&p=%s&verifycode=%s&aid=549000912' \
              '&u1=http%%3A%%2F%%2Fqun.qzone.qq.com%%2Fgroup&h=1&ptredirect=1&ptlang=2052&from_ui=1' \
              '&dumy=&low_login_enable=0&regmaster=&fp=loginerroralert&action=1-12-%s' \
              '&mibao_css=&t=1&g=1&js_ver=10080&js_type=1&login_sig=%s&pt_uistyle=12&pt_rsa=0&pt_3rd_aid=' % (qq, p, vcode, utime, login_sig)
        ref = 'http://ui.ptlogin2.qq.com/cgi-bin/login?appid=549000912&style=12&s_url=http://qun.qzone.qq.com/group'
        headers = {'Referer':ref}
        cookies['ptui_loginuin'] = str(qq)
        #int cookies
        ret = requests.get(url, cookies = cookies, headers = headers)
        try:
            #print ret.status_code
            #print ret.cookies
            if not 'skey' in ret.cookies:
                logging.error('登录失败:获取COOKIE失败')
                return False
            return ret.cookies
        except:
            return False
    
    def autologin(self, hand = False):
        login_sig, vocde_cd, cookies = self.get_vcode_cd()
        if vocde_cd == False:
            return False , 'get get_vcode_cd faild'
    
        #print vocde_cd
        if len(vocde_cd) == 4:
            #没验证码vocde_cd当验证码
            pass
        elif (hand == True):
            vocde_cd, cookies = self.get_captcha(vocde_cd, cookies)
        else:
            return False , 'need vcode'
    
        p = self.get_token_p(self.password, self.uin2hex(self.qq), vocde_cd)

        return self.login(self.qq, p, vocde_cd, login_sig, cookies), None


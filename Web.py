#!/usr/bin/python
# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web
import Data
import time
import Run
import os
import re

import Config
import libs.mail
import libs.captcha

class NormalHandler(tornado.web.RequestHandler):
    def get(self):
        strtime = time.strftime("%H:%M")
        self.render("template_index.html",
                    title = 'QQ群自动签到',
                    time = strtime,
                    captcha = libs.captcha.displayhtml(Config.recaptcha_publickey))

class TakenHandler(tornado.web.RequestHandler):
    def get(self):
        qq = self.get_argument('qq', None)
        passwd = self.get_argument('skey', None)
        email = self.get_argument('email', None)
        recaptcha_response_field = self.get_argument('recaptcha_response_field', None)
        recaptcha_challenge_field = self.get_argument('recaptcha_challenge_field', None)

        print recaptcha_response_field
        #block waring need Async!!
        ret = libs.captcha.submit(recaptcha_challenge_field, recaptcha_response_field, Config.recaptcha_privatekey, self.request.remote_ip)
        print ret.is_valid
        tips = ''
        while True:
            if ret.is_valid == False:
                tips = '验证码错误'
                break
            if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) == None:
                email = None
            if passwd == None or qq == None:
                tips = 'SKey or QQ 不合法,重新输入'
                break
            if email != None:
                Data.updateUserEmailData(qq, email)
            Data.updateUserData(qq, passwd)
            tips = '提交成功,每日0和12点自动签到'
            break
        self.render("template_taken.html",
        title = 'QQ群自动签到',
        tips = tips)

if __name__ == "__main__":
    settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static")
    }

    application = tornado.web.Application([
        (r"/taken", TakenHandler),
        (r"/", NormalHandler),
    ], **settings)
    application.listen(7788)

    Run.Run()

    tornado.ioloop.IOLoop.instance().start()
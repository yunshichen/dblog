#! /usr/bin/python
# -*- coding: UTF-8 -*-
"""
    处理主页面,登陆,注册等功能.
"""

import logging

from dblog.biz.webs import DBackHandler
from dblog.service.blog_service import user_service


class ItWorks(DBackHandler):
    def get(self):
        self.write('it works.')


class Index(DBackHandler):
    """
        首页
    """

    def get(self):
        if not self.get_current_user():
            return self.render('login.html')

        return self.render('index.html')


class LoginAjax(DBackHandler):
    def post(self):

        # -- 是否从模态框登录
        from_modal = self.get_argument('from_global_modal')
        if from_modal == 'Y':
            account_text = self.get_mandatory('global_login_account_text', u'请输入账号')
            password = self.get_mandatory('global_login_password', u'请输入密码')
        else:
            account_text = self.get_mandatory('account_text', u'请输入账号')
            password = self.get_mandatory('password', u'请输入密码')

        user_dict = user_service.do_login(account_text, password)

        logging.debug('----- user[%s] login. ' % account_text)

        # 设置session
        self.handle_after_login(user_dict['id'], user_dict['role_index'])

        self.json_ok(user_dict)


class Logout(DBackHandler):
    """
        退出登录
    """

    def get(self):
        self.do_logout()

        self.render('login.html')

    def post(self):
        self.get()

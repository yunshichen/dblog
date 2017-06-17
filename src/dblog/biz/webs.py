#! /usr/bin/python
# -*- coding: UTF-8 -*-

import json
import logging
import tornado.web
from globals import g_role
from dblog.biz.beans import *


class DJsonEncoder(json.JSONEncoder):
    """
    将对象变成json的时候.
    """

    def default(self, obj):
        cls_name = obj.__class__.__name__
        if cls_name in ['int', 'str', 'long', 'dict', 'list']:
            return super(DJsonEncoder, self).default(obj)

        if cls_name == 'datetime':
            return str(obj)

        # print '-- cls_name: %s  and value: %s' % (cls_name, obj)
        # 如果是自定义对象, 将之作为dict 处理
        return obj.__dict__


def find_header_by_index(header_list, index):
    index = int(index)
    for header in header_list:
        if header.index == index:
            return header

    return None


def find_menu_by_index(menu_list, index):
    index = int(index)
    for menu in menu_list:
        if menu.index == index:
            return menu

        for sub in menu.sub_menus:
            if sub.index == index:
                return sub

    return None


class DBackHandler(tornado.web.RequestHandler):
    """
    tornado 后台基类
    """

    # --  在登录后调用此方法
    def handle_after_login(self, user_id, role_index):

        # 得到用户的权限角色
        user_headers, user_menus = g_role.get_header_and_menus_by_role(role_index)
        session = SessionDto()
        session.uid = str(user_id)
        session.user_headers = user_headers
        session.user_menus = user_menus

        # -- 默认当前选中的头部
        header_index = 1
        for header in user_headers:
            if header.index == header_index:
                session.select_header = header
                break

        # -- 默认头部下的左侧菜单
        for menu in user_menus:
            if menu.parent_index == header_index:
                session.current_left_menus.append(menu)

        # -- parent 和 child 默认不打开.
        # -- 为了避免tornado 模板的限制, 要给一个空对象
        session.select_parent = BackMenuDto()
        session.select_child = BackMenuDto()

        session_helper = self.application.session_helper
        session_helper.set_session(self, session)

    def check_login(self):
        """
        检查用户是否登录
        :return:
        """

        if not self.get_current_user():
            return False

        return True

    def get_current_user(self):
        """
        获得当前已登录用户
        :return:
        """
        session_helper = self.application.session_helper

        # -- 现在判断用户是否存在有2个依据:
        # -- 1. current user 是否存在
        # -- 2. 内存数据是否存在.
        # -- 所以要两者一起判断
        uid = self.get_secure_cookie(session_helper.cookie_key)
        if not uid:
            return None

        user_session = session_helper.get_session(self)
        if not user_session:
            self.set_secure_cookie(session_helper.cookie_key, '')
            return None

        return uid

    def do_logout(self):
        session_helper = self.application.session_helper
        session_helper.remove_session(self)

    #  --------------- 和用户登录有关的方法 end ---------------

    # --------------- 和权限, 菜单相关的方法 begin ---------------

    def is_ajax(self):
        if 'x-requested-with' in self.request.headers:
            return True
        return False

    def is_avoid_url(self):
        request_uri = self.request.uri
        # print '---- request_uri: ' + request_uri

        if request_uri.startswith('/front') or request_uri.startswith('/upload'):
            return True

        return request_uri in ['/', '/admin/login', '/admin/ajax/login', '/admin/logout']

    def prepare(self):
        """
        类似java 的filter, 在每个请求的开始做一些操作, 包括
        1. 检查session. 必须要求用户登录
        2. 设置页面信息
        :return:
        """

        if self.is_avoid_url():
            return

        # -- 如果还没登录, 抛出异常
        if not self.get_current_user():
            raise SessionException()

        session_helper = self.application.session_helper
        user_session = session_helper.get_session(self)
        user_headers = user_session.user_headers
        user_menus = user_session.user_menus

        # -- 查看当前选择的头部菜单
        select_header_index = self.get_arg('select_header_index')
        if select_header_index:
            select_header_index = int(select_header_index)
            select_header = find_header_by_index(user_headers, select_header_index)

            if user_session.select_header.index != select_header.index:
                # -- 更新select header 和 menu
                user_session.select_header = select_header
                user_session.current_left_menus = []
                for menu in user_menus:
                    if menu.parent_index == select_header_index:
                        user_session.current_left_menus.append(menu)

                        # else: # -- 如果相等, 表示还在同一头部菜单下, 不需要更新

        # -- 查看当前选择的左侧父菜单
        select_parent_index = self.get_arg('select_parent_index')
        if select_parent_index:
            select_parent_index = int(select_parent_index)
            select_parent = find_menu_by_index(user_menus, select_parent_index)
            if not select_parent:
                select_parent = BackMenuDto()
                select_parent.index = -999
            user_session.select_parent = select_parent

        # -- 查看当前选择的左侧子菜单
        select_child_index = self.get_arg('select_child_index')
        if select_child_index:
            select_child_index = int(select_child_index)
            select_child = find_menu_by_index(user_menus, select_child_index)
            if not select_child:
                select_child = BackMenuDto()
                select_child.index = -999
            user_session.select_child = select_child

        # -- 更新session, 从而更新菜单配置
        session_helper.set_session(self, user_session)

    def get_template_namespace(self):
        """
        用于每次request的时候,自动设置变量到template
        :return:
        """

        ns = super(DBackHandler, self).get_template_namespace()

        if self.is_ajax():
            return ns

        # -- 不检查的链接
        if self.is_avoid_url():
            return ns

        session_helper = self.application.session_helper
        user_session = session_helper.get_session(self)

        if not user_session:
            return ns

        # -- 设置变量到 template
        ns.update({
            'USER_HEADERS': user_session.user_headers,
            'SELECTED_HEADER': user_session.select_header,
            'CURRENT_LEFT_MENUS': user_session.current_left_menus,
            'SELECTED_LEFT_PARENT': user_session.select_parent,
            'SELECTED_LEFT_CHILD': user_session.select_child,
        })

        return ns

    def get_page_info(self):
        """
        获得分页信息
        :return:
        """

        page_size = self.get_argument('page_size', '20')
        page_no = self.get_argument('page_no', '1')

        page_size = int(page_size)
        page_no = int(page_no)

        return page_size, page_no

    def get_arg(self, name, strip=True):
        return self.get_argument(name=name, default="", strip=strip)

    def get_int(self, name):
        """
        在python 里处理 int 很麻烦. 所以独立一个方法.
        :param name:
        :return:
        """
        v = self.get_arg(name)
        if v:
            return int(v)

        return v

    def get_mandatory(self, name, empty_msg):
        v = self.get_arg(name)
        if not v or v.strip() == '':
            raise LogicException(empty_msg)

        return v

    def json_ok(self, data=''):
        json_obj = {'data': data}
        t = json.dumps(json_obj, cls=DJsonEncoder)
        self.write(t)

    def json_fail(self, msg):
        json_obj = {'error': msg}
        t = json.dumps(json_obj, cls=DJsonEncoder)
        self.write(t)

    def get_client_ip(self):

        if 'X-Real-Ip' in self.request.headers:
            return self.request.headers['X-Real-Ip']

        return self.request.remote_ip

    def _handle_request_exception(self, ex):
        # request_uri = self.request.uri

        # if isinstance(ex, LogicException) and request_uri.startswith('/api/'):
        if isinstance(ex, LogicException):
            # self.json_fail(ex.msg)
            logging.warn(u' ------业务异常: %s' % ex.msg)
            self.set_status(200)
            self.finish({'error': ex.msg})
            return

        if isinstance(ex, SessionException):
            logging.warn(u' ------登录超时, url: %s ' % self.request.uri)
            logging.warn(' is ajax: ' + str(self.is_ajax()))
            self.set_status(200)

            if self.is_ajax():
                self.finish({'session_expire': 'Y'})

            else:
                self.render('login.html')

        else:
            # tornado.web.RequestHandler._handle_request_exception(self, ex)
            # self.set_status(500)
            # self.finish({'error': ex.msg})

            logging.exception(' ========== get server 500 exception =============')
            self.set_status(200)
            self.finish({'error': u'访问服务器发生错误,请联系管理员'})

    def _get_upload_file_info(self, param_name, limit_m=4):
        # 检查图片是否上传
        if self.request.files == {} or (param_name not in self.request.files):
            raise LogicException(u'没有图片数据')

        a_file = self.request.files[param_name][0]
        file_data = a_file['body']

        # 限制上传文件的大小，通过len获取字节数
        if len(file_data) > limit_m * 1024 * 1024:
            raise LogicException(u'图片不能大于%dM' % limit_m)

        # -- 文件后缀名
        ext = a_file['content_type'].split('/')[1]

        return file_data, ext

        # def write_error(self, status_code, **kwargs):
        #     logging.error('++++++++++++++++++ error ssss +++++++++++++++++')
        #     # super(BaseWebFrontHandler, self).write_error(status_code, **kwargs)
        #
        #     request_uri = self.request.uri
        #
        #     exception = kwargs['exc_info'][1]
        #
        #     if isinstance(exception, LogicException) and request_uri.startswith('/api/'):
        #         self.json_fail(exception.msg)
        #         logging.warn(u' ------业务异常: %s' % exception.msg)
        #         self.finish()
        #         return
        #
        #     self.render('common/error_500.html')

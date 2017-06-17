#! /usr/bin/python
# -*- coding: UTF-8 -*-
import ConfigParser
import logging
import os
import os.path
import sys

import tornado
import tornado.web
from tornado.ioloop import IOLoop

from dblog.biz import utils

"""
    读取${工程根目录}/conf/dblog.conf 进行初始化
    以g_开头的全局变量, 会被工程的其他类共享使用. 所以, 除了初始化之后, 不要再次初始化它们.
"""

# ==================================================================
# -------------------- 以 g_ 开头的变量表示全工程共用
# ==================================================================
g_project_root = ''  # 工程根目录
g_config_parser = None  # 保存config, 方便其他类使用
g_role = None  # 全局权限类
g_session_helper = None  # session 处理类
g_upload_service = None  # 上传文件处理类
g_water_path = None  # 水印图片路径
g_file_server = ''  # 文件服务器前缀
g_template_maker = None  # tornado模板文件生成器
g_static_path = ''  # static 文件夹路径
g_template_path = ''  # template 文件夹路径

# ---- 查找根目录
script_path = utils.get_script_path(sys.path[0])
rel_path = '../'  # 当前脚本相对于src目录的路径
g_project_root = os.path.abspath(os.path.join(script_path, rel_path))
# print '---- g_project_root: ' + g_project_root

# ---- 读取app.conf 文件
g_config_parser = ConfigParser.ConfigParser()
g_config_parser.readfp(open(os.path.join(g_project_root, 'conf/dblog.conf')))

# ---- 初始化log
log_path = g_config_parser.get('logging', 'log_path')
log_level = g_config_parser.get('logging', 'log_level')
utils.init_logging(log_path, log_level)

# ---- 打印config 参数
logging.info(u'==== 工程根目录: %s ' % g_project_root)
utils.log_config_params(g_config_parser)

# ---- 初始化权限
xml_path = os.path.join(g_project_root, 'conf/menu.xml')
from dblog.biz.modals import SimpleBackRoleService

g_role = SimpleBackRoleService(xml_path)
logging.info(u'---- 菜单权限初始化完成')

# ---- 水印图片
water_mark = g_config_parser.get('upload', 'water_mark')
water_mark = os.path.join(g_project_root, water_mark)
logging.debug('---- water_path: ' + water_mark)

# ---- 上传文件处理类, 文件会放到根目录的upload目录下.
from dblog.biz.image_utils import FileUploadService
upload_save_dir = os.path.join(g_project_root, 'upload')
g_upload_service = FileUploadService(upload_save_dir, water_mark)

# ---- 文件服务器前缀
g_file_server = g_config_parser.get('upload', 'file_server')

# ---- 设置 static 和 template 路径
g_static_path = os.path.join(g_project_root, 'static')
g_template_path = os.path.join(g_project_root, 'template')
from dblog.biz.modals import TemplateMaker

g_template_maker = TemplateMaker(g_template_path)


def start_tornado():
    """
    方便启动tornado的类
    :return:
    """

    # ---- tornado 相关参数
    app_port = g_config_parser.get('tornado', 'port')
    debug_flag = g_config_parser.get('tornado', 'debug')
    cookie_key = g_config_parser.get('tornado', 'cookie_key')
    if debug_flag == 'Y':
        debug = True
    else:
        debug = False

    # ---- 设置 static 和 template 路径

    settings = {
        "static_path": g_static_path,
        "template_path": g_template_path,
        "debug": debug,
        "cookie_secret": '62oETzKXQAGaYdkL5gEmGeKJFuYh7EQnp2XdTP1o/Vo=',  # With the signature of cookie
        # "cookie_secret": '61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=',  # With the signature of cookie
        # "xsrf_cookies": "False", # Cross Site Request Forgery (Cross-site Request Forgery) strategy for preventing xsrf_cookies
    }

    # ---- 设置 url
    from dblog.handler.urls import urls
    app = tornado.web.Application(urls, **settings)

    # -- 初始化 session helper 到 application 对象
    from dblog.biz.modals import CookieSessionHelper
    app.session_helper = CookieSessionHelper(cookie_key)
    log_info = """
        ========================================

             服务器已启动于 : %s

        ========================================
        """

    logging.info(log_info % app_port)
    app.listen(app_port)
    IOLoop.instance().start()

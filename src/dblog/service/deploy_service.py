#! /usr/bin/python
# -*- coding: UTF-8 -*-

import os
import os.path
from datetime import datetime

from fabric.api import cd, run, env, lcd, local
from dblog.biz import pw_utils
from dblog.db import BlogArticle
import re

#  fab -f back_deploy.py make_product_war

"""

    依赖 python的 fabric 模块:  sudo pip install fabric
    
    步骤:

    1. 备份远程目录上的 app目录下的内容, 备份完后清除
    2. 上传新内容
"""

# 远程发布机器
REMOTE_IP = '119.23.134.243'

# 用户
REMOTE_USER = 'dblog'
REMOTE_PASSWORD = '#@home2011'

# 远程发布目录
REMOTE_PATH = '/home/dblog/app/'

# 必须要在全局设置hosts
env.host_string = REMOTE_IP
env.user = REMOTE_USER
env.password = REMOTE_PASSWORD

# 上传资料所在目录
FILE_DIR = '/home/cys/test_proj/dblog'

# 上传文件所在目录
LOCAL_UPLOAD_DIR = '/home/cys/test_proj/dblog_upload'
REMOTE_UPLOAD_DIR = '/home/dblog/app/upload'


def make_temp_dir(base_path):
    """
        在指定目录下生成 yyyymmddhhss 的目录, 用于临时操作.
    :return:
    """
    path = datetime.now().strftime('%Y%m%d%H%M%S')
    path = os.path.join(base_path, path)
    os.makedirs(path)

    return path


def change_upload_prefix_in_article(find_pattern='http://localhost:29999'
                                    , to_pattern='http://blog.yunshichen.com/upload'):
    """
    将富文本里的前缀改掉.
    :return:
    """
    # FIXME: re的匹配字符串应该从用户配置而来.

    article_list = pw_utils.get_entity_list(BlogArticle)
    for article in article_list:
        if article.content is None:
            continue

        match_list = re.findall(find_pattern, article.content)
        if not match_list:
            continue

        for url_str in match_list:
            print url_str


def do_it():
    # -- 将远程war资源先备份并清空
    # with cd(REMOTE_PATH):
    # -- 备份到temp 目录
    # to_dir = make_temp_dir('/tmp/dblog/app')
    # run('mkdir -p ' + to_dir)
    # run('touch xx.txt')
    # run('cp -r * ' + to_dir)
    #
    # # -- 清空之
    # run('rm -rf * ')

    # -- 上传资料
    with lcd(FILE_DIR):
        local('scp -r * ' + REMOTE_USER + '@' + REMOTE_IP + ':' + REMOTE_PATH)


if __name__ == '__main__':
    do_it()

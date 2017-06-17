#! /usr/bin/python
# -*- coding: UTF-8 -*-
import logging
from datetime import datetime
import os
from peewee import *

from globals import g_config_parser, g_project_root

"""
    这里有一个无奈的地方: 数据库必须初始化一个db对象, 由于peewee的限制,很难把这个代码分离出去.
    所以这个db 类要先启动.
"""
# ---- 从配置文件读取数据库配置
db_name = g_config_parser.get('db', 'name')
g_db = SqliteDatabase(os.path.join(g_project_root, db_name))


class BackUser(Model):
    """
        后台用户
    """
    account_text = CharField(max_length=40)
    password = CharField(max_length=40)
    role_index = CharField(max_length=10)
    last_operation_time = DateTimeField(default=datetime.now())

    avatar_id = CharField(null=True)
    nickname = FixedCharField(null=True)

    class Meta:
        database = g_db
        db_table = 'back_user'


class BlogArticleCategory(Model):
    """
        博客文章分类
    """
    label = CharField(max_length=40)
    order = IntegerField()

    class Meta:
        database = g_db
        db_table = 'article_cat'


class BlogArticle(Model):
    """
        博客文章
    """
    title = CharField(max_length=100)
    short_desc = CharField()
    content = TextField()  # Text field 对应mysql的text, 可以无限存数据.
    status = CharField(default='N')
    read_count = IntegerField(default=0)

    is_delete = CharField(default='N')
    delete_time = CharField(null=True)
    create_time = CharField()

    # -- 外键
    # cat = ForeignKeyField(BlogArticleCategory, related_name='cat_articles')
    # column = ForeignKeyField(BlogArticleColumn, related_name='column_articles', null=True)
    cat_id = IntegerField()
    cat_label = CharField()

    class Meta:
        database = g_db
        db_table = 'blog_article'


# ========================================================
# ---------- 连接数据库, 初始化表. 必须将这行放在所有表类的最后面
# ========================================================

# ----------- 新增表之后, 记得加到list 里
table_list = [
    BackUser, BlogArticleCategory, BlogArticle
]

g_db.connect()
g_db.create_tables(table_list, safe=True)
logging.info(u'---- 数据库初始化完成')

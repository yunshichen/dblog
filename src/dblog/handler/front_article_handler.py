#! /usr/bin/python
# -*- coding: UTF-8 -*-

from dblog.db import BlogArticle, BlogArticleCategory
from dblog.biz.webs import DBackHandler
from dblog.service.blog_service import cat_service, article_service
from dblog.service import blog_maker
from dblog.biz import pw_utils, utils
from globals import g_template_maker


class Index(DBackHandler):
    """
        博客首页
    """

    def get(self):
        # ---- 文章分类
        cat_list = cat_service.get_all_bean()

        return self.render('index/article_index.html', cat_list=cat_list)

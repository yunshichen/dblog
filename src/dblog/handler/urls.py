#! /usr/bin/python
# -*- coding: UTF-8 -*-

from dblog.handler import index_handler
from dblog.handler import cat_handler
from dblog.handler import back_article_handler
from dblog.handler import ckeditor_handler
from dblog.handler import front_handler

urls = [
    # -------- 博客首页
    (r"/", front_handler.FrontIndex),
    (r"/front", front_handler.FrontIndex),
    (r"/front/article/detail", front_handler.Detail),

    # -------- 后台登录
    (r"/admin", index_handler.Index),
    (r"/admin/index", index_handler.Index),
    (r"/admin/ajax/login", index_handler.LoginAjax),
    (r"/admin/logout", index_handler.Logout),

    # -------- 分类
    (r"/admin/cat/index", cat_handler.Index),
    (r"/admin/ajax/cat/save", cat_handler.Save),
    (r"/admin/ajax/cat/page", cat_handler.Page),
    (r"/admin/ajax/cat/get", cat_handler.Get),
    (r"/admin/ajax/cat/delete", cat_handler.Delete),
    (r"/admin/ajax/cat/move_up", cat_handler.MoveUp),
    (r"/admin/ajax/cat/move_down", cat_handler.MoveDown),

    # -------- 文章
    (r"/admin/article/index", back_article_handler.Index),
    (r"/admin/article/detail", back_article_handler.Detail),
    (r"/admin/ajax/article/save", back_article_handler.Save),
    (r"/admin/ajax/article/page", back_article_handler.Page),
    (r"/admin/ajax/article/get_content", back_article_handler.GetContent),
    (r"/admin/ajax/article/delete", back_article_handler.Delete),
    (r"/admin/ajax/article/toggle_status", back_article_handler.ToggleStatus),
    (r"/admin/article/preview", back_article_handler.Preview),
    #
    # # -------- 网站管理
    # (r"/site/index", site_handler.Index),
    # (r"/ajax/site/make_it", site_handler.MakeIt),
    #
    # -------- 上传下载
    (r"/admin/ajax/ckeditor/upload_image", ckeditor_handler.UploadImage),
    (r"/upload/(.*)", ckeditor_handler.ReadUpload),
    #
    # # -------- 前台模板
    (r"/temp/front/v1/index", front_handler.FrontIndex),
    (r"/temp/front/v1/detail", front_handler.Detail),
]

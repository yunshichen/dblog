#! /usr/bin/python
# -*- coding: UTF-8 -*-

from dblog.biz.webs import DBackHandler
from dblog.biz import utils
from dblog.db import BlogArticle, BlogArticleCategory
from dblog.service.blog_service import cat_service, article_service


class FrontIndex(DBackHandler):
    """
        博客首页
    """

    def get(self):

        page_size, page_no = self.get_page_info()

        query_filter = {'status': 'Y'}
        cat_id = self.get_arg('cat_id')

        if cat_id:
            query_filter['cat_id'] = cat_id

        page_holder = article_service.get_bean_page(page_size, page_no, query_filter, None)

        for bean in page_holder.data_list:
            bean.create_time = utils.change_time_format(bean.create_time)

        # ---- 文章分类
        cat_list = cat_service.get_all_bean()

        return self.render('for_front/v1/front_index_v1.html', page_holder=page_holder,
                           cat_list=cat_list)


class Detail(DBackHandler):
    """
        测试前端页面详细页
    """

    def get(self):
        aid = self.get_arg('id')

        article_dto = article_service.get_bean_by_id(aid)

        # ---- 文章分类
        cat_list = cat_service.get_all_bean()

        return self.render('for_front/v1/front_article_detail_v1.html', article_dto=article_dto, cat_list=cat_list)

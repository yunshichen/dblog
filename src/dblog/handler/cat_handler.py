#! /usr/bin/python
# -*- coding: UTF-8 -*-
"""
    文章分页
"""

from dblog.biz.webs import DBackHandler
from dblog.service.blog_service import cat_service


class Index(DBackHandler):
    """
        首页
    """

    def get(self):
        return self.render('index/cat_index.html')


class Save(DBackHandler):
    def post(self):
        uid = self.get_current_user()
        aid = self.get_int('aid')
        label = self.get_mandatory('label', u'请输入分类名称')

        map_data = dict()
        map_data['id'] = aid
        map_data['label'] = label

        aid = cat_service.save_entity_by_map(uid, map_data)

        self.json_ok(aid)


class Page(DBackHandler):
    def post(self):
        page_size, page_no = self.get_page_info()
        page_holder = cat_service.get_bean_page(page_size, page_no)

        self.json_ok(page_holder)


class Get(DBackHandler):
    def get(self):
        self.post()

    def post(self):
        aid = self.get_arg('aid')
        dto = cat_service.get_bean_by_id(aid)

        self.json_ok(dto)


class Delete(DBackHandler):
    def post(self):
        aid = self.get_arg('aid')
        cat_service.delete_entity(aid)

        self.json_ok()


class MoveUp(DBackHandler):
    def post(self):
        aid = self.get_arg('aid')
        cat_service.do_move_up(aid)

        self.json_ok()


class MoveDown(DBackHandler):
    def post(self):
        aid = self.get_arg('aid')
        cat_service.do_move_down(aid)

        self.json_ok()

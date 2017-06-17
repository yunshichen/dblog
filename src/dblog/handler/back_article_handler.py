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
        首页
    """

    def get(self):
        # ---- 文章分类
        cat_list = cat_service.get_all_bean()

        return self.render('index/article_index.html', cat_list=cat_list)


class Detail(DBackHandler):
    """
        到新建/修改文章页
    """

    def get(self):
        aid = self.get_arg('aid')
        title_str = u'新增文章'
        if aid:
            data = pw_utils.get_bean_by_id(BlogArticle, aid)
            title_str = u'修改文章: ' + data.title
        else:
            data = pw_utils.make_empty_bean(BlogArticle)

        # ---- 文章分类
        cat_list = cat_service.get_all_bean()

        """
        ---- 备注:
        一般来说, 富文本编辑器的初始化过程比较久. 所以文章会分两阶段获取. 第一次获取信息, 第二次获取内容.
        为了避免第一次获取信息的时候把内容也传过去(降低传输速度), 特将内容清空
        """
        data.content = ''
        return self.render('detail/article_detail.html', cat_list=cat_list, article_dto=data
                           , title_str=title_str)


class GetContent(DBackHandler):
    """
        获取文章的内容, 由富文本编辑器调用
    """

    def get(self):
        aid = self.get_arg('aid')
        if aid and not aid.lower() == 'none':
            bean = pw_utils.get_bean_by_id(BlogArticle, aid)
            self.write(bean.content)
        else:
            self.write('')


class Save(DBackHandler):
    """
        新建/修改文章

    """

    def post(self):
        uid = self.get_current_user()

        cat_id = self.get_arg('cat_id')
        column_id = self.get_arg('column_id')

        map_data = dict()
        map_data['title'] = self.get_arg('title')
        map_data['short_desc'] = self.get_arg('short_desc')
        map_data['content'] = self.get_arg('content')
        map_data['status'] = self.get_arg('status')

        # -- service 方法会根据id属性判断是新增还是修改
        aid = self.get_arg('aid')

        # -- 根据外建取出对象
        if cat_id:
            cat_entity = cat_service.get_entity_by_id(cat_id)
            map_data['cat_id'] = cat_id
            map_data['cat_label'] = cat_entity.label

        if column_id:
            column_entity = column_service.get_entity_by_id(column_id)
            map_data['column_id'] = column_id
            map_data['column_label'] = column_entity.label

        if aid:
            map_data['id'] = int(aid)

        article_id = article_service.save_entity_by_map(uid, map_data)

        self.json_ok(article_id)


class Page(DBackHandler):
    """
    分页
    """

    def post(self):
        page_size, page_no = self.get_page_info()

        query_filter = {}
        cat_id = self.get_arg('cat_id')
        column_id = self.get_arg('column_id')

        if cat_id:
            query_filter['cat_id'] = cat_id

        if column_id:
            query_filter['column_id'] = column_id

        page_holder = article_service.get_bean_page(page_size, page_no, query_filter, None)

        for bean in page_holder.data_list:
            bean.create_time = utils.change_time_format(bean.create_time)

        self.json_ok(page_holder)


class Delete(DBackHandler):
    def post(self):
        aid = self.get_arg('aid')
        article_service.delete_entity(aid, True)

        self.json_ok()


class ToggleStatus(DBackHandler):
    def post(self):
        aid = self.get_arg('aid')
        article_service.toggle_field_value(aid, 'status')

        self.json_ok()


class Preview(DBackHandler):
    def get(self):
        aid = self.get_arg('aid')
        article_dto = article_service.get_bean_by_id(aid)

        article_dto.create_time = utils.change_time_format(article_dto.create_time, '%Y年 %m月 %d日')

        # ---- 文章分类
        cat_list = cat_service.get_all_bean()

        # ---- 文章专栏

        self.render('for_front/v1/front_article_detail_v1.html', article_dto=article_dto, cat_list=cat_list
                    , static_path_rel='')

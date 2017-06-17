#! /usr/bin/python
# -*- coding: UTF-8 -*-
from dblog.biz.modals import *
from dblog.db import BlogArticleCategory, BlogArticle
from playhouse import shortcuts
from dblog.biz import utils
from dblog.biz.modals import LogicException
from dblog.db import BackUser


class CategoryService(BaseCRUDOrderService):
    """
    分类 / 专栏 共用 service
    """

    def __init__(self, entity_class):
        BaseCRUDOrderService.__init__(self, entity_class, 'order')

    def check_when_update(self, map_data):
        # 如果待修改的label 和其他记录相同, 抛出异常.
        exist_cat = pw_utils.get_entity_by_field(self.entity_class, 'label', map_data['label'])
        if exist_cat and exist_cat.id != map_data['id']:
            raise LogicException(u'名称[%s]已存在' % map_data['label'])

    def check_when_create(self, map_data):
        exist_cat = pw_utils.get_entity_by_field(self.entity_class, 'label', map_data['label'])
        if exist_cat:
            raise LogicException(u'名称[%s]已存在' % map_data['label'])

    def get_bean_page(self, page_size, page_no, where=None, order=None):
        return BaseCRUDService.get_bean_page(self, page_size, page_no, None, self.entity_class.order.asc())


class UserService(object):
    """
    后台用户
    """

    def __init__(self):
        pass

    def do_login(self, account_text, raw_password):
        """
        数据库存的字段必须是 account_text, cellPhone 或者 password
        :param account_text:
        :param raw_password:
        :return:
        """

        exist_user = BackUser.get(account_text=account_text)
        if not exist_user:
            raise LogicException(u'用户[%s]不存在' % account_text)

        en_pass = utils.encrypt_to_md5(raw_password)
        if exist_user.password != en_pass:
            raise LogicException(u'密码不对')

        return shortcuts.model_to_dict(exist_user)


class ArticleService(BaseCRUDService):
    def __init__(self):
        BaseCRUDService.__init__(self, BlogArticle)

    def check_when_create(self, map_data):
        exist_entity = pw_utils.get_entity_by_field(self.entity_class, 'title', map_data['title'])
        if exist_entity:
            raise LogicException(u'标题[%s]已存在' % map_data['title'])

    def check_when_update(self, map_data):
        exist_entity = pw_utils.get_entity_by_field(self.entity_class, 'title', map_data['title'])
        if exist_entity and exist_entity.id != map_data['id']:
            raise LogicException(u'标题[%s]已存在' % map_data['title'])


cat_service = CategoryService(BlogArticleCategory)  # -- 分类 service
user_service = UserService()  # -- 用户 service
article_service = ArticleService()  # -- 博客 service

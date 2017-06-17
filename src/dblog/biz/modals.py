#! /usr/bin/python
# -*- coding: UTF-8 -*-
"""
    封装一些常用的业务类
"""
import logging
from xml.dom import minidom
from beans import *
import pw_utils
from tornado import template
import utils
import os, os.path
import utils
from datetime import datetime


class CookieSessionHelper(object):
    """
    简单的cookie session, 需要配合 tornado 的request使用

    现在, "所有的"用户session 都放到这个类里(仿照tomcat), 即放到内存里.
    虽然如此, 这个类设计为小型应用(小于500人访问), 应该不会有问题

    """

    def __init__(self, cookie_key):
        self.cookie_key = cookie_key
        self.session_map = dict()

    def _make_session_key(self, uid):
        return self.cookie_key + '_' + uid

    def set_session(self, request, data_obj):
        uid = data_obj.uid
        request.set_secure_cookie(self.cookie_key, uid)
        ck = self._make_session_key(uid)
        self.session_map[ck] = data_obj

    def get_session(self, request):
        uid = request.get_secure_cookie(self.cookie_key)
        uid = str(uid)
        ck = self._make_session_key(uid)
        if ck not in self.session_map:
            return None

        return self.session_map[ck]

    # def update_value(self, request, name, value):
    #     session_obj = self.get_session(request)
    #     if not session_obj:
    #         return
    #
    #     session_obj[name] = value
    #     self.set_session(request, session_obj)

    def remove_session(self, request):
        uid = request.get_secure_cookie(self.cookie_key)
        uid = str(uid)
        request.set_secure_cookie(self.cookie_key, '')
        if not uid:
            return

        ck = self._make_session_key(uid)
        if ck in self.session_map:
            self.session_map.pop(ck)


# ==================================== 常用基类 ============================================
class SimpleBackRoleService:
    """
    用于小型后台系统的权限管理类. 这类系统权限简单,由程序员在xml里指定,客户并不关心.
    一个例子请看 dblog 的 menu.xml
    """

    def __init__(self, xml_path):
        doc = minidom.parse(xml_path)
        self.all_headers = []
        self.all_menus = []
        self.all_roles = []
        self._init_menus(doc)
        self._init_role(doc)
        logging.info(u'---- 权限初始化完成 ----')

    def get_all_headers(self):
        """
        返回所有最顶层的菜单
        :return:
        """
        return self.all_headers

    def get_menu_by_header(self, header_index):
        """
        根据header index, 返回其下的2级菜单
        :return:
        """
        all_menus = []
        for menu in self.all_menus:
            if menu.parent_index == header_index:
                all_menus.append(menu)

        return all_menus

    def get_all_roles(self):
        """
        返回所有的权限
        :return:
        """
        return self.all_roles

    def get_header_and_menus_by_role(self, role_index):
        """
        返回权限所对应的头部和左侧菜单
        :param role_index:
        :return:
        """

        find_role = None
        for role in self.all_roles:
            if role.index == role_index:
                find_role = role

        if not find_role:
            return [], []

        user_headers = []
        for user_header_index in find_role.header_index_list:
            for header in self.all_headers:
                if user_header_index == header.index:
                    user_headers.append(header)

        user_menus = []
        for user_menu_index in find_role.menu_index_list:
            for menu in self.all_menus:
                if user_menu_index == menu.index:
                    user_menus.append(menu)

        return user_headers, user_menus

    def get_role_admin(self):
        """
        返回管理员的权限
        :return:
        """
        for role in self.all_roles:
            if role.label in [u'超级管理员', u'管理员']:
                return role

    def _init_menus(self, doc):
        """
        初始化菜单
        :param doc:
        :return:
        """
        header_nodes = doc.getElementsByTagName('header')
        headers = []
        menus = []

        # ---- 获取最顶层的菜单
        for node in header_nodes:
            # print node.getAttribute('label')
            # print 'value %s ' % node.getAttribute('value')
            header = BackHeaderDto()
            header.index = int(node.getAttribute('index'))
            header.label = node.getAttribute('label')
            header.icon = node.getAttribute('icon')
            header.parent_index = 0
            header.level = 1

            headers.append(header)

            current_header_index = header.index

            # ---- 获取2级菜单
            parent_list = node.getElementsByTagName('parent')
            for parent_node in parent_list:
                parent = BackMenuDto()
                parent.index = int(parent_node.getAttribute('index'))
                parent.label = parent_node.getAttribute('label')
                parent.icon = parent_node.getAttribute('icon')
                parent.parent_index = current_header_index
                parent.level = 2

                current_parent_index = parent.index
                menus.append(parent)

                # ---- 获取3级菜单
                child_list = parent_node.getElementsByTagName('sub')
                for child in child_list:
                    sub_menu = BackMenuDto()
                    sub_menu.index = int(child.getAttribute('index'))
                    sub_menu.label = child.getAttribute('label')
                    sub_menu.link = child.getAttribute('link')
                    sub_menu.icon = child.getAttribute('icon')
                    sub_menu.parent_index = current_parent_index
                    sub_menu.level = 3

                    parent.sub_menus.append(sub_menu)

        self.all_headers = headers  # 头部菜单
        self.all_menus = menus  # 左侧菜单

    def _init_role(self, doc):
        """
        初始化权限
        :param doc:
        :return:
        """

        role_nodes = doc.getElementsByTagName('role')
        all_roles = []
        for node in role_nodes:

            role = BackRoleDto()

            role.index = node.getAttribute('index')
            role.label = node.getAttribute('label')

            for ref_header in node.getElementsByTagName('ref_header'):
                ref_index = int(ref_header.getAttribute('index'))
                role.header_index_list.append(ref_index)

                menu_index_list = ref_header.getAttribute('ref_menu').split(',')
                menu_index_list = map(lambda x: int(x), menu_index_list)
                role.menu_index_list.extend(menu_index_list)

            all_roles.append(role)

        self.all_roles = all_roles


# ==================================== 常用基类 ============================================


class BaseCRUDService(object):
    """
    常用 crud service
    """

    def __init__(self, entity_class):
        self.entity_class = entity_class

    def get_bean_page(self, page_size, page_no, where=None, order=None):
        """
        返回 pojo page
        :param page_no:
        :param page_size:
        :param where:
        :param order:
        :return:
        """
        entity_class = self.entity_class

        page = pw_utils.get_entity_page(entity_class, page_no, page_size, where, order)
        dto_list = []

        # -- 不能直接用peewee的entity 变成json, 会报错.
        # -- 关于 dicts 方法, 见这里:
        # http://docs.peewee-orm.com/en/latest/peewee/querying.html#retrieving-raw-tuples-dictionaries
        for data in page.data_list:
            dto_list.append(dict_to_bean(data))

        page.data_list = dto_list

        return page

    def check_when_update(self, map_data):
        pass

    def check_when_create(self, map_data):
        pass

    def save_entity_by_map(self, uid, map_data):

        aid = None
        if 'id' in map_data:
            aid = map_data['id']

        if aid:
            # 更新记录
            #
            self.check_when_update(map_data)

            exist_data = pw_utils.get_entity_by_id(self.entity_class, aid)

            for field_name in map_data.keys():
                if field_name == 'id' or not map_data[field_name]:
                    continue

                setattr(exist_data, field_name, map_data[field_name])

            exist_data.save()
            return exist_data.get_id()

        # -- 新建记录的情况
        self.check_when_create(map_data)

        if 'id' in map_data:
            del map_data['id']

        map_data['create_time'] = utils.f_time_now()

        new_data = self.entity_class.create(**map_data)
        return new_data.get_id()

    def delete_entity(self, aid, real_del=True):
        self.before_delete_entity(aid)

        # -- 真删除
        if real_del:
            pw_utils.delete_entity_by_id(self.entity_class, aid)
            return

        entity = self.get_entity_by_id(aid)
        if entity:
            entity.is_delete = 'Y'
            entity.delete_time = utils.f_time_now()
            entity.save()

    def before_delete_entity(self, aid):
        pass

    def get_bean_by_id(self, aid):

        db_modal = self.entity_class.select(self.entity_class).where(self.entity_class.id == aid).first()

        return pw_utils.modal_to_bean(db_modal)

    def get_entity_by_id(self, aid):

        db_modal = self.entity_class.select(self.entity_class).where(self.entity_class.id == aid).first()

        return db_modal

    def get_all_bean(self, order_by=None):
        """
        当表数量少的时候可以用这个方法.
        :return:
        """

        entity_class = self.entity_class

        return pw_utils.get_all_bean(entity_class, None, order_by)

    def make_empty_bean(self):
        return pw_utils.make_empty_bean(self.entity_class)

    def toggle_field_value(self, aid, field_name):
        entity = self.get_entity_by_id(aid)
        if not entity:
            return

        v = getattr(entity, field_name)
        if v == 'Y':
            v = 'N'
        else:
            v = 'Y'

        setattr(entity, field_name, v)
        entity.save()


class BaseCRUDOrderService(BaseCRUDService):
    """
    用某个字段排序的 crud service
    """

    def __init__(self, entity_class, order_field):
        BaseCRUDService.__init__(self, entity_class)
        self.order_field = order_field

    def save_entity_by_map(self, uid, map_data):

        aid = map_data['id']

        if aid:
            # 更新记录
            #
            self.check_when_update(map_data)

            exist_data = pw_utils.get_entity_by_id(self.entity_class, aid)

            for field_name in map_data.keys():
                if field_name == 'id' or not map_data[field_name]:
                    continue

                setattr(exist_data, field_name, map_data[field_name])

            exist_data.save()
            return exist_data.get_id()

        # -- 新建记录的情况
        self.check_when_create(map_data)

        max_value = pw_utils.get_max_of_field(self.entity_class, self.order_field)
        map_data[self.order_field] = max_value + 1
        if 'id' in map_data:
            del map_data['id']

        new_data = self.entity_class.create(**map_data)
        return new_data.get_id()

    def do_move_up(self, aid):

        from_obj = pw_utils.get_entity_by_id(self.entity_class, aid)

        min_order = pw_utils.get_min_of_field(self.entity_class, self.order_field)

        from_order_value = getattr(from_obj, self.order_field)
        if from_order_value == min_order:
            raise LogicException(u'已移到顶部')

        to_order_value = from_order_value - 1
        to_obj = pw_utils.get_entity_by_field(self.entity_class, self.order_field, to_order_value)
        to_order_value += 1
        setattr(to_obj, self.order_field, to_order_value)
        to_obj.save()

        from_order_value -= 1
        setattr(from_obj, self.order_field, from_order_value)
        from_obj.save()

    def do_move_down(self, aid):

        from_obj = pw_utils.get_entity_by_id(self.entity_class, aid)

        max_order = pw_utils.get_max_of_field(self.entity_class, self.order_field)

        from_order_value = getattr(from_obj, self.order_field)
        if from_order_value == max_order:
            raise LogicException(u'已移到底部')

        to_order_value = from_order_value + 1
        to_obj = pw_utils.get_entity_by_field(self.entity_class, self.order_field, to_order_value)
        to_order_value -= 1
        setattr(to_obj, self.order_field, to_order_value)
        to_obj.save()

        from_order_value += 1
        setattr(from_obj, self.order_field, from_order_value)
        from_obj.save()

    def delete_entity(self, aid, real=True):
        """
        删除元素之后, 将其他所有元素重新排序.
        """
        BaseCRUDService.delete_entity(self, aid, real)
        order_value = 1
        for entity in pw_utils.get_entity_list(self.entity_class):
            setattr(entity, self.order_field, order_value)
            entity.save()
            order_value += 1


class FileUploadService(object):
    def __init__(self, base_dir):
        self.base_dir = base_dir
        # 检查 upload的目录是否存在, 如果不存在则创建.
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

    def do_save(self, file_data, ext):

        # 构造 upload/2017/12/xxssdfjsfdj-sdfjsdfksfj-sfskdfj.jpg 的文件格式
        now_time = datetime.now()
        year = utils.f_time(now_time, '%Y')
        month = utils.f_time(now_time, '%m')
        path = os.path.join(self.base_dir, year)
        path = os.path.join(path, month)

        if not os.path.exists(path):
            os.makedirs(path)

        from uuid import uuid4
        file_name = str(uuid4()) + '.' + ext
        path = os.path.join(path, file_name)
        f = open(path, 'wb')
        f.write(file_data)
        f.close()

        rel_path = str(year) + '/' + str(month) + '/' + file_name

        map_data = dict()
        map_data['rel_path'] = rel_path
        map_data['file_name'] = file_name

        file_dto = dict_to_bean(map_data)

        return file_dto


class TemplateMaker(object):
    """
    用于加载tornado的模板, 通过传入参数生成新的内容, 这个工具很方便用于网站的静态化.
    建议在程序加载的时候初始化一个实例,并作为全局对象使用.
    """

    def __init__(self, template_base_path):
        self.base_path = template_base_path
        self.loader = template.Loader(template_base_path)

    def make_string(self, relative_path, **kwargs):
        """
        生成字符串
        :param relative_path: 模板的相对路径, 如  article/article_detail.html
        :param kwargs:
        :return: 字符串
        """
        # fullPath = self.base_path + relative_path
        return self.loader.load(relative_path).generate(**kwargs)

    def make_file(self, relative_path, file_path_abs, **kwargs):
        """
        根据模板内容生成文件
        :param relative_path: 模板的相对路径, 如  article/article_detail.html
        :param file_path_abs: 待生成文件的绝对路径, 如  /home/cys/test/test.html
        :param kwargs:
        :return: 字符串
        """
        content_str = self.loader.load(relative_path).generate(**kwargs)
        file_obj = open(file_path_abs, 'w')
        file_obj.write(content_str)
        file_obj.close()

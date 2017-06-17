#! /usr/bin/python
# -*- coding: UTF-8 -*-


class Dict2Class(object):
    """
    方便dict 转变成object
    """

    def __init__(self, **entries):
        self.__dict__.update(entries)


def dict_to_bean(dict_obj):
    dict_obj = Dict2Class(**dict_obj)
    return dict_obj


def make_empty_object():
    dict_obj = dict()
    dict_obj = Dict2Class(**dict_obj)
    return dict_obj


# -- 将dto的同名字段更新到map
def object_to_dict(dto):
    dto_fields = set(dir(dto))
    map_data = dict()

    for name in dto_fields:
        # 特别地, 对id做出处理
        if name.startswith('__'):
            continue

        v = getattr(dto, name)
        if v:
            map_data[name] = v

    return map_data


class LogicException(Exception):
    def __init__(self, msg=None):
        self.msg = msg

    def __repr__(self):
        return self.msg


class SessionException(Exception):
    def __init__(self):
        pass


class PageHolder(object):
    def __init__(self):
        self.page_size = 10  # 每页记录数
        self.page_no = 1  # 当前页, 如 第1页, 第2页, 第3页...
        self.data_list = []  # 存放数据
        self.total_count = 0  # 总记录数
        self.page_count = 0  # 有多少页


class BackHeaderDto:
    """
        头部菜单
    """

    def __init__(self):
        self.index = ''
        self.label = ''
        self.level = 1  # 按 1,2,3 从高到底排列. 即 1 是最顶层菜单
        self.icon = ''


class BackMenuDto(BackHeaderDto):
    """
        左侧树形菜单
    """

    def __init__(self):
        BackHeaderDto.__init__(self)
        self.parent_index = ''
        self.link = ''
        self.sub_menus = []


class SessionDto(object):
    def __init__(self):
        self.uid = ''
        self.user_headers = ''
        self.user_menus = ''
        self.select_header = ''  # 当前选中的头部模块
        self.current_left_menus = []  # 当前头部模块下的菜单
        self.select_parent = ''  # 正打开的父菜单
        self.select_child = ''  # 正打开的子菜单


class BackRoleDto:
    """
        后台权限
    """

    def __init__(self):
        self.header_index_list = []  # 拥有的头部菜单. 头部菜单和 menu_index_list 有重合
        self.menu_index_list = []
        self.label = ''
        self.index = ''

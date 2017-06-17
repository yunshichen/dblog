#! /usr/bin/python
# -*- coding: UTF-8 -*-
from beans import PageHolder, dict_to_bean
from peewee import Field
from playhouse import shortcuts


# ===================== 关于 get / select 的方法 ================================


def get_entity_list(entity_class, where=None, order_by=None):
    if where:
        if order_by:
            q = entity_class.select().where(**where).order_by(order_by)
        else:
            q = entity_class.select().where(**where)
    else:
        if order_by:
            q = entity_class.select().order_by(order_by)
        else:
            q = entity_class.select()

    data_list = []
    for data in q.execute():
        data_list.append(data)

    return data_list


def get_all_bean(entity_class, where=None, order_by=None):
    if where:
        if order_by:
            q = entity_class.select().where(**where).order_by(order_by)
        else:
            q = entity_class.select().where(**where)
    else:
        if order_by:
            q = entity_class.select().order_by(order_by)
        else:
            q = entity_class.select()

    data_list = []
    for dict_data in q.dicts():
        d = dict_to_bean(dict_data)
        data_list.append(d)

    return data_list


def get_min_of_field(entity_class, field_name):
    """
    返回某个字段最小的值
    :param entity_class:
    :param field_name:
    :return:
    """
    field = getattr(entity_class, field_name)
    entity = entity_class.select().order_by(field.asc()).first()
    if not entity:
        return 0

    return getattr(entity, field_name)


def get_max_of_field(entity_class, field_name):
    """
    返回某个字段最大的值
    :param entity_class:
    :param field_name:
    :return:
    """
    field = getattr(entity_class, field_name)
    entity = entity_class.select().order_by(field.desc()).first()
    if not entity:
        return 0

    return getattr(entity, field_name)


def get_entity_by_id(entity_class, aid):
    """
    通过主键获得 entity
    :param entity_class:
    :param aid:
    :return:
    """
    return entity_class.select().where(entity_class.id == aid).first()


def get_bean_by_id(entity_class, aid):
    """
    通过主键获得 entity
    :param entity_class:
    :param aid:
    :return:
    """
    entity = entity_class.select().where(entity_class.id == aid).first()
    if not entity:
        return None

    return modal_to_bean(entity)


def get_entity_by_field(entity_class, field_name, field_value):
    """
    通过字段值获得entity
    :param entity_class:
    :param field_name:
    :param field_value:
    :return:
    """
    p = getattr(entity_class, field_name)
    return entity_class.select().where(p == field_value).first()


def delete_entity_by_id(entity_class, aid):
    q = entity_class.delete().where(entity_class.id == aid)
    if q:
        q.execute()


# -- 获取分页数据
def get_entity_page(entity_class, page_no, page_size, where=None, order_by=None):
    total_count = entity_class.select(entity_class.id).count()

    if order_by:
        dict_list = entity_class.select().order_by(order_by).paginate(page_no, page_size)
    else:
        dict_list = entity_class.select().paginate(page_no, page_size)

    page_count = calculate_page_count(page_size, total_count)

    page = PageHolder()
    page.data_list = dict_list.dicts()
    page.page_size = page_size
    page.page_no = page_no
    page.total_count = total_count
    page.page_count = page_count

    return page


# -- 计算分页数目. 这个通用方法可以用到各个需要计算分页的子方法.
def calculate_page_count(page_size, total_count):
    if total_count <= page_size:
        return 1

    t = total_count / page_size
    if total_count % page_size != 0:
        t += 1

    return t


# -- 将modal变成dto
def make_empty_bean(entity):
    field_tuple = set(dir(entity))

    data = dict()
    for field_name in field_tuple:
        f = getattr(entity, field_name)
        if isinstance(f, Field):
            # print fname
            data[field_name] = ''

    data = dict_to_bean(data)

    return data


# -- 将dto的同名字段值更新到modal_data
def update_modal_by_dto(modal_data, dto):
    dto_fields = set(dir(dto))
    modal_fields = set(dir(modal_data))

    for name in dto_fields:
        # 特别地, 对id做出处理
        if name == 'id':
            continue

        if name not in modal_fields:
            continue

        v = getattr(dto, name)
        if v:
            setattr(modal_data, name, v)


# -- 将map数据生成 peewee的 where 条件
def make_where_filter(entity_class, map_data):
    if not map_data:
        return None

    params = []
    for k, v in map_data.items():
        p = getattr(entity_class, k)
        params.append(p == v)

    return tuple(params)


def modal_to_bean(modal):
    dict_obj = shortcuts.model_to_dict(modal)
    return dict_to_bean(dict_obj)

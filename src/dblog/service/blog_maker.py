#! /usr/bin/python
# -*- coding: UTF-8 -*-

import logging
import os
import os.path

from dblog.biz import utils, pw_utils
from dblog.biz.beans import PageHolder
from dblog.service.blog_service import cat_service, article_service
from globals import g_static_path
from dblog.db import BlogArticle
import re

"""
    将博客生成静态网页, 然后扔到nginx 目录. 静态网站的布局:
        ----static

            index_1.html
            index_2.html
            ...
            index_n.html ( 1, 2 ... n 代表分页页码)

            -- blog
                -- 20160504
                    python入门教程.html
                    java入门教程.html
                -- 20170508
                    python高级教程.html
                    tornado网站入门.html
"""

blog_rel = 'blog'
article_template_path = 'for_front/v1/front_article_detail_v1.html'
index_template_path = 'for_front/v1/front_index_v1.html'


class MakeSiteParam:
    def __init__(self):
        self.save_site_path = ''  # 待生成site的路径
        self.maker = None  # templateMaker

        """
        =============================================
        == 如果使用本地上传
        =============================================
        """
        # self.is_deploy = True             # 本地预览和远程发布的标志
        # self.local_upload_dir = ''        # 上传文件的本地保存路径


def make_site(make_site_param):
    prepare_dirs(make_site_param)

    # -- 查找所有的文章

    article_dto_list = article_service.get_all_bean()
    logging.info(u'------- 共有 %d 篇文章待处理' % len(article_dto_list))

    page_size = 10  # 每10页生成一个静态文件
    page_count = pw_utils.calculate_page_count(page_size, len(article_dto_list))
    cat_list = cat_service.get_all_bean()
    page_holder = PageHolder()
    record_count = 1  # 计数
    page_no = 1  # 当前页码
    page_holder.page_count = page_count

    at_least_one_index = False  # 至少有1个index文件
    for dto in article_dto_list:

        # 生成子页文章
        _make_article_detail(dto, cat_list, make_site_param)

        if record_count < page_size:
            # 小于10的时候, 不需要生成索引页
            page_holder.data_list.append(dto)

        elif record_count == page_size:
            # 已经到第10页, 开始生成索引页, 并重新初始化pageholder 信息
            _make_article_index(page_holder, cat_list, make_site_param)
            at_least_one_index = True
            record_count = 1
            page_no += 1
            page_holder = PageHolder()
            page_holder.page_no = page_no
            page_holder.page_count = page_count

        else:
            # --- 不可能到这里. 如果到了就是程序有问题.
            logging.error(u'==== 程序出错了')

    if not at_least_one_index:
        _make_article_index(page_holder, cat_list, make_site_param)

    # -- 复制静态资源
    _copy_static_resources(make_site_param)

    """
    =============================================
    == 如果使用本地上传
    =============================================
    """
    # -- 复制上传资料
    # _copy_upload_files(make_site_param)


def _copy_static_resources(make_site_param):
    save_site_path = make_site_param.save_site_path
    from_static_path = g_static_path + '/for_front'
    to_static_path = os.path.join(save_site_path, 'static/for_front')
    utils.my_copy_tree(from_static_path, to_static_path)


def _copy_upload_files(make_site_param):
    from_path = make_site_param.local_upload_dir
    to_path = os.path.join(make_site_param.save_site_path, 'upload')
    utils.my_copy_tree(from_path, to_path)


def prepare_dirs(make_site_param):
    # -- 清除 base_path 下的文件
    save_site_path = make_site_param.save_site_path
    utils.ensure_dir_exist_and_empty(save_site_path)

    base_path = make_site_param.save_site_path

    blog_path = os.path.join(base_path, blog_rel)
    os.makedirs(blog_path)


def _make_article_detail(dto, cat_list, make_site_param):
    maker = make_site_param.maker
    base_path = make_site_param.save_site_path

    ori_create_time = dto.create_time

    # --- 文章的生成路径规则: blog/yyyymm/文章名字.html

    # -- 路径
    month_str = utils.change_time_format(ori_create_time, from_format='%Y%m%d%H%M%S', to_format='%Y%m')
    file_path_rel = blog_rel + '/' + month_str + '/' + dto.title + '.html'  # 文章相对路径
    file_path = os.path.join(base_path, file_path_rel)

    # -- 确保父目录存在
    utils.ensure_parent_exist(file_path)

    # -- 更改日期格式
    new_article_time = utils.change_time_format(ori_create_time, from_format='%Y%m%d%H%M%S'
                                                , to_format='%Y-%m-%d %H:%M')
    dto.create_time = new_article_time

    """
    =============================================
    == 如果使用本地上传
    =============================================
    """
    # -- 将文章的上传路径改掉
    # if make_site_param.is_deploy:
    #     _change_file_server(dto)

    # -- 调用模板类生成文章
    maker.make_file(article_template_path, file_path, article_dto=dto, static_path_rel='../..', cat_list=cat_list)

    dto.file_path_rel = file_path_rel

    logging.info(u'---- 已生成: ' + file_path_rel)


def _change_file_server(file_dto, find_pattern='http://localhost:29999'
                        , to_pattern='http://blog.yunshichen.com/upload'):
    """
    将富文本里的前缀改掉.
    例如, 某个图片是 http://localhost:29999/2017/05/xxx.jpg 会改成
            http://blog.yunshichen.com/upload/2017/05/xxx.jpg

    这样才能匹配远程路径.

    """
    content = file_dto.content

    if content is None:
        return

    match_list = re.findall(find_pattern, content)
    if not match_list:
        return

    # for url_str in match_list:
    #     print url_str

    new_content = re.sub(find_pattern, to_pattern, content)

    file_dto.content = new_content


def _make_article_index(page_holder, cat_list, make_site_param):
    """
    在根目录下生成索引页, 规律:  index_x.html  x 表示分页页码
    :param page_holder:
    :param make_site_param:
    :return:
    """

    save_site_path = make_site_param.save_site_path
    index_file_path = os.path.join(save_site_path, 'index_' + str(page_holder.page_no) + '.html')

    maker = make_site_param.maker
    maker.make_file(index_template_path, index_file_path,
                    page_holder=page_holder, static_path_rel='./', cat_list=cat_list)

    logging.info(u'---- 已生成索引文件: ' + index_file_path)

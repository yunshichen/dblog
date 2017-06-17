#! /usr/bin/python
# -*- coding: UTF-8 -*-
import os, sys, inspect
import logging
import hashlib
import datetime
import shutil


def get_script_path(spath):
    """
        查找脚本所在的路径
    """
    script_path = os.path.realpath(spath)
    if os.path.isfile(script_path):
        script_path = os.path.dirname(script_path)
        script_path = os.path.abspath(script_path)
    else:
        caller_file = inspect.stack()[1][1]
        script_path = os.path.abspath(os.path.dirname(caller_file))

    return script_path


def init_logging(log_path, log_level='debug'):
    """
        初始化log
    :param log_path:
    :param log_level:
    :return:
    """

    if log_level in ['debug', 'DEBUG']:
        log_level = logging.DEBUG
    elif log_level in ['warn', 'WARNING', 'warning', 'WARN']:
        log_level = logging.WARN
    elif log_level in ['info', 'INFO']:
        log_level = logging.INFO
    elif log_level in ['error', 'ERROR']:
        log_level = logging.ERROR
    elif log_level in ['critical', 'CRITICAL']:
        log_level = logging.CRITICAL
    else:
        log_level = logging.DEBUG

    s_format = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
    s_fmt = '%Y/%m/%d %H:%M:%S'

    logging.basicConfig(level=log_level, format=s_format, datefmt=s_fmt)

    from logging.handlers import TimedRotatingFileHandler

    import os.path
    s_parent, f = os.path.split(log_path)
    if not os.path.exists(s_parent):
        os.makedirs(s_parent)

    #################################################################################################
    time_handler = TimedRotatingFileHandler(log_path, when="midnight")
    time_handler.setLevel(log_level)
    formatter = logging.Formatter(s_format)
    time_handler.setFormatter(formatter)
    logging.getLogger('').addHandler(time_handler)
    ################################################################################################


def log_config_params(config_parser):
    """
        打印config parser 参数, 通常用于启动的时候
    :param config_parser:
    :return:
    """
    logging.info('==== 配置参数: ')
    for section in config_parser.sections():
        for k, v in config_parser.items(section):
            logging.info('---- ' + k + ': ' + v)


def encrypt_to_md5(raw_string):
    return hashlib.md5(raw_string).hexdigest()


# parse time, this is a safe method.
def p_time(dstr, time_format="%Y%m%d%H%M%S"):
    if dstr is None:
        return None
    try:
        v = datetime.datetime.strptime(dstr, time_format)
    except ValueError:
        v = None

    return v


def f_time(d, time_format="%Y%m%d%H%M%S"):
    return d.strftime(time_format)


def f_time_now(time_format="%Y%m%d%H%M%S"):
    d = datetime.datetime.now()
    return d.strftime(time_format)


def change_time_format(dstr, to_format='%Y-%m-%d %H:%M:%S', from_format="%Y%m%d%H%M%S"):
    d = p_time(dstr, from_format)
    return f_time(d, to_format)


def ensure_dir_exist_and_empty(path):
    """
    确保该目录是可用的空目录. 如果目录不存在,创建之.
    如果目录存在, 清空目录下的内容. 方法: 先删除目录, 再重新创建.
    :param path:
    :return:
    """
    if os.path.exists(path):
        shutil.rmtree(path)

    os.makedirs(path)


def ensure_parent_exist(path):
    parent_path = os.path.abspath(os.path.dirname(path))
    if not os.path.exists(parent_path):
        os.makedirs(parent_path)


def my_copy_tree(from_dir, to_dir):
    """
    复制目标, 设:
    from_dir =  /mydir/dir_a
    to_dir = /the_dir/dir_a

    目的是把dir_a 复制到 /the_dir 目录. 而dir_a目录已经存在, shutil.copytree 会失败. 所以特意封装一下.

    :param from_dir:
    :param to_dir:
    :return:
    """
    if os.path.exists(to_dir):
        shutil.rmtree(to_dir)

    shutil.copytree(from_dir, to_dir)

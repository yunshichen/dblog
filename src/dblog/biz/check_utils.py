#! /usr/bin/python
# -*- coding: UTF-8 -*-
from beans import LogicException


def check_require_str(str_value, msg):
    if not str_value:
        raise LogicException(msg)


def check_require_str_in_dict(map_data, str_key, msg):
    if not map_data[str_key] or map_data[str_key].strip() == '':
        raise LogicException(msg)

#! /usr/bin/python
# -*- coding: UTF-8 -*-
from dblog.biz import utils
from globals import g_role


def create_admin(account_text, pwd):
    admin_role = g_role.get_role_admin()

    pwd = utils.encrypt_to_md5(pwd)
    from dblog.db import BackUser

    # ---- get_or_create 很好用
    user, is_create = BackUser.get_or_create(account_text=account_text, password=pwd
                                             , role_index=admin_role.index)

    print 'user.id: %d ' % user.id


if __name__ == "__main__":
    create_admin('sa_diego', '123456')

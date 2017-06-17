#! /usr/bin/python
# -*- coding: UTF-8 -*-
"""
    处理主页面,登陆,注册等功能.
"""

from dblog.biz.webs import DBackHandler
from dblog.biz.beans import LogicException
import logging
from globals import g_upload_service, g_file_server, g_project_root
import os

"""
CKEditor 有两种上传图片的方式, 一种使用控件, 另一种使用 copy & paste 的方式. (为什么两种不同, 问设计者吧... )

cp方式的文档: http://docs.ckeditor.com/#!/guide/dev_file_upload

文件浏览器(file browser) 上传的方式: http://docs.ckeditor.com/#!/guide/dev_file_browse_upload

都很容易配置

"""

LIMIT_M = 4


class UploadImage(DBackHandler):
    def post(self):

        callback_name = self.get_arg('CKEditorFuncNum')
        if callback_name:
            self._using_file_browser(callback_name)
        else:
            self._using_cp_style()

    def _using_cp_style(self):
        """
        使用文件上传的方式
        使用 copy & paste 上传
        :return:
        """
        # --- 主动捕获异常, 以免被 默认的异常处理代码处理掉.
        succ = 1
        fail = 0
        try:
            file_data, ext = self._get_upload_file_info('upload', LIMIT_M)
            upload_dto = g_upload_service.do_save(file_data, ext)
            full_path = g_file_server + '/' + upload_dto.rel_path
            logging.debug('----- full_path: ' + full_path)
            result = {
                'uploaded': succ,
                "fileName": upload_dto.file_name,
                "url": full_path
            }
        except Exception, ex:
            logging.error(ex)
            result = {
                'uploaded': fail,
                "error": {
                    "message": ex.message
                }
            }

        self.write(result)

    def _using_file_browser(self, callback):
        """
        使用 file browser 上传
        :return:
        """
        file_data, ext = self._get_upload_file_info('upload', LIMIT_M)
        upload_dto = g_upload_service.do_save(file_data, ext)
        full_path = g_file_server + '/' + upload_dto.rel_path
        logging.debug('----- full_path: ' + full_path)

        result = "<script type=\"text/javascript\">"
        result += "window.parent.CKEDITOR.tools.callFunction(" + callback + ",'" + full_path + "','')"
        result += "</script>"

        self.write(result)


class ReadUpload(DBackHandler):

    def get(self, *args):

        uri = self.request.uri
        uri = uri[1:]           # 去掉第一个 /
        path = os.path.join(g_project_root, uri)
        logging.debug('--- file path: ' + path)
        f, ext = os.path.splitext(uri)
        self.set_header('Content-Type', 'image/' + ext)
        self.write(bytes(open(path).read()))

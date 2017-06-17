#! /usr/bin/python
# -*- coding: UTF-8 -*-

"""
    来自博客:云师兄写字的地方(yunshichen.com), 作者邮箱 4986350@qq.com
    你可以自由转载此文章, 但请注明出处.
"""

import Image, ImageEnhance
from beans import LogicException, dict_to_bean
import os
from datetime import datetime
import utils

LEFT_TOP = 'lt'
LEFT_BOTTOM = 'lb'
RIGHT_TOP = 'rt'
RIGHT_BOTTOM = 'rb'

WIDTH_GRID = 30.0
HIGHT_GRID = 30.0


def mark_layout(im, mark, layout=RIGHT_BOTTOM):
    im_width, im_hight = im.size[0], im.size[1]
    mark_width, mark_hight = mark.size[0], mark.size[1]

    coordinates = {LEFT_TOP: (int(im_width / WIDTH_GRID), int(im_hight / HIGHT_GRID)),
                   LEFT_BOTTOM: (int(im_width / WIDTH_GRID), int(im_hight - mark_hight - im_hight / HIGHT_GRID)),
                   RIGHT_TOP: (int(im_width - mark_width - im_width / WIDTH_GRID), int(im_hight / HIGHT_GRID)),
                   RIGHT_BOTTOM: (int(im_width - mark_width - im_width / WIDTH_GRID), \
                                  int(im_hight - mark_hight - im_hight / HIGHT_GRID)),
                   }
    return coordinates[layout]


def reduce_opacity(mark, opacity):
    assert opacity >= 0 and opacity <= 1
    mark = mark.convert('RGBA') if mark.mode != 'RGBA' else mark.copy()
    alpha = mark.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    mark.putalpha(alpha)
    return mark


def water_mark(img, mark, opacity=1):
    if opacity < 1:
        mark = reduce_opacity(mark, opacity)

    if img.mode != 'RGBA':
        img = img.convert('RGBA')
        img_format = 'JPEG'
    else:
        img_format = 'PNG'

    # 指定上传图片最大宽度580和高宽600，如超过进行resize
    # if img.size[0] > 580:
    #     img = img.resize((580, img.size[1]/(img.size[0]/580.0)), resample=1)
    #
    # if img.size[1] > 600:
    #     img = img.resize((img.size[0]/(img.size[1]/600.0),600), resample=1)

    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    layer.paste(mark, mark_layout(img, mark))

    img = Image.composite(layer, img, layer)

    return img

    # new_img = StringIO()
    # img.save(new_img, img_format, quality=100)
    #
    # return new_img.getvalue()


def check_and_get_image_meta(file_data, water_image_path=None):
    """
    检查并取得图片信息
    :param file_data:
    :param water_image_path: 水印图片地址
    :return:
    """
    from PIL import Image
    import StringIO

    img = StringIO.StringIO(file_data)
    a_image = Image.open(img)
    a_fmt = a_image.format.lower()

    format_list = ['gif', 'jpg', 'jpeg', 'bmp', 'png', 'x-png', 'pjpeg']

    if a_fmt not in format_list:
        raise LogicException(u'上传的文件必须是图片')

    # ---- 如果水印图片不为空, 打水印
    if water_image_path:
        mark = Image.open(water_image_path)
        new_image = water_mark(a_image, mark, 0.99)
        # new_image.show()
        # Image 无法直接得到 file-like 对象, 所以先将之保存到临时文件
        temp_path = '/tmp/test.' + a_fmt
        fb = open(temp_path, 'w')
        new_image.save(fb)
        fb.close()
        file_data = open(temp_path, 'r').read()

    content_type = 'image/' + a_fmt

    map_data = dict()

    map_data['width'] = a_image.size[0]
    map_data['height'] = a_image.size[1]
    map_data['file_data'] = file_data
    map_data['content_type'] = content_type
    map_data['ext'] = a_fmt

    return dict_to_bean(map_data)


class FileUploadService(object):
    def __init__(self, base_dir, water_mark=None):
        self.base_dir = base_dir
        self.water_mark = water_mark
        # 检查 upload的目录是否存在, 如果不存在则创建.
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

    def do_save(self, byte_data):

        file_dto = check_and_get_image_meta(byte_data, self.water_mark)

        # 构造 base_dir/2017/12/xxssdfjsfdj-sdfjsdfksfj-sfskdfj.jpg 的文件格式
        now_time = datetime.now()
        year = utils.f_time(now_time, '%Y')
        month = utils.f_time(now_time, '%m')
        path = os.path.join(self.base_dir, year)
        path = os.path.join(path, month)

        if not os.path.exists(path):
            os.makedirs(path)

        from uuid import uuid4
        file_name = str(uuid4()) + '.' + file_dto.ext
        path = os.path.join(path, file_name)
        f = open(path, 'wb')
        f.write(file_dto.file_data)
        f.close()

        rel_path = str(year) + '/' + str(month) + '/' + file_name

        file_dto.rel_path = rel_path
        file_dto.file_name = file_name

        return file_dto


def test():
    im = Image.open('test.jpeg')
    mark = Image.open('blog.png')
    water_mark(im, mark).show()


if __name__ == '__main__':
    test()

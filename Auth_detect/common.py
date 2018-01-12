# coding:utf-8

import datetime


def get_current_time():
    """\
    获取当前时间
    """
    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def unicode2zh(unicode_str):
    return unicode_str.decode('unicode_escape')

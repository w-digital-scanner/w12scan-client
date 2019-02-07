#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/23 5:19 PM
# @Author  : w8ay
# @File    : webtitle.py
import re

from lib.data import collector


def poc(target):
    '''
    这个插件的作用是从html中获取网站title
    :param target:
    :return:
    '''
    html = collector.get_domain_info(target, "body")
    if html:
        m = re.search('<title>(.*)?<\/title>', html, re.IGNORECASE)
        if m:
            collector.add_domain_info(target, {"title": m.group(1)})

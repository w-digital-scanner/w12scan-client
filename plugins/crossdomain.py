#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/23 5:43 PM
# @Author  : w8ay
# @File    : crossdomain.py
import requests
from lib.data import collector
from urllib.parse import urlparse

'''
name: crossdomain.xml文件发现
referer: unknown
author: Lucifer
description: crossdomain错误配置可导致。
'''


def poc(arg):
    url = arg + "/crossdomain.xml"

    try:
        header = dict()
        header[
            "User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
        r = requests.get(url, headers=header, timeout=5)
        if 'allow-access-from domain="*"' in r.text:
            collector.add_domain_bug(arg, {"crossdomain leak": url})
        else:
            return False
    except Exception:
        return False

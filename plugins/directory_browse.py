#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/2/25 2:38 PM
# @Author  : w8ay
# @File    : directory_browse.py
# Author:w8ay
# Name:目录浏览

import HackRequests
from urllib.parse import urlparse
from lib.data import collector


def poc(arg, **kwargs):
    URL = arg
    netloc = urlparse(arg).netloc
    flag_list = [
        "index of",
        "directory listing for",
        "{} - /".format(netloc)
    ]
    hack = HackRequests.hackRequests()
    url_list = [
        URL + "/css/", URL + "/js/", URL + "/img/", URL + "/images/", URL + "/upload/", URL + "/inc/"
    ]
    for u in url_list:
        try:
            hh = hack.http(u)
        except:
            continue
        if hh.status_code == 404:
            continue
        for i in flag_list:
            try:
                html = hh.text()
            except:
                html = ""
            if i in html.lower():
                result = {
                    "name": "web目录浏览",  # 插件名称
                    "content": "通过此功能可获取web目录程序结构",  # 插件返回内容详情，会造成什么后果。
                    "url": u,  # 漏洞存在url
                    "log": hh.log,
                    "tag": "info_leak"  # 漏洞标签
                }
                collector.add_domain_bug(arg, {"directory_browse": repr(result)})
    return False

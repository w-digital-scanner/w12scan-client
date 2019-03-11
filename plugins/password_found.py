#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/3/11 11:22 AM
# @Author  : w8ay
# @File    : password_found.py
import re

from lib.data import collector


def poc(arg):
    html = collector.get_domain_info(arg, "body")

    if html:
        m = re.search('password', html, re.I | re.M | re.S)
        if m:
            collector.add_domain_bug(arg, {"登录平台发现": arg})

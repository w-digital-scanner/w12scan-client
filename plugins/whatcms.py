#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/23 11:04 PM
# @Author  : w8ay
# @File    : whatcms.py
# 精简版的whatcms
import hashlib
import json
import os

import HackRequests

from lib.data import collector, PATHS


def poc(domain):
    cms = collector.get_domain_info(domain, "CMS")
    if cms:
        return False
    data = read_config()
    hack = HackRequests.hackRequests()
    cache = {}
    for k, v in data.items():
        for item in v:
            path = item["path"]
            _url = domain + path

            if path not in cache:
                try:
                    hh = hack.http(_url)
                    if hh.status_code != 200:
                        raise Exception
                    content = hh.content()
                    cache[path] = content
                except:
                    continue
            else:
                content = cache[path]
            try:
                html = content.decode('utf-8', 'ignore')
            except:
                html = str(content)
            option = item["option"]
            vaild = item["content"]
            if option == "md5":
                m = hashlib.md5()
                m.update(content)
                if m.hexdigest() == vaild:
                    collector.add_domain_info(domain, {"CMS": k})
                    return True
            elif option == "keyword":
                if vaild in html:
                    collector.add_domain_info(domain, {"CMS": k})
                    return True


def read_config():
    path = os.path.join(PATHS.DATA_PATH, "cms.json")
    with open(path) as f:
        data = json.load(f)

    return data

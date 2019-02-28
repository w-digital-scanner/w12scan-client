#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/23 4:46 PM
# @Author  : w8ay
# @File    : separate_server.py
import os
import re

from lib.data import collector, PATHS, logger


def poc(target):
    '''
    这个插件的作用是从html或header中分离出有用的数据
    :param target:
    :return:
    '''

    def discern_from_header(name, discern_type, key, reg):
        if "Server" in headers:
            result.add("Server:" + headers["Server"])
        if "X-Powered-By" in headers:
            result.add("X-Powered-By:" + headers["X-Powered-By"])
        if key in headers and (re.search(reg, headers[key], re.I)):
            result.add(name)
        else:
            pass

    def discern_from_index(name, discern_type, key, reg):
        if re.search(reg, html, re.I):
            result.add(name)
        else:
            pass

    html = collector.get_domain_info(target, "body")
    headers = collector.get_domain_info(target, "headers")
    result = set()
    result_dict = {}
    if html and headers:
        mark_list = read_config()
        for mark_info in mark_list:
            name, discern_type, key, reg = mark_info
            if discern_type == 'headers':
                discern_from_header(name, discern_type, key, reg)
            elif discern_type == 'index':
                discern_from_index(name, discern_type, key, reg)
    for i in result:
        try:
            k, *v = i.split(":")
            v = ' '.join(v)
            # 'X-Powered-By:Servlet 2.4; JBoss-4.0.3SP1 (build: CVSTag=JBoss_4_0_3_SP1 date=200510231054)/Tomcat-5.5'"
            result_dict[k] = v
        except:
            logger.error("webeye error split:" + repr(i))
    collector.add_domain_info(target, result_dict)


def read_config():
    mark_list = []
    config_file = open(os.path.join(PATHS.DATA_PATH, "webeye.txt"), 'r')
    for mark in config_file:
        # remove comment, group, blank line
        if re.match("\[.*?\]|^;", mark) or not mark.split():
            continue
        name, location, key, value = mark.strip().split("|", 3)
        mark_list.append([name, location, key, value])
    config_file.close()
    return mark_list

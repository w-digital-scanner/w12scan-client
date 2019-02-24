#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/23 5:40 PM
# @Author  : w8ay
# @File    : bakfile.py
from urllib.parse import urlparse

import requests

from lib.data import collector


def poc(url):
    audit(url)


def audit(arg):
    url = arg
    arg = urlparse(url).netloc
    dirs = '''wwwroot.rar
wwwroot.zip
wwwroot.tar
wwwroot.tar.gz
web.rar
web.zip
web.tar
web.tar
ftp.rar
ftp.zip
ftp.tar
ftp.tar.gz
admin.rar
admin.zip
admin.tar
admin.tar.gz
www.rar
www.zip
www.tar
www.tar.gz
'''
    host_keys = arg.split(".")
    listFile = []
    for i in dirs.strip().splitlines():
        listFile.append(i)
    for key in host_keys:
        if key is '':
            host_keys.remove(key)
            continue
        if '.' in key:
            new = key.replace('.', "_")
            host_keys.append(new)
    host_keys.append(arg)
    for i in host_keys:
        new = "%s.rar" % (i)
        listFile.append(new)
        new = "%s.zip" % (i)
        listFile.append(new)
        new = "%s.tar.gz" % (i)
        listFile.append(new)
        new = "%s.tar" % (i)
        listFile.append(new)

    warning_list = []
    for payload in listFile:
        loads = url + "/" + payload
        try:
            header = dict()
            header[
                "User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
            r = requests.head(loads, headers=header, timeout=7)
            if r.status_code != 200:
                continue
            r = requests.get(loads, header=header, timeout=7)
            if r.status_code == 200 and "Content-Type" in r.headers and "application" in r.headers["Content-Type"]:
                warning_list.append("[BAKFILE] " + loads)
        except Exception:
            pass

    # In order to  solve the misreport
    if len(warning_list) > 6:
        return False
    elif warning_list:
        collector.add_domain_bug(url, {"bakfile": repr(warning_list)})

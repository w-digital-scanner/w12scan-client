#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/23 6:11 PM
# @Author  : w8ay
# @File    : gitleak.py
import requests
from lib.data import collector


def poc(arg):
    url = arg + "/.git/config"
    try:
        header = dict()
        header[
            "User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
        r = requests.get(url, headers=header, timeout=5)
        if "repositoryformatversion" in r.text:
            collector.add_domain_bug(arg, {"Git Leak": url})
        else:
            return False
    except Exception:
        return False

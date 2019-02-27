#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/23 6:14 PM
# @Author  : w8ay
# @File    : phpinfo.py
import requests
from lib.data import collector


def poc(arg):
    phpinfoList = r"""
    phpinfo.php
PhpInfo.php
PHPinfo.php
PHPINFO.php
phpInfo.php
info.php
Info.php
INFO.php
phpversion.php
phpVersion.php
test1.php
test.php
test2.php
phpinfo1.php
phpInfo1.php
info1.php
PHPversion.php
x.php
xx.php
xxx.php
    """
    paths = phpinfoList.strip().splitlines()
    result = []
    for path in paths:
        try:
            payload = arg + "/" + path.strip()
            header = dict()
            header[
                "User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
            h = requests.head(payload, headers=header, timeout=5)
            if h.status_code != 200:
                continue
            r = requests.get(payload, headers=header, timeout=5)
            if "allow_url_fopen" in r.text and r.status_code == 200:
                result.append(payload)
        except Exception:
            pass
    if result:
        collector.add_domain_bug(arg, {"phpinfo": result})
        return result
    else:
        return False

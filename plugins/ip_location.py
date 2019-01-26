#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/26 11:56 PM
# @Author  : w8ay
# @File    : ip_location.py
import requests
import json


def poc(arg):
    api = "http://ip.taobao.com/service/getIpInfo.php?ip={0}".format(arg)
    r = requests.get(api)
    if r.status_code != 200:
        return False
    jsonp = r.text
    data = json.loads(jsonp)
    if data.get("data", None):
        d = {
            "country_id": data["data"]["country_id"],
            "country": data["data"]["country"],
            "region": data["data"]["region"]
        }
        return d
    else:
        return False

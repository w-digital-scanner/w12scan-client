#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/26 11:56 PM
# @Author  : w8ay
# @File    : ip_location.py
import os
from functools import reduce

import requests
import json
from lib.data import logger, PATHS
import geoip2.database


def taobao_api(arg):
    api = "http://ip.taobao.com/service/getIpInfo.php?ip={0}".format(arg)
    try:
        r = requests.get(api)
    except Exception as e:
        logger.error("ip_location request faild:" + str(e))
        return False
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


def geoip(arg):
    filename = os.path.join(PATHS.DATA_PATH, "GeoLite2", "GeoLite2-City.mmdb")
    reader = geoip2.database.Reader(filename)
    response = reader.city(arg)
    d = {
        "country_id": response.country.iso_code,
        "country": response.country.name,
        "region": response.city.name
    }

    return d


def ip_into_int(ip):
    # 先把 192.168.1.13 变成16进制的 c0.a8.01.0d ，再去了“.”后转成10进制的 3232235789 即可。
    # (((((192 * 256) + 168) * 256) + 1) * 256) + 13
    return reduce(lambda x, y: (x << 8) + y, map(int, ip.split('.')))


def is_internal_ip(ip):
    ip = ip_into_int(ip)
    net_a = ip_into_int('10.255.255.255') >> 24
    net_b = ip_into_int('172.31.255.255') >> 20
    net_c = ip_into_int('192.168.255.255') >> 16
    return ip >> 24 == net_a or ip >> 20 == net_b or ip >> 16 == net_c


def poc(ip):
    if is_internal_ip(ip):
        d = {
            "country_id": "internal icon-disc",
            "country": "Internal Ip",
            "region": ""
        }
        return d
    interface = geoip(ip)
    return interface

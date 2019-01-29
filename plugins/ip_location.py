#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/26 11:56 PM
# @Author  : w8ay
# @File    : ip_location.py
import os

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


def poc(ip):
    interface = geoip(ip)
    return interface

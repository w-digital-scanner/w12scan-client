#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/14 5:26 PM
# @Author  : w8ay
# @File    : data.py
from lib.collector import Collector
from lib.log import LOGGER
import redis  # 导入redis模块，通过python操作redis 也可以直接在redis主机的服务端操作缓存数据库

from config import REDIS_HOST

logger = LOGGER()


class PATHS:
    ROOT_PATH = ''
    PLUGIN_PATH = ''
    OUTPUT_PATH = ''
    DATA_PATH = ''


collector = Collector()


def redis_concet():
    host, port = REDIS_HOST.split(":")
    pool = redis.ConnectionPool(host=host, port=port,
                                decode_responses=True)  # host是redis主机，需要redis服务端和客户端都起着 redis默认端口是6379
    redis_con = redis.Redis(connection_pool=pool)
    return redis_con


redis_con = redis_concet()

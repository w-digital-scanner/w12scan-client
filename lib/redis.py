#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/2/13 1:50 PM
# @Author  : w8ay
# @File    : redis.py
import time

import redis  # 导入redis模块，通过python操作redis 也可以直接在redis主机的服务端操作缓存数据库

from config import NODE_NAME
from config import REDIS_HOST
from lib.common import lstrsub


def redis_concet():
    host, port = REDIS_HOST.split(":")
    r = redis.Redis(host=host, port=port)
    while 1:
        print("redis check...")
        try:
            r.ping()
            break
        except:
            pass
        time.sleep(3)
    print("redis check success..")
    pool = redis.ConnectionPool(host=host, port=port,
                                decode_responses=True)  # host是redis主机，需要redis服务端和客户端都起着 redis默认端口是6379
    redis_con = redis.Redis(connection_pool=pool)
    return redis_con


def add_redis_log(log):
    '''
    添加任务log到redis队列，并对redis队列进行清理，如果超过500则弹出老的
    :param log:
    :return:
    '''
    node_name = "w12_log_{}".format(lstrsub(NODE_NAME, "w12_node_"))
    redis_con.lpush(node_name, repr(log))
    # while redis_con.llen(node_name) > 500:
    #     redis_con.rpop(node_name)


def task_update(key: str, value: int):
    '''

    :param key:tasks running finished
    :param value:
    :return:
    '''
    field = ["tasks", "running", "finished"]
    if key not in field:
        print("{key} error".format(key=key))
        return False
    if key == "running" or key == "finished":
        redis_con.hincrby(NODE_NAME, key, value)
    else:
        redis_con.hset(NODE_NAME, key, value)


redis_con = redis_concet()

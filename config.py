#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/21 10:08 PM
# @Author  : w8ay
# @File    : config.py

# 程序运行的线程数
import os

THREAD_NUM = 20
DEBUG = True
# Ip的缓存数量
NUM_CACHE_IP = 70

# 域名的缓存数量
NUM_CACHE_DOMAIN = 10

# Masscan相关
MASSCAN_RATE = 3000  # masscan 的速率
MASSCAN_DEFAULT_PORT = "21,23,80,443,1433,3306,5432,6379,9200,11211,27017,8081,8000,8080,8888"
MASSCAN_FULL_SCAN = False  # 是否扫描全端口

# WEB Restful接口地址
WEB_INTERFACE = "http://127.0.0.1:8000/"
WEB_INTERFACE_KEY = "hello-w12scan!"

# WEB POCS repository 提供指纹识别对应的poc仓库
WEB_REPOSITORY = "https://github.com/boy-hack/airbug"

# reids数据库
REDIS_HOST = "127.0.0.1:6379"

# docker config
RUNMODEL = os.environ.get("RUNMODEL") or 'dev'
if RUNMODEL == "docker":
    WEB_INTERFACE = os.environ.get("WEB_INTERFACE")
    REDIS_HOST = os.environ.get("REDIS_HOST")
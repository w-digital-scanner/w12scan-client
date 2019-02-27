#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/21 10:08 PM
# @Author  : w8ay
# @File    : config.py

# 程序运行的线程数
import os

THREAD_NUM = 40
DEBUG = False
# Ip的缓存数量
NUM_CACHE_IP = 256

# 域名的缓存数量
NUM_CACHE_DOMAIN = 5

# Masscan相关
MASSCAN_RATE = 3000  # masscan 的速率
MASSCAN_DEFAULT_PORT = "21,22,23,80-90,161,389,443,445,873,1099,1433,1521,1900,2082,2083,2222,2601,2604,3128,3306,3311,3312,3389,4440,4848,5432,5560,5900,5901,5902,6082,6379,7001-7010,7778,8080-8090,8649,8888,9000,9200,10000,11211,27017,28017,50000,50030,50060"
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

# 该扫描节点的名称(自定义)
NODE_NAME = "w12_node_{0}".format(os.environ.get("NODE_NAME", "w12ss"))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/21 10:08 PM
# @Author  : w8ay
# @File    : config.py

# 程序运行的线程数
THREAD_NUM = 5

# Ip的缓存数量
NUM_CACHE_IP = 10

# 域名的缓存数量
NUM_CACHE_DOMAIN = 1

# Masscan相关
MASSCAN_RATE = 1000  # masscan 的速率
MASSCAN_DEFAULT_PORT = "21,23,80,443,1433,3306,5432,6379,9200,11211,27017"
MASSCAN_FULL_SCAN = False  # 是否扫描全端口

# WEB Restful接口地址
WEB_INTERFACE = ""

# WEB POCS repository 提供指纹识别对应的poc仓库
WEB_REPOSITORY = "https://github.com/boy-hack/airbug"
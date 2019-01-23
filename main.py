#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/14 4:35 PM
# @Author  : w8ay
# @File    : main.py
import os
from lib.data import PATHS, logger
from lib.engine import Schedular
from config import THREAD_NUM


def module_path():
    """
    This will get us the program's directory
    """
    return os.path.dirname(os.path.realpath(__file__))


def main():
    PATHS.ROOT_PATH = module_path()
    PATHS.PLUGIN_PATH = os.path.join(PATHS.ROOT_PATH, "pocs")
    PATHS.OUTPUT_PATH = os.path.join(PATHS.ROOT_PATH, "output")

    logger.info("Hello W12SCAN !")
    targets = ["https://x.hacking8.com"] * 10
    # init path
    # domain域名整理（统一格式：无论是域名还是二级目录，右边没有 /），ip cidr模式识别，ip整理

    # 访问redis去重验证
    schedular = Schedular(threadnum=THREAD_NUM)
    for t in targets:
        schedular.put_target(t)
    schedular.start()
    # 启动任务分发调度器
    while 1:
        pass


if __name__ == '__main__':
    main()

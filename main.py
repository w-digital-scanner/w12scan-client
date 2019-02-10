#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/14 4:35 PM
# @Author  : w8ay
# @File    : main.py
import os
import threading

from config import THREAD_NUM, DEBUG
from lib.data import PATHS, logger, redis_con
from lib.engine import Schedular
from thirdpart.requests import patch_all


def module_path():
    """
    This will get us the program's directory
    """
    return os.path.dirname(os.path.realpath(__file__))


def main():
    PATHS.ROOT_PATH = module_path()
    PATHS.PLUGIN_PATH = os.path.join(PATHS.ROOT_PATH, "pocs")
    PATHS.OUTPUT_PATH = os.path.join(PATHS.ROOT_PATH, "output")
    PATHS.DATA_PATH = os.path.join(PATHS.ROOT_PATH, "data")

    patch_all()
    logger.info("Hello W12SCAN !")

    # domain域名整理（统一格式：无论是域名还是二级目录，右边没有 /），ip cidr模式识别，ip整理

    # 访问redis获取目标
    def redis_get():
        list_name = "w12scan_scanned"
        while 1:
            target = redis_con.blpop(list_name)[1]
            logger.debug("redis get " + target)
            schedular.put_target(target)

    def debug_get():
        target = "188.131.196.108"
        schedular.put_target(target)

    schedular = Schedular(threadnum=THREAD_NUM)
    # for t in targets:
    #     schedular.put_target(t)
    schedular.start()
    # 启动任务分发调度器
    # while 1:
    #     pass
    if DEBUG:
        func_target = debug_get
    else:
        func_target = redis_get
    t = threading.Thread(target=func_target, name='LoopThread')
    t.start()
    while 1:
        schedular.run()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/21 10:05 PM
# @Author  : w8ay
# @File    : masscan.py
import os
import time

from config import MASSCAN_RATE
from lib.data import PATHS, logger


def masscan(target, ports):
    output = os.path.join(PATHS.OUTPUT_PATH, "output_" + str(time.time()) + ".log")
    cmd = "masscan -p {} --rate={} --randomize-hosts -iL \"{}\" -oL \"{}\"".format(ports, MASSCAN_RATE, target, output)
    os.system(cmd)
    open_list = []

    with open(output, "r") as f:
        result_json = f.readlines()
    if result_json:
        try:
            del result_json[0]
            del result_json[-1]
            open_list = {}
            for res in result_json:
                try:
                    p = res.split()
                    ip = p[3]
                    port = p[2]
                    if ip not in open_list:
                        open_list[ip] = set()
                    open_list[ip].add(port)
                except:
                    pass

        except Exception as e:
            logger.error("masscan read faild")
    os.unlink(output)
    os.unlink(target)
    if open_list:
        return open_list
    return None

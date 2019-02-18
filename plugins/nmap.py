#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/21 10:05 PM
# @Author  : w8ay
# @File    : nmap.py
import nmap
from lib.data import logger


def nmapscan(host, ports):
    # 接受从masscan上扫描出来的结果
    # 为了可以多线程使用，此函数支持多线程调用
    nm = nmap.PortScanner()
    argument = "-sV -sS -Pn --host-timeout 1m -p{}".format(','.join(ports))
    try:
        ret = nm.scan(host, arguments=argument)
    except nmap.PortScannerError:
        logger.debug("Nmap PortScannerError host:{}".format(host))
        return None
    except:
        return None

    # debug
    elapsed = ret["nmap"]["scanstats"]["elapsed"]
    command_line = ret["nmap"]["command_line"]
    logger.debug("[nmap] successed,elapsed:%s command_line:%s" % (elapsed, command_line))

    if host in ret["scan"]:
        try:
            result = ret["scan"][host]["tcp"]
        except KeyError:
            return None
        return result

    return None

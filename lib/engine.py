#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/14 5:41 PM
# @Author  : w8ay
# @File    : engine.py
# 分发调度引擎
import _thread
import os
import threading
import time
from queue import Queue

from lib.common import is_ip_address_format, is_url_format
from lib.data import logger, PATHS,collector
from config import NUM_CACHE_DOMAIN, NUM_CACHE_IP, MASSCAN_DEFAULT_PORT, MASSCAN_FULL_SCAN
from plugins.masscan import masscan
from plugins.nmap import nmapscan


class Schedular:

    def __init__(self, threadnum=1):

        self.queue = Queue()
        self.threadNum = threadnum
        self.lock = threading.Lock()
        self.cache_ips = []  # IP缓冲池
        self.cache_domains = []  # 域名缓冲池
        logger.info("Start number of threading {}".format(self.threadNum))

    def put(self, target):
        # 判断是IP还是域名，加入不同的字段
        serviceType = "domain"
        if is_ip_address_format(target):
            serviceType = "ip"
        elif is_url_format(target):
            serviceType = "domain"
        else:
            serviceType = "other"

        tmp = {
            "target": target,
            "serviceType": serviceType
        }

        self.queue.put(tmp)

    def receive(self):
        while 1:
            struct = self.queue.get()
            serviceType = struct.get("serviceType", 'other')
            if serviceType == "other":
                msg = "not matches target:{}".format(repr(struct))
                logger.error(msg)
                continue
            if serviceType == "ip":
                flag = False
                self.lock.acquire()
                self.cache_ips.append(struct)
                num = len(self.cache_ips)
                if num >= NUM_CACHE_IP:
                    flag = True
                    serviceTypes = self.cache_ips
                    self.cache_ips = []
                self.lock.release()
                if not flag:
                    continue
                self.hand_ip(serviceTypes)
            elif serviceType == "domain":
                flag = False
                self.lock.acquire()
                self.cache_domains.append(struct)
                num = len(self.cache_domains)
                if num >= NUM_CACHE_DOMAIN:
                    flag = True
                    serviceTypes = self.cache_domains
                    self.cache_domains = []
                self.lock.release()
                if not flag:
                    continue
                self.hand_domain(serviceTypes)

    def start(self):
        for i in range(self.threadNum):
            _thread.start_new_thread(self.receive, ())

    def hand_ip(self, serviceTypes):
        IP_LIST = []
        for item in serviceTypes:
            IP_LIST.append(item["target"])
        ports = MASSCAN_DEFAULT_PORT
        if MASSCAN_FULL_SCAN:
            ports = "1-65535"
        target = os.path.join(PATHS.OUTPUT_PATH, "target_" + str(time.time()) + ".log")
        with open(target, "w+") as fp:
            fp.write('\n'.join(IP_LIST))
        result = masscan(target, ports)
        if result is None:
            return None
        result2 = {}
        # format:{'115.159.39.75': ['80'], '115.159.39.215': ['80', '3306'],}
        for host, ports in result.items():
            if host not in result2:
                result2[host] = []
            result_nmap = nmapscan(host, ports)
            if result_nmap is None:
                for tmp_port in ports:
                    result2[host].append({"port": tmp_port})
                continue
            # return like this dict
            # {
            #     49152: {
            #         'product': 'Microsoft Windows RPC',
            #         'state': 'open',
            #         'version': '',
            #         'name': 'msrpc',
            #         'conf': '10',
            #         'extrainfo': '',
            #         'reason': 'syn-ack',
            #         'cpe': 'cpe:/o:microsoft:windows'
            #     },
            #     49168: {
            #         'product': 'Microsoft Windows RPC',
            #         'state': 'open',
            #         'version': '',
            #         'name': 'msrpc',
            #         'conf': '10',
            #         'extrainfo': '',
            #         'reason': 'syn-ack',
            #         'cpe': 'cpe:/o:microsoft:windows'
            #     }
            #       version:2.2.15
            #       product:'Tengine httpd'
            # }
            # to solve state:open
            for port, portInfo in result_nmap.items():
                if portInfo["state"] != "open":
                    continue
                name = portInfo.get("name", "")
                product = portInfo.get("product", "")
                version = portInfo.get("version", "")
                extrainfo = portInfo.get("extrainfo", "")
                if name == "http":
                    _url = "http://" + host + ":" + port
                    self.put(_url)
                elif name == "https":
                    _url = "https://" + host
                    self.put(_url)
                result2[host].append(
                    {"port": port, "name": name, "product": product, "version": version, "extrainfo": extrainfo})

        logger.info(repr(result2))
        collector.add_ips(result2)


    def hand_domain(self, serviceTypes):
        for serviceType in serviceTypes:
            target = serviceType["target"]

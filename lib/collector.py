#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/23 10:29 AM
# @Author  : w8ay
# @File    : collector.py
# 收集器，用于收集信息传递参数
import threading
import copy
import queue
import json
from urllib.parse import urljoin

import requests

from config import WEB_INTERFACE, WEB_INTERFACE_KEY, DEBUG, NODE_NAME
from lib.redis import redis_con, task_update


class Collector:

    def __init__(self):
        self.collect_lock = threading.Lock()
        self.collect_domains = {}
        self.collect_ips = {}
        # domain cache 缓存队列
        self.cache_queue = queue.Queue()
        # ip cache 缓存队列
        self.cache_ips = queue.Queue()

    def add_domain(self, domain):
        self.collect_lock.acquire()
        if domain not in self.collect_domains:
            self.collect_domains[domain] = {}
        self.collect_lock.release()

    def add_domain_info(self, domain, infos: dict):
        if domain not in self.collect_domains:
            self.add_domain(domain)
        for k, v in infos.items():
            self.collect_lock.acquire()
            self.collect_domains[domain][k] = v
            self.collect_lock.release()

    def add_domain_bug(self, domain, infos: dict):
        self.collect_lock.acquire()
        if "bugs" not in self.collect_domains[domain]:
            self.collect_domains[domain]["bugs"] = {}
        for k, v in infos.items():
            self.collect_domains[domain]["bugs"][k] = v
        self.collect_lock.release()

    def add_ips(self, infos: dict):
        for k, v in infos.items():
            self.collect_lock.acquire()
            self.collect_ips[k] = v
            self.collect_lock.release()

    def get_ip(self, target):
        self.collect_lock.acquire()
        data = copy.deepcopy(self.collect_ips[target])
        self.collect_lock.release()
        return data

    def get_domain(self, domain):
        self.collect_lock.acquire()
        data = copy.deepcopy(self.collect_domains[domain])
        self.collect_lock.release()
        # 删除一些不想显示的key
        if data.get("headers"):
            tmp_headers = "\n".join([k + ":" + v for k, v in data["headers"].items()])
            del data["headers"]
            data["headers"] = tmp_headers
        return data

    def get_domain_info(self, domain, k):
        self.collect_lock.acquire()
        ret = self.collect_domains[domain].get(k, None)
        self.collect_lock.release()
        return ret

    def del_domain(self, domain):
        self.collect_lock.acquire()
        del self.collect_domains[domain]
        self.collect_lock.release()

    def del_ip(self, target):
        self.collect_lock.acquire()
        del self.collect_ips[target]
        self.collect_lock.release()

    def send_ok(self, domain):
        '''
        传递ok信号，将域名缓存到缓冲队列，自动检测缓冲队列，大于10个则自动发送到接口
        :param domain:
        :return:
        '''
        data = self.get_domain(domain)
        data["url"] = domain
        self.cache_queue.put(data)
        self.del_domain(domain)

        task_update("finished", 1)

        if self.cache_queue.qsize() > 10:
            self.submit()

    def send_ok_ip(self, target):
        data = self.get_ip(target)
        data['target'] = target
        self.del_ip(target)
        self.cache_ips.put(data)

        task_update("finished", 1)

        if self.cache_ips.qsize() > 10:
            self.submit()

    def submit(self):
        '''
        传递信息给web restful接口
        :return:
        '''
        # domain
        while not self.cache_queue.empty():
            data = self.cache_queue.get()
            # self.collect_lock.acquire()
            # with open("domain.result.txt", "a+") as f:
            #     f.write(json.dumps(data) + ",")
            # self.collect_lock.release()
            if DEBUG:
                print("[submit] " + repr(data))
                continue
            _api = urljoin(WEB_INTERFACE, "./api/v1/domain")
            headers = {
                "W12SCAN": WEB_INTERFACE_KEY
            }
            try:
                r = requests.post(_api, json=data, headers=headers)
            except Exception as e:
                print("api request faild: {0} ".format(str(e)))
                continue
            if r.status_code == 200:
                status = json.loads(r.text)
                if status["status"] != 200:
                    print("api request faild(status!=200) " + status["msg"])

        # ips
        while not self.cache_ips.empty():
            data = self.cache_ips.get()
            # self.collect_lock.acquire()
            # with open("ips.result.txt", "a+") as f:
            #     f.write(json.dumps(data) + ",")
            # self.collect_lock.release()
            if DEBUG:
                print("[submit] " + repr(data))
                continue
            _api = urljoin(WEB_INTERFACE, "./api/v1/ip")
            headers = {
                "w12scan": WEB_INTERFACE_KEY
            }
            try:
                r = requests.post(_api, json=data, headers=headers)
            except Exception as e:
                print("api request faild: {0} ".format(str(e)))
                continue
            if r.status_code == 200:
                status = json.loads(r.text)
                if status["status"] != 200:
                    print("api request faild(status!=200) " + status["msg"])


if __name__ == '__main__':
    c = Collector()
    c.add_domain("test.com")
    c.add_domain_info("test.com", {"xx": "11"})
    c.send_ok("test.com")
    c.submit()

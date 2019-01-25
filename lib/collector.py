#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/23 10:29 AM
# @Author  : w8ay
# @File    : collector.py
# 收集器，用于收集信息传递参数
import threading
import copy
import queue


class Collector:

    def __init__(self):
        self.collect_lock = threading.Lock()
        self.collect_domains = {}
        self.cache_queue = queue.Queue()

    def add_ip(self, info):
        pass

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

    def add_ips(self, infos):
        pass

    def get_domain(self, domain):
        self.collect_lock.acquire()
        data = copy.deepcopy(self.collect_domains[domain])
        self.collect_lock.release()
        # 删除一些不想显示的key
        del data["body"]
        del data["headers"]
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

    def send_ok(self, domain):
        '''
        传递ok信号，将域名缓存到缓冲队列，自动检测缓冲队列，大于10个则自动发送到接口
        :param domain:
        :return:
        '''
        data = self.get_domain(domain)
        self.cache_queue.put(data)
        self.del_domain(domain)
        if self.cache_queue.qsize() > 10:
            self.submit()

    def submit(self):
        '''
        传递信息给web restful接口
        :return:
        '''
        while not self.cache_queue.empty():
            data = self.cache_queue.get()
            print(data)

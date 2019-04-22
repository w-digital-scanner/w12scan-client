#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/14 5:41 PM
# @Author  : w8ay
# @File    : engine.py
# 分发调度引擎
import _thread
import os
import random
import socket
import sys
import threading
import time
from concurrent import futures
from queue import Queue
from urllib.parse import urlparse

import requests

from config import NUM_CACHE_DOMAIN, NUM_CACHE_IP, MASSCAN_DEFAULT_PORT, MASSCAN_FULL_SCAN, IS_START_PLUGINS
from lib.common import is_ip_address_format, is_url_format
from lib.data import logger, PATHS, collector
from lib.loader import load_remote_poc, load_string_to_module
from lib.redis import task_update
from plugins import webeye, webtitle, crossdomain, gitleak, iis_parse, phpinfo, svnleak, tomcat_leak, whatcms, \
    ip_location, wappalyzer, directory_browse, password_found
from plugins.masscan import masscan
from plugins.nmap import nmapscan


class Schedular:

    def __init__(self, threadnum=1):

        self.queue = Queue()
        self.threadNum = threadnum
        self.lock = threading.Lock()
        self.ip_lock = threading.Lock()  # makesure only one ip process run
        self.cache_ips = []  # IP缓冲池
        self.cache_domains = []  # 域名缓冲池
        logger.info("Start number of threading {}".format(self.threadNum))

    def put_target(self, target):
        # 判断是IP还是域名，加入不同的字段
        serviceType = "domain"
        if is_ip_address_format(target):
            serviceType = "ip"
        elif is_url_format(target):
            serviceType = "domain"
            target = target.rstrip('/')
        else:
            serviceType = "other"

        tmp = {
            "target": target,
            "serviceType": serviceType
        }

        self.queue.put(tmp)
        task_update("tasks", self.queue.qsize())

    def put_struct(self, struct):
        self.queue.put(struct)

    def receive(self):
        while 1:
            struct = self.queue.get()

            task_update("tasks", self.queue.qsize())

            serviceType = struct.get("serviceType", 'other')
            if serviceType == "other":
                msg = "not matches target:{}".format(repr(struct))
                logger.error(msg)
                self.queue.task_done()
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
                    self.queue.task_done()
                    continue
                task_update("running", 1)
                try:
                    self.hand_ip(serviceTypes)
                except Exception as e:
                    logger.error("hand ip error:{}".format(repr(e)))
                    logger.error(repr(sys.exc_info()))
                task_update("running", -1)
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
                    self.queue.task_done()
                    continue
                # 多线程启动扫描域名
                for serviceType in serviceTypes:
                    task_update("running", 1)
                    try:
                        self.hand_domain(serviceType)
                    except Exception as e:
                        logger.error("hand domain error:{}".format(repr(e)))
                        logger.error(repr(sys.exc_info()))
                    task_update("running", -1)
            self.queue.task_done()
            task_update("tasks", self.queue.qsize())

    def start(self):
        for i in range(self.threadNum):
            _thread.start_new_thread(self.receive, ())

    def nmap_result_handle(self, result_nmap: dict, host):
        if result_nmap is None:
            return None
        result2 = {}
        for port, portInfo in result_nmap.items():
            if host not in result2:
                result2[host] = []
            if portInfo["state"] != "open":
                continue
            name = portInfo.get("name", "")
            # hand namp bug
            product = portInfo.get("product", "")
            version = portInfo.get("version", "")
            extrainfo = portInfo.get("extrainfo", "")
            if "http" in name and "https" not in name:
                if port == 443:
                    _url = "https://{0}:{1}".format(host, port)
                else:
                    _url = "http://{0}:{1}".format(host, port)
                self.put_target(_url)
            elif "https" in name:
                _url = "https://{0}:{1}".format(host, port)
                self.put_target(_url)
            result2[host].append(
                {"port": port, "name": name, "product": product, "version": version, "extrainfo": extrainfo})
        return result2

    def hand_ip(self, serviceTypes, option='masscan'):
        IP_LIST = []

        for item in serviceTypes:
            IP_LIST.append(item["target"])
        ports = MASSCAN_DEFAULT_PORT
        result2 = {}
        if option == 'masscan':
            if MASSCAN_FULL_SCAN:
                ports = "1-65535"
            target = os.path.join(PATHS.OUTPUT_PATH, "target_{0}.log".format(time.time()))
            with open(target, "w+") as fp:
                fp.write('\n'.join(IP_LIST))

            logger.debug("ip:" + repr(IP_LIST))
            self.ip_lock.acquire()
            try:
                result = masscan(target, ports)
            except Exception as e:
                logger.error("masscan error msg:{}".format(repr(e)))
                result = None
            self.ip_lock.release()
            if result is None:
                return None
            # format:{'115.159.39.75': ['80'], '115.159.39.215': ['80', '3306'],}
            for host, ports in result.items():
                ports = list(ports)
                if host not in result2:
                    result2[host] = []
                task_update("running", 1)
                try:
                    result_nmap = nmapscan(host, ports)
                except:
                    result_nmap = None
                task_update("running", -1)
                if result_nmap is None:
                    for tmp_port in ports:
                        result2[host].append({"port": tmp_port})
                    continue
                tmp_r = self.nmap_result_handle(result_nmap, host=host)
                result2.update(tmp_r)
        elif option == "nmap":
            logger.debug("ip:" + repr(IP_LIST))
            for host in IP_LIST:
                result_nmap = nmapscan(host, ports.split(","))
                tmp_r = self.nmap_result_handle(result_nmap, host=host)
                if tmp_r:
                    result2.update(tmp_r)

        data = {}
        for ip in result2.keys():
            # result2[ip]
            if ip not in data:
                data[ip] = {}
            d = ip_location.poc(ip)
            if d:
                data[ip]["location"] = d
            data[ip]["infos"] = result2[ip]

        collector.add_ips(data)
        for ip in result2.keys():
            collector.send_ok_ip(ip)

    def hand_domain(self, serviceType):
        target = serviceType["target"]
        logger.info(target)
        # 添加这条记录
        collector.add_domain(target)
        # 发起请求
        try:
            r = requests.get(target, timeout=30, verify=False, allow_redirects=False)
            collector.add_domain_info(target,
                                      {"headers": r.headers, "body": r.text, "status_code": r.status_code})
        except Exception as e:
            logger.error("request url error:" + str(e))
            collector.del_domain(target)
            return
        logger.debug("target:{} over,start to scan".format(target))

        # Get hostname
        hostname = urlparse(target).netloc.split(":")[0]
        if not is_ip_address_format(hostname):
            try:
                _ip = socket.gethostbyname(hostname)
                collector.add_domain_info(target, {"ip": _ip})
            except:
                pass
        else:
            collector.add_domain_info(target, {"ip": hostname})

        work_list = [webeye.poc, webtitle.poc, wappalyzer.poc, password_found.poc]

        if IS_START_PLUGINS:
            work_list.append(crossdomain.poc)
            work_list.append(directory_browse.poc)
            work_list.append(gitleak.poc)
            work_list.append(iis_parse.poc)
            work_list.append(phpinfo.poc)
            work_list.append(svnleak.poc)
            work_list.append(tomcat_leak.poc)
            work_list.append(whatcms.poc)

        # WorkList.append(bakfile.poc) # 去除备份文件扫描模块，原因：太费时

        # th = []
        # try:
        #     for func in work_list:
        #         i = threading.Thread(target=func, args=(target,))
        #         i.start()
        #         th.append(i)
        #     for thi in th:
        #         thi.join()
        # except Exception as e:
        #     logger.error("domain plugin threading error {}:{}".format(repr(Exception), str(e)))
        for func in work_list:
            try:
                func(target)
            except Exception as e:
                logger.error("domain plugin threading error {}:{}".format(repr(Exception), str(e)))

        logger.debug("target:{} End of scan".format(target))
        infos = collector.get_domain(target)
        _pocs = []
        temp = {}
        if IS_START_PLUGINS and "CMS" in infos:
            if infos.get("app"):
                temp["app"] = []
                temp["app"].append(infos["CMS"])
            else:
                temp["app"] = [infos["CMS"]]
            # update domain app
            collector.add_domain_info(target, temp)

        if temp.get("app"):
            keywords = temp["app"]
            # 远程读取插件
            pocs = load_remote_poc()

            for poc in pocs:
                for keyword in keywords:
                    if poc["name"] == keyword:
                        webfile = poc["webfile"]
                        logger.debug("load {0} poc:{1} poc_time:{2}".format(poc["type"], webfile, poc["time"]))
                        # 加载插件
                        code = requests.get(webfile).text
                        obj = load_string_to_module(code, webfile)
                        _pocs.append(obj)

        # 并发执行插件
        if _pocs:
            executor = futures.ThreadPoolExecutor(len(_pocs))
            fs = []
            for f in _pocs:
                taks = executor.submit(f.poc, target)
                fs.append(taks)
            for f in futures.as_completed(fs):
                try:
                    res = f.result()
                except Exception as e:
                    res = None
                    logger.error("load poc error:{} error:{}".format(target, str(e)))
                if res:
                    name = res.get("name") or "scan_" + str(time.time())
                    collector.add_domain_bug(target, {name: res})

        collector.send_ok(target)

    def run(self):
        while 1:
            if self.queue.qsize() > 0:
                time.sleep(random.randint(1, 15))
                continue
            logger.debug("run...")
            # 对剩余未处理的域名进行处理
            if self.cache_domains:
                self.lock.acquire()
                service_types = self.cache_domains
                self.cache_domains = []
                self.lock.release()

                # 多线程启动扫描域名
                for serviceType in service_types:
                    task_update("running", 1)
                    try:
                        self.hand_domain(serviceType)
                    except Exception as e:
                        logger.error(repr(sys.exc_info()))
                    task_update("running", -1)

            # 对剩余未处理的ip进行处理
            if self.cache_ips:
                self.lock.acquire()
                service_types = self.cache_ips
                self.cache_ips = []
                self.lock.release()

                task_update("running", 1)
                try:
                    self.hand_ip(service_types)
                except Exception as e:
                    logger.error(repr(sys.exc_info()))
                task_update("running", -1)

            # 最后一次提交
            collector.submit()
            task_update("tasks", self.queue.qsize())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/14 4:44 PM
# @Author  : w8ay
# @File    : log.py

import logging
import threading
from config import LOGGER_LEVEL

from thirdpart.ansistrm import ColorizingStreamHandler

DEBUG, INFO, WARN, ERROR, SUCCESS = range(1, 6)
logging.addLevelName(DEBUG, '^')
logging.addLevelName(INFO, '*')
logging.addLevelName(WARN, '!')
logging.addLevelName(ERROR, 'x')
logging.addLevelName(SUCCESS, '+')

logger = logging.getLogger("w12scan")

handle = ColorizingStreamHandler()
handle.level_map[logging.getLevelName('^')] = (None, 'white', False)
handle.level_map[logging.getLevelName('*')] = (None, 'cyan', False)
handle.level_map[logging.getLevelName('+')] = (None, 'green', False)
handle.level_map[logging.getLevelName('x')] = (None, 'red', False)
handle.level_map[logging.getLevelName('!')] = (None, 'yellow', False)

logger.setLevel(LOGGER_LEVEL)

formatter = logging.Formatter(fmt='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y/%m/%d %H:%M:%S')
handle.setFormatter(formatter)
logger.addHandler(handle)


class LOGGER:
    def __init__(self):
        self.lock = threading.Lock()

    def info(self, msg):
        self.lock.acquire()
        logger.log(INFO, msg)
        self.lock.release()

    def warning(self, msg):
        self.lock.acquire()
        logger.log(WARN, msg)
        self.lock.release()

    def error(self, msg):
        self.lock.acquire()
        logger.log(ERROR, msg)
        self.lock.release()

    def success(self, msg):
        self.lock.acquire()
        logger.log(SUCCESS, msg)
        self.lock.release()

    def debug(self, msg):
        self.lock.acquire()
        logger.log(DEBUG, msg)
        self.lock.release()

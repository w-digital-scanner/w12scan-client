#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/14 5:26 PM
# @Author  : w8ay
# @File    : data.py
from lib.collector import Collector
from lib.log import LOGGER

logger = LOGGER()


class PATHS:
    ROOT_PATH = ''
    PLUGIN_PATH = ''
    OUTPUT_PATH = ''
    DATA_PATH = ''


collector = Collector()

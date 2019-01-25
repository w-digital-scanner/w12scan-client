#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/1/26 12:00 AM
# @Author  : w8ay
# @File    : loader.py
import importlib
import os
from importlib.abc import Loader

import requests
from config import WEB_REPOSITORY
import json

from lib.common import get_md5, get_filename
from lib.data import PATHS, logger


def load_remote_poc():
    filename = os.path.join(PATHS.DATA_PATH, "api.json")
    if os.path.exists(filename):
        with open(filename) as f:
            datas = json.load(f)
        return datas
    _middle = "/master"
    _suffix = "/API.json"
    _profix = WEB_REPOSITORY.replace("github.com", "raw.githubusercontent.com")
    _api = _profix + _middle + _suffix
    r = requests.get(_api)
    datas = json.loads(r.text, encoding='utf-8')
    for data in datas:
        data["webfile"] = _profix + _middle + data["filepath"]
    with open(filename, "w") as f:
        json.dump(datas, f)

    return datas


def load_file_to_module(file_path):
    if '' not in importlib.machinery.SOURCE_SUFFIXES:
        importlib.machinery.SOURCE_SUFFIXES.append('')
    try:
        module_name = 'pocs_{0}'.format(get_filename(file_path, with_ext=False))
        spec = importlib.util.spec_from_file_location(module_name, file_path, loader=PocLoader(module_name, file_path))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    except ImportError:
        error_msg = "load module failed! '{}'".format(file_path)
        logger.error(error_msg)
        raise


def load_string_to_module(code_string, fullname=None):
    try:
        module_name = 'pocs_{0}'.format(get_md5(code_string)) if fullname is None else fullname
        file_path = 'w12scan://{0}'.format(module_name)
        poc_loader = PocLoader(module_name, file_path)
        poc_loader.set_data(code_string)
        spec = importlib.util.spec_from_file_location(module_name, file_path, loader=poc_loader)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    except ImportError:
        error_msg = "load module '{0}' failed!".format(fullname)
        logger.error(error_msg)
        raise


class PocLoader(Loader):
    def __init__(self, fullname, path):
        self.fullname = fullname
        self.path = path
        self.data = None

    def set_data(self, data):
        self.data = data

    def get_filename(self, fullname):
        return self.path

    def get_data(self, filename):
        if filename.startswith('w12scan://') and self.data:
            data = self.data
        else:
            with open(filename, encoding='utf-8') as f:
                data = f.read()
        return data

    def exec_module(self, module):
        filename = self.get_filename(self.fullname)
        poc_code = self.get_data(filename)
        obj = compile(poc_code, filename, 'exec', dont_inherit=True, optimize=-1)
        exec(obj, module.__dict__)

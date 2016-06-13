#!/usr/bin/env python
# encoding: utf-8

"""
@author: zhanghe
@software: PyCharm
@file: views.py
@time: 16-6-6 下午1:07
"""


import json
from lib.taobao_item_list import get_item_list
from app import app


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/item_list/<key>/')
def item_list(key):
    """
    获取关键词查询结果
    http://127.0.0.1:5000/item_list/连衣裙/
    100 kb
    300 ms
    """
    result = get_item_list(key)
    return json.dumps(result, indent=4, ensure_ascii=False)

#!/usr/bin/env python
# encoding: utf-8

"""
@author: zhanghe
@software: PyCharm
@file: taobao_item_list.py
@time: 16-6-6 上午8:51
"""


import requests
import json
import re

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
    }

s = requests.session()


def get_item_list(key=''):
    """
    获取物品列表
    性能测试：
    $ python -m cProfile app/lib/taobao_item_list.py
    59934 function calls (58975 primitive calls) in 0.375 seconds
    """
    result = {}
    url = 'https://s.taobao.com/search?q=%s' % key
    response = s.get(url, headers=header)
    html = response.text
    # print html
    item_list_rule = re.compile('g_page_config = (.*);', re.I)
    g_page_configs = item_list_rule.findall(html)
    # print g_page_configs
    page_configs_result = json.loads(g_page_configs[0]) if g_page_configs else None
    if page_configs_result:
        result['item_list'] = page_configs_result['mods']['itemlist']['data']['auctions']
        result['page_info'] = page_configs_result['mods']['pager']['data']
    # print json.dumps(result, indent=4, ensure_ascii=False)
    return result

if __name__ == '__main__':
    get_item_list('连衣裙')

"""
Created on Wed Feb  6 14:20:25 2019
利用百度新闻爬虫，统计包含地区和关键词的数据的新闻页面的数量
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import urllib.parse as parse
import json
import os
from search_by_baidu import *
from multiprocessing import Pool

import numpy as np

keywords = ['EB级存储', 'NFC支付', '云计算', '互联网金融', '人工智能', '亿级并发', '信息物理系统', '内存计算',
            '分布式计算', '区块链', '商业智能', '图像理解', '图计算', '多方安全计算', '大数据', '差分隐私技术',
            '开放银行', '异构数据', '征信', '投资决策辅助系统', '数字货币', '数据可视化', '数据挖掘', '文本挖掘',
            '智能客服', '智能投顾', '智能数据分析', '智能金融合约', '机器学习', '流计算', '深度学习', '物联网',
            '生物识别技术', '移动互联', '移动支付', '第三方支付', '类脑计算', '绿色计算', '网联', '股权众筹融资',
            '自然语言处理', '虚拟现实', '融合架构', '认知计算', '语义搜索', '语音识别', '身份验证', '量化金融']
# keywords = ['EB级存储', 'NFC支付']



# def test_search():
#     stime = '20110101'
#     etime = '20221231'
#     q = parse.quote('云计算 崂山区')
#
#     url = 'https://www.chinaso.com/v5/general/v1/web/search?q={q}&pn=1&ps=15&stime=20110101&etime=20221231'.format(q=q)
#     # url = ('https://www.chinaso.com/newssearch/all/allResults?q={'
#     #                'q}&pn=1&source=&order=&stime={st}&etime={et}').format(q=q, st=stime, et=etime)
#     res = search(url)
#     print(res)


# 从百度搜索关键词，统计搜索结果条数

def search(kw='', site='chinaso'):
    # 从百度搜索
    if site == 'baidu':
        return search_by_baidu(kw)

    # 从chinaso搜索
    stime = '20110101'
    etime = '20221231'
    url = ('https://www.chinaso.com/v5/general/v1/web/search?q={'
           'q}&pn=1&source=&order=&stime={st}&etime={et}').format(q=kw, st=stime, et=etime)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.76',
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip, deflate, br",
        "Host": "www.chinaso.com",
        "Cookie": 'uid=CgqATmT9yQ5wZ3xXD2XUAg==; cookie_name=223.99.13.248.1694353681106871; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2218a7f59628ab41-0e0c6aa9ca36a6-7f5d547e-2073600-18a7f59628b1741%22%2C%22%24device_id%22%3A%2218a7f59628ab41-0e0c6aa9ca36a6-7f5d547e-2073600-18a7f59628b1741%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E8%87%AA%E7%84%B6%E6%90%9C%E7%B4%A2%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fwww.baidu.com%2Flink%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfYW5vbnltb3VzX2lkIjoiMThhN2Y1OTYyOGFiNDEtMGUwYzZhYTljYTM2YTYtN2Y1ZDU0N2UtMjA3MzYwMC0xOGE3ZjU5NjI4YjE3NDEiLCIkaWRlbnRpdHlfY29va2llX2lkIjoiMThhODIwODA2MWZkNjUtMDMxMWZmNGMzM2Y4ZmEtN2Y1ZDU0N2UtMjA3MzYwMC0xOGE4MjA4MDYyMDE4MGUifQ%3D%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%7D'
    }
    res = requests.get(url, headers=headers)
    res.encoding = 'utf-8'
    res = json.loads(res.text)
    if res['msg'] == 'empty result':
        return 0
    return res['data']['display_result_count']


def statistic(pca):
    pca_data_raw = pd.read_csv(f'{pca}.csv', header=None)
    pca_data_raw.fillna(value='', inplace=True)
    pca_data_raw.columns = ['ch', 'p', 'c', 'a', 'k1', 'k2']
    pca_data_raw['f'] = pca_data_raw['c'] + pca_data_raw['a']
    pca_data = pca_data_raw[['p', 'f', 'a']]
    pca_data_list = pca_data.values.tolist()

    if os.path.exists(f'{pca}_save.csv'):
        pca_df = pd.read_csv(f'{pca}_save.csv')
    else:
        pca_df = pd.DataFrame(columns=keywords)
        pca_df = pd.concat([pca_data, pca_df], axis=1)
    for district in pca_data_list:
        if district[2] == '':
            print('开始统计', district[1])
            continue
        if not pd.isnull(pca_df.loc[pca_df['f'] == district[1]]['EB级存储']).all():
            print(district[1], '已经统计过了')
            continue
        start = time.perf_counter()
        for kw in keywords:
            # if not pd.isnull(pca_df.loc[pca_df['f'] == district[1], kw]).all():
            #     # print(district[1], '已经统计过了')
            #     break
            q = parse.quote(f'"{district[1]}" "{kw}"')

            num = search(kw=q, site='baidu')

            pca_df.loc[pca_df['f'] == district[1], kw] = num
            # print(district[1], kw, '总数：', num)
            # time.sleep(1)
        end = time.perf_counter()
        print('统计', district[1], '耗时：', end - start)

        pca_df.to_csv(f'{pca}_save.csv', index=False, encoding='utf-8-sig')

    pca_df.astype('int', errors='ignore')
    pca_df.to_csv(f'{pca}_save.csv', index=False, encoding='utf-8-sig')


if __name__ == '__main__':
    # pca_file = ['pca1', 'pca2', 'pca3', 'pca4']
    # pool = Pool(processes=4)
    # pool.map(statistic, pca_file)
    # pool.close()
    # pool.join()

    statistic('pca')
# 使用pandas进行数据处理，每一次有新的数据就写入数据表，应该怎么写

"""
百度指数数据获取最佳实践
此脚本完成
1. 清洗关键词
2. 发更少请求获取更多的数据
3. 请求容错
4. 容错后并保留当前已经请求过的数据，并print已请求过的keywords
"""
from queue import Queue
from typing import Dict, List
import traceback
import time
from multiprocessing import Pool
import pandas as pd
# from qdata.baidu_index.baidu_index import get_search_index
from baidu_index import get_search_index
from qdata.baidu_index.common import check_keywords_exists, split_keywords
from city import *
import os
from cookie_pool import cookies

# from qdata.baidu_index.config import PROVINCE_CODE, CITY_CODE
city_file = [CITY_CODE_1, CITY_CODE_2, CITY_CODE_3, CITY_CODE_4]

keywords_list = [
    ['大数据'], ['云计算'], ['人工智能'], ['区块链'], ['生物识别'], ['在线支付'], ['移动支付'], ['第三方支付'],
    ['网贷'], ['网上融资'], ['网络融资'], ['网络小额贷款'], ['网络贷款'], ['网银'], ['网络银行'], ['电子银行'],
    ['在线银行'], ['开放银行'], ['互联网银行'], ['直销银行'], ['互联网金融'], ['金融科技'], ['数字金融'],
    ['EB级存储'], ['NFC支付'], ['亿级并发'], ['信息物理系统'], ['内存计算'], ['分布式计算'], ['商业智能'],
    ['图像理解'], ['图计算'], ['多方安全计算'], ['差分隐私技术'], ['异构数据'], ['征信'], ['投资决策辅助系统'],
    ['数字货币'], ['数据可视化'], ['数据挖掘'], ['文本挖掘'], ['智能客服'], ['智能投顾'], ['智能数据分析'],
    ['智能金融合约'], ['机器学习'], ['流计算'], ['深度学习'], ['物联网'], ['生物识别技术'], ['移动互联'],
    ['类脑计算'], ['绿色计算'], ['网联'], ['股权众筹融资 自然语言处理'], ['虚拟现实'], ['融合架构'], ['认知计算'],
    ['语义搜索'], ['语音识别'], ['身份验证'], ['量化金融']
]

clear_keywords_list = [['大数据'], ['云计算'], ['人工智能'], ['区块链'], ['生物识别'], ['在线支付'], ['移动支付'],
                       ['第三方支付'], ['网贷'], ['网络贷款'], ['网银'], ['网络银行'], ['电子银行'], ['互联网银行'],
                       ['直销银行'], ['互联网金融'], ['金融科技'], ['EB级存储'], ['NFC支付'], ['商业智能'], ['征信'],
                       ['数字货币'], ['数据可视化'], ['数据挖掘'], ['智能客服'], ['智能投顾'], ['机器学习'], ['流计算'],
                       ['深度学习'], ['物联网'], ['移动互联'], ['网联'], ['虚拟现实'], ['语音识别']]


def get_clear_keywords_list(keywords_list: List[List[str]]) -> List[List[str]]:
    q = Queue(-1)

    cur_keywords_list = []
    for keywords in keywords_list:
        cur_keywords_list.extend(keywords)

    # 先找到所有未收录的关键词
    for start in range(0, len(cur_keywords_list), 15):
        q.put(cur_keywords_list[start:start + 15])

    not_exist_keyword_set = set()
    while not q.empty():
        keywords = q.get()
        try:
            check_result = check_keywords_exists(keywords, cookies)
            time.sleep(5)
        except:
            traceback.print_exc()
            q.put(keywords)
            time.sleep(90)

        for keyword in check_result["not_exists_keywords"]:
            not_exist_keyword_set.add(keyword)

    # 在原有的keywords_list拎出没有收录的关键词
    new_keywords_list = []
    for keywords in keywords_list:
        not_exists_count = len([None for keyword in keywords if keyword in not_exist_keyword_set])
        if not_exists_count == 0:
            new_keywords_list.append(keywords)

    return new_keywords_list


# def save_to_excel(datas: List[Dict]):
#     pd.DataFrame(datas).to_excel("index.xlsx")


def get_search_index_demo(pool_id: int):
    """
        1. 先清洗keywords数据，把没有收录的关键词拎出来
        2. 然后split_keywords关键词正常请求
        3. 数据存入excel
    """
    print("开始清洗关键词")
    requested_keywords = []
    # keywords_lists = get_clear_keywords_list(keywords_list)
    # print(keywords_lists)
    q = Queue(-1)
    print("开始请求百度指数")

    CITY_CODE = city_file[pool_id]
    years = range(2011, 2023)
    # 检测之前是否已经爬过
    if os.path.exists(f"./res/index_{pool_id}.csv"):
        datas = pd.read_csv(f"./res/index_{pool_id}.csv")
    else:
        datas = pd.DataFrame()
        datas["City"] = None
        datas["Year"] = None
        for kw in keywords_list:
            datas["(pc+wise)-"+kw[0]] = None
            datas["(pc)-"+kw[0]] = None
            datas["(wise)-" + kw[0]] = None
        for city in CITY_CODE.keys():
            for year in years:
                index_row = pd.Series([city, year], index=['City', 'Year'])
                datas.loc[len(datas)] = index_row
        datas.to_csv(f"./res/index_{pool_id}.csv", index=False)

    for col, row in datas.iterrows():
        # 如果都统计过了就开始下一行。
        if not row.isnull().any():
            continue
        for splited_keywords_list in split_keywords(clear_keywords_list):
            q.put(splited_keywords_list)
        city, year = row['City'], row['Year']

        while not q.empty():
            cur_keywords_list = q.get()
            try:
                print(f"{year}==={city}===开始请求: {cur_keywords_list}")
                # 尝试按照队列请求index
                for index in get_search_index(
                        keywords_list=cur_keywords_list,
                        start_date=str(year) + '-01-01',
                        end_date=str(year) + '-12-31',
                        cookies=cookies[pool_id],
                        area=CITY_CODE[city],
                ):
                    index["keyword"] = ",".join(index["keyword"])
                    datas.at[col, "(pc+wise)-"+index["keyword"]] = index['all']
                    datas.at[col, "(pc)-"+index["keyword"]] = index['pc']
                    datas.at[col, "(wise)-"+index["keyword"]] = index['wise']

                requested_keywords.extend(cur_keywords_list)
                print(f"请求完成: {cur_keywords_list}")
                time.sleep(15)
            except:
                print(f"请求出错, requested_keywords: {requested_keywords}")
                datas.to_csv(f"./res/index_{pool_id}.csv", index=False)
                q.put(cur_keywords_list)
                time.sleep(120)
        row.fillna(0, inplace=True)
        print(f'{year}==={city}===爬取结果保存')
        datas.to_csv(f"./res/index_{pool_id}.csv", index=False)


if __name__ == "__main__":
    # keywords_list = [
    #     ['大数据'], ['云计算'], ['人工智能']
    # ]
    # loopNum = range(1)
    # pool = Pool(processes=1)
    # pool.map(get_search_index_demo, loopNum)
    # pool.close()
    # pool.join()
    get_search_index_demo(0)

from typing import List, Dict
import datetime
import json

from qdata.baidu_index import common
from qdata.errors import QdataError, ErrorCode

# ALL_KIND = ['all', 'pc', 'wise']
ALL_KIND = ['all']


def get_search_index(
    *,
    keywords_list: List[List[str]],
    start_date: str,
    end_date: str,
    cookies: str,
    area: int = 0
):
    if len(keywords_list) > 5:
        raise QdataError(ErrorCode.KEYWORD_LIMITED)
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    encrypt_json = common.get_encrypt_json(
        start_date=start_date,
        end_date=end_date,
        keywords=keywords_list,
        type='search',
        area=area,
        cookies=cookies
    )
    encrypt_datas = encrypt_json['data']['generalRatio']

    for encrypt_data in encrypt_datas:
        encrypt_data['year'] = start_date.year
        for formatted_data in format_data(encrypt_data):
            yield formatted_data



def format_data(data: Dict):
    """
        格式化堆在一起的数据
    """
    keyword = str(data['word'])


    index_all_data = data['all']['avg']
    index_pc_data = data['pc']['avg']
    index_wise_data = data['wise']['avg']
    formatted_data = {
        'keyword': [keyword_info['name'] for keyword_info in json.loads(keyword.replace('\'', '"'))],
        'all': index_all_data if index_all_data else '0',
        'pc': index_pc_data if index_pc_data else '0',
        'wise': index_wise_data if index_wise_data else '0',
    }

    yield formatted_data

def decrypt_func(kw, kind, encrypt_data):
    """
        选择kw为word的数据的三条属性
    """
    kw_data = [d for d in encrypt_data if 'word' in d and d['word'][0]['name'] == kw]

    if kind in kw_data[0]:
        return kw_data[0][kind]
    else:
        raise QdataError(ErrorCode.KIND_ERROR)



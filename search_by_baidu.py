import requests
from bs4 import BeautifulSoup
import re
import urllib.parse as parse
import time

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'AES256'
try:
    requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += 'AES256'
except AttributeError:
    # no pyopenssl support used / needed / available
    pass


def search_by_baidu(keyword):
    url = f'https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&rsv_dl=ns_pc&word={keyword}'

    cookie = 'BIDUPSID=D0E1ABB3ED6A8FF9B4406674A01A2B94; PSTM=1600161654; BAIDUID=300113ABFE398BED6ECBDF202A47AC44:FG=1; BDUSS=01zQjktTTdkZ0FRdVNBSXBPMWtpQ2JFOWVUMlotQjBTWWxIYWRYejRKYWRYRDlrRUFBQUFBJCQAAAAAAAAAAAEAAACeeTs21-6wrk9LMTIzQQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJ3PF2Sdzxdkd; BDUSS_BFESS=01zQjktTTdkZ0FRdVNBSXBPMWtpQ2JFOWVUMlotQjBTWWxIYWRYejRKYWRYRDlrRUFBQUFBJCQAAAAAAAAAAAEAAACeeTs21-6wrk9LMTIzQQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJ3PF2Sdzxdkd; BD_UPN=12314753; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BDSFRCVID=KfLOJeC62lTcJrrfpo0PuYurwDpGWe6TH6_nIIOOlhfTAs0Dv8DgEG0PgU8g0KAb6jXGogKKymOTHrAF_2uxOjjg8UtVJeC6EG0Ptf8g0x5; H_BDCLCKID_SF=tbC8VCDatCL3fn5kMn__-4_tbh_X5-RLf23h2p7F5l8-hRR2-U6KK4KQhN3T-lct-jvRQp365CQxOKQ3hxrzXU4jMMjn3Rtj3TFOKn3N3KJmeUK9bT3vLtjBMR7x2-biW55L2Mbd-qjP_IoG2Mn8M4bb3qOpBtQmJeTxoUJ25DnJh-PGe4bK-TrLDHt8tUK; BDSFRCVID_BFESS=KfLOJeC62lTcJrrfpo0PuYurwDpGWe6TH6_nIIOOlhfTAs0Dv8DgEG0PgU8g0KAb6jXGogKKymOTHrAF_2uxOjjg8UtVJeC6EG0Ptf8g0x5; H_BDCLCKID_SF_BFESS=tbC8VCDatCL3fn5kMn__-4_tbh_X5-RLf23h2p7F5l8-hRR2-U6KK4KQhN3T-lct-jvRQp365CQxOKQ3hxrzXU4jMMjn3Rtj3TFOKn3N3KJmeUK9bT3vLtjBMR7x2-biW55L2Mbd-qjP_IoG2Mn8M4bb3qOpBtQmJeTxoUJ25DnJh-PGe4bK-TrLDHt8tUK; BAIDUID_BFESS=300113ABFE398BED6ECBDF202A47AC44:FG=1; BD_CK_SAM=1; delPer=0; BA_HECTOR=0h0la5048l0g2184a5848h2u1ifst4j1o; ZFY=hnhqzI4Goixop0rUFt93gwZCLG:ATZY7OZNE10z0VE:AA:C; BDRCVFR[C0p6oIjvx-c]=rJZwba6_rOCfAF9pywd; BDRCVFR[gUg2cUtcsBT]=_M5urk4djP3fA4-ILn; BDRCVFR[fBLL8ZbbiMm]=e-qmLS9UcYYf7P7gv9_uZ0sn163n7q3; RT="z=1&dm=baidu.com&si=1b88bd8e-dd6a-4fa9-b872-63cce10b70e6&ss=lmdh4rmb&sl=0&tt=0&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ld=mil&ul=13pcdu&hd=13pcj1"; COOKIE_SESSION=665_0_12_2_105_10_1_0_2_10_0_10_174_0_844_0_1694353046_0_1694352202%7C9%2356612530_5_1656778143%7C2; ZD_ENTRY=bing; ab_sr=1.0.1_ZTQ3MTIwM2M5NzczNDI2NzIyNGQ0NzY0NzgzZjcyZDc5ODc4MzVmMTg1NDE2NTc2NTVjOGQzNDgyMTg3ZjZmYTJmMDQ4YmYzYjE2NjhkYjZkZWRmYzM0MTMyNzUxZjcyOTM2MTA0ZWU1NWE5YTcwZTI0YzdiM2JjOTkyMzBiOWEyMWNhYjM3NjA4OTlhM2Y3Yjc0NTVmNDQyYmU2N2JmOQ==; kleck=d306c773d739873bd4e37ace9139559d; PSINO=5; H_PS_PSSID=39314_39223_39350_39097_39198_39294_39261_39359_39240_39233_26350_39238_39149; sugstore=1; H_PS_645EC=d28baLcLxMquMKVoRQ34uLxLxy5WEchYZyI3vu8QW4pj%2BByqymZePG6NbbI; BDSVRTM=0; B64_BOT=1'
    Referer = 'https://news.baidu.com/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.76',
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip, deflate, br",
        "Host": "www.baidu.com",
        "Cookie": cookie,
        'Referer': Referer,
    }

    while True:  # 相当于一直请求，直到成功后break
        try:
            # 能运行到这一步说明请求成功，可以跳出循环了
            res = requests.get(url=url, headers=headers)
            res.close()
            soup = BeautifulSoup(res.text, 'html.parser')
            retext=soup.find(class_='nums c-color-gray2')
            num=re.match(r'<span class="nums c-color-gray2">百度为您找到相关资讯(.*)个</span>',str(retext))
            # print(url, num.group(1))
            break
        except:
            time.sleep(10)  # 暂停1秒，之后回到while True继续请求
            print('---------sleep----------')
            # print(num.group(1))

    return num.group(1)
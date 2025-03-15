from lxml import etree

from duckduckgo_search import DDGS
import requests
from src.config import Config

import re
from urllib.parse import unquote
from html import unescape
import orjson


class BingSearch:
    def __init__(self):
        self.config = Config()
        self.bing_api_key = self.config.get_bing_api_key()
        self.bing_api_endpoint = self.config.get_bing_api_endpoint()
        self.query_result = None

    def search(self, query):
        headers = {"Ocp-Apim-Subscription-Key": self.bing_api_key}
        params = {"q": query, "mkt": "en-US"}

        try:
            response = requests.get(self.bing_api_endpoint, headers=headers, params=params)
            response.raise_for_status()
            self.query_result = response.json()
            return self.query_result
        except Exception as error:
            return error

    def get_first_link(self):
        return self.query_result["webPages"]["value"][0]["url"]


class GoogleSearch:
    def __init__(self):
        self.config = Config()
        self.google_search_api_key = self.config.get_google_search_api_key()
        self.google_search_engine_ID = self.config.get_google_search_engine_id()
        self.google_search_api_endpoint = self.config.get_google_search_api_endpoint()
        self.query_result = None

    def search(self, query):
        params = {
            "key": self.google_search_api_key,
            "cx": self.google_search_engine_ID,
            "q": query
        }
        try:
            print("Searching in Google...")
            response = requests.get(self.google_search_api_endpoint, params=params)
            # response.raise_for_status()
            self.query_result = response.json()
        except Exception as error:
            return error

    def get_first_link(self):
        item = ""
        try:
            if 'items' in self.query_result:
                item = self.query_result['items'][0]['link']
            return item
        except Exception as error:
            print(error)
            return ""


# class DuckDuckGoSearch:
#     def __init__(self):
#         self.query_result = None
#
#     def search(self, query):
#         from duckduckgo_search import DDGS
#         try:
#             self.query_result = DDGS().text(query, max_results=5, region="us")
#             print(self.query_result)
#
#         except Exception as err:
#             print(err)
#
#     def get_first_link(self):
#         if self.query_result:
#             return self.query_result[0]["href"]
#         else:
#             return None
#


class DuckDuckGoSearch:
    """DuckDuckGo search engine class.
    methods are inherited from the duckduckgo_search package.
    do not change the methods.

    currently, the package is not working with our current setup.
    """

    def __init__(self):
        from curl_cffi import requests as curl_requests
        self.query_result = None
        self.asession = curl_requests.Session(impersonate="chrome", allow_redirects=False)
        self.asession.headers["Referer"] = "https://duckduckgo.com/"

    def _get_url(self, method, url, data):
        try:
            return None
        except Exception as error:
            if "timeout" in str(error).lower():
                raise TimeoutError("Duckduckgo timed out error")

    def duck(self, query):
        results = []
        with DDGS(timeout=20, proxies=None) as ddgs:
            for r in ddgs.text(keywords=query, max_results=3, backend="html"):
                # print(r)
                if r is not None:
                    r['content'] = get_html_content(r['href'])
                if r['content']:
                    results.append({
                        "title": self.normalize(r['title']),
                        "href": self.normalize_url(r['href']),
                        "body": r['content'],
                    })

        self.query_result = results

    def search(self, query):
        self.duck(query)

    def get_first_link(self):
        if len(self.query_result) > 0:
            return self.query_result[0]["href"]
        return ""

    @staticmethod
    def extract_vqd(html_bytes: bytes) -> str:
        patterns = [(b'vqd="', 5, b'"'), (b"vqd=", 4, b"&"), (b"vqd='", 5, b"'")]
        for start_pattern, offset, end_pattern in patterns:
            try:
                start = html_bytes.index(start_pattern) + offset
                end = html_bytes.index(end_pattern, start)
                return html_bytes[start:end].decode()
            except ValueError:
                continue

    @staticmethod
    def text_extract_json(html_bytes):
        try:
            start = html_bytes.index(b"DDG.pageLayout.load('d',") + 24
            end = html_bytes.index(b");DDG.duckbar.load(", start)
            return orjson.loads(html_bytes[start:end])
        except Exception as ex:
            print(f"Error extracting JSON: {type(ex).__name__}: {ex}")

    @staticmethod
    def normalize_url(url: str) -> str:
        return unquote(url.replace(" ", "+")) if url else ""

    @staticmethod
    def normalize(raw_html: str) -> str:
        return unescape(re.sub("<.*?>", "", raw_html)) if raw_html else ""


def get_html_content(url):
    # 发送HTTP请求获取网页源代码
    if url is None:
        return "url为空！"
    try:
        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'cookie': '__yjs_duid=1_b1ac9fc87dce4de5552d7cf0924fb4981686228951567; u=b0281776fd75d3eefeb3562b2a5e6534; '
                      '__bid_n=1889b14047a51b2b754207; '
                      'FPTOKEN=qU+ieOMqkW6y6DlsOZ+D/T'
                      '+SCY6yS3dYvGXKibFoGBijKuUuSbc3ACFDzjlcC18wuDjNLENrw4ktAFAqnl3Akg492Lr4fbvNrkdJ'
                      '/ZQrluIdklkNDAKYnPrpcbe2H9y7AtX+/b+FCTkSTNv5+qB3OtQQ3BXXsEen72oEoAfK+H6'
                      '/u6ltZPdyHttJBJiXEDDS3EiUVt+S2w+8ozXENWbNt/AHeCgNUMmdeDinAKCR+nQSGK/twOoTLOU/nxBeSAazg'
                      '+wu5K8ooRmW00Bk6XAqC4Cb829XR3UinZHRsJxt7q9biKzYQh'
                      '+Yu5s6EHypKwpA6RPtVAC1axxbxza0l5LJ5hX8IxJXDaQ6srFoEzQ92jM0rmDynp+gT'
                      '+3qNfEtB2PjkURvmRghGUn8wOcUUKPOqg==|mfg5DyAulnBuIm/fNO5JCrEm9g5yXrV1etiaV0jqQEw=|10'
                      '|dcfdbf664758c47995de31b90def5ca5; PHPSESSID=18397defd82b1b3ef009662dc77fe210; '
                      'Hm_lvt_de3f6fd28ec4ac19170f18e2a8777593=1686322028,1686360205; '
                      'history=cid%3A2455%2Ccid%3A2476%2Ccid%3A5474%2Ccid%3A5475%2Ccid%3A2814%2Cbid%3A3667; '
                      'Hm_lpvt_de3f6fd28ec4ac19170f18e2a8777593=1686360427'}
        response = requests.get(url, header)
        response.encoding = response.apparent_encoding
        html_content = response.text

        # 使用lxml解析网页源代码
        tree = etree.HTML(html_content)

        # 使用XPath选择器提取纯文本内容
        # 这里假设要提取的内容位于<p>标签内，你可以根据实际情况调整XPath表达式
        content = get_text(tree, url, '//p/text()')

        if (len(content) == 0):
            content = get_text(tree, url, '//body/text()')
        return content
    except BaseException as e:
        print(e)
        return None


def get_text(tree, url, regex):
    paragraphs = tree.xpath(regex)
    content = []
    # 打印提取的文本内容
    for paragraph in paragraphs:
        content.append(paragraph)
    return content

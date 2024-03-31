from itertools import islice

import re
from urllib.parse import unquote
from html import unescape
from curl_cffi import requests as curl_requests
import orjson

# class DuckDuckGoSearch1:
#     def __init__(self):
#         self.query_result = None
#         from curl_cffi import requests as curl_requests
#         self.asession = curl_requests.Session(
#             impersonate="chrome",
#             allow_redirects=False,
#         )
#         self.asession.headers["Referer"] = "https://duckduckgo.com/"
#
#     def extract_vqd(self, html_bytes: bytes) -> str:
#         """Extract vqd from html bytes."""
#         for c1, c1_len, c2 in (
#                 (b'vqd="', 5, b'"'),
#                 (b"vqd=", 4, b"&"),
#                 (b"vqd='", 5, b"'"),
#         ):
#             try:
#                 start = html_bytes.index(c1) + c1_len
#                 end = html_bytes.index(c2, start)
#                 return html_bytes[start:end].decode()
#             except ValueError:
#                 pass
#
#     def text_extract_json(self, html_bytes, keywords):
#         """text(backend="api") -> extract json from html."""
#         try:
#             import orjson
#             start = html_bytes.index(b"DDG.pageLayout.load('d',") + 24
#             end = html_bytes.index(b");DDG.duckbar.load(", start)
#             data = html_bytes[start:end]
#             result = orjson.loads(data)
#             return result
#         except Exception as ex:
#             print(f"_text_extract_json() {keywords=} {type(ex).__name__}: {ex}")
#
#     def duck(self, query):
#         resp = self.asession.request("POST", "https://duckduckgo.com/", data={"q": query})
#         resp_content = resp.content
#         vqd = self.extract_vqd(resp_content)
#
#         payload = {
#             "q": query,
#             "kl": 'en-us',
#             "p": "1",
#             "s": "0",
#             "df": "",
#             "vqd": vqd,
#             "ex": "",
#         }
#
#         resp1 = self.asession.request("GET", "https://links.duckduckgo.com/d.js", params=payload)
#         resp_content1 = resp1.content
#         page_data = self.text_extract_json(resp_content1, query)
#         priority = 0
#
#         results = [None] * 1100
#
#         for row in page_data:
#             href = row.get("u", None)
#             if href and href != f"http://www.google.com/search?q={query}":
#                 body = self.normalize(row["a"])
#                 if body:
#                     priority += 1
#                     result = {
#                         "title": self.normalize(row["t"]),
#                         "href": self.normalize_url(href),
#                         "body": body,
#                     }
#                     results[priority] = result
#
#         print(list(islice(filter(None, results), 1)))
#
#     def normalize_url(self, url: str) -> str:
#         from urllib.parse import unquote
#
#         """Unquote URL and replace spaces with '+'."""
#         return unquote(url.replace(" ", "+")) if url else ""
#
#     def normalize(self, raw_html: str) -> str:
#         """Strip HTML tags from the raw_html string."""
#         from html import unescape
#         import re
#         REGEX_STRIP_TAGS = re.compile("<.*?>")
#
#         return unescape(REGEX_STRIP_TAGS.sub("", raw_html)) if raw_html else ""
#
#     def search(self, query):
#         self.duck(query)
#
# class DuckDuckGoSearch:
#     """DuckDuckGo search engine class.
#     methods are inherited from the duckduckgo_search package.
#     do not change the methods.
#
#     currently, the package is not working with our current setup.
#     """
#
#     def __init__(self):
#         self.query_result = None
#         self.asession = curl_requests.Session(impersonate="chrome", allow_redirects=False)
#         self.asession.headers["Referer"] = "https://duckduckgo.com/"
#
#     def duck(self, query):
#         resp = self.asession.request("POST", "https://duckduckgo.com/", data={"q": query})
#         vqd = self.extract_vqd(resp.content)
#
#         params = {"q": query, "kl": 'en-us', "p": "1", "s": "0", "df": "", "vqd": vqd, "ex": ""}
#         resp = self.asession.request("GET", "https://links.duckduckgo.com/d.js", params=params)
#         page_data = self.text_extract_json(resp.content)
#
#         results = []
#         for row in page_data:
#             href = row.get("u")
#             if href and href != f"http://www.google.com/search?q={query}":
#                 result = {
#                     "title": self.normalize(row["t"]),
#                     "href": self.normalize_url(href),
#                     "body": self.normalize(row["a"]),
#                 }
#                 results.append(result)
#
#         self.query_result = results
#
#     def search(self, query):
#         self.duck(query)
#
#     def get_first_link(self):
#         print(self.query_result)
#         return self.query_result[0]["href"]
#
#     @staticmethod
#     def extract_vqd(html_bytes: bytes) -> str:
#         patterns = [(b'vqd="', 5, b'"'), (b"vqd=", 4, b"&"), (b"vqd='", 5, b"'")]
#         for start_pattern, offset, end_pattern in patterns:
#             try:
#                 start = html_bytes.index(start_pattern) + offset
#                 end = html_bytes.index(end_pattern, start)
#                 return html_bytes[start:end].decode()
#             except ValueError:
#                 continue
#
#     @staticmethod
#     def text_extract_json(html_bytes):
#         try:
#             start = html_bytes.index(b"DDG.pageLayout.load('d',") + 24
#             end = html_bytes.index(b");DDG.duckbar.load(", start)
#             return orjson.loads(html_bytes[start:end])
#         except Exception as ex:
#             print(f"Error extracting JSON: {type(ex).__name__}: {ex}")
#
#     @staticmethod
#     def normalize_url(url: str) -> str:
#         return unquote(url.replace(" ", "+")) if url else ""
#
#     @staticmethod
#     def normalize(raw_html: str) -> str:
#         return unescape(re.sub("<.*?>", "", raw_html)) if raw_html else ""


if __name__ == "__main__":
    # ddgs = DuckDuckGoSearch1()
    # ddgs.search("python")
    from duckduckgo_search import DDGS
    a = DDGS().text("python")
    print(a)
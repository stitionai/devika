from enum import Enum
# from src.config import Config
from .search_engines import BingSearch , DuckDuckGoSearch


class SearchEngine(Enum):
    BING = BingSearch()
    DUCKDUCKGO = DuckDuckGoSearch()


class WebSearch:
    def __init__(self):
        # self.config = Config()
        self.search_engine = SearchEngine.DUCKDUCKGO.value
        self.query_result = None

    def search(self, query):
        if self.search_engine == SearchEngine.BING:
            bing_search = BingSearch()
            self.query_result = bing_search.search(query)
            return self.query_result
        elif self.search_engine == SearchEngine.DUCKDUCKGO:
            duckduckgo_search = DuckDuckGoSearch()
            self.query_result = duckduckgo_search.search(query)
            return self.query_result

    def get_first_link(self):
        return self.search_engine.get_first_link()

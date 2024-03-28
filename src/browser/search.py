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
        
    def set_search_engine(self, search_engine : SearchEngine):
        self.search_engine = search_engine.value

    def search(self, query):
        self.query_result = self.search_engine.search(query)
        return self.query_result

    def get_first_link(self):
        return self.search_engine.get_first_link()
from enum import Enum
from src.config import Config
from .search_engines import BingSearch , DuckDuckGoSearch


class SearchEngine(Enum):
    BING = BingSearch()
    DUCKDUCKGO = DuckDuckGoSearch()


class WebSearch:
    def __init__(self):
        self.config = Config()
        self.search_engine = self.load_search_engine()
        self.query_result = None
        
    def load_search_engine(self):
        return SearchEngine[self.config.get_search_engine_type()].value

    def search(self, query):
        self.query_result = self.search_engine.search(query)
        return self.query_result

    def get_first_link(self):
        return self.search_engine.get_first_link()
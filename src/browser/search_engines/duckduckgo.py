from src.config import Config
from duckduckgo_search import DDGS


class DuckDuckGoSearch():

    def __init__(self):
        self.config = Config()
        self.query_result = None

    def search(self, query):
        try:
            self.query_result = DDGS().text(query, max_results=1)
            print(self.query_result)
            return self.query_result
        except Exception as err:
            return err

    def get_first_link(self):
        return self.query_result[0]["href"]

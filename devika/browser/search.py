"""Search module for search engines"""

from abc import abstractmethod

import requests
from duckduckgo_search import DDGS

from devika.config import Config

from .params import BrowserParams


# TODO: Add api limit handling
class BaseSearch:
    """Base class for search engines"""

    def __init__(self):
        self.query_result = None

    @abstractmethod
    def search(self, query):
        """Search for the given query"""
        raise NotImplementedError

    @abstractmethod
    def get_first_link(self):
        """Get the first link from the search result"""
        raise NotImplementedError

    @abstractmethod
    def get_expected_result_fields(self):
        """Get the expected fields from the search result"""
        raise NotImplementedError

    def validate_query(self, query):
        """Validate the query"""
        # TODO: Advanced query validation
        if not query:
            return False
        return True

    def validate_result(self):
        """Validate the search result"""
        if not self.query_result:
            raise ValueError("Search result is empty")

        # Make sure the search result contains the expected fields
        # TODO: Check if the search result should be return gently
        for result in self.query_result:
            if not all(
                key in result for key in self.get_expected_result_fields().values()
            ):
                raise ValueError("Search result is missing expected fields")

        # Rewrite the search result to only include the expected fields
        results = []
        for result in self.query_result:
            item = {}
            for key, value in self.get_expected_result_fields().items():
                item[key] = result[value]
            results.append(item)
        return results


class BingSearch(BaseSearch):
    """Bing search engine class"""

    def __init__(self):
        self.config = Config()
        self.bing_api_key = self.config.get_bing_api_key()
        self.bing_api_endpoint = self.config.get_bing_api_endpoint()

        super().__init__()

    def search(self, query):

        if not self.validate_query(query):
            return []

        headers = {"Ocp-Apim-Subscription-Key": self.bing_api_key}
        params = {"q": query, "mkt": "en-US"}

        # TODO: handle HHTP errors
        # TODO: handle API limit
        # TODO: Handle the case when the search result is empty
        try:
            response = requests.get(
                self.bing_api_endpoint,
                headers=headers,
                params=params,
                timeout=BrowserParams.SEARCH_TIMEOUT / 1000,
            )
            response.raise_for_status()
            self.query_result = response.json()
            return self.query_result
        except requests.exceptions.RequestException:
            return []

    def get_first_link(self):
        return self.query_result["webPages"]["value"][0]["url"]

    def get_expected_result_fields(self):
        # Map the expected fields to the actual fields
        return {
            "url": "url",
            "title": "name",
            "body": "snippet",
        }


class GoogleSearch(BaseSearch):
    """Google search engine class"""

    def __init__(self):
        self.config = Config()
        self.google_search_api_key = self.config.get_google_search_api_key()
        self.google_search_engine_id = self.config.get_google_search_engine_id()
        self.google_search_api_endpoint = self.config.get_google_search_api_endpoint()

        super().__init__()

    def search(self, query):
        if not self.validate_query(query):
            return []

        try:
            params = {
                "q": query,
                "key": self.google_search_api_key,
                "cx": self.google_search_engine_id,
            }
            response = requests.get(
                self.google_search_api_endpoint,
                params=params,
                timeout=BrowserParams.SEARCH_TIMEOUT / 1000,
            )
            self.query_result = response.json()["items"]
            return self.validate_result()
        except requests.exceptions.RequestException:
            return []

    def get_first_link(self):
        item = ""
        if "items" in self.query_result:
            item = self.query_result["items"][0]["link"]
        return item

    def get_expected_result_fields(self):
        # Map the expected fields to the actual fields
        return {
            "url": "link",
            "title": "title",
            "body": "snippet",
        }


class DuckDuckGoSearch(BaseSearch):
    """DuckDuckGo search engine class"""

    def search(self, query):

        if not self.validate_query(query):
            return []

        self.query_result = DDGS().text(
            query, max_results=BrowserParams.MAX_SEARCH_RESULTS
        )
        return self.validate_result()

    def get_first_link(self):
        return self.query_result[0]["href"]

    def get_expected_result_fields(self):
        # Map the expected fields to the actual fields
        return {
            "url": "href",
            "title": "title",
            "body": "body",
        }

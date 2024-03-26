import requests
from src.config import Config


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
        except Exception as err:
            return err

    def get_first_link(self):
        return self.query_result["webPages"]["value"][0]["url"]


class GoogleSearch:
    def __init__(self):
        self.config = Config()
        self.google_api_key = self.config.get_google_api_key()
        self.google_api_endpoint = self.config.get_google_api_endpoint()
        self.google_cx = self.config.get_google_cx()
        self.query_result = None

    def search(self, query):
        params = {
            "key": self.google_api_key,
            "cx": self.google_cx,
            "q": query
        }
        try:
            print("Searching in Google...")
            response = requests.get(self.google_api_endpoint, params=params)
            # response.raise_for_status()
            self.query_result = response.json()
        except Exception as error:
            return error

    def get_first_link(self):
        return self.query_result["items"][0]["link"]

import requests
from src.config import Config
import serpapi

class SerpSearch:
    def __init__(self):
        self.config= Config()
        self.serp_api_key = self.config.get_serp_api_key()
        self.serp_api_endpoint = self.config.get_serp_api_endpoint()
        self.query_result = None

    def search(self, query):
        try:
            client = serpapi.Client(api_key = self.serp_api_key)
            self.query_result = client.search({
                'engine': 'google',
                'q': query,
            })
            return self.query_result
        except Exception as err:
            return err

    def get_first_link(self):
        return self.query_result["organic_results"][0]["link"]


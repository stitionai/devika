from devika.config import Config

from .browser import Browser
from .interaction import start_interaction
from .search import BingSearch, DuckDuckGoSearch, GoogleSearch

__all__ = [
    "Browser",
    "start_interaction",
    "BingSearch",
    "GoogleSearch",
    "DuckDuckGoSearch",
]

# Get the search engine from the config file
web_search_engine = Config().get_web_search()

# Search engine
SearchEngine = GoogleSearch  # pylint: disable=invalid-name

if web_search_engine == "bing":
    SearchEngine = BingSearch  # type: ignore
elif web_search_engine == "ddgs":
    SearchEngine = DuckDuckGoSearch  # type: ignore

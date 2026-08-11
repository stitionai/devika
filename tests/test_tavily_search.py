import importlib.util
import sys
import types


browser_package = types.ModuleType("src.browser")
browser_package.__path__ = []
sys.modules["src.browser"] = browser_package
config_module = types.ModuleType("src.config")
config_module.Config = object
sys.modules["src.config"] = config_module

spec = importlib.util.spec_from_file_location("src.browser.search", "src/browser/search.py")
search_module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = search_module
spec.loader.exec_module(search_module)


class ConfigStub:
    def get_tavily_api_key(self):
        return "test-key"


def test_tavily_search_normalizes_results_and_attributes_client(monkeypatch):
    client_args = {}
    search_args = {}

    class ClientStub:
        def __init__(self, **kwargs):
            client_args.update(kwargs)

        def search(self, **kwargs):
            search_args.update(kwargs)
            return {
                "results": [
                    {
                        "title": "First source",
                        "url": "https://example.com/one",
                        "content": "First content",
                        "score": 0.91,
                    },
                    {
                        "title": "Second source",
                        "url": "https://example.com/two",
                        "content": "Second content",
                        "score": 0.72,
                    },
                    {"title": "Missing URL"},
                    "invalid",
                ]
            }

    monkeypatch.setattr(search_module, "Config", ConfigStub)
    monkeypatch.setattr(search_module, "TavilyClient", ClientStub)

    search = search_module.TavilySearch()

    assert search.search("test query") == [
        {
            "title": "First source",
            "url": "https://example.com/one",
            "content": "First content",
            "score": 0.91,
        },
        {
            "title": "Second source",
            "url": "https://example.com/two",
            "content": "Second content",
            "score": 0.72,
        },
    ]
    assert client_args == {
        "api_key": "test-key",
        "client_name": "open-monitor/stitionai/devika",
    }
    assert search_args == {
        "query": "test query",
        "max_results": 5,
        "include_answer": False,
        "include_raw_content": False,
    }


def test_tavily_search_returns_empty_results_for_invalid_response(monkeypatch):
    class ClientStub:
        def __init__(self, **kwargs):
            pass

        def search(self, **kwargs):
            return {"results": [{"title": "No URL"}, "invalid"]}

    monkeypatch.setattr(search_module, "Config", ConfigStub)
    monkeypatch.setattr(search_module, "TavilyClient", ClientStub)

    assert search_module.TavilySearch().search("test query") == []


def test_tavily_search_isolates_provider_errors(monkeypatch):
    class ClientStub:
        def __init__(self, **kwargs):
            pass

        def search(self, **kwargs):
            raise RuntimeError("provider unavailable")

    monkeypatch.setattr(search_module, "Config", ConfigStub)
    monkeypatch.setattr(search_module, "TavilyClient", ClientStub)

    assert search_module.TavilySearch().search("test query") == []

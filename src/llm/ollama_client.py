import httpx
from ollama import Client
from src.config import Config

from src.logger import Logger


class Ollama:

    def __init__(self):
        self.client = Client(host=Config().get_ollama_api_endpoint())

    def list_models(self):
        try:
            return self.client.list()["models"]
        except httpx.ConnectError:
            Logger().warning(
                "Ollama server not running, please start the server to use models from Ollama."
            )
        except Exception as e:
            Logger().error(f"Failed to list Ollama models: {e}")

        return []

    def inference(self, model_id: str, prompt: str) -> str:
        response = self.client.generate(model=model_id, prompt=prompt.strip())

        return response["response"]

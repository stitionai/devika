import httpx
from ollama import Client
from src.config import Config

from src.logger import Logger

client = Client(host=Config().get_ollama_api_endpoint())


class Ollama:
    @staticmethod
    def list_models():
        try:
            self.client = ollama.Client(Config().get_ollama_api_endpoint())
            self.models = self.client.list()["models"]
            log.info("Ollama available")
        except:
            self.client = None
            log.warning("Ollama not available")
            log.warning("run ollama server to use ollama models otherwise use other models")

    def inference(self, model_id: str, prompt: str) -> str:
        response = client.generate(model=model_id, prompt=prompt.strip())

        return response["response"]

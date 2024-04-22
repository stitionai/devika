import ollama
from src.logger import Logger
from src.config import Config

log = Logger()


class Ollama:
    def __init__(self):
        try:
            self.client = ollama.Client(Config().get_ollama_api_endpoint())
            self.models = self.client.list()["models"]
            log.info("Ollama available")
        except:
            self.client = None
            log.warning("Ollama is not running on your local machine / no server provided...")
            log.warning("run ollama server to use ollama models otherwise use other models that we have provided ")

    def inference(self, model_id: str, prompt: str) -> str:
        response = self.client.generate(
            model=model_id,
            prompt=prompt.strip()
        )
        return response['response']
    
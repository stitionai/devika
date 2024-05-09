import ollama
from src.logger import Logger
from src.config import Config


class Ollama:
    def __init__(self):
        self.logger = Logger()

        try:
            self.client = ollama.Client(Config().get_ollama_api_endpoint())
            self.models = self.client.list()["models"]
            self.logger.info("Ollama available")
        except Exception as e:
            self.client = None
            self.logger.warning(f"Ollama client could not be created: {e}")
            self.logger.warning("run ollama server to use ollama models otherwise use API models")

    def inference(self, model_id: str, prompt: str) -> str:
        response = self.client.generate(
            model=model_id,
            prompt=prompt.strip(),
            options={"temperature": 0}
        )
        return response['response']

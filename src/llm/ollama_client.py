import ollama
from src.config import Config


class Ollama:
    def __init__(self):
        config = Config()
        self.client = ollama.Client(config.get_ollama_endpoint())

    def list_models(self) -> list[dict]:
        models = self.client.list()["models"]
        return models

    def inference(self, model_id: str, prompt: str) -> str:
        response = self.client.generate(
            model=model_id,
            prompt=prompt.strip()
        )
        return response['response']

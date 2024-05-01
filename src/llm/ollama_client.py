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
            log.warning("Ollama not available!")
            log.warning("Make sure that the ollama server is running locally to use ollama models otherwise use other models")
            log.warning("We are also supporting now LLAMA3 , So you can use it by running it locally or by using Groq's api.")

    def inference(self, model_id: str, prompt: str) -> str:
        response = self.client.generate(
            model=model_id,
            prompt=prompt.strip()
        )
        return response['response']

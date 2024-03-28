import httpx
from ollama import Client
from src.config import Config

from src.logger import Logger

logger = Logger()

client = Client(host=Config().get_ollama_api_endpoint())


class Ollama:
    @staticmethod
    def list_models():
        try:
            return client.list()["models"]
        except httpx.ConnectError:
            logger.warning("Ollama server not running, please start the server to use models from Ollama.")
        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")
        return []

    def inference(self, model_id: str, prompt: str) -> str:
        try:
            response = client.generate(model=model_id, prompt=prompt.strip())
            return response['response']
        except Exception as e:
            logger.error(f"Error during model inference: {e}")
        return ""
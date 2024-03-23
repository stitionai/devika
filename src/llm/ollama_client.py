import httpx
import ollama

from src.logger import Logger


class Ollama:
    @staticmethod
    def list_models():
        try:
            return ollama.list()["models"]
        except httpx.ConnectError:
            Logger().warning("Ollama server not running, please start the server to use models from Ollama.")
        except Exception as e:
            Logger().error(f"Failed to list Ollama models: {e}")

        return []

    def inference(self, model_id: str, prompt: str) -> str:
        response = ollama.generate(
            model = model_id,
            prompt = prompt.strip()
        )

        return response['response']

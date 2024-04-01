import httpx
from ollama import Client
from src.config import Config
from src.logger import Logger

client = Client(host=Config().get_ollama_api_endpoint())

class Ollama:
    _ollama_client = None
    @classmethod
    def configure_ollama_client(self):
        config = Config()
        ollama_base = config.get_llm_endpoint_ollama()
        if ollama_base is not None:
            Logger().info(f"Using Ollama server at {ollama_base}")    
            self._ollama_client = ollama.Client(host=ollama_base)
        else:
            Logger().info(f"Using Ollama server at localhost")    
            self._ollama_client = ollama

    @classmethod
    def list_models(self):
        # if ollama_base is None - use ollama, else use the provided ollama_base by creating new client 
        if self._ollama_client is None:
            self.configure_ollama_client()

        try:
            models = self._ollama_client.list()["models"]
            Logger().debug(f"Using Ollama server is serving these models: {models}")   
        except httpx.ConnectError:
            Logger().warning(
                "Ollama server not running, please start the server to use models from Ollama."
            )
        except Exception as e:
            Logger().error(f"Failed to list Ollama models: {e}")

        return []
    

    @classmethod
    def inference(self, model_id: str, prompt: str) -> str:
        if self._ollama_client is None:
            self.configure_ollama_client()
        response = self._ollama_client.generate(
             model=model_id, prompt=prompt.strip())

        return response["response"]

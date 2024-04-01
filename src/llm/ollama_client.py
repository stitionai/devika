import httpx
from ollama import Client
from src.config import Config
from src.logger import Logger

log = Logger()

class Ollama:
    client = None
    def __init__(self):
        try:
            config = Config()
            ollama_base = config.get_ollama_api_endpoint()
            if ollama_base is not None:
                log.info(f"Using Ollama server at {ollama_base}")    
                self.client = Client(host=ollama_base)
            else:
                log.info(f"Using Ollama server at localhost")    
                self.client = Client()
            self.models = self.client.list()["models"]
            log.info("Ollama available")
        except:
            self.client = None
            log.warning("Ollama not available")
            log.warning("run ollama server to use ollama models otherwise use other models")


    @classmethod
    def list_models(self):
        try:
            models = self.client.list()["models"]
            log.debug(f"Using Ollama server is serving these models: {models}")   
        except httpx.ConnectError:
            log.warning(
                "Ollama server not running, please start the server to use models from Ollama."
            )
        except Exception as e:
            log.error(f"Failed to list Ollama models: {e}")
        return []
    
    @classmethod
    def inference(self, model_id: str, prompt: str) -> str:
        response = self.client.generate(model=model_id, prompt=prompt.strip())
        return response["response"]

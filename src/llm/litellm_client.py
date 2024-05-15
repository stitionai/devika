import os
from litellm import completion
from src.config import Config

class LiteLLM:
    def __init__(self):
        self.config = Config()

    def set_api_key(self, model_id: str):
        if "openrouter" in model_id:
            os.environ["OPENROUTER_API_KEY"] = self.config.get_openrouter_api_key() 
        elif "deepinfra" in model_id:
            os.environ["DEEPINFRA_API_KEY"] = self.config.get_deepinfra_api_key() 
        elif "openai" in model_id:
            os.environ["OPENAI_API_KEY"] = self.config.get_openai_api_key() 
        elif "anthropic" in model_id:
            os.environ["ANTHROPIC_API_KEY"] = self.config.get_anthropic_api_key() 
        elif "mistral" in model_id:
            os.environ["MISTRAL_API_KEY"] = self.config.get_mistral_api_key()
        elif "cohere" in model_id:
            os.environ["COHERE_API_KEY"] = self.config.get_cohere_api_key() 
        

    def inference(self, model_id: str, prompt: str) -> str:
        self.set_api_key(model_id)
        messages = [{"role": "user", "content": prompt.strip()}]
        response = completion(model=model_id, messages=messages)
        return response['choices'][0]['message']['content']
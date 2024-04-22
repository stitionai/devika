from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

from src.config import Config


class MistralAi:
    def __init__(self):
        config = Config()
        api_key = config.get_mistral_api_key()
        self.client = MistralClient(api_key=api_key)

    def inference(self, model_id: str, prompt: str) -> str:
        print("prompt", prompt.strip())
        chat_completion = self.client.chat(
            model=model_id,
            messages=[
                ChatMessage(role="user", content=prompt.strip())
            ]
        )
        return chat_completion.choices[0].message.content
    

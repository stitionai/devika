from openai import OpenAI as OAI

from src.config import Config

class OpenAI:
    def __init__(self):
        config = Config()
        api_key = config.get_openai_api_key()
        api_base = config.get_openai_api_endpoint()        
        self.client = OAI(api_key=api_key, base_url = api_base)

    def inference(self, model_id: str, prompt: str) -> str:
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt.strip(),
                }
            ],
            model=model_id,
        )

        return chat_completion.choices[0].message.content
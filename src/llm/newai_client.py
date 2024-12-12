from openai import OpenAI

from src.config import Config

class NewAi:
    def __init__(self):
        config = Config()
        api_key = config.get_newai_api_key()
        base_url = config.get_newai_api_endpoint()
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def inference(self, model_id: str, prompt: str) -> str:
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt.strip(),
                }
            ],
            model=model_id,
            temperature=0
        )
        return chat_completion.choices[0].message.content
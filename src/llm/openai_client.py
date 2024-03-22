from openai import OpenAI as OpenAIClient

from src.config import Config

class OpenAI:
    def __init__(self, api_key: str):
        config = Config()
        api_key = config.get_openai_api_key()
        self.client = OpenAIClient(api_key=api_key)  # Use the OpenAIClient class from the library

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

from groq import Groq as _Groq

from src.config import Config


class Groq:
    def __init__(self):
        config = Config()
        api_key = config.get_groq_api_key()
        self.client = _Groq(api_key=api_key)

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

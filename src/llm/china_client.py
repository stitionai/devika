from openai import OpenAI

from config import Config


class China:
    def __init__(self):
        config = Config()
        api_key = config.get_kimi_api_key()
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.moonshot.cn/v1",
        )

    def inference(self, model_id: str, prompt: str) -> str:
        result = self.client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return result.choices[0].message.content

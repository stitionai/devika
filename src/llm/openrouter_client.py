from openai import OpenAI

from src.config import Config


class OpenRouter:
    def __init__(self):
        config = Config()
        api_key = config.get_openrouter_api_key()
        self.client = OpenAI(base_url="https://openrouter.ai/api/v1",api_key=api_key)

    def inference(self, model_id: str, prompt: str) -> str:
        chat_completion = self.client.chat.completions.create(
            #should be uncommented if we want to show devika in openrouter
#             extra_headers={
#     "HTTP-Referer": "https://github.com/stitionai/devika", # Optional, for including your app on openrouter.ai rankings.
#     "X-Title": "Devika", # Optional. Shows in rankings on openrouter.ai.
#   },
            messages=[
                {
                    "role": "user",
                    "content": prompt.strip(),
                }
            ],
            model=model_id if model_id != "Default" else None,
        )
        return chat_completion.choices[0].message.content
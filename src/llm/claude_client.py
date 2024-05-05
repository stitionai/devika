from anthropic import Anthropic

from src.config import Config

class Claude:
    def __init__(self):
        config = Config()
        api_key = config.get_claude_api_key()
        self.client = Anthropic(
            api_key=api_key,
        )

    def inference(self, model_id: str, prompt: str) -> str:
        message = self.client.messages.create(
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": prompt.strip(),
                }
            ],
            model=model_id,
            temperature=0
        )

        return message.content[0].text

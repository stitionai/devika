from g4f.client import Client as g4f
import asyncio

from src.config import Config

# adding g4f- in and removing it while calling inference is needed because if i put the same model name in llm.py as an other model it won't work
class GPT4FREE:
    def __init__(self):
        config = Config()
        self.client = g4f()

    def inference(self, model_id: str, prompt: str) -> str:
        model_id = model_id.replace("g4f-", "")
        chat_completion = self.client.chat.completions.create(
            model=model_id,
            messages=[
                {
                    "role": "user",
                    "content": prompt.strip(),
                }
            ],
            temperature=0
        )
        return chat_completion.choices[0].message.content

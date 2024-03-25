from openai import OpenAI

from src.config import Config

class TogetherAI:
    def __init__(self):
        config=Config()
        api_key=config.get_together_key()
        self.client = OpenAI(
            api_key=api_key,
            base_url='https://api.together.xyz/v1',
        )
    

    def inference(self,model_id:str,prompt: str)->str:
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt.strip(),
                }
            ],
            model=model_id,
        )
        print(chat_completion.choices[0].message.content)
        return chat_completion.choices[0].message.content

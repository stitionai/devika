from groq import Groq as _Groq
import time
from src.config import Config


class Groq:
    def __init__(self):
        config = Config()
        api_key = config.get_groq_api_key()
        self.client = _Groq(api_key=api_key)

    def inference(self, model_id: str, prompt: str,retries:int=0) -> str:
        try:        
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt.strip(),
                    }
                ],
                model=model_id,
                temperature=0, 
            )
            return chat_completion.choices[0].message.content
        except Exception as e:  
            if e.response.status_code == 429:
                if retries <= 10:
                    retry_after = e.response.headers['retry-after'] 
                    print(f"Rate limit exceeded, waiting for {int(retry_after)+1} seconds, then retrying...")
                    time.sleep(int(retry_after)+1)

                    return self.inference(model_id, prompt,retries+1)
                else:
                    raise RuntimeError(e.response.text)
            else:
                raise RuntimeError(e.response.text)
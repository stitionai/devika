from anthropic import Anthropic, APIConnectionError, RateLimitError, APIStatusError
from src.config import Config

class Claude:
    def __init__(self):
        config = Config()
        api_key = config.get_claude_api_key()
        self.client = Anthropic(
            api_key=api_key,
        )

    def inference(self, model_id: str, prompt: str) -> str:
        try:
            message = self.client.messages.create(
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": prompt.strip(),
                    }
                ],
                model=model_id,
            )
            return message.content[0].text
        except APIConnectionError as e:
            print("The server could not be reached.")
            print(e.__cause__) # This will print the underlying exception, likely from httpx.
        except RateLimitError as e:
            print("A 429 status code was received; we should back off a bit.")
        except APIStatusError as e:
            print("Another non-200-range status code was received.")
            print(f"Status code: {e.status_code}")
            print(f"Response: {e.response}")
        return None
    

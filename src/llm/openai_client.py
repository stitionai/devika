from openai import OpenAI as OAI
from openai import AzureOpenAI as AZURE_OAI

from src.config import Config

class OpenAI:
    def __init__(self):
        config = Config()
        openai_type = config.get_openai_type()
        api_key = config.get_openai_api_key()
        if openai_type == 'azure':
            api_version = config.get_azure_openai_api_version()
            endpoint = config.get_azure_openai_endpoint()
            self.client = AZURE_OAI(
                api_version=api_version,
                azure_endpoint=endpoint,
                api_key=api_key
            )
        elif openai_type == 'openai':
            self.client = OAI(
                api_key=api_key,
            )
        
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

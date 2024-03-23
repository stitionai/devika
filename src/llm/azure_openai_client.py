from openai import AzureOpenAI as AzureAI

from src.config import Config

class AzureOpenAI:
    def __init__(self):
        config = Config()
        api_key = config.get_azure_openai_api_key()
        azure_endpoint = config.get_azure_openai_api_endpoint()
        api_version = config.get_azure_openai_api_version()
        self.client = AzureAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint
        )
 
    def inference(self, prompt: str) -> str:
        api_deployment = Config().get_azure_openai_deployment_name()
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt.strip(),
                }
            ],
            model=api_deployment
        )
        return chat_completion.choices[0].message.content

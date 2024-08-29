import os
from mistralai import Mistral, UserMessage  # Updated import from mistralai

from src.config import Config


class MistralAi:
    def __init__(self):
        config = Config()
        api_key = config.get_mistral_api_key()  # Retrieve API key using the existing Config class
        self.client = Mistral(api_key=api_key)  # Initialize Mistral client with the new class

    def inference(self, model_id: str, prompt: str) -> str:
        print("prompt", prompt.strip())
        # Use the new method for chat completion
        chat_response = self.client.chat.complete(
            model=model_id,  # Model ID remains the same
            messages=[  # Update to use dictionary format for messages
                {
                    "role": "user",
                    "content": prompt.strip()
                }
            ],
        )
        # Access the response using the new structure
        return chat_response.choices[0].message.content  # Extract content from the response

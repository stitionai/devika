"""OpenAI client for interacting with OpenAI API."""

from openai import OpenAI as OAI
from openai import RateLimitError

from src.config import Config

from .base import BaseLLMModel
from .exception import ModelNotSupported, TokenUsageExceeded


class OpenAI(BaseLLMModel):
    """OpenAI client for interacting with OpenAI API."""

    SUPPORTED_MODELS = {
        "gpt-4-0125-preview": "GPT-4 Turbo",
        "gpt-3.5-turbo-0125": "GPT-3.5",
    }

    def __init__(self, model_id: str, timeout: int = 30):

        if model_id not in self.SUPPORTED_MODELS:
            raise ModelNotSupported(f"Model {model_id} is not supported.")

        self._model_id = model_id
        self._model_name = self.SUPPORTED_MODELS[model_id]

        config = Config()
        api_key = config.get_openai_api_key()
        self.client = OAI(api_key=api_key, timeout=timeout)

    def _inference(self, prompt: str) -> str:

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt.strip(),
                    }
                ],
                model=self.model_id,
            )
        except RateLimitError as e:
            raise TokenUsageExceeded("Token usage exceeded for OpenAI.") from e

        return chat_completion.choices[0].message.content  # type: ignore

    def supported_models(self) -> dict:
        return self.SUPPORTED_MODELS

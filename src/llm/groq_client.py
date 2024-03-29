"""Groq client for interacting with Groq API."""

from groq import Groq as _Groq

from src.config import Config
from .base import BaseLLMModel
from .exception import ModelNotSupported, TokenUsageExceeded


class Groq(BaseLLMModel):
    """Groq client for interacting with Groq API."""

    SUPPORTED_MODELS = {
        "mixtral-8x7b-32768": "GROQ Mixtral",
        "llama2-70b-4096": "GROQ LLAMA2-70B",
        "gemma-7b-it": "GROQ GEMMA-7B-IT",
    }

    def __init__(self, model_id: str, timeout: int = 30):

        if model_id not in self.SUPPORTED_MODELS:
            raise ModelNotSupported(f"Model {model_id} is not supported.")

        self._model_id = model_id
        self._model_name = self.SUPPORTED_MODELS[model_id]

        config = Config()
        api_key = config.get_groq_api_key()
        self.client = _Groq(api_key=api_key, timeout=timeout)

    def _inference(self, prompt: str) -> str:
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt.strip(),
                }
            ],
            model=self.model_id,
        )

        if chat_completion.choices[0].finish_reason in ["max_tokens", "length"]:
            raise TokenUsageExceeded("Token usage exceeded for Groq.")

        return chat_completion.choices[0].message.content

    def supported_models(self) -> dict:
        return self.SUPPORTED_MODELS

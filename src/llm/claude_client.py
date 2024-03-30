"""Claude API client."""

from anthropic import Anthropic

from src.config import Config

from .base import BaseLLMModel
from .exception import ModelNotSupported, TokenUsageExceeded


class Claude(BaseLLMModel):
    """Claude API client."""

    SUPPORTED_MODELS = {
        "claude-3-opus-20240229": "Claude 3 Opus",
        "claude-3-sonnet-20240229": "Claude 3 Sonnet",
        "claude-3-haiku-20240307": "Claude 3 Haiku",
    }

    def __init__(self, model_id: str, timeout: int = 30):

        # Check if the model is supported
        if model_id not in self.SUPPORTED_MODELS:
            raise ModelNotSupported(f"Model {model_id} is not supported.")

        self._model_id = model_id
        self._model_name = self.SUPPORTED_MODELS[model_id]
        self._timeout = timeout

        config = Config()
        api_key = config.get_claude_api_key()
        self.client = Anthropic(
            api_key=api_key,
        )

    def _inference(self, prompt: str) -> str:
        """Inference using Claude API."""
        message = self.client.messages.create(
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": prompt.strip(),
                }
            ],
            model=self.model_id,
            timeout=self._timeout,
        )

        if message.stop_reason == "max_tokens":
            raise TokenUsageExceeded("Token usage exceeded for Claude.")

        return message.content[0].text

    def supported_models(self) -> dict:
        """List supported models."""
        return self.SUPPORTED_MODELS

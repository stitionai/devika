"""Base class for the llm module."""

from abc import abstractmethod
from typing import Dict


class BaseLLMModel:
    """Base class for the llm module."""

    _model_id: str = ""
    _model_name: str = ""
    SUPPORTED_MODELS: Dict[str, str] = {}

    @property
    def model_id(self):
        """Model ID."""
        return self._model_id

    @property
    def model_name(self):
        """Model name."""
        return self._model_name

    def inference(self, prompt: str) -> str:
        """Inference using the model."""
        return self._inference(prompt)

    @abstractmethod
    def _inference(self, prompt: str) -> str:
        """Inference using the model."""
        raise NotImplementedError

    @abstractmethod
    def supported_models(self) -> dict:
        """List supported models."""
        raise NotImplementedError

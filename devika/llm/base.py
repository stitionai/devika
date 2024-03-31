"""Base class for the llm module."""

from abc import abstractmethod
from multiprocessing import RLock
from typing import Dict


class BaseLLMModel:
    """Base class for the llm module."""

    _model_id: str = ""
    _model_name: str = ""
    SUPPORTED_MODELS: Dict[str, str] = {}

    _lock = RLock()

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
        # TODO: Remove this lock once we have a proper way to handle multiple parallel requests.
        with self._lock:
            return self._inference(prompt)

    @abstractmethod
    def _inference(self, prompt: str) -> str:
        """Inference using the model."""
        raise NotImplementedError

    @abstractmethod
    def supported_models(self) -> dict:
        """List supported models."""
        raise NotImplementedError

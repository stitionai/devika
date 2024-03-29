"""Ollama client for interacting with Ollama API."""

from typing import Dict
import httpx
from ollama import Client  # type: ignore

from src.config import Config
from .base import BaseLLMModel
from .exception import (
    ModelNotSupported,
    LLMException,
    LLMConfigException,
)


class Ollama(BaseLLMModel):
    """Ollama client for interacting with Ollama API."""

    SUPPORTED_MODELS: Dict[str, str] = {}

    def __init__(self, model_id: str, timeout: int = 30) -> None:
        config = Config()
        api_endpoint = config.get_ollama_api_endpoint()
        if not api_endpoint:
            raise LLMConfigException("Ollama API endpoint not configured.")

        self._client = Client(host=api_endpoint)
        # Check if ollama server is running

        try:
            self._client.list()
        except httpx.ConnectError as e:
            raise LLMException(
                "Ollama server not running, please start the server to use models from Ollama."
            ) from e

        # Get supported models
        self._process_models_info()

        if model_id not in self.SUPPORTED_MODELS:
            raise ModelNotSupported(
                f"Model '{model_id}' is not supported. Supported models: {self.SUPPORTED_MODELS.keys()}"  #  pylint: disable=line-too-long
            )

        self._model_id = model_id
        self._model_name = self.SUPPORTED_MODELS[model_id]
        self._timeout = timeout

    def _process_models_info(self) -> None:
        for model in self._client.list()["models"]:
            model_name = model["name"].split(":")[0]
            # model_id = model["name"] + "-" + model["details"]["parameter_size"]
            model_id = model["name"]

            self.SUPPORTED_MODELS[model_id] = model_name

    def _inference(self, prompt: str) -> str:
        try:
            response = self._client.generate(model=self.model_id, prompt=prompt.strip())
            return response["response"]
        except Exception as e:
            raise LLMException("Error during model inference.") from e

    def supported_models(self) -> dict:
        return self.SUPPORTED_MODELS

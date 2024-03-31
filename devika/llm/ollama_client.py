"""Ollama client for interacting with Ollama API."""

import httpx
from ollama import Client  # type: ignore

from devika.config import Config

from .base import BaseLLMModel
from .exception import LLMException, LLMWarning, ModelNotSupported


def get_ollama_info():
    """Get supported models from Ollama API."""

    ollama_client = Client(host=Config().get_ollama_api_endpoint())

    try:
        ollama_client.list()
    except httpx.ConnectError as e:
        raise LLMWarning(
            "Ollama server not running, please start the server to use models from Ollama."
        ) from e

    supported_models = {}
    for model in ollama_client.list()["models"]:
        model_name = model["name"].split(":")[0]
        # model_id = model["name"] + "-" + model["details"]["parameter_size"]
        model_id = model["name"]

        supported_models[model_id] = model_name

    return supported_models, ollama_client


class Ollama(BaseLLMModel):
    """Ollama client for interacting with Ollama API."""

    SUPPORTED_MODELS, _client = get_ollama_info()

    def __init__(self, model_id: str, timeout: int = 30) -> None:
        if model_id not in self.SUPPORTED_MODELS:
            raise ModelNotSupported(
                f"Model '{model_id}' is not supported. Supported models: {self.SUPPORTED_MODELS.keys()}"  #  pylint: disable=line-too-long
            )

        self._model_id = model_id
        self._model_name = self.SUPPORTED_MODELS[model_id]
        self._timeout = timeout

    def _inference(self, prompt: str) -> str:
        try:
            response = self._client.generate(model=self.model_id, prompt=prompt.strip())
            return response["response"]
        except Exception as e:
            raise LLMException("Error during model inference.") from e

    def supported_models(self) -> dict:
        return self.SUPPORTED_MODELS

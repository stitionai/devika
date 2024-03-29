"""LLM class to handle inference for different models."""

from typing import Dict
import tiktoken

from src.state import AgentState

from ..config import Config
from .claude_client import Claude
from .gemini_client import Gemini
from .groq_client import Groq
from .ollama_client import Ollama
from .openai_client import OpenAI
from .exception import ModelNotSupported

# TODO: Add prompt logging
# TODO: Bug in getting ollama supported models


class LLM:
    """LLM class to handle inference for different models."""

    CLIENTS = [Ollama, Claude, OpenAI, Groq]
    _supported_models: Dict[str, str] = {}

    def __init__(self, model_id: str):
        self.model_id = model_id
        self.log_prompts = Config().get_logging_prompts()

        # Check which client to use based on model_id
        self._client = self._get_model_client(model_id)
        self.tiktoken_encoder = tiktoken.get_encoding("cl100k_base")

        if self._client is None:
            raise ModelNotSupported(f"Model {model_id} is not supported.")

        self._supported_models = self._get_supported_models()

    def _get_supported_models(self) -> Dict[str, str]:
        """Get supported models from all clients."""

        supported_models = {}
        for client in self.CLIENTS:
            supported_models.update(client.SUPPORTED_MODELS)

        return supported_models

    def _get_model_client(self, model_id: str):
        """Check if the model is supported."""

        for client in self.CLIENTS:
            if model_id in client.SUPPORTED_MODELS:
                return client(model_id)  # type: ignore

            if client == Ollama:
                # FIXME: This is a hack to check if the model is supported by Ollama
                try:
                    return client(model_id)  # type: ignore
                except ModelNotSupported:
                    continue

        return None

    def update_global_token_usage(self, string: str, project_name: str):
        # TODO: Add send and receive token usage
        token_usage = len(self.tiktoken_encoder.encode(string))
        AgentState().update_token_usage(project_name, token_usage)

    def inference(self, prompt: str, project_name: str) -> str:

        response = self._client.inference(prompt)

        if response:
            self.update_global_token_usage(prompt, project_name)
            self.update_global_token_usage(response, project_name)

            return response

        return ""

    def supported_models(self) -> Dict[str, str]:
        return self._supported_models

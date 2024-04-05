import tiktoken
from typing import List, Tuple

from src.socket_instance import emit_agent
from .ollama_client import Ollama
from .claude_client import Claude
from .openai_client import OpenAi
from .gemini_client import Gemini
from .mistral_client import MistralAi
from .groq_client import Groq

from src.state import AgentState

from src.config import Config
from src.logger import Logger

TIKTOKEN_ENC = tiktoken.get_encoding("cl100k_base")

ollama = Ollama()
logger = Logger()
agentState = AgentState()


class LLM:
    def __init__(self, model_id: str = None):
        self.model_id = model_id
        self.log_prompts = Config().get_logging_prompts()
        self.models = {
            "CLAUDE": [
                ("Claude 3 Opus", "claude-3-opus-20240229"),
                ("Claude 3 Sonnet", "claude-3-sonnet-20240229"),
                ("Claude 3 Haiku", "claude-3-haiku-20240307"),
            ],
            "OPENAI": [
                ("GPT-4 Turbo", "gpt-4-0125-preview"),
                ("GPT-3.5", "gpt-3.5-turbo-0125"),
            ],
            "GOOGLE": [
                ("Gemini 1.0 Pro", "gemini-pro"),
            ],
            "MISTRAL": [
                ("Mistral 7b", "open-mistral-7b"),
                ("Mistral 8x7b", "open-mixtral-8x7b"),
                ("Mistral Medium", "mistral-medium-latest"),
                ("Mistral Small", "mistral-small-latest"),
                ("Mistral Large", "mistral-large-latest"),
            ],
            "GROQ": [
                ("GROQ Mixtral", "mixtral-8x7b-32768"),
                ("GROQ LLAMA2 70B", "llama2-70b-4096"),
                ("GROQ GEMMA 7B IT", "gemma-7b-it"),
            ],
            "OLLAMA": []
        }
        if ollama.client:
            self.models["OLLAMA"] = [(model["name"].split(":")[0], model["name"]) for model in
                                     ollama.models]

    def list_models(self) -> dict:
        return self.models

    def model_id_to_enum_mapping(self) -> dict:
        mapping = {}
        for enum_name, models in self.models.items():
            for model_name, model_id in models:
                mapping[model_id] = enum_name
        return mapping

    @staticmethod
    def update_global_token_usage(string: str, project_name: str):
        token_usage = len(TIKTOKEN_ENC.encode(string))
        agentState.update_token_usage(project_name, token_usage)

        total = agentState.get_latest_token_usage(project_name) + token_usage
        emit_agent("tokens", {"token_usage": total})

    def inference(self, prompt: str, project_name: str) -> str:
        self.update_global_token_usage(prompt, project_name)

        model_enum = self.model_id_to_enum_mapping().get(self.model_id)
        print(f"Model: {self.model_id}, Enum: {model_enum}")
        if model_enum is None:
            raise ValueError(f"Model {self.model_id} not supported")

        model_mapping = {
            "OLLAMA": ollama,
            "CLAUDE": Claude(),
            "OPENAI": OpenAi(),
            "GOOGLE": Gemini(),
            "MISTRAL": MistralAi(),
            "GROQ": Groq()
        }

        try:
            model = model_mapping[model_enum]
            response = model.inference(self.model_id, prompt).strip()
        except KeyError:
            raise ValueError(f"Model {model_enum} not supported")

        if self.log_prompts:
            logger.debug(f"Response ({model}): --> {response}")

        self.update_global_token_usage(response, project_name)

        return response

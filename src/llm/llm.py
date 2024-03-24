from enum import Enum

from .ollama_client import Ollama
from .claude_client import Claude
from .openai_client import OpenAI
from .gemini_client import Gemini

import tiktoken

TOKEN_USAGE = 0
TIKTOKEN_ENC = tiktoken.get_encoding("cl100k_base")

class Model(Enum):
    CLAUDE_3_OPUS = ("Claude 3 Opus", "claude-3-opus-20240229")
    CLAUDE_3_SONNET = ("Claude 3 Sonnet", "claude-3-sonnet-20240229")
    CLAUDE_3_HAIKU = ("Claude 3 Haiku", "claude-3-haiku-20240307")
    GPT_4_TURBO = ("GPT-4 Turbo", "gpt-4-0125-preview")
    GPT_3_5 = ("GPT-3.5", "gpt-3.5-turbo-0125")
    GEMINI_1_0_PRO = ("Gemini 1.0 Pro", "gemini-1.0-pro")
    GEMINI_1_5_PRO = ("Gemini 1.5 Pro", "gemini-1.5-pro")
    OLLAMA_MODELS = [
        (
            model["name"].split(":")[0],
            model["name"],
        )
        for model in Ollama.list_models()
    ]

class LLM:
    def __init__(self, model_id: str = None):
        self.model_id = model_id
    
    def list_models(self) -> list[tuple[str, str]]:
        return [model.value for model in Model if model.name != "OLLAMA_MODELS"] + list(
            Model.OLLAMA_MODELS.value
        )

    def model_id_to_enum_mapping(self):
        models = {model.value[1]: model for model in Model if model.name != "OLLAMA_MODELS"}
        ollama_models = {model[1]: "OLLAMA_MODELS" for model in Model.OLLAMA_MODELS.value}
        models.update(ollama_models)
        return models

    def update_global_token_usage(self, string: str):
        global TOKEN_USAGE
        TOKEN_USAGE += len(TIKTOKEN_ENC.encode(string))
        print(f"Token usage: {TOKEN_USAGE}")

    def inference(
        self, prompt: str
    ) -> str:
        self.update_global_token_usage(prompt)
        
        model = self.model_id_to_enum_mapping()[self.model_id]

        if model == "OLLAMA_MODELS":
            response = Ollama().inference(self.model_id, prompt).strip()
        elif "CLAUDE" in str(model):
            response = Claude().inference(self.model_id, prompt).strip()
        elif "GPT" in str(model):
            response = OpenAI().inference(self.model_id, prompt).strip()
        elif "GEMINI" in str(model):
            response = Gemini().inference(self.model_id, prompt).strip()
        else:
            raise ValueError(f"Model {model} not supported")

        self.update_global_token_usage(response)
        
        return response

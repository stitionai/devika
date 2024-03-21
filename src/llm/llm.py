from enum import Enum
from src.state import AgentState
import tiktoken
from .ollama_client import Ollama
from .claude_client import Claude
from .openai_client import Openai
from .gemini_client import Gemini

TOKEN_USAGE = 0
TIKTOKEN_ENC = tiktoken.get_encoding("cl100k_base")

ollama = Ollama()


class Model(Enum):
    CLAUDE_3_OPUS = ("Claude 3 Opus", "claude-3-opus-20240229")
    CLAUDE_3_SONNET = ("Claude 3 Sonnet", "claude-3-sonnet-20240229")
    CLAUDE_3_HAIKU = ("Claude 3 Haiku", "claude-3-haiku-20240307")
    GPT_4_TURBO = ("GPT-4 Turbo", "gpt-4-0125-preview")
    GPT_3_5 = ("GPT-3.5", "gpt-3.5-turbo-0125")
    GEMINI_1_5_PRO = ("Gemini 1.5 Pro", "gemini-pro")

    @staticmethod
    def ollama_models():
        try:
            return [
                (
                    model["name"],
                    f"{model['details']['parameter_size']} - {model['details']['quantization_level']}",
                )
                for model in ollama.list_models()
            ]
        except:
            return []


class LLM:
    def __init__(self, model_id: str = None):
        self.model_id = model_id

    def list_models(self) -> list[tuple[str, str]]:
        return [model.value for model in Model] + Model.ollama_models()

    def model_id_to_enum_mapping(self):
        models = {model.value[1]: model for model in Model}
        models.update({model[0]: "OLLAMA_MODELS" for model in Model.ollama_models()})
        return models

    @staticmethod
    def update_global_token_usage(string: str):
        global TOKEN_USAGE
        TOKEN_USAGE += len(TIKTOKEN_ENC.encode(string))
        print(f"Token usage: {TOKEN_USAGE}")

    def inference(self, prompt: str) -> str:
        self.update_global_token_usage(prompt)

        model_enum = self.model_id_to_enum_mapping().get(self.model_id)
        if model_enum is None:
            raise ValueError(f"Model {self.model_id} not supported")

        if model_enum == "OLLAMA_MODELS":
            response = ollama.inference(self.model_id, prompt).strip()
        elif "CLAUDE" in model_enum.name:
            response = Claude().inference(self.model_id, prompt).strip()
        elif "GPT" in model_enum.name:
            response = Openai().inference(self.model_id, prompt).strip()
        elif "GEMINI" in model_enum.name:
            response = Gemini().inference(self.model_id, prompt).strip()
        else:
            raise ValueError(f"Model {model_enum} not supported")

        self.update_global_token_usage(response)

        return response

import sys
import concurrent.futures
import time

import tiktoken
from typing import List, Tuple

from src.socket_instance import emit_agent
from .ollama_client import Ollama
from .claude_client import Claude
from .openai_client import OpenAi
from .gemini_client import Gemini
from .mistral_client import MistralAi
from .groq_client import Groq
from .lm_studio_client import LMStudio

from src.state import AgentState

from src.config import Config
from src.logger import Logger

TIKTOKEN_ENC = tiktoken.get_encoding("cl100k_base")

ollama = Ollama()
logger = Logger()
agentState = AgentState()
config = Config()


class LLM:
    def __init__(self, model_id: str = None):
        self.model_id = model_id
        self.log_prompts = config.get_logging_prompts()
        self.timeout_inference = config.get_timeout_inference()
        self.models = {
            "CLAUDE": [
                ("Claude 3 Opus", "claude-3-opus-20240229"),
                ("Claude 3 Sonnet", "claude-3-sonnet-20240229"),
                ("Claude 3 Haiku", "claude-3-haiku-20240307"),
            ],
            "OPENAI": [
                ("GPT-4o-mini", "gpt-4o-mini"),
                ("GPT-4o", "gpt-4o"),
                ("GPT-4 Turbo", "gpt-4-turbo"),
                ("GPT-3.5 Turbo", "gpt-3.5-turbo-0125"),
            ],
            "GOOGLE": [
                ("Gemini 1.0 Pro", "gemini-pro"),
                ("Gemini 1.5 Flash", "gemini-1.5-flash"),
                ("Gemini 1.5 Pro", "gemini-1.5-pro"),
            ],
            "MISTRAL": [
                ("Mistral 7b", "open-mistral-7b"),
                ("Mistral 8x7b", "open-mixtral-8x7b"),
                ("Mistral Medium", "mistral-medium-latest"),
                ("Mistral Small", "mistral-small-latest"),
                ("Mistral Large", "mistral-large-latest"),
            ],
            "GROQ": [
                ("LLAMA3 8B", "llama3-8b-8192"),
                ("LLAMA3 70B", "llama3-70b-8192"),
                ("LLAMA2 70B", "llama2-70b-4096"),
                ("Mixtral", "mixtral-8x7b-32768"),
                ("GEMMA 7B", "gemma-7b-it"),
            ],
            "OLLAMA": [],
            "LM_STUDIO": [
                ("LM Studio", "local-model"),    
            ],
            
        }
        if ollama.client:
            try:
                self.models["OLLAMA"] = [(model["name"], model["name"]) for model in ollama.models]
            except Exception as e:
                logger.warning(f"Failed to load Ollama models: {str(e)}")
                self.models["OLLAMA"] = []

    def list_models(self) -> dict:
        return self.models

    def model_enum(self, model_name: str) -> Tuple[str, str]:
        model_dict = {
            model[0]: (model_enum, model[1]) 
            for model_enum, models in self.models.items() 
            for model in models
        }
        return model_dict.get(model_name, (None, None))

    @staticmethod
    def update_global_token_usage(string: str, project_name: str):
        try:
            token_usage = len(TIKTOKEN_ENC.encode(string))
            agentState.update_token_usage(project_name, token_usage)

            total = agentState.get_latest_token_usage(project_name) + token_usage
            emit_agent("tokens", {"token_usage": total})
        except Exception as e:
            logger.error(f"Error updating token usage: {str(e)}")

    def inference(self, prompt: str, project_name: str) -> str:
        try:
            self.update_global_token_usage(prompt, project_name)

            model_enum, model_name = self.model_enum(self.model_id)
                    
            print(f"Model: {self.model_id}, Enum: {model_enum}")
            if model_enum is None:
                raise ValueError(f"Model {self.model_id} not supported")

            model_mapping = {
                "OLLAMA": ollama,
                "CLAUDE": Claude(),
                "OPENAI": OpenAi(),
                "GOOGLE": Gemini(),
                "MISTRAL": MistralAi(),
                "GROQ": Groq(),
                "LM_STUDIO": LMStudio()
            }

            start_time = time.time()
            model = model_mapping.get(model_enum)
            
            if not model:
                raise ValueError(f"Model provider {model_enum} not available")
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(model.inference, model_name, prompt)
                
                try:
                    while True:
                        elapsed_time = time.time() - start_time
                        elapsed_seconds = format(elapsed_time, ".2f")
                        emit_agent("inference", {"type": "time", "elapsed_time": elapsed_seconds})
                        
                        if int(elapsed_time) == 5:
                            emit_agent("inference", {"type": "warning", "message": "Inference is taking longer than expected"})
                        
                        if elapsed_time > self.timeout_inference:
                            future.cancel()
                            raise concurrent.futures.TimeoutError("Inference timeout")
                        
                        if future.done():
                            break
                            
                        time.sleep(0.5)

                    response = future.result(timeout=1)  # Short timeout since we know it's done
                    
                    if not response:
                        raise ValueError("Empty response from model")
                        
                    response = response.strip()

                except concurrent.futures.TimeoutError:
                    logger.error(f"Inference timeout. Model: {model_enum}, Model ID: {self.model_id}")
                    emit_agent("inference", {"type": "error", "message": "Inference took too long. Please try again."})
                    return ""
                    
                except Exception as e:
                    logger.error(f"Inference error: {str(e)}")
                    emit_agent("inference", {"type": "error", "message": f"Inference failed: {str(e)}"})
                    return ""

            if self.log_prompts:
                logger.debug(f"Response ({model_enum}): --> {response[:200]}...")

            self.update_global_token_usage(response, project_name)

            return response

        except Exception as e:
            logger.error(f"LLM inference error: {str(e)}")
            emit_agent("inference", {"type": "error", "message": f"LLM error: {str(e)}"})
            return ""
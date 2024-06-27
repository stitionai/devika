import sys

import tiktoken
import asyncio
from asyncio import WindowsSelectorEventLoopPolicy
from typing import List, Tuple

from src.socket_instance import emit_agent
from .ollama_client import Ollama
from .claude_client import Claude
from .g4f_client import GPT4FREE
from .openai_client import OpenAi
from .gemini_client import Gemini
from .mistral_client import MistralAi
from .groq_client import Groq

from src.state import AgentState

from src.config import Config
from src.logger import Logger

TIKTOKEN_ENC = tiktoken.get_encoding("cl100k_base")

ollama = Ollama()
gpt4f = GPT4FREE()
logger = Logger()
agentState = AgentState()
config = Config()

# asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

class LLM:
    def __init__(self, model_id: str = None):
        self.model_id = model_id
        self.log_prompts = config.get_logging_prompts()
        self.timeout_inference = config.get_timeout_inference()
        self.models = {
            "GPT4FREE": [
                ("Free GPT-4 Turbo", "g4f-gpt-4-turbo"),
                ("Free GPT-4", "g4f-gpt-4"),
                ("Free GPT-3.5 Turbo", "g4f-gpt-3.5-turbo-16k"),
                ("Free GPT-3.5", "g4f-gpt-3.5-long"),
                ("Free Llama3 70b", "g4f-llama3-70b"),
                ("Free Llama3 8b", "g4f-llama3-8b"),
                ("Free Llama3 70b Instruct", "g4f-llama3-70b-instruct"),
                ("Free Llama3 8b Instruct", "g4f-llama3-8b-instruct"),
                ("Free Mixtral 8x7B", "g4f-mixtral-8x7b"),
                ("Free Gemini", "g4f-gemini"),
                ("Free Gemini Pro", "g4f-gemini-pro"),
                ("Free Claude 3 Sonnet", "g4f-claude-3-sonnet"),
                ("Free Claude 3 Opus", "g4f-claude-3-opus"),
                ("Free Openchat 3.5", "g4f-openchat_3.5"),
            ],
            "CLAUDE": [
                ("Claude 3 Opus", "claude-3-opus-20240229"),
                ("Claude 3 Sonnet", "claude-3-sonnet-20240229"),
                ("Claude 3 Haiku", "claude-3-haiku-20240307"),
            ],
            "OPENAI": [
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
            "OLLAMA": []
        }
        if ollama.client:
            self.models["OLLAMA"] = [(model["name"], model["name"]) for model in ollama.models]

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
        token_usage = len(TIKTOKEN_ENC.encode(string))
        agentState.update_token_usage(project_name, token_usage)

        total = agentState.get_latest_token_usage(project_name) + token_usage
        emit_agent("tokens", {"token_usage": total})

    def inference(self, prompt: str, project_name: str) -> str:
        self.update_global_token_usage(prompt, project_name)
        if sys.platform == 'win32':
            try:
                asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
            except ImportError:
                asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
                print("WindowsSelectorEventLoopPolicy not available, using default event loop policy.")
        else:
            asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

        model_enum, model_name = self.model_enum(self.model_id)
                
        print(f"Model: {self.model_id}, Enum: {model_enum}")
        if model_enum is None:
            raise ValueError(f"Model {self.model_id} not supported")

        model_mapping = {
            "OLLAMA": ollama,
            "GPT4FREE": gpt4f,
            "CLAUDE": Claude(),
            "OPENAI": OpenAi(),
            "GOOGLE": Gemini(),
            "MISTRAL": MistralAi(),
            "GROQ": Groq()
        }

        try:
            import concurrent.futures
            import time

            start_time = time.time()
            model = model_mapping[model_enum]
            
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
                            raise concurrent.futures.TimeoutError
                        if future.done():
                            break
                        time.sleep(0.5)

                    response = future.result(timeout=self.timeout_inference).strip()

                except concurrent.futures.TimeoutError:
                    logger.error(f"Inference failed. took too long. Model: {model_enum}, Model ID: {self.model_id}")
                    emit_agent("inference", {"type": "error", "message": "Inference took too long. Please try again."})
                    response = False
                    sys.exit()
                
                except Exception as e:
                    logger.error(str(e))
                    response = False
                    emit_agent("inference", {"type": "error", "message": str(e)})
                    sys.exit()


        except KeyError:
            raise ValueError(f"Model {model_enum} not supported")

        if self.log_prompts:
            logger.debug(f"Response ({model}): --> {response}")

        self.update_global_token_usage(response, project_name)
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

        return response

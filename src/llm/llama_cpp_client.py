import llama_cpp
from src.logger import Logger
from src.config import Config
class LlamaCpp:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if not self.initialized:
            config = Config()
            model_path = config.get_model_path()
            gpu_layers = int(config.get_gpu_layers())
            context_size = int(config.get_context_size())
            self.model = llama_cpp.Llama(model_path=model_path, n_gpu_layers=gpu_layers, n_ctx=context_size)
            self.initialized = True

    def inference(self, prompt):
        response = self.model.create_completion(prompt=prompt, max_tokens=2048)
        return response["choices"][0]["text"]






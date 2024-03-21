import ollama

class Ollama:
    @staticmethod
    def list_models():
        return ollama.list()["models"]

    def inference(self, model_id: str, prompt: str) -> str:
        response = ollama.generate(
            model = model_id,
            prompt = prompt.strip()
        )
        
        return response['response']
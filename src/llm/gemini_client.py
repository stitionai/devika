import google.generativeai as Gemini

from src.config import Config

class Gemini:
    def __init__(self):
        config = Config()
        api_key = config.get_gemini_api_key()
        Gemini.configure(api_key=api_key)
        

    def inference(self, model_id: str, prompt: str) -> str:
        generation_config = {
            "temperature": 0.5,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 4096,
        }

        model = genai.GenerativeModel(model_name=model_id,
                                    generation_config=generation_config)

        convo = model.start_chat(history=[])

        convo.send_message(prompt.strip())

        return convo.last.text

    
    
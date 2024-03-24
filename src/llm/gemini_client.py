import google.generativeai as GAI

from src.config import Config

class GEMINI: 
    def __init__(self): 
        config = Config()
        api_key = config.get_gemini_api_key()
        GAI.configure(api_key=api_key)

    def inference(self, model_name: str, prompt: str) -> str:
        model = GAI.GenerativeModel(model_name=model_name) 

        messages = [
            {
                "role": "user", 
                "parts": [prompt]
            }
        ]

        response = model.generate_content(messages).text 

        return response




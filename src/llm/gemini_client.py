import google.generativeai as genai

from src.config import Config

class Gemini:
    def __init__(self):
        config = Config()
        api_key = config.get_gemini_api_key()
        genai.configure(api_key=api_key)

    def inference(self, model_id: str, prompt: str) -> str:
        model = genai.GenerativeModel(model_id)
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                retry_count += 1
                print(f"Error occurred. Attempt {retry_count}: {str(e)}")
        
        raise RuntimeError("Failed after 4 attempts due to errors.")

import google.generativeai as genai

from src.config import Config


class Gemini:
    def __init__(self):
        config = Config()
        api_key = config.get_gemini_api_key()
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel('gemini-pro')

    def inference(self, model_id: str, prompt: str) -> str:
        response = self.client.generate_content(contents=prompt.strip())
        return response.text

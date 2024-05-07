import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from src.config import Config

class Gemini:
    def __init__(self):
        config = Config()
        api_key = config.get_gemini_api_key()
        genai.configure(api_key=api_key)

    def inference(self, model_id: str, prompt: str) -> str:
        config = genai.GenerationConfig(temperature=0)
        model = genai.GenerativeModel(model_id, generation_config=config)
        # Set safety settings for the request
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            # You can adjust other categories as needed
        }
        response = model.generate_content(prompt, safety_settings=safety_settings)
        try:
            # Check if the response contains text
            return response.text
        except ValueError:
            # If the response doesn't contain text, check if the prompt was blocked
            print("Prompt feedback:", response.prompt_feedback)
            # Also check the finish reason to see if the response was blocked
            print("Finish reason:", response.candidates[0].finish_reason)
            # If the finish reason was SAFETY, the safety ratings have more details
            print("Safety ratings:", response.candidates[0].safety_ratings)
            # Handle the error or return an appropriate message
            return "Error: Unable to generate content Gemini API"

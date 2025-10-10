import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from src.config import Config
from src.logger import Logger

logger = Logger()
config = Config()

class Gemini:
    def __init__(self):
        api_key = config.get_gemini_api_key()
        if not api_key:
            error_msg = ("Gemini API key not found in configuration. "
                        "Please add your Gemini API key to config.toml under [API_KEYS] "
                        "section as GEMINI = 'your-api-key'")
            logger.error(error_msg)
            raise ValueError(error_msg)
        try:
            genai.configure(api_key=api_key)
            logger.info("Successfully initialized Gemini client")
        except Exception as e:
            error_msg = f"Failed to configure Gemini client: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def inference(self, model_id: str, prompt: str) -> str:
        try:
            logger.info(f"Initializing Gemini model: {model_id}")
            config = genai.GenerationConfig(temperature=0)
            model = genai.GenerativeModel(model_id, generation_config=config)

            safety_settings = {
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            }

            logger.info("Generating response with Gemini")
            response = model.generate_content(prompt, safety_settings=safety_settings)

            try:
                if response.text:
                    logger.info("Successfully generated response")
                    return response.text
                else:
                    error_msg = f"Empty response from Gemini model {model_id}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
            except ValueError:
                logger.error("Failed to get response text")
                logger.error(f"Prompt feedback: {response.prompt_feedback}")
                logger.error(f"Finish reason: {response.candidates[0].finish_reason}")
                logger.error(f"Safety ratings: {response.candidates[0].safety_ratings}")
                return "Error: Unable to generate content with Gemini API"

        except Exception as e:
            error_msg = f"Error during Gemini inference: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

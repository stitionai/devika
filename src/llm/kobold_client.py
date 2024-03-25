import httpx
import json

from src.logger import Logger

# API Documentation at: https://lite.koboldai.net/koboldcpp_api
class Kobold:
    @staticmethod
    def list_model():
        url = "http://localhost:5001/api"
        try:
            # Get current model name
            response = httpx.get(url + "/v1/model")
            # Parse the json response
            data = json.loads(response.text)

            return ["KoboldCpp", data["result"].replace("koboldcpp/", "")]

        except httpx.ConnectError:
            Logger().warning("KoboldCpp not running, please start the server to use models from KoboldCpp.")
        except Exception as e:
            Logger().error(f"Failed to get KoboldCpp model: {e}")

        return []

    def inference(self, model_id: str, prompt: str) -> str:
        url = "http://localhost:5001/api"

        # Use the LLAMA Instruct prompt for reply
        actualprompt = f"\n### Instruction:\n{prompt}\n### Response:\n"

        # Fetch the Max Context Length
        context_length = httpx.get(url + "/extra/true_max_context_length", timeout=None)
        max_context_length = json.loads(context_length.text)["value"]

        data = {
        "max_context_length": max_context_length,
        "max_length": 2048,
        "prompt": actualprompt,
        "quiet": False,
        "rep_pen": 1.1,
        "rep_pen_range": 256,
        "rep_pen_slope": 1,
        "temperature": 0.5,
        "tfs": 1,
        "top_a": 0,
        "top_k": 100,
        "top_p": 0.9,
        "typical": 1
        }

        # Send generate request to KoboldCpp
        response = httpx.post(url + "/v1/generate", json=data, timeout=None)

        # Parse the JSON result
        result = json.loads(response.text)["results"][0]["text"]
        return result

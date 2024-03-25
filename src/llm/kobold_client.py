import httpx
import json

from src.logger import Logger


class Kobold:
    @staticmethod
    def list_model():
        url = "http://localhost:5001/api"
        try:
            response = httpx.get(url + "/v1/model")
            data = json.loads(response.text)
            return ["KoboldCpp", data["result"].replace("koboldcpp/", "")]
        except httpx.ConnectError:
            Logger().warning("KoboldCpp not running, please start the server to use models from KoboldCpp.")
        except Exception as e:
            Logger().error(f"Failed to get KoboldCpp model: {e}")

        return []

    def inference(self, model_id: str, prompt: str) -> str:
        url = "http://localhost:5001/api"
        actualprompt = f"\n### Instruction:\n{prompt}\n### Response:\n"

        data = {
        "max_context_length": 4096,
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

        response = httpx.post(url + "/v1/generate", json=data, timeout=None)
        result = json.loads(response.text)["results"][0]["text"]
        return result

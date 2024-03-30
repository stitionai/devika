import json

from jinja2 import Environment, BaseLoader

from src.llm import LLM

PROMPT = open("src/agents/decision/prompt.jinja2").read().strip()

class Decision:
    def __init__(self, base_model: str):
        self.llm = LLM(model_id=base_model)

    def render(self, prompt: str) -> str:
        env = Environment(loader=BaseLoader())
        template = env.from_string(PROMPT)
        return template.render(prompt=prompt)

    def validate_response(self, response: str):
        response = response.strip().replace("```json", "```")
        
        if response.startswith("```") and response.endswith("```"):
            response = response[3:-3].strip()

        try:
            response = json.loads(response)
        except Exception as _:
            return False
        
        for item in response:
            if "function" not in item or "args" not in item or "reply" not in item:
                return False
        
        return response

    def execute(self, prompt: str, project_name: str) -> str:
        rendered_prompt = self.render(prompt)
        response = self.llm.inference(rendered_prompt, project_name)
        
        valid_response = self.validate_response(response)
        
        while not valid_response:
            print("Invalid response from the model, trying again...")
            return self.execute(prompt, project_name)

        return valid_response
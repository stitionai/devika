import json

from jinja2 import Environment, BaseLoader

from src.llm import LLM

PROMPT = open("src/agents/internal_monologue/prompt.jinja2").read().strip()

class InternalMonologue:
    def __init__(self, base_model: str):
        self.llm = LLM(model_id=base_model)

    def render(self, current_prompt: str) -> str:
        env = Environment(loader=BaseLoader())
        template = env.from_string(PROMPT)
        return template.render(current_prompt=current_prompt)

    def validate_response(self, response: str):
        response = response.strip().replace("```json", "```")
        
        if response.startswith("```") and response.endswith("```"):
            response = response[3:-3].strip()
 
        try:
            response = json.loads(response)
        except Exception as _:
            return False
        
        response = {k.replace("\\", ""): v for k, v in response.items()}

        if "internal_monologue" not in response:
            return False
        else:
            return response["internal_monologue"]

    def execute(self, current_prompt: str, project_name: str) -> str:
        rendered_prompt = self.render(current_prompt)
        response = self.llm.inference(rendered_prompt, project_name)
        
        valid_response = self.validate_response(response)
        
        while not valid_response:
            print("Invalid response from the model, trying again...")
            return self.execute(current_prompt, project_name)

        return valid_response


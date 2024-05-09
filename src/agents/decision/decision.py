from jinja2 import Environment, BaseLoader
from pathlib import Path

from src.services.utils import retry_wrapper, validate_responses
from src.llm import LLM


class Decision:
    def __init__(self, base_model: str):
        self.llm = LLM(model_id=base_model)
        parent = Path(__file__).resolve().parent
        with open(parent.joinpath("prompt.jinja2"), 'r') as file:
            self.prompt_template = file.read().strip()

    def render(self, prompt: str) -> str:
        env = Environment(loader=BaseLoader())
        template = env.from_string(self.prompt_template)
        return template.render(prompt=prompt)

    @validate_responses
    def validate_response(self, response: str):
        for item in response:
            if "function" not in item or "args" not in item or "reply" not in item:
                return False
        
        return response

    @retry_wrapper
    def execute(self, prompt: str, project_name: str) -> str:
        rendered_prompt = self.render(prompt)
        response = self.llm.inference(rendered_prompt, project_name)
        
        valid_response = self.validate_response(response)

        return valid_response

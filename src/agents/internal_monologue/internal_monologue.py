from jinja2 import Environment, BaseLoader
from pathlib import Path

from src.llm import LLM
from src.services.utils import retry_wrapper, validate_responses


class InternalMonologue:
    def __init__(self, base_model: str):
        self.llm = LLM(model_id=base_model)
        parent = Path(__file__).resolve().parent
        with open(parent.joinpath("prompt.jinja2"), 'r') as file:
            self.prompt_template = file.read().strip()

    def render(self, current_prompt: str) -> str:
        env = Environment(loader=BaseLoader())
        template = env.from_string(self.prompt_template)
        return template.render(current_prompt=current_prompt)

    @validate_responses
    def validate_response(self, response: str):
        print('-------------------> ', response)
        print("####", type(response))
        if "internal_monologue" not in response:
            return False
        else:
            return response["internal_monologue"]

    @retry_wrapper
    def execute(self, current_prompt: str, project_name: str) -> str:
        rendered_prompt = self.render(current_prompt)
        response = self.llm.inference(rendered_prompt, project_name)
        valid_response = self.validate_response(response)
        return valid_response

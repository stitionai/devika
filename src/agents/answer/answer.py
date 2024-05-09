from jinja2 import Environment, BaseLoader
from pathlib import Path

from src.services.utils import retry_wrapper, validate_responses
from src.config import Config
from src.llm import LLM


class Answer:
    def __init__(self, base_model: str):
        config = Config()
        self.project_dir = config.get_projects_dir()
        
        self.llm = LLM(model_id=base_model)
        parent = Path(__file__).resolve().parent
        with open(parent.joinpath("prompt.jinja2"), 'r') as file:
            self.prompt_template = file.read().strip()

    def render(
        self, conversation: str, code_markdown: str
    ) -> str:
        env = Environment(loader=BaseLoader())
        template = env.from_string(self.prompt_template)
        return template.render(
            conversation=conversation,
            code_markdown=code_markdown
        )

    @validate_responses
    def validate_response(self, response: str):
        if "response" not in response:
            return False
        else:
            return response["response"]

    @retry_wrapper
    def execute(self, conversation: list, code_markdown: str, project_name: str) -> str:
        prompt = self.render(conversation, code_markdown)
        response = self.llm.inference(prompt, project_name)
        
        valid_response = self.validate_response(response)
        
        return valid_response

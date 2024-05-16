import json

from jinja2 import Environment, BaseLoader

from src.services.utils import retry_wrapper, validate_responses
from src.config import Config
from src.llm import LLM

PROMPT = open("src/agents/answer/prompt.jinja2", "r").read().strip()

class Answer:
    def __init__(self, base_model: str):
        config = Config()
        self.project_dir = config.get_projects_dir()
        
        self.llm = LLM(model_id=base_model)

    def render(
        self, conversation: str, code_markdown: str
    ) -> str:
        env = Environment(loader=BaseLoader())
        template = env.from_string(PROMPT)
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

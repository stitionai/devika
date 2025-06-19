import json
from jinja2 import Environment, BaseLoader
from src.services.utils import retry_wrapper, validate_responses
from src.config import Config
from src.llm import LLM

PROMPT = open("src/agents/performance_optimizer/prompt.jinja2", "r").read().strip()

class PerformanceOptimizer:
    def __init__(self, base_model: str):
        config = Config()
        self.project_dir = config.get_projects_dir()
        self.llm = LLM(model_id=base_model)

    def render(self, code_markdown: str, performance_metrics: str = "") -> str:
        env = Environment(loader=BaseLoader())
        template = env.from_string(PROMPT)
        return template.render(
            code_markdown=code_markdown,
            performance_metrics=performance_metrics
        )

    @validate_responses
    def validate_response(self, response: str):
        if "analysis" not in response or "optimizations" not in response:
            return False
        else:
            return response

    @retry_wrapper
    def execute(self, code_markdown: str, performance_metrics: str, project_name: str) -> str:
        prompt = self.render(code_markdown, performance_metrics)
        response = self.llm.inference(prompt, project_name)
        
        valid_response = self.validate_response(response)
        
        return valid_response
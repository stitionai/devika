from typing import List

from jinja2 import BaseLoader, Environment

from src.agents.agent import Agent
from src.browser.search import BingSearch
from src.llm import LLM


class Researcher(Agent):
    def __init__(self, base_model: str):
        self.bing_search = BingSearch()
        self.llm = LLM(model_id=base_model)

        super().__init__()

    def execute(
        self, step_by_step_plan: str, contextual_keywords: List[str], project_name: str
    ) -> dict | bool:
        contextual_keywords_str = ", ".join(
            map(lambda k: k.capitalize(), contextual_keywords)
        )
        prompt = self.render(
            step_by_step_plan=step_by_step_plan,
            contextual_keywords=contextual_keywords_str,
        )

        response = self.llm.inference(prompt, project_name)

        valid_response = self.validate_response(response)

        while not valid_response:
            print("Invalid response from the model, trying again...")
            return self.execute(step_by_step_plan, contextual_keywords, project_name)

        return valid_response

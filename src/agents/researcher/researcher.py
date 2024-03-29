"""Researcher agent module"""

import json
import os
from typing import List

from src.agents.base import BaseAgent
from src.browser.search import BingSearch


class Researcher(BaseAgent):
    """Researcher agent class"""

    _prompt = (
        open(
            os.path.join(os.path.dirname(__file__), "prompt.jinja2"),
            "r",
            encoding="utf-8",
        )
        .read()
        .strip()
    )

    def __init__(self, base_model: str):
        super().__init__(base_model)
        self.bing_search = BingSearch()

    def validate_response(self, response: str):
        response = response.strip().replace("```json", "```")

        if response.startswith("```") and response.endswith("```"):
            response = response[3:-3].strip()

        try:
            response = json.loads(response)
        except json.JSONDecodeError:
            return False

        response = {k.replace("\\", ""): v for k, v in response.items()}

        if "queries" not in response and "ask_user" not in response:
            return False
        else:
            return {"queries": response["queries"], "ask_user": response["ask_user"]}

    def execute(
        self, step_by_step_plan: str, contextual_keywords: List[str], project_name: str
    ) -> str:
        contextual_keywords_str = ", ".join(
            map(lambda k: k.capitalize(), contextual_keywords)
        )
        prompt = self.render(
            step_by_step_plan=step_by_step_plan, keywords=contextual_keywords_str
        )

        response = self.llm.inference(prompt, project_name)

        valid_response = self.validate_response(response)

        while not valid_response:
            print("Invalid response from the model, trying again...")
            return self.execute(step_by_step_plan, contextual_keywords, project_name)

        return valid_response

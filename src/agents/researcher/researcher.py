import json
from typing import List
import re

from jinja2 import Environment, BaseLoader

from src.llm import LLM
from src.browser.search import BingSearch

PROMPT = open("src/agents/researcher/prompt.jinja2").read().strip()


class Researcher:
    def __init__(self, base_model: str):
        self.bing_search = BingSearch()
        self.llm = LLM(model_id=base_model)

    def render(self, step_by_step_plan: str, contextual_keywords: str) -> str:
        env = Environment(loader=BaseLoader())
        template = env.from_string(PROMPT)
        return template.render(
            step_by_step_plan=step_by_step_plan, contextual_keywords=contextual_keywords
        )

    def validate_response(self, response: str) -> dict | bool:
        response = response.strip().replace("```json", "```")

        blocs_json = re.findall(r"{(.*?)}", response, re.DOTALL)

        resultats_json = []
        for bloc in blocs_json:
            bloc_nettoye = bloc.replace("\n", "").replace("```\n\n```", "")
            bloc_json = json.loads("{" + bloc_nettoye + "}")
            resultats_json.append(bloc_json)

        json_final = json.dumps(resultats_json, indent=4)

        try:
            response = json.loads(json_final)
        except Exception as _:
            return False

        response = {k.replace("\\", ""): v for k, v in response.items()}

        if "queries" not in response and "ask_user" not in response:
            return False
        else:
            return {"queries": response["queries"], "ask_user": response["ask_user"]}

    def execute(
        self, step_by_step_plan: str, contextual_keywords: List[str], project_name: str
    ) -> dict | bool:
        contextual_keywords_str = ", ".join(
            map(lambda k: k.capitalize(), contextual_keywords)
        )
        prompt = self.render(step_by_step_plan, contextual_keywords_str)

        response = self.llm.inference(prompt, project_name)

        valid_response = self.validate_response(response)

        while not valid_response:
            print("Invalid response from the model, trying again...")
            return self.execute(step_by_step_plan, contextual_keywords, project_name)

        return valid_response

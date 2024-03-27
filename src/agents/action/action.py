import json

from jinja2 import Environment, BaseLoader

from src.config import Config
from src.llm import LLM

PROMPT = open("src/agents/action/prompt.jinja2", "r").read().strip()

class Action:
    def __init__(self, base_model: str):
        config = Config()
        self.project_dir = config.get_projects_dir()
        
        self.llm = LLM(model_id=base_model)

    def render(
        self, conversation: str
    ) -> str:
        env = Environment(loader=BaseLoader())
        template = env.from_string(PROMPT)
        return template.render(
            conversation=conversation
        )

    def validate_response(self, response: str):
        response = response.strip().replace("```json", "```")
        
        if response.startswith("```") and response.endswith("```"):
            response = response[3:-3].strip()
 
        try:
            response = json.loads(response)
        except Exception as _:
            return False

        if "response" not in response and "action" not in response:
            return False
        else:
            return response["response"], response["action"]

    def execute(self, conversation: list, project_name: str) -> str:
        prompt = self.render(conversation)
        response = self.llm.inference(prompt, project_name)
        
        valid_response = self.validate_response(response)
        
        while not valid_response:
            print("Invalid response from the model, trying again...")
            return self.execute(conversation, project_name)
        
        print("===" * 10)
        print(valid_response)

        return valid_response

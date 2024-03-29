"""Base class for all agents"""

import json
from jinja2 import Environment, BaseLoader

from src.llm import LLM
from src.config import Config


class BaseAgent:
    """Base class for all agents"""

    _prompt = None

    _response_key = None

    def __init__(self, base_model: str):
        self._config = Config()
        self.llm = LLM(model_id=base_model)
        self._environment = Environment(loader=BaseLoader())

        if self._prompt is None:
            raise ValueError(
                "Prompt not set. Try setting the JINJA2 template in the child class."
            )

        self._template = self._environment.from_string(self._prompt)

    def render(self, conversation: str, code_markdown: str):
        """Render the prompt template"""

        return self._template.render(
            conversation=conversation, code_markdown=code_markdown
        )

    def validate_response(self, response: str):
        """Validate the response from the model"""

        response = response.strip().replace("```json", "```")

        if response.startswith("```") and response.endswith("```"):
            response = response[3:-3].strip()

        try:
            response = json.loads(response)
        except json.JSONDecodeError:
            return False

        if "response" not in response:
            return False

        if self._response_key is not None and self._response_key not in response:
            return False

        response = self._post_validate_response(response)

        if not response:
            return False

        return response["response"], response[self._response_key]

    def execute(self, conversation: list, code_markdown: str, project_name: str):
        """Execute the agent"""

        prompt = self.render(conversation, code_markdown)
        response = self.llm.inference(prompt, project_name)

        valid_response = self.validate_response(response)

        while not valid_response:
            return self.execute(conversation, code_markdown, project_name)

        return valid_response

    def _post_validate_response(self, response: str):
        """Post validate the response from the model"""

        return response

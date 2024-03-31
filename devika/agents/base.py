"""Base class for all agents"""

import json
import os
from typing import Dict, List

from jinja2 import BaseLoader, Environment

from devika.config import Config
from devika.llm import LLM


class BaseAgent:
    """Base class for all agents"""

    _prompt = None

    _response_key = None

    def __init__(self, base_model: str):
        self._config = Config()
        self.llm = LLM(model_id=base_model)
        self._environment = Environment(loader=BaseLoader())
        self._project_dir = self._config.get_projects_dir()

        if self._prompt is None:
            raise ValueError(
                "Prompt not set. Try setting the JINJA2 template in the child class."
            )

        self._template = self._environment.from_string(self._prompt)

    def render(self, **kwargs):
        """Render the prompt template"""

        return self._template.render(**kwargs)

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

        if self._response_key is None:
            return response["response"]

        return response["response"], response[self._response_key]

    def _execute(self, project_name: str, **kwargs):
        """Execute the agent"""

        prompt = self.render(**kwargs)
        response = self.llm.inference(prompt, project_name)

        valid_response = self.validate_response(response)

        while not valid_response:
            return self._execute(project_name, **kwargs)

        return valid_response

    def execute(self, **kwargs):
        """Action execution method to be inherited by the child classes"""
        self._execute(**kwargs)

    def _post_validate_response(self, response: str):
        """Post validate the response from the model"""

        return response


class BaseWriterAgent(BaseAgent):
    """Base class for all writer agents"""

    # TODO: Add emulate_code_writing method to the base class

    def save_code_to_project(self, response: List[Dict[str, str]], project_name: str):
        """Save the code to the project directory"""
        file_path_dir = None
        project_name = project_name.lower().replace(" ", "-")

        for file in response:
            file_path = f"{self._project_dir}/{project_name}/{file['file']}"
            file_path_dir = file_path[: file_path.rfind("/")]
            os.makedirs(file_path_dir, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(file["code"])

        return file_path_dir

    def get_project_path(self, project_name: str):
        """Get the project path"""
        project_name = project_name.lower().replace(" ", "-")
        return f"{self._project_dir}/{project_name}"

    def response_to_markdown_prompt(self, response: List[Dict[str, str]]) -> str:
        """Response to markdown prompt"""
        response = "\n".join(
            [f"File: `{file['file']}`:\n```\n{file['code']}\n```" for file in response]
        )
        return f"~~~\n{response}\n~~~"

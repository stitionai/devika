"""Decision Agent Module"""

import os

from src.agents import BaseAgent


class Decision(BaseAgent):
    """Decision agent class"""

    _prompt = (
        open(
            os.path.join(os.path.dirname(__file__), "prompt.jinja2"),
            "r",
            encoding="utf-8",
        )
        .read()
        .strip()
    )

    def _post_validate_response(self, response: str):
        """Post validate respone for decision agent."""

        for item in response:
            # TODO: Check if the change is correct since I am not sure what is the item here
            if item not in ["function", "args", "reply"]:
                return False
        return response

    def execute(self, prompt: str, project_name: str):
        return self._execute(prompt=prompt, project_name=project_name)

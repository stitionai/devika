"""Formatter agent module"""

import os

from src.agents.base import BaseAgent


# TODO: Confirm the Formatter agent class inherits from the BaseAgent class
class Formatter(BaseAgent):
    """Formatter agent class"""

    _prompt = (
        open(
            os.path.join(os.path.dirname(__file__), "prompt.jinja2"),
            "r",
            encoding="utf-8",
        )
        .read()
        .strip()
    )

    def execute(self, raw_text: str, project_name: str):
        return self._execute(raw_text=raw_text, project_name=project_name)

"""Reporter Agent Module."""

import os

from src.agents import BaseAgent


class Reporter(BaseAgent):
    """Reporter agent class"""

    _prompt = (
        open(
            os.path.join(os.path.dirname(__file__), "prompt.jinja2"),
            "r",
            encoding="utf-8",
        )
        .read()
        .strip()
    )

    def execute(self, conversation: list, code_markdown: str, project_name: str):
        return self._execute(
            conversation=conversation,
            code_markdown=code_markdown,
            project_name=project_name,
        )

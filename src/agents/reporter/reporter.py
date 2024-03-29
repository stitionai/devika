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

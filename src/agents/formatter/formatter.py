"""Formatter agent module"""

import os

from src.agents import BaseAgent


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

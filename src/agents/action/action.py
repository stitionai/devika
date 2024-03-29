"""Action agent module"""

import os

from src.agents import BaseAgent


class Action(BaseAgent):
    """Action agent class"""

    _prompt = (
        open(
            os.path.join(os.path.dirname(__file__), "prompt.jinja2"),
            "r",
            encoding="utf-8",
        )
        .read()
        .strip()
    )

    _response_key = "action"

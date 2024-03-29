"""Internal Monologue Agent"""

import os

from src.agents import BaseAgent


class InternalMonologue(BaseAgent):
    """Internal Monologue agent class"""

    _prompt = (
        open(
            os.path.join(os.path.dirname(__file__), "prompt.jinja2"),
            "r",
            encoding="utf-8",
        )
        .read()
        .strip()
    )

    _response_key = "internal_monologue"

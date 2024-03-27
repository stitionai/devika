"""This module allows the agent to take up the ideation phase of the design process."""

from src.agents.roles import Designer, Ideator

from src.config import Config
from src.project import ProjectManager


class Ideation:

    def __init__(self):
        self.ideation = Ideator()
        self.design = Designer()

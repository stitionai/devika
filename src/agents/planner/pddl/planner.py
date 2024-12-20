"""
PDDL-based planner integration for Devika's advanced planning system.
Based on the approach described in https://arxiv.org/abs/2305.14909
"""
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from .domain import PDDLDomain
from .problem import PDDLProblem
from .predicate import PDDLPredicate
from .action import PDDLAction

@dataclass
class Plan:
    """Represents a sequence of actions forming a plan."""
    steps: List[Dict[str, str]]  # List of {action: params} dicts
    cost: Optional[float] = None
    metadata: Dict[str, any] = None

class PDDLPlanner:
    """PDDL-based planner that integrates with LLM for domain modeling."""

    def __init__(self, llm_client):
        """Initialize planner with LLM client for domain modeling."""
        self.llm = llm_client

    async def generate_domain_model(self, task_description: str) -> PDDLDomain:
        """Generate PDDL domain model from natural language description."""
        # Prompt LLM to generate domain model
        prompt = f"""Given the following task description, generate a PDDL domain model
        with appropriate types, predicates, and actions:

        {task_description}

        Format the response as a Python dict with keys:
        - name: domain name
        - types: list of type names
        - predicates: list of {{"name": pred_name, "parameters": [{"name": param_name, "type": type_name}]}}
        - actions: list of {{"name": action_name, "parameters": [...], "preconditions": [...], "effects": [...]}}
        """

        response = await self.llm.generate(prompt)
        # Parse response and create PDDLDomain
        domain_spec = eval(response)  # Safe since we control the LLM prompt

        domain = PDDLDomain(name=domain_spec["name"])
        domain.types = domain_spec["types"]

        for pred_spec in domain_spec["predicates"]:
            domain.add_predicate(PDDLPredicate(**pred_spec))

        for action_spec in domain_spec["actions"]:
            domain.add_action(PDDLAction(**action_spec))

        return domain

    async def solve(self, domain: PDDLDomain, problem: PDDLProblem) -> Optional[Plan]:
        """Generate a plan for the given PDDL domain and problem."""
        # Convert domain and problem to PDDL
        domain_pddl = domain.to_pddl()
        problem_pddl = problem.to_pddl()

        # Use LLM to generate plan
        prompt = f"""Given the following PDDL domain and problem, generate a valid plan:

        Domain:
        {domain_pddl}

        Problem:
        {problem_pddl}

        Format the response as a list of action applications, one per line:
        (action param1 param2 ...)
        """

        response = await self.llm.generate(prompt)

        # Parse plan from response
        if not response.strip():
            return None

        steps = []
        for line in response.strip().split('\n'):
            if not line.strip():
                continue
            # Parse (action param1 param2 ...) format
            parts = line.strip('()').split()
            steps.append({parts[0]: ' '.join(parts[1:])})

        return Plan(steps=steps)

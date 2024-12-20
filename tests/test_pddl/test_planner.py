"""
Tests for the PDDL planner implementation.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.agents.planner.pddl import PDDLPlanner, PDDLDomain, PDDLProblem

@pytest.fixture
def mock_llm():
    """Create a mock LLM client."""
    llm = MagicMock()
    llm.generate = AsyncMock()
    return llm

@pytest.mark.asyncio
async def test_generate_domain_model(mock_llm):
    """Test domain model generation from task description."""
    mock_llm.generate.return_value = """{
        "name": "navigation",
        "types": ["location", "vehicle"],
        "predicates": [
            {"name": "at", "parameters": [{"name": "loc", "type": "location"}]}
        ],
        "actions": [
            {
                "name": "move",
                "parameters": [
                    {"from": "location"},
                    {"to": "location"}
                ],
                "preconditions": ["at ?from"],
                "effects": ["not (at ?from)", "at ?to"]
            }
        ]
    }"""

    planner = PDDLPlanner(mock_llm)
    domain = await planner.generate_domain_model("Navigate from A to B")

    assert domain.name == "navigation"
    assert "location" in domain.types
    assert len(domain.predicates) == 1
    assert len(domain.actions) == 1

@pytest.mark.asyncio
async def test_solve_planning_problem(mock_llm):
    """Test plan generation for a PDDL problem."""
    mock_llm.generate.return_value = """(move locA locB)
(move locB locC)"""

    planner = PDDLPlanner(mock_llm)
    domain = PDDLDomain(name="navigation")
    problem = PDDLProblem(
        name="nav-prob1",
        domain="navigation",
        objects={"location": ["locA", "locB", "locC"]},
        init=["at locA"],
        goal=["at locC"]
    )

    plan = await planner.solve(domain, problem)

    assert plan is not None
    assert len(plan.steps) == 2
    assert plan.steps[0] == {"move": "locA locB"}
    assert plan.steps[1] == {"move": "locB locC"}

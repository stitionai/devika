"""
Tests for the PDDL predicate implementation.
"""
import pytest
from src.agents.planner.pddl.predicate import PDDLPredicate

def test_pddl_predicate():
    """Test PDDLPredicate creation and PDDL output."""
    pred = PDDLPredicate(
        name="at",
        parameters=[{"loc": "location"}]
    )
    assert pred.to_pddl() == "(at ?loc - location)"

def test_pddl_predicate_multiple_params():
    """Test PDDLPredicate with multiple parameters."""
    pred = PDDLPredicate(
        name="connected",
        parameters=[
            {"from": "location"},
            {"to": "location"}
        ]
    )
    assert pred.to_pddl() == "(connected ?from - location ?to - location)"

"""
Tests for the PDDL action implementation.
"""
import pytest
from src.agents.planner.pddl import PDDLAction

def test_basic_action():
    """Test basic PDDLAction creation and PDDL output."""
    action = PDDLAction(
        name="move",
        parameters=[
            {"from": "location"},
            {"to": "location"}
        ],
        preconditions=["at ?from", "connected ?from ?to"],
        effects=["not (at ?from)", "at ?to"]
    )
    pddl = action.to_pddl()
    assert ":action move" in pddl
    assert ":parameters (?from - location ?to - location)" in pddl
    assert ":precondition (and (at ?from) (connected ?from ?to))" in pddl
    assert ":effect (and (not (at ?from)) (at ?to))" in pddl

def test_temporal_action():
    """Test PDDLAction with duration for temporal planning."""
    action = PDDLAction(
        name="drive",
        parameters=[
            {"v": "vehicle"},
            {"from": "location"},
            {"to": "location"}
        ],
        preconditions=["at ?v ?from"],
        effects=["not (at ?v ?from)", "at ?v ?to"],
        duration=5.0
    )
    pddl = action.to_pddl()
    assert ":duration 5.0" in pddl

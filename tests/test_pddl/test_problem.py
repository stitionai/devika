"""
Tests for the PDDL problem implementation.
"""
import pytest
from src.agents.planner.pddl import PDDLProblem

def test_basic_problem():
    """Test basic PDDLProblem creation and PDDL output."""
    problem = PDDLProblem(
        name="nav-prob1",
        domain="navigation",
        objects={"location": ["locA", "locB", "locC"]},
        init=["at locA", "connected locA locB", "connected locB locC"],
        goal=["at locC"]
    )
    pddl = problem.to_pddl()
    assert "(define (problem nav-prob1)" in pddl
    assert "(:domain navigation)" in pddl
    assert "(:objects locA locB locC - location)" in pddl
    assert "(:init (at locA) (connected locA locB) (connected locB locC))" in pddl
    assert "(:goal (and (at locC)))" in pddl

def test_problem_with_metric():
    """Test PDDLProblem with optimization metric."""
    problem = PDDLProblem(
        name="nav-prob2",
        domain="navigation",
        objects={"location": ["locA", "locB"],
                "vehicle": ["car1"]},
        init=["at car1 locA", "connected locA locB"],
        goal=["at car1 locB"],
        metric="minimize (total-cost)"
    )
    pddl = problem.to_pddl()
    assert "(:metric minimize (total-cost))" in pddl

"""
Tests for the PDDL domain implementation.
"""
import pytest
from src.agents.planner.pddl import PDDLDomain, PDDLPredicate

def test_pddl_domain_creation():
    """Test basic PDDLDomain creation."""
    domain = PDDLDomain(name="navigation")
    assert domain.name == "navigation"
    assert domain.requirements == ['strips', 'typing']
    assert domain.types == []
    assert domain.predicates == []

def test_pddl_domain_with_predicates():
    """Test PDDLDomain with predicates."""
    domain = PDDLDomain(name="navigation")
    pred1 = PDDLPredicate(
        name="at",
        parameters=[{"loc": "location"}]
    )
    pred2 = PDDLPredicate(
        name="connected",
        parameters=[
            {"from": "location"},
            {"to": "location"}
        ]
    )
    domain.add_predicate(pred1)
    domain.add_predicate(pred2)

    pddl = domain.to_pddl()
    assert "(define (domain navigation)" in pddl
    assert ":requirements :strips :typing" in pddl
    assert "(at ?loc - location)" in pddl
    assert "(connected ?from - location ?to - location)" in pddl

def test_pddl_domain_with_types():
    """Test PDDLDomain with custom types."""
    domain = PDDLDomain(
        name="robot-world",
        types=["location", "robot", "object"]
    )
    pddl = domain.to_pddl()
    assert "(:types location robot object)" in pddl

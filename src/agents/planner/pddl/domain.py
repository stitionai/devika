"""
PDDL Domain class for defining planning domains.
"""
from typing import List, Dict, Optional
from dataclasses import dataclass, field

from .predicate import PDDLPredicate

@dataclass
class PDDLDomain:
    """Represents a PDDL domain with predicates and requirements."""
    name: str
    predicates: List[PDDLPredicate] = field(default_factory=list)
    requirements: List[str] = field(default_factory=lambda: ['strips', 'typing'])
    types: List[str] = field(default_factory=list)

    def add_predicate(self, predicate: PDDLPredicate) -> None:
        """Add a predicate to the domain."""
        self.predicates.append(predicate)

    def to_pddl(self) -> str:
        """Convert the domain to PDDL string representation."""
        pddl = [f"(define (domain {self.name})"]

        # Add requirements
        if self.requirements:
            reqs = ' '.join(f":{req}" for req in self.requirements)
            pddl.append(f"  (:requirements {reqs})")

        # Add types
        if self.types:
            types = ' '.join(self.types)
            pddl.append(f"  (:types {types})")

        # Add predicates
        if self.predicates:
            pddl.append("  (:predicates")
            for pred in self.predicates:
                pddl.append(f"    {pred.to_pddl()}")
            pddl.append("  )")

        pddl.append(")")
        return '\n'.join(pddl)

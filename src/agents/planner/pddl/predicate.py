"""
PDDL Predicate class for defining planning predicates.
"""
from typing import List, Dict, Optional
from dataclasses import dataclass, field

@dataclass
class PDDLPredicate:
    """Represents a PDDL predicate with typed parameters."""
    name: str
    parameters: List[Dict[str, str]]  # List of {name: type} dicts

    def to_pddl(self) -> str:
        """Convert the predicate to PDDL string representation."""
        params = ' '.join(f"?{name} - {type}"
                         for param in self.parameters
                         for name, type in param.items())
        return f"({self.name} {params})"

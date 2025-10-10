"""
PDDL Action class for defining planning actions.
"""
from typing import List, Dict, Optional
from dataclasses import dataclass, field

@dataclass
class PDDLAction:
    """Represents a PDDL action with parameters, preconditions, and effects."""
    name: str
    parameters: List[Dict[str, str]]  # List of {name: type} dicts
    preconditions: List[str]
    effects: List[str]
    duration: Optional[float] = None  # For temporal planning support

    def to_pddl(self) -> str:
        """Convert the action to PDDL string representation."""
        # Format parameters
        params = ' '.join(f"?{name} - {type}"
                         for param in self.parameters
                         for name, type in param.items())

        # Format preconditions and effects
        pre = ' '.join(f"({p})" if not p.startswith('(') else p
                      for p in self.preconditions)
        eff = ' '.join(f"({e})" if not e.startswith('(') else e
                      for e in self.effects)

        # Basic action format
        pddl = [
            f"  (:action {self.name}",
            f"    :parameters ({params})",
            f"    :precondition (and {pre})",
            f"    :effect (and {eff})"
        ]

        # Add duration if specified (for temporal planning)
        if self.duration is not None:
            pddl.insert(2, f"    :duration {self.duration}")

        pddl.append("  )")
        return '\n'.join(pddl)

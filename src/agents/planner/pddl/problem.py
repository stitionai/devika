"""
PDDL Problem class for defining planning problems.
"""
from typing import List, Dict, Optional
from dataclasses import dataclass, field

@dataclass
class PDDLProblem:
    """Represents a PDDL problem with objects, initial state, and goal state."""
    name: str
    domain: str
    objects: Dict[str, List[str]]  # type -> list of objects
    init: List[str]  # List of initial state predicates
    goal: List[str]  # List of goal state predicates
    metric: Optional[str] = None  # For optimization problems

    def to_pddl(self) -> str:
        """Convert the problem to PDDL string representation."""
        pddl = [
            f"(define (problem {self.name})",
            f"  (:domain {self.domain})"
        ]

        # Add objects
        if self.objects:
            obj_strs = []
            for type_name, objs in self.objects.items():
                obj_list = ' '.join(objs)
                obj_strs.append(f"{obj_list} - {type_name}")
            pddl.append(f"  (:objects {' '.join(obj_strs)})")

        # Add initial state
        init_str = ' '.join(f"({pred})" if not pred.startswith('(') else pred
                           for pred in self.init)
        pddl.append(f"  (:init {init_str})")

        # Add goal state
        goal_str = ' '.join(f"({pred})" if not pred.startswith('(') else pred
                           for pred in self.goal)
        pddl.append(f"  (:goal (and {goal_str}))")

        # Add optimization metric if specified
        if self.metric:
            pddl.append(f"  (:metric {self.metric})")

        pddl.append(")")
        return '\n'.join(pddl)

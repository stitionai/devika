"""
SWE-bench integration module for Devika.

This module provides integration with the SWE-bench benchmark for evaluating
code generation capabilities on real-world GitHub issues.
"""

from .swebench import SWEBenchRunner
from .dataset import SWEBenchDataset
from .evaluator import SWEBenchEvaluator
from .reporter import SWEBenchReporter

__all__ = [
    'SWEBenchRunner',
    'SWEBenchDataset',
    'SWEBenchEvaluator',
    'SWEBenchReporter',
]

"""Pytest configuration for benchmark tests."""

import pytest
from pathlib import Path

@pytest.fixture
def sample_instance():
    """Sample benchmark instance for testing."""
    return {
        'instance_id': 'test_instance',
        'repo': 'test/repo',
        'issue': 'Sample issue description',
        'patch': 'Sample patch content'
    }

@pytest.fixture
def sample_results():
    """Sample benchmark results for testing."""
    return {
        'test_instance_1': {
            'status': 'success',
            'metrics': {'accuracy': 0.95}
        },
        'test_instance_2': {
            'status': 'error',
            'error': 'Test error message'
        }
    }

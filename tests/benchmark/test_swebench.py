"""Tests for SWE-bench integration."""

import json
import pytest
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.benchmark.swebench import (
    SWEBenchRunner,
    SWEBenchDataset,
    SWEBenchEvaluator,
    SWEBenchReporter
)

def test_dataset_loading():
    """Test dataset loading functionality."""
    dataset = SWEBenchDataset("princeton-nlp/SWE-bench_Lite")
    instances = dataset.load_instances()
    assert isinstance(instances, list)
    assert len(instances) > 0

def test_reporter_summary():
    """Test report generation."""
    reporter = SWEBenchReporter()
    results = {
        'test1': {'status': 'success'},
        'test2': {'status': 'error'}
    }
    report = reporter.generate_report(results)
    assert report['summary']['total_instances'] == 2
    assert report['summary']['successful'] == 1
    assert report['summary']['failed'] == 1
    assert report['summary']['success_rate'] == 0.5

@pytest.fixture
def temp_working_dir(tmp_path):
    """Fixture for temporary working directory."""
    return tmp_path / "swebench_test"

@pytest.fixture
def mock_subprocess():
    """Mock subprocess for testing Docker evaluation."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(
            stdout='Test output\nMetrics: {"accuracy": 0.95}',
            returncode=0
        )
        yield mock_run

def test_runner_initialization(temp_working_dir):
    """Test runner initialization."""
    runner = SWEBenchRunner(
        dataset_name="princeton-nlp/SWE-bench_Lite",
        working_dir=temp_working_dir
    )
    assert runner.working_dir.exists()
    assert isinstance(runner.dataset, SWEBenchDataset)
    assert isinstance(runner.evaluator, SWEBenchEvaluator)
    assert isinstance(runner.reporter, SWEBenchReporter)

def test_evaluator_initialization(temp_working_dir):
    """Test evaluator initialization."""
    evaluator = SWEBenchEvaluator(working_dir=temp_working_dir)
    assert evaluator.working_dir.exists()
    assert evaluator.max_workers == 4

@pytest.mark.parametrize("max_workers", [1, 4, 8])
def test_evaluator_max_workers(max_workers):
    """Test evaluator with different worker counts."""
    evaluator = SWEBenchEvaluator(max_workers=max_workers)
    assert evaluator.max_workers == max_workers

def test_evaluator_docker_run(temp_working_dir, mock_subprocess, sample_instance):
    """Test Docker-based evaluation."""
    evaluator = SWEBenchEvaluator(working_dir=temp_working_dir)

    # Mock successful evaluation output
    mock_subprocess.return_value.stdout = (
        f"{sample_instance['instance_id']}: "
        '{"success": true, "metrics": {"accuracy": 0.95}}\n'
    )

    results = evaluator.evaluate_instances([sample_instance], run_id="test_run")

    assert sample_instance['instance_id'] in results
    result = results[sample_instance['instance_id']]
    assert result['status'] == 'success'
    assert result['metrics']['accuracy'] == 0.95

    # Verify Docker command
    mock_subprocess.assert_called_once()
    cmd_args = mock_subprocess.call_args[0][0]
    assert '--predictions_path' in cmd_args
    assert '--max_workers' in cmd_args
    assert str(evaluator.max_workers) in cmd_args

def test_evaluator_docker_failure(temp_working_dir, mock_subprocess, sample_instance):
    """Test Docker evaluation failure handling."""
    evaluator = SWEBenchEvaluator(working_dir=temp_working_dir)

    # Mock subprocess failure
    error_msg = "Docker evaluation failed"
    mock_subprocess.side_effect = subprocess.CalledProcessError(
        1, [], output=error_msg
    )

    results = evaluator.evaluate_instances([sample_instance])

    assert sample_instance['instance_id'] in results
    result = results[sample_instance['instance_id']]
    assert result['status'] == 'error'
    assert 'Docker evaluation failed' in result['error']

def test_evaluator_parse_results():
    """Test evaluation results parsing."""
    evaluator = SWEBenchEvaluator()

    # Test successful parsing
    output = 'test_1: {"accuracy": 0.95}\ntest_2: {"accuracy": 0.85}\n'
    results = evaluator._parse_evaluation_results(output)

    assert len(results) == 2
    assert results['test_1']['status'] == 'success'
    assert results['test_1']['metrics']['accuracy'] == 0.95
    assert results['test_2']['metrics']['accuracy'] == 0.85

def test_evaluator_parse_results_failure():
    """Test evaluation results parsing failure."""
    evaluator = SWEBenchEvaluator()

    # Test invalid JSON
    output = 'test_1: invalid_json\n'
    results = evaluator._parse_evaluation_results(output)

    assert results['test_1']['status'] == 'error'
    assert 'Failed to parse metrics' in results['test_1']['error']

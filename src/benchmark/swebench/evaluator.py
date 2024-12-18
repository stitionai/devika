"""Docker-based evaluation harness for SWE-bench."""

import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class SWEBenchEvaluator:
    """Evaluator for running SWE-bench in Docker containers."""

    def __init__(self, max_workers: int = 4, working_dir: Optional[Path] = None):
        """Initialize evaluator.

        Args:
            max_workers: Number of parallel workers
            working_dir: Working directory for evaluation files
        """
        self.max_workers = max_workers
        self.working_dir = working_dir or Path(tempfile.mkdtemp(prefix='swebench_'))
        self.working_dir.mkdir(parents=True, exist_ok=True)

    def evaluate_instances(
        self,
        instances: List[Dict],
        run_id: Optional[str] = None
    ) -> Dict:
        """Evaluate benchmark instances.

        Args:
            instances: List of benchmark instances to evaluate
            run_id: Optional identifier for this evaluation run

        Returns:
            Dictionary containing evaluation results
        """
        results = {}
        run_dir = self.working_dir / (run_id or 'default')
        run_dir.mkdir(parents=True, exist_ok=True)

        # Save predictions for batch evaluation
        predictions_dir = run_dir / 'predictions'
        predictions_dir.mkdir(parents=True, exist_ok=True)

        for instance in instances:
            try:
                # Save instance prediction
                instance_dir = predictions_dir / instance['instance_id']
                instance_dir.mkdir(parents=True, exist_ok=True)
                with open(instance_dir / 'prediction.json', 'w') as f:
                    json.dump(instance, f, indent=2)
            except Exception as e:
                logger.error(f"Error preparing {instance['instance_id']}: {e}")
                results[instance['instance_id']] = {
                    'status': 'error',
                    'error': f"Failed to prepare instance: {str(e)}"
                }

        # Run batch evaluation using SWE-bench harness
        try:
            result = self._run_docker_evaluation(predictions_dir, run_id)
            results.update(self._parse_evaluation_results(result))
        except Exception as e:
            logger.error(f"Docker evaluation failed: {e}")
            for instance in instances:
                if instance['instance_id'] not in results:
                    results[instance['instance_id']] = {
                        'status': 'error',
                        'error': f"Docker evaluation failed: {str(e)}"
                    }

        return results

    def _run_docker_evaluation(self, predictions_dir: Path, run_id: str) -> str:
        """Run Docker-based evaluation using SWE-bench harness.

        Args:
            predictions_dir: Directory containing instance predictions
            run_id: Identifier for this evaluation run

        Returns:
            Raw evaluation output
        """
        cmd = [
            'python', '-m', 'swebench.harness.run_evaluation',
            '--predictions_path', str(predictions_dir),
            '--max_workers', str(self.max_workers),
            '--run_id', run_id or 'default'
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Docker evaluation command failed: {e.output}")
            raise RuntimeError(f"Docker evaluation failed: {str(e)}")

    def _parse_evaluation_results(self, output: str) -> Dict:
        """Parse evaluation output to extract metrics.

        Args:
            output: Raw evaluation output string

        Returns:
            Dictionary containing parsed metrics per instance
        """
        results = {}
        try:
            # Extract results from evaluation output
            # Format: instance_id: {metrics}
            for line in output.splitlines():
                if ':' in line:
                    instance_id, metrics_str = line.split(':', 1)
                    instance_id = instance_id.strip()
                    try:
                        metrics = json.loads(metrics_str.strip())
                        results[instance_id] = {
                            'status': 'success',
                            'metrics': metrics
                        }
                    except json.JSONDecodeError:
                        results[instance_id] = {
                            'status': 'error',
                            'error': f"Failed to parse metrics: {metrics_str}"
                        }
        except Exception as e:
            logger.error(f"Failed to parse evaluation results: {e}")
            raise RuntimeError(f"Failed to parse evaluation results: {str(e)}")

        return results

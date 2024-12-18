"""Main SWE-bench runner implementation."""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from .dataset import SWEBenchDataset
from .evaluator import SWEBenchEvaluator
from .reporter import SWEBenchReporter

logger = logging.getLogger(__name__)

class SWEBenchRunner:
    """Main class for running SWE-bench benchmarks."""

    def __init__(
        self,
        dataset_name: str = "princeton-nlp/SWE-bench",
        max_workers: int = 4,
        working_dir: Optional[Path] = None
    ):
        """Initialize SWE-bench runner.

        Args:
            dataset_name: HuggingFace dataset name
            max_workers: Number of parallel workers for evaluation
            working_dir: Working directory for benchmark files
        """
        self.dataset = SWEBenchDataset(dataset_name)
        self.evaluator = SWEBenchEvaluator(max_workers=max_workers)
        self.reporter = SWEBenchReporter()
        self.working_dir = working_dir or Path.cwd() / "swebench_results"
        self.working_dir.mkdir(parents=True, exist_ok=True)

    def run_benchmark(
        self,
        instance_ids: Optional[List[str]] = None,
        run_id: Optional[str] = None
    ) -> Dict:
        """Run benchmark evaluation.

        Args:
            instance_ids: Optional list of specific instances to evaluate
            run_id: Optional identifier for this benchmark run

        Returns:
            Dictionary containing benchmark results
        """
        logger.info("Loading benchmark dataset...")
        instances = self.dataset.load_instances(instance_ids)

        logger.info("Running evaluations...")
        results = self.evaluator.evaluate_instances(instances, run_id)

        logger.info("Generating report...")
        report = self.reporter.generate_report(results)

        # Save results
        results_file = self.working_dir / f"results_{run_id or 'default'}.json"
        self.reporter.save_report(report, results_file)

        return report

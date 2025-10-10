"""Results reporting for SWE-bench benchmark."""

import json
from pathlib import Path
from typing import Dict

class SWEBenchReporter:
    """Reporter for SWE-bench benchmark results."""

    def generate_report(self, results: Dict) -> Dict:
        """Generate benchmark report.

        Args:
            results: Dictionary containing benchmark results

        Returns:
            Dictionary containing formatted report
        """
        report = {
            'summary': self._generate_summary(results),
            'details': results
        }
        return report

    def save_report(self, report: Dict, output_file: Path):
        """Save benchmark report to file.

        Args:
            report: Dictionary containing benchmark report
            output_file: Path to save report
        """
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

    def _generate_summary(self, results: Dict) -> Dict:
        """Generate summary statistics from results.

        Args:
            results: Dictionary containing benchmark results

        Returns:
            Dictionary containing summary statistics
        """
        total = len(results)
        successful = sum(1 for r in results.values() if r.get('status') == 'success')
        failed = sum(1 for r in results.values() if r.get('status') == 'error')

        return {
            'total_instances': total,
            'successful': successful,
            'failed': failed,
            'success_rate': successful / total if total > 0 else 0
        }

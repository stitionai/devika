"""SWE-bench dataset loading and management."""

from typing import Dict, List, Optional
from datasets import load_dataset

class SWEBenchDataset:
    """Handler for SWE-bench dataset operations."""

    def __init__(self, dataset_name: str = "princeton-nlp/SWE-bench"):
        """Initialize dataset handler.

        Args:
            dataset_name: HuggingFace dataset name
        """
        self.dataset_name = dataset_name
        self.dataset = None

    def load_instances(self, instance_ids: Optional[List[str]] = None) -> List[Dict]:
        """Load benchmark instances.

        Args:
            instance_ids: Optional list of specific instances to load

        Returns:
            List of benchmark instances
        """
        if self.dataset is None:
            self.dataset = load_dataset(self.dataset_name, split='test')

        if instance_ids:
            instances = [
                inst for inst in self.dataset
                if inst['instance_id'] in instance_ids
            ]
        else:
            instances = list(self.dataset)

        return instances

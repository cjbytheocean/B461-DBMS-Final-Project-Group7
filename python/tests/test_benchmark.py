"""Public benchmark tests shared by student_starter and instructor_reference."""

import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from benchmark import run_benchmark
from config import DEFAULT_PAGE_CAPACITY


class BenchmarkTests(unittest.TestCase):
    def test_benchmark_writes_csv(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_csv = Path(temp_dir) / "results.csv"
            rows = run_benchmark(
                output_csv=str(output_csv),
                policies=("lru",),
                buffer_sizes=(4,),
                page_capacities=(DEFAULT_PAGE_CAPACITY,),
                workload_types=("point",),
                operation_count=10,
                seed=5,
            )

            self.assertEqual(len(rows), 1)
            with output_csv.open("r", newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                self.assertEqual(len(list(reader)), 1)


if __name__ == "__main__":
    unittest.main()

"""Public integration tests shared by student_starter and instructor_reference."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dbsim.simulation import run_simulation


class IntegrationTests(unittest.TestCase):
    def test_run_simulation_smoke(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_file = Path(temp_dir) / "sim.db"
            result = run_simulation(
                db_file=str(db_file),
                pool_size=4,
                replacement_policy="clock",
                workload_type="range",
                operation_count=25,
                seed=11,
            )

            self.assertEqual(result["operation_count"], 25)
            self.assertGreaterEqual(result["disk_reads"], 1)
            self.assertGreaterEqual(result["buffer_misses"], 1)


if __name__ == "__main__":
    unittest.main()

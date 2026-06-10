"""Public workload tests shared by student_starter and instructor_reference."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dbsim.workload import WorkloadGenerator


class WorkloadGeneratorTests(unittest.TestCase):
    def test_point_workload_is_reproducible(self) -> None:
        first = WorkloadGenerator(seed=7, key_space=20)
        second = WorkloadGenerator(seed=7, key_space=20)

        self.assertEqual(
            first.generate("point", count=8),
            second.generate("point", count=8),
        )

    def test_range_workload_stays_within_key_space(self) -> None:
        generator = WorkloadGenerator(seed=11, key_space=20)
        operations = generator.generate_range_workload(count=5, width=4)

        self.assertEqual(len(operations), 5)
        for operation in operations:
            self.assertEqual(operation.kind, "range")
            self.assertIsNotNone(operation.start_key)
            self.assertIsNotNone(operation.end_key)
            self.assertLessEqual(operation.start_key, operation.end_key)
            self.assertLess(operation.end_key, 20)

    def test_mixed_workload_is_reproducible_and_varied(self) -> None:
        first = WorkloadGenerator(seed=13, key_space=25)
        second = WorkloadGenerator(seed=13, key_space=25)

        first_ops = first.generate("mixed", count=12)
        second_ops = second.generate("mixed", count=12)

        self.assertEqual(first_ops, second_ops)
        self.assertEqual(len(first_ops), 12)
        self.assertTrue(any(operation.kind == "search" for operation in first_ops))
        self.assertTrue(any(operation.kind in {"range", "scan", "insert"} for operation in first_ops))


if __name__ == "__main__":
    unittest.main()

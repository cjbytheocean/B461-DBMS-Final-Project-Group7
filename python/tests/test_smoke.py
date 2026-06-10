"""Public smoke tests shared by student_starter and instructor_reference."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from benchmark import run_benchmark
from dbsim.bplustree import BPlusTree
from dbsim.buffer_pool import BufferPoolManager
from dbsim.disk_manager import DiskManager
from dbsim.replacement import ClockReplacer, LRUReplacer
from dbsim.simulation import run_simulation
from dbsim.workload import WorkloadGenerator


class PublicSmokeTests(unittest.TestCase):
    def test_public_interfaces_import(self) -> None:
        self.assertTrue(hasattr(DiskManager, "read_page"))
        self.assertTrue(hasattr(BufferPoolManager, "fetch_page"))
        self.assertTrue(hasattr(BPlusTree, "search"))
        self.assertTrue(hasattr(LRUReplacer, "evict"))
        self.assertTrue(hasattr(ClockReplacer, "evict"))
        self.assertTrue(hasattr(WorkloadGenerator, "generate"))
        self.assertTrue(callable(run_simulation))
        self.assertTrue(callable(run_benchmark))


if __name__ == "__main__":
    unittest.main()

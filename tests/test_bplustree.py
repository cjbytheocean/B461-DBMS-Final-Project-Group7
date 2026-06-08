"""Public B+ tree tests shared by student_starter and instructor_reference."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dbsim.bplustree import BPlusTree
from dbsim.buffer_pool import BufferPoolManager
from dbsim.disk_manager import DiskManager


class BPlusTreeTests(unittest.TestCase):
    def test_insert_search_and_range_search(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_file = Path(temp_dir) / "tree.db"
            disk = DiskManager(str(db_file))
            buffer_pool = BufferPoolManager(pool_size=8, disk_manager=disk, replacement_policy="clock")
            tree = BPlusTree(buffer_pool_manager=buffer_pool, order=3)

            for key in range(20):
                tree.insert(key, key * 100)

            self.assertEqual(tree.search(7), 700)
            self.assertIsNone(tree.search(999))
            self.assertEqual(
                tree.range_search(5, 9),
                [(5, 500), (6, 600), (7, 700), (8, 800), (9, 900)],
            )


if __name__ == "__main__":
    unittest.main()

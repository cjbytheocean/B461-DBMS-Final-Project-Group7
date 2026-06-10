"""Public disk manager tests shared by student_starter and instructor_reference."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dbsim.disk_manager import DiskManager
from models import Page


class DiskManagerTests(unittest.TestCase):
    def test_allocate_write_and_read_page(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_file = Path(temp_dir) / "disk.db"
            disk = DiskManager(str(db_file))
            page_id = disk.allocate_page()
            page = Page(page_id=page_id)
            page.data[:10] = b"hello page"
            disk.write_page(page)

            payload = disk.read_page(page_id)

            self.assertEqual(page_id, 0)
            self.assertEqual(bytes(payload.data[:10]), b"hello page")
            stats = disk.get_stats()
            self.assertEqual(stats["reads"], 1)
            self.assertGreaterEqual(stats["writes"], 1)

    def test_reset_cost_clears_cost_counters(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_file = Path(temp_dir) / "disk.db"
            disk = DiskManager(str(db_file))
            first_page_id = disk.allocate_page()
            second_page_id = disk.allocate_page()

            disk.read_page(first_page_id)
            disk.read_page(second_page_id)
            self.assertGreater(disk.simulated_time_ms, 0.0)

            disk.reset_cost()

            stats = disk.get_stats()
            self.assertEqual(stats["simulated_time_ms"], 0.0)
            self.assertEqual(stats["sequential_reads"], 0)
            self.assertEqual(stats["random_reads"], 0)


if __name__ == "__main__":
    unittest.main()

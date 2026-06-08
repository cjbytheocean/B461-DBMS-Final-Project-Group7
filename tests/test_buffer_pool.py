"""Public buffer pool tests shared by student_starter and instructor_reference."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dbsim.buffer_pool import BufferPoolManager
from dbsim.disk_manager import DiskManager


class BufferPoolManagerTests(unittest.TestCase):
    def test_fetch_unpin_and_evict(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_file = Path(temp_dir) / "buffer.db"
            disk = DiskManager(str(db_file))
            buffer_pool = BufferPoolManager(pool_size=2, disk_manager=disk, replacement_policy="lru")

            first = buffer_pool.new_page()
            first.data[:5] = b"first"
            buffer_pool.unpin_page(first.page_id, is_dirty=True)

            second = buffer_pool.new_page()
            second.data[:6] = b"second"
            buffer_pool.unpin_page(second.page_id, is_dirty=True)

            third = buffer_pool.new_page()
            third.data[:5] = b"third"
            buffer_pool.unpin_page(third.page_id, is_dirty=True)

            fetched = buffer_pool.fetch_page(second.page_id)
            self.assertEqual(bytes(fetched.data[:6]), b"second")
            buffer_pool.unpin_page(second.page_id)

            stats = buffer_pool.get_stats()
            self.assertGreaterEqual(stats["evictions"], 1)


if __name__ == "__main__":
    unittest.main()

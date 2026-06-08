"""Public replacement policy tests shared by student_starter and instructor_reference."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dbsim.replacement import ClockReplacer, LRUReplacer


class ReplacementPolicyTests(unittest.TestCase):
    def test_lru_evicts_oldest_evictable_frame(self) -> None:
        replacer = LRUReplacer(pool_size=3)
        for frame_id in (0, 1, 2):
            replacer.record_access(frame_id)
            replacer.set_evictable(frame_id, True)

        replacer.record_access(1)

        self.assertEqual(replacer.evict(), 0)

    def test_clock_gives_second_chance_before_evicting(self) -> None:
        replacer = ClockReplacer(pool_size=3)
        for frame_id in (0, 1, 2):
            replacer.record_access(frame_id)
            replacer.set_evictable(frame_id, True)

        self.assertEqual(replacer.evict(), 0)


if __name__ == "__main__":
    unittest.main()

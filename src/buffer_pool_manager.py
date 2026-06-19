"""
Project: B461-Database Concepts - Summer 2026
Author: [Student Name]
Role: Student Starter Code

Students are expected to complete the TODO sections in this file.
Do not modify protected sections marked as [INSTRUCTOR ONLY].
"""

"""Buffer pool manager for the student starter."""

try:
    from .config import BUFFER_POOL_SIZE
    from .disk_manager import DiskManager
    from .models import Page
    from .replacement import ClockReplacementPolicy, LRUReplacementPolicy
except ImportError:
    from config import BUFFER_POOL_SIZE
    from disk_manager import DiskManager
    from models import Page
    from replacement import ClockReplacementPolicy, LRUReplacementPolicy


# ================================
# [STUDENT TODO] IMPLEMENT BELOW
# ================================
class BufferPoolManager:
    def __init__(
        self,
        pool_size: int = BUFFER_POOL_SIZE,
        disk_manager: DiskManager | None = None,
        replacement_policy: str = "lru",
    ) -> None:
        if pool_size <= 0:
            raise ValueError("Buffer pool size must be positive.")

        self.pool_size = pool_size
        self.disk_manager = disk_manager if disk_manager is not None else DiskManager()
        self.page_table: dict[int, int] = {}
        self.frames: list[Page | None] = [None for _ in range(pool_size)]
        self.free_list = list(range(pool_size))
        self.replacer = self._build_replacer(replacement_policy)
        self.replacement_policy_name = replacement_policy.lower()

        self.hit_count = 0
        self.miss_count = 0
        self.eviction_count = 0
        self.flush_count = 0
        self.delete_count = 0

        # ================================
        # [INSTRUCTOR ONLY] DO NOT MODIFY
        # ================================
        # [INSTRUCTOR ONLY] Shared-state orchestration or locking belongs here.

    def _build_replacer(self, replacement_policy: str):
        normalized = replacement_policy.lower()
        if normalized == "lru":
            return LRUReplacementPolicy(self.pool_size)
        if normalized == "clock":
            return ClockReplacementPolicy(self.pool_size)
        raise ValueError(f"Unknown replacement policy: {replacement_policy}")

    def _get_frame_id(self, page_id: int) -> int | None:
        return self.page_table.get(page_id)

    def _mark_frame_evictable(self, frame_id: int, evictable: bool) -> None:
        self.replacer.record_access(frame_id)
        self.replacer.set_evictable(frame_id, evictable)

    def _evict_if_needed(self) -> int:
        if self.free_list:
            return self.free_list.pop(0)

        # the frame id for the next page.
        victim_frame = self.replacer.evict()

        if victim_frame is None:
            return self.free_list.pop(0)

        victim_page_id = None
        for page_id, frame_id in self.page_table.items():
            if frame_id == victim_frame:
                victim_page_id = page_id
                break

        if victim_page_id is not None:
            page = self.frames[victim_frame]
            if page is not None and page.is_dirty:
                self.disk_manager.write_page(page)
                self.flush_count += 1
            self.page_table.pop(victim_page_id, None)

        self.replacer.remove(victim_frame)
        self.frames[victim_frame] = None
        self.eviction_count += 1

        return victim_frame

    def fetch_page(self, page_id: int) -> Page:
        # stats updates here.

        frame_id = self._get_frame_id(page_id)

        if frame_id is not None:
            self.hit_count += 1
            page = self.frames[frame_id]
            self.replacer.record_access(frame_id)
            self._mark_frame_evictable(frame_id, False)
            page.pin_count += 1
            return page

        self.miss_count += 1

        frame_id = self._evict_if_needed()
        page = self.disk_manager.read_page(page_id)

        self.frames[frame_id] = page
        self.page_table[page_id] = frame_id

        page.pin_count = 1
        self._mark_frame_evictable(frame_id, False)

        return page

    def new_page(self) -> Page:
        # [STUDENT TODO] Allocate a new disk page and place it in a buffer
        # frame.
        raise NotImplementedError("Students should implement new_page.")

    def unpin_page(self, page_id: int, is_dirty: bool = False) -> bool:
        # needed, and make it evictable once no clients still hold it.

        frame_id = self._get_frame_id(page_id)

        if frame_id is None:
            return False

        page = self.frames[frame_id]
        if page is None:
            return False

        if is_dirty:
            page.is_dirty = True

        page.pin_count = max(0, page.pin_count - 1)

        if page.pin_count == 0:
            self._mark_frame_evictable(frame_id, True)

        return True

    def flush_page(self, page_id: int) -> bool:
        # [STUDENT TODO] Write a single page back to disk and clear its dirty
        # flag.
        raise NotImplementedError("Students should implement flush_page.")

    def flush_all_pages(self) -> None:
        # [STUDENT TODO] Flush every dirty page currently cached in memory.
        raise NotImplementedError("Students should implement flush_all_pages.")

    def delete_page(self, page_id: int) -> bool:
        # [STUDENT TODO] Remove an unpinned page from the buffer and then clear
        # its disk slot.
        raise NotImplementedError("Students should implement delete_page.")

    def get_stats(self) -> dict[str, float]:
        disk_stats = self.disk_manager.get_stats()
        return {
            "pool_size": self.pool_size,
            "policy": self.replacement_policy_name,
            "hits": self.hit_count,
            "misses": self.miss_count,
            "evictions": self.eviction_count,
            "flushes": self.flush_count,
            "deletes": self.delete_count,
            "disk_reads": disk_stats["reads"],
            "disk_writes": disk_stats["writes"],
            "simulated_time_ms": disk_stats["simulated_time_ms"],
        }
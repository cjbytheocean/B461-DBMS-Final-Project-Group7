"""
Project: B461-Database Concepts - Summer 2026
Role: Instructor Provided File

Students should not modify this file.
"""

"""File-backed disk manager for the student starter.

External callers should prefer importing this through ``dbsim.disk_manager``.
"""

from pathlib import Path

try:
    from .config import DISK_FILE, PAGE_SIZE, SEEK_COST, TRANSFER_COST
    from .models import Page
except ImportError:
    from config import DISK_FILE, PAGE_SIZE, SEEK_COST, TRANSFER_COST
    from models import Page


# ================================
# [INSTRUCTOR ONLY] DO NOT MODIFY
# ================================
class DiskManager:
    def __init__(
        self,
        db_file: str = DISK_FILE,
        page_size: int = PAGE_SIZE,
        seek_cost: float = SEEK_COST,
        transfer_cost: float = TRANSFER_COST,
    ) -> None:
        self.db_file = Path(db_file)
        self.page_size = page_size
        self.seek_cost = seek_cost
        self.transfer_cost = transfer_cost

        self.db_file.parent.mkdir(parents=True, exist_ok=True)
        self.db_file.touch(exist_ok=True)

        self.read_count = 0
        self.write_count = 0
        self.delete_count = 0
        self.allocated_pages = 0
        self.simulated_time_ms = 0.0
        self.sequential_reads = 0
        self.random_reads = 0
        self.sequential_writes = 0
        self.random_writes = 0
        self.last_accessed_page_id: int | None = None
        self.next_page_id = self._file_page_count()

    def _file_page_count(self) -> int:
        size = self.db_file.stat().st_size
        if size == 0:
            return 0
        return size // self.page_size

    def _offset_for(self, page_id: int) -> int:
        return page_id * self.page_size

    def _validate_page_id(self, page_id: int) -> None:
        if page_id < 0 or page_id >= self.next_page_id:
            raise IndexError(f"Page id {page_id} is out of range.")

    def _ensure_capacity(self, page_id: int) -> None:
        target_size = (page_id + 1) * self.page_size
        current_size = self.db_file.stat().st_size
        if current_size >= target_size:
            return
        with self.db_file.open("ab") as handle:
            handle.write(b"\x00" * (target_size - current_size))

    def _is_sequential(self, page_id: int) -> bool:
        return self.last_accessed_page_id is not None and page_id == self.last_accessed_page_id + 1

    def _record_cost(self, page_id: int, operation: str) -> None:
        sequential = self._is_sequential(page_id)
        self.simulated_time_ms += self.transfer_cost
        if operation == "write" or not sequential:
            self.simulated_time_ms += self.seek_cost

        if operation == "read":
            if sequential:
                self.sequential_reads += 1
            else:
                self.random_reads += 1
        else:
            if sequential:
                self.sequential_writes += 1
            else:
                self.random_writes += 1

        self.last_accessed_page_id = page_id

    def _normalize_data(self, data: bytes | bytearray) -> bytes:
        if len(data) > self.page_size:
            raise ValueError("Page data exceeds the configured page size.")
        return bytes(data).ljust(self.page_size, b"\x00")

    def allocate_page(self) -> int:
        page_id = self.next_page_id
        self.next_page_id += 1
        self.allocated_pages += 1
        self._ensure_capacity(page_id)
        return page_id

    def read_page(self, page_id: int) -> Page:
        self._validate_page_id(page_id)
        self.read_count += 1
        self._record_cost(page_id, operation="read")

        with self.db_file.open("rb") as handle:
            handle.seek(self._offset_for(page_id))
            data = handle.read(self.page_size)

        return Page(page_id=page_id, data=bytearray(data.ljust(self.page_size, b"\x00")))

    def write_page(self, page: Page) -> None:
        page_id = page.page_id
        payload = self._normalize_data(page.data)
        self._validate_page_id(page_id)
        self.write_count += 1
        self._record_cost(page_id, operation="write")
        self._ensure_capacity(page_id)

        with self.db_file.open("r+b") as handle:
            handle.seek(self._offset_for(page_id))
            handle.write(payload)
        page.is_dirty = False

    def delete_page(self, page_id: int) -> bool:
        self._validate_page_id(page_id)
        self.delete_count += 1
        blank_page = Page(page_id=page_id, data=bytearray(self.page_size))
        self.write_page(blank_page)
        return True

    def reset_cost(self) -> None:
        self.simulated_time_ms = 0.0
        self.sequential_reads = 0
        self.random_reads = 0
        self.sequential_writes = 0
        self.random_writes = 0
        self.last_accessed_page_id = None

    def get_stats(self) -> dict[str, float]:
        return {
            "reads": self.read_count,
            "writes": self.write_count,
            "deletes": self.delete_count,
            "allocated_pages": self.allocated_pages,
            "simulated_time_ms": round(self.simulated_time_ms, 4),
            "sequential_reads": self.sequential_reads,
            "random_reads": self.random_reads,
            "sequential_writes": self.sequential_writes,
            "random_writes": self.random_writes,
        }

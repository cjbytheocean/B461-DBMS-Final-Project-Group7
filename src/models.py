"""
Project: B461-Database Concepts - Summer 2026
Role: Instructor Provided File

Students should not modify this file.
"""

"""Shared data models for the student starter."""

from dataclasses import dataclass, field

try:
    from .config import PAGE_SIZE
except ImportError:
    from config import PAGE_SIZE


# ================================
# [INSTRUCTOR ONLY] DO NOT MODIFY
# ================================
@dataclass
class Record:
    key: int
    value: int


@dataclass
class Page:
    page_id: int
    data: bytearray = field(default_factory=lambda: bytearray(PAGE_SIZE))
    pin_count: int = 0
    is_dirty: bool = False

    def copy_bytes(self) -> bytes:
        return bytes(self.data)


@dataclass
class Query:
    kind: str
    key: int | None = None
    value: int | None = None
    start_key: int | None = None
    end_key: int | None = None


@dataclass
class Stats:
    reads: int = 0
    writes: int = 0
    deletes: int = 0
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    flushes: int = 0
    simulated_time_ms: float = 0.0
    elapsed_seconds: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return {
            "reads": self.reads,
            "writes": self.writes,
            "deletes": self.deletes,
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "flushes": self.flushes,
            "simulated_time_ms": self.simulated_time_ms,
            "elapsed_seconds": self.elapsed_seconds,
        }

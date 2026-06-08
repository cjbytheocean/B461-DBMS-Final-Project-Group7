"""
Project: B461-Database Concepts - Summer 2026
Author: [Student Name]
Role: Student Starter Code

Students are expected to complete the TODO sections in this file.
Do not modify protected sections marked as [INSTRUCTOR ONLY].
"""

"""Simple reproducible workload generator for the student starter."""

import random

try:
    from .config import DEFAULT_NUM_QUERIES, DEFAULT_NUM_RECORDS, RANDOM_SEED
    from .models import Query
except ImportError:
    from config import DEFAULT_NUM_QUERIES, DEFAULT_NUM_RECORDS, RANDOM_SEED
    from models import Query


WorkloadOperation = Query


class WorkloadGenerator:
    def __init__(
        self,
        seed: int = RANDOM_SEED,
        key_space: int = DEFAULT_NUM_RECORDS,
    ) -> None:
        self.seed = seed
        self.key_space = max(1, key_space)
        self._random = random.Random(seed)

    def generate_initial_load(self, count: int = DEFAULT_NUM_RECORDS) -> list[WorkloadOperation]:
        return [
            WorkloadOperation(kind="insert", key=key, value=key * 10)
            for key in range(min(count, self.key_space))
        ]

    def generate_point_workload(
        self,
        count: int = DEFAULT_NUM_QUERIES,
        insert_probability: float = 0.3,
    ) -> list[WorkloadOperation]:
        operations: list[WorkloadOperation] = []
        for _ in range(count):
            if self._random.random() < insert_probability:
                key = self._random.randrange(self.key_space)
                operations.append(
                    WorkloadOperation(kind="insert", key=key, value=key * 10 + 1)
                )
            else:
                operations.append(
                    WorkloadOperation(kind="search", key=self._random.randrange(self.key_space))
                )
        return operations

    def generate_range_workload(
        self,
        count: int = DEFAULT_NUM_QUERIES,
        width: int = 10,
    ) -> list[WorkloadOperation]:
        width = max(1, width)
        operations: list[WorkloadOperation] = []
        upper_bound = max(1, self.key_space - width + 1)
        for _ in range(count):
            start_key = self._random.randrange(upper_bound)
            operations.append(
                WorkloadOperation(
                    kind="range",
                    start_key=start_key,
                    end_key=min(self.key_space - 1, start_key + width - 1),
                )
            )
        return operations

    def generate_scan_workload(
        self,
        count: int = DEFAULT_NUM_QUERIES,
        width: int = 20,
    ) -> list[WorkloadOperation]:
        width = max(1, width)
        step = max(1, width // 2)
        operations: list[WorkloadOperation] = []
        cursor = 0
        for _ in range(count):
            start_key = cursor % self.key_space
            end_key = min(self.key_space - 1, start_key + width - 1)
            operations.append(
                WorkloadOperation(kind="scan", start_key=start_key, end_key=end_key)
            )
            cursor += step
        return operations

    def generate_skewed_workload(
        self,
        count: int = DEFAULT_NUM_QUERIES,
        hot_fraction: float = 0.2,
        hot_probability: float = 0.8,
    ) -> list[WorkloadOperation]:
        hot_key_count = max(1, int(self.key_space * hot_fraction))
        operations: list[WorkloadOperation] = []
        for _ in range(count):
            if self._random.random() < hot_probability:
                key = self._random.randrange(hot_key_count)
            else:
                key = self._random.randrange(self.key_space)
            operations.append(WorkloadOperation(kind="search", key=key))
        return operations

    def generate_mixed_workload(
        self,
        count: int = DEFAULT_NUM_QUERIES,
        range_width: int = 8,
        scan_width: int = 12,
    ) -> list[WorkloadOperation]:
        operations: list[WorkloadOperation] = []
        point_ops = self.generate_point_workload(count=max(1, count), insert_probability=0.2)
        point_index = 0

        for _ in range(count):
            choice = self._random.random()
            if choice < 0.45:
                operations.append(point_ops[point_index % len(point_ops)])
                point_index += 1
            elif choice < 0.7:
                operations.extend(self.generate_range_workload(count=1, width=range_width))
            elif choice < 0.9:
                operations.extend(self.generate_scan_workload(count=1, width=scan_width))
            else:
                key = self._random.randrange(self.key_space)
                operations.append(WorkloadOperation(kind="insert", key=key, value=key * 10 + 5))
        return operations

    def generate(
        self,
        workload_type: str,
        count: int = DEFAULT_NUM_QUERIES,
    ) -> list[WorkloadOperation]:
        normalized = workload_type.lower()
        if normalized == "point":
            return self.generate_point_workload(count)
        if normalized == "range":
            return self.generate_range_workload(count)
        if normalized == "scan":
            return self.generate_scan_workload(count)
        if normalized == "skewed":
            return self.generate_skewed_workload(count)
        if normalized == "mixed":
            return self.generate_mixed_workload(count)
        raise ValueError(f"Unknown workload type: {workload_type}")


__all__ = ["WorkloadGenerator", "WorkloadOperation"]

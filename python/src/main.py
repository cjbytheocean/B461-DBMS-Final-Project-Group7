"""
Project: B461-Database Concepts - Summer 2026
Author: [Student Name]
Role: Student Starter Code

Students are expected to complete the TODO sections in this file.
Do not modify protected sections marked as [INSTRUCTOR ONLY].
"""

import tempfile
from pathlib import Path

try:
    from .config import BUFFER_POOL_SIZE, DEFAULT_NUM_QUERIES, DEFAULT_NUM_RECORDS, RANDOM_SEED
    from .simulator import run_simulation
except ImportError:
    from config import BUFFER_POOL_SIZE, DEFAULT_NUM_QUERIES, DEFAULT_NUM_RECORDS, RANDOM_SEED
    from simulator import run_simulation


def main() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        db_file = Path(temp_dir) / "demo.db"
        result = run_simulation(
            db_file=str(db_file),
            pool_size=BUFFER_POOL_SIZE,
            replacement_policy="lru",
            workload_type="point",
            operation_count=min(DEFAULT_NUM_QUERIES, 25),
            key_space=DEFAULT_NUM_RECORDS,
            seed=RANDOM_SEED,
        )

    print(result)


if __name__ == "__main__":
    main()

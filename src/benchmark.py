"""
Project: B461-Database Concepts - Summer 2026
Role: Instructor Provided File

Students should not modify this file.
"""

import argparse
import csv
import tempfile
from pathlib import Path

try:
    from .config import DEFAULT_NUM_QUERIES, DEFAULT_NUM_RECORDS, DEFAULT_PAGE_CAPACITY, RANDOM_SEED, RESULTS_DIR
    from .simulator import run_simulation
except ImportError:
    from config import DEFAULT_NUM_QUERIES, DEFAULT_NUM_RECORDS, DEFAULT_PAGE_CAPACITY, RANDOM_SEED, RESULTS_DIR
    from simulator import run_simulation

def run_benchmark(
    output_csv: str = str(Path(RESULTS_DIR) / "benchmark_results.csv"),
    policies: tuple[str, ...] = ("lru", "clock"),
    buffer_sizes: tuple[int, ...] = (4, 8, 16),
    page_capacities: tuple[int, ...] = (
        max(1, DEFAULT_PAGE_CAPACITY // 2),
        DEFAULT_PAGE_CAPACITY,
    ),
    workload_types: tuple[str, ...] = ("point", "range", "scan", "skewed", "mixed"),
    operation_count: int = min(DEFAULT_NUM_QUERIES, 50),
    seed: int = RANDOM_SEED,
) -> list[dict[str, object]]:
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []

    with tempfile.TemporaryDirectory() as temp_dir:
        for policy in policies:
            for buffer_size in buffer_sizes:
                for page_capacity in page_capacities:
                    for workload_type in workload_types:
                        db_file = Path(temp_dir) / (
                            f"{policy}_{buffer_size}_{page_capacity}_{workload_type}.db"
                        )
                        result = run_simulation(
                            db_file=str(db_file),
                            pool_size=buffer_size,
                            replacement_policy=policy,
                            workload_type=workload_type,
                            operation_count=operation_count,
                            key_space=DEFAULT_NUM_RECORDS,
                            seed=seed,
                            page_capacity=page_capacity,
                        )
                        rows.append(result)

    if not rows:
        return rows

    fieldnames = list(rows[0].keys())
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return rows


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run DB simulator benchmarks.")
    parser.add_argument(
        "--output-csv",
        default=str(Path(RESULTS_DIR) / "benchmark_results.csv"),
        help="Path to the CSV output file.",
    )
    parser.add_argument(
        "--operation-count",
        type=int,
        default=min(DEFAULT_NUM_QUERIES, 50),
        help="Number of workload operations per benchmark run.",
    )
    return parser


def main() -> None:
    args = build_argument_parser().parse_args()
    rows = run_benchmark(
        output_csv=args.output_csv,
        operation_count=args.operation_count,
    )
    print(f"Wrote {len(rows)} benchmark rows to {args.output_csv}")


if __name__ == "__main__":
    main()

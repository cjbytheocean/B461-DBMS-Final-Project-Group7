"""
Project: B461-Database Concepts - Summer 2026
Role: Instructor Provided File

Students should not modify this file.
"""

"""End-to-end simulator integration.

External callers should prefer importing this through ``dbsim.simulation``.
"""

import time

try:
    from .bplustree import BPlusTree
    from .buffer_pool_manager import BufferPoolManager
    from .config import (
        BPLUS_ORDER,
        BUFFER_POOL_SIZE,
        DEFAULT_NUM_QUERIES,
        DEFAULT_NUM_RECORDS,
        DISK_FILE,
        MEMORY_HIT_COST,
        RANDOM_SEED,
    )
    from .disk_manager import DiskManager
    from .workload import WorkloadGenerator
except ImportError:
    from bplustree import BPlusTree
    from buffer_pool_manager import BufferPoolManager
    from config import (
        BPLUS_ORDER,
        BUFFER_POOL_SIZE,
        DEFAULT_NUM_QUERIES,
        DEFAULT_NUM_RECORDS,
        DISK_FILE,
        MEMORY_HIT_COST,
        RANDOM_SEED,
    )
    from disk_manager import DiskManager
    from workload import WorkloadGenerator


def run_simulation(
    db_file: str = DISK_FILE,
    pool_size: int = BUFFER_POOL_SIZE,
    replacement_policy: str = "lru",
    tree_order: int = BPLUS_ORDER,
    workload_type: str = "point",
    operation_count: int = DEFAULT_NUM_QUERIES,
    key_space: int = DEFAULT_NUM_RECORDS,
    seed: int = RANDOM_SEED,
    page_capacity: int | None = None,
) -> dict[str, float | int | str]:
    effective_tree_order = max(3, page_capacity) if page_capacity is not None else tree_order
    disk_manager = DiskManager(db_file=db_file)
    buffer_pool = BufferPoolManager(
        pool_size=pool_size,
        disk_manager=disk_manager,
        replacement_policy=replacement_policy,
    )
    tree = BPlusTree(buffer_pool_manager=buffer_pool, order=effective_tree_order)
    workload = WorkloadGenerator(seed=seed, key_space=key_space)

    preload_count = max(effective_tree_order * 2, min(key_space, operation_count))
    initial_records = workload.generate_initial_load(preload_count)
    for record in initial_records:
        tree.insert(record.key, record.value)  # type: ignore[arg-type]

    operations = workload.generate(workload_type=workload_type, count=operation_count)
    point_hits = 0
    range_result_count = 0

    started_at = time.perf_counter()
    for operation in operations:
        if operation.kind == "insert":
            tree.insert(operation.key, operation.value)  # type: ignore[arg-type]
        elif operation.kind == "search":
            result = tree.search(operation.key)  # type: ignore[arg-type]
            if result is not None:
                point_hits += 1
        elif operation.kind in {"range", "scan"}:
            results = tree.range_search(
                operation.start_key,  # type: ignore[arg-type]
                operation.end_key,  # type: ignore[arg-type]
            )
            range_result_count += len(results)
        else:
            raise ValueError(f"Unsupported operation kind: {operation.kind}")
    elapsed_seconds = time.perf_counter() - started_at

    buffer_pool.flush_all_pages()
    buffer_stats = buffer_pool.get_stats()
    hits = int(buffer_stats["hits"])
    misses = int(buffer_stats["misses"])
    total_accesses = hits + misses
    hit_rate = hits / total_accesses if total_accesses else 0.0
    simulated_time_ms = float(buffer_stats["simulated_time_ms"]) + (hits * MEMORY_HIT_COST)
    throughput = operation_count / elapsed_seconds if elapsed_seconds > 0 else float("inf")

    return {
        "policy": replacement_policy.lower(),
        "pool_size": pool_size,
        "tree_order": effective_tree_order,
        "page_capacity": page_capacity if page_capacity is not None else effective_tree_order,
        "workload_type": workload_type.lower(),
        "operation_count": operation_count,
        "preload_count": preload_count,
        "seed": seed,
        "point_hits": point_hits,
        "range_result_count": range_result_count,
        "hits": hits,
        "misses": misses,
        "evictions": int(buffer_stats["evictions"]),
        "disk_reads": int(buffer_stats["disk_reads"]),
        "disk_writes": int(buffer_stats["disk_writes"]),
        "hit_rate": round(hit_rate, 4),
        "simulated_time_ms": round(simulated_time_ms, 4),
        "elapsed_seconds": round(elapsed_seconds, 6),
        "throughput_ops_per_sec": round(throughput, 2),
        "buffer_hits": hits,
        "buffer_misses": misses,
        "buffer_evictions": int(buffer_stats["evictions"]),
        "buffer_flushes": int(buffer_stats["flushes"]),
        "simulated_disk_ms": float(buffer_stats["simulated_time_ms"]),
    }


__all__ = ["run_simulation"]

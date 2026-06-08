"""
Project: B461-Database Concepts - Summer 2026
Role: Instructor Provided File

Students should not modify this file.
"""

import argparse
import csv
from collections import defaultdict
from pathlib import Path

try:
    from .config import RESULTS_DIR
except ImportError:
    from config import RESULTS_DIR


POLICY_COLORS = {
    "lru": "#1f77b4",
    "clock": "#d62728",
}

LINE_STYLES = ["-", "--", "-.", ":"]


def _build_line_style_map(page_capacities: list[str]) -> dict[str, str]:
    ordered = sorted(page_capacities, key=lambda value: int(value))
    return {
        page_capacity: LINE_STYLES[index % len(LINE_STYLES)]
        for index, page_capacity in enumerate(ordered)
    }


def _save_metric_plot(
    rows: list[dict[str, str]],
    metric_key: str,
    metric_label: str,
    output_dir: Path,
) -> Path:
    try:
        import matplotlib.pyplot as plt
        from matplotlib.lines import Line2D
    except ImportError as exc:
        raise RuntimeError("matplotlib is required to generate PNG benchmark plots.") from exc

    filtered_rows = [row for row in rows if row["policy"].lower() in {"lru", "clock"}]
    if not filtered_rows:
        raise ValueError("Benchmark CSV does not contain LRU/Clock rows to plot.")

    workloads = sorted({row["workload_type"] for row in filtered_rows})
    page_capacities = sorted({row.get("page_capacity", "default") for row in filtered_rows}, key=lambda value: int(value))
    line_style_map = _build_line_style_map(page_capacities)

    grouped: dict[tuple[str, str, str], list[tuple[int, float]]] = defaultdict(list)
    metric_min = None
    metric_max = None
    for row in filtered_rows:
        page_capacity = row.get("page_capacity", "default")
        label = (row["workload_type"], row["policy"].lower(), page_capacity)
        metric_value = float(row[metric_key])
        grouped[label].append((int(row["pool_size"]), metric_value))
        metric_min = metric_value if metric_min is None else min(metric_min, metric_value)
        metric_max = metric_value if metric_max is None else max(metric_max, metric_value)

    subplot_count = len(workloads)
    columns = 2 if subplot_count > 1 else 1
    rows_needed = (subplot_count + columns - 1) // columns
    figure, axes = plt.subplots(
        rows_needed,
        columns,
        figsize=(12, 3.6 * rows_needed),
        sharex=True,
        squeeze=False,
    )
    flat_axes = list(axes.flatten())

    for axis, workload in zip(flat_axes, workloads):
        for policy in ("lru", "clock"):
            for page_capacity in page_capacities:
                points = grouped.get((workload, policy, page_capacity), [])
                if not points:
                    continue
                points.sort(key=lambda item: item[0])
                x_values = [item[0] for item in points]
                y_values = [item[1] for item in points]
                axis.plot(
                    x_values,
                    y_values,
                    color=POLICY_COLORS[policy],
                    linestyle=line_style_map[page_capacity],
                    marker="o",
                    linewidth=2,
                    markersize=4,
                )

        axis.set_title(workload.capitalize())
        axis.set_xlabel("Buffer Pool Size")
        axis.set_ylabel(metric_label)
        axis.grid(True, linestyle="--", alpha=0.35)
        axis.set_xticks(sorted({int(row["pool_size"]) for row in filtered_rows}))

        if metric_min is not None and metric_max is not None and metric_min != metric_max:
            padding = (metric_max - metric_min) * 0.08
            axis.set_ylim(metric_min - padding, metric_max + padding)

    for axis in flat_axes[subplot_count:]:
        axis.set_visible(False)

    policy_handles = [
        Line2D([0], [0], color=POLICY_COLORS["lru"], linewidth=2, marker="o", markersize=4, label="LRU"),
        Line2D([0], [0], color=POLICY_COLORS["clock"], linewidth=2, marker="o", markersize=4, label="Clock"),
    ]
    figure.legend(
        handles=policy_handles,
        labels=["LRU", "Clock"],
        loc="lower center",
        ncol=2,
        frameon=False,
        bbox_to_anchor=(0.5, 0.02),
    )

    if page_capacities:
        style_note = ", ".join(
            f"{line_style_map[page_capacity]} = {page_capacity}"
            for page_capacity in page_capacities
        )
        figure.text(
            0.5,
            0.0,
            f"Line style shows page capacity: {style_note}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    figure.suptitle(f"DB Simulator {metric_label}", fontsize=14, y=0.98)
    figure.tight_layout(rect=(0, 0.08, 1, 0.95))

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{metric_key}.png"
    figure.savefig(output_path, dpi=150)
    plt.close(figure)
    return output_path


def plot_results(csv_path: str, output_dir: str = str(Path(RESULTS_DIR) / "plots")) -> list[str]:
    rows: list[dict[str, str]] = []
    with Path(csv_path).open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows.extend(reader)

    if not rows:
        raise ValueError("Benchmark CSV is empty.")

    metric_specs = [
        ("hit_rate", "Hit Rate"),
        ("simulated_time_ms", "Simulated Time (ms)"),
        ("disk_reads", "Disk Reads"),
        ("evictions", "Evictions"),
    ]

    output_path = Path(output_dir)
    saved_paths: list[str] = []
    for metric_key, metric_label in metric_specs:
        saved_path = _save_metric_plot(rows, metric_key, metric_label, output_path)
        saved_paths.append(str(saved_path))

    return saved_paths


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Plot DB simulator benchmark results.")
    parser.add_argument("csv_path", help="Benchmark CSV file to plot.")
    parser.add_argument(
        "--output-dir",
        default=str(Path(RESULTS_DIR) / "plots"),
        help="Directory where PNG plots will be saved.",
    )
    return parser


def main() -> None:
    args = build_argument_parser().parse_args()
    saved_paths = plot_results(csv_path=args.csv_path, output_dir=args.output_dir)
    print(f"Saved {len(saved_paths)} plots to {args.output_dir}")


if __name__ == "__main__":
    main()

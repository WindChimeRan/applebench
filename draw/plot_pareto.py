"""Throughput-vs-memory Pareto scatter, one panel per concurrency.

One row, three columns — one scatter per concurrency level (1, 8, 16). Each
point is a framework; x = output throughput (tok/s, linear), y = peak system
memory (GB, linear, inverted so less-is-higher). A dashed staircase connects
the Pareto frontier (non-dominated points: no other framework has both higher
throughput *and* lower memory).

Usage:
    python draw/plot_pareto.py                          # Qwen3-0.6B chat
    python draw/plot_pareto.py --split agent
    python draw/plot_pareto.py --model Qwen3-8B --split chat
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse import CVD_COLORS, discover_traces, load_concurrency_metric  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
CONCURRENCIES = [1, 8, 16]
THROUGHPUT_KEY = "output_throughput_tps"
MEMORY_KEY = "mem_used_gb"


def load_throughput(split_dir: Path) -> dict[str, dict[int, float]]:
    by_fw: dict[str, tuple[str, dict[int, float]]] = {}
    for path in sorted(split_dir.glob("*.json")):
        if path.name == "comparison.json" or "metalstat" in path.name:
            continue
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        fw = data.get("framework")
        ts = data.get("timestamp")
        if not fw or not ts:
            continue
        if fw in by_fw and by_fw[fw][0] >= ts:
            continue
        by_fw[fw] = (ts, load_concurrency_metric(path, THROUGHPUT_KEY))
    return {fw: ccs for fw, (_, ccs) in by_fw.items()}


def load_peak_memory(split_dir: Path) -> dict[str, dict[int, float]]:
    traces = discover_traces(split_dir)
    out: dict[str, dict[int, float]] = {}
    for fw, tr in traces.items():
        series = tr.series(MEMORY_KEY)
        per_c: dict[int, float] = {}
        for c in CONCURRENCIES:
            phase = tr.phase_slice(c)
            if phase is None:
                continue
            _, idxs = phase
            vals = [series[i] for i in idxs if series[i] is not None]
            if vals:
                per_c[c] = max(vals)
        out[fw] = per_c
    return out


def pareto_front(points: list[tuple[float, float]]) -> list[int]:
    """Indices of non-dominated points under (maximize x, minimize y).
    A point i is dominated iff ∃ j ≠ i with x_j ≥ x_i and y_j ≤ y_i and
    at least one strict. Returns indices sorted by x ascending."""
    keep: list[int] = []
    for i, (xi, yi) in enumerate(points):
        dominated = False
        for j, (xj, yj) in enumerate(points):
            if i == j:
                continue
            if xj >= xi and yj <= yi and (xj > xi or yj < yi):
                dominated = True
                break
        if not dominated:
            keep.append(i)
    keep.sort(key=lambda i: points[i][0])
    return keep


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen3-0.6B")
    ap.add_argument("--split", default="chat", choices=["chat", "agent"])
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    split_dir = REPO_ROOT / "results" / args.model / args.split
    tput = load_throughput(split_dir)
    mem = load_peak_memory(split_dir)
    if not tput:
        raise SystemExit(f"No benchmark result JSONs under {split_dir}")

    all_fw = sorted(set(tput) | set(mem))
    colors = {fw: CVD_COLORS[i % len(CVD_COLORS)] for i, fw in enumerate(all_fw)}

    tput_vals = [v for ccs in tput.values() for v in ccs.values() if v > 0]
    mem_vals = [v for ccs in mem.values() for v in ccs.values()]
    x_lo = 0
    x_hi = max(tput_vals) * 1.15  # headroom so rightmost inline labels don't clip
    y_lo = 0
    y_hi = max(mem_vals) * 1.08 if mem_vals else 1

    fig, axes = plt.subplots(1, 3, figsize=(16, 5.3), sharey=True)

    for ax, c in zip(axes, CONCURRENCIES):
        xs, ys, fws = [], [], []
        for fw in all_fw:
            x = tput.get(fw, {}).get(c)
            y = mem.get(fw, {}).get(c)
            if x is None or y is None or x <= 0:
                continue
            xs.append(x)
            ys.append(y)
            fws.append(fw)

        front_idx = pareto_front(list(zip(xs, ys)))
        front_set = set(front_idx)

        if front_idx:
            fx = [xs[i] for i in front_idx]
            fy = [ys[i] for i in front_idx]
            step_x = [fx[0]]
            step_y = [fy[0]]
            for i in range(1, len(fx)):
                step_x.extend([fx[i], fx[i]])
                step_y.extend([fy[i - 1], fy[i]])
            line_x = [x_lo, *step_x, x_hi]
            line_y = [step_y[0], *step_y, step_y[-1]]
            ax.plot(line_x, line_y, "k--", linewidth=1.0, alpha=0.55, zorder=2)
            ax.fill_between(
                line_x, line_y, y_hi,
                color="gray", alpha=0.08, zorder=1,
            )

        for i, (x, y, fw) in enumerate(zip(xs, ys, fws)):
            on_front = i in front_set
            ax.scatter(
                x, y,
                s=140 if on_front else 70,
                marker="o",
                color=colors[fw],
                edgecolors="black" if on_front else "#666666",
                linewidths=1.6 if on_front else 0.5,
                alpha=1.0 if on_front else 0.7,
                zorder=4 if on_front else 3,
            )
            ax.annotate(
                fw, (x, y),
                xytext=(8, 3), textcoords="offset points",
                fontsize=8,
                fontweight="bold" if on_front else "normal",
                color="black" if on_front else "#3d3d3d",
                zorder=5,
            )

        ax.set_xlim(x_lo, x_hi)
        # Invert so "less memory" sits higher — with "more throughput to the
        # right," up-and-to-the-right becomes the good corner.
        ax.set_ylim(y_hi, y_lo)
        ax.set_title(f"concurrency {c}")
        ax.set_xlabel("output throughput (tok/s)")
        ax.grid(True, alpha=0.25)

    axes[0].set_ylabel("peak system memory (GB)")

    style_handles = [
        plt.Line2D([0], [0], linestyle="--", color="black", alpha=0.6,
                   label="Pareto frontier"),
        plt.Line2D([0], [0], marker="o", color="white",
                   markerfacecolor="#aaa", markeredgecolor="black",
                   markersize=11, markeredgewidth=1.6, linestyle="None",
                   label="on frontier"),
    ]
    fig.legend(
        handles=style_handles,
        loc="upper center", bbox_to_anchor=(0.5, 0.02),
        ncol=2, frameon=False, fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))

    out = args.out or REPO_ROOT / "draw" / f"pareto_{args.model}_{args.split}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()

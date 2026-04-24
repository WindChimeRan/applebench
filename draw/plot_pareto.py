"""Throughput-vs-memory Pareto scatter, one panel per concurrency.

One row, three columns — one scatter per concurrency level (1, 8, 16). Each
point is a framework; x = output throughput (tok/s, log), y = peak system
memory (GB, linear). A dashed line connects the Pareto frontier (non-dominated
points: no other framework has both higher throughput *and* lower memory).

This replaces the earlier grouped bar chart. Bars with dual log/linear axes
invite visual false-comparison between height and value; a Pareto plot makes
the speed-vs-memory tradeoff explicit and naturally surfaces off-frontier
frameworks (e.g. inferrs, hf_transformers) without misleading empty slots.

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
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse import discover_traces  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
CONCURRENCIES = [1, 8, 16]
THROUGHPUT_KEY = "output_throughput_tps"
MEMORY_KEY = "mem_used_gb"

# Same CVD-safe palette as plot_memory.py so framework colors are stable
# across figures in the paper.
CVD_COLORS = [
    "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2",
    "#D55E00", "#CC79A7", "#000000", "#999999",
]
MARKERS = ["o", "s", "^", "D", "v", "P", "X", "<", ">"]


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
        if not fw or not ts or "concurrency_results" not in data:
            continue
        if fw in by_fw and by_fw[fw][0] >= ts:
            continue
        ccs = {
            int(r["concurrency"]): float(r[THROUGHPUT_KEY])
            for r in data["concurrency_results"]
            if r.get("concurrency") is not None and r.get(THROUGHPUT_KEY) is not None
        }
        by_fw[fw] = (ts, ccs)
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
    markers = {fw: MARKERS[i % len(MARKERS)] for i, fw in enumerate(all_fw)}

    # Shared axis bounds so panels are visually comparable.
    tput_vals = [v for ccs in tput.values() for v in ccs.values() if v > 0]
    mem_vals = [v for ccs in mem.values() for v in ccs.values()]
    x_lo = min(tput_vals) * 0.6
    x_hi = max(tput_vals) * 1.6
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

        # Pareto frontier — dashed line through non-dominated points,
        # extended to the plot edges to visually suggest the unreachable region.
        if len(front_idx) >= 1:
            fx = [xs[i] for i in front_idx]
            fy = [ys[i] for i in front_idx]
            # Staircase step: best-throughput-so-far at each memory level.
            # Draw only between frontier points themselves; avoid extrapolating.
            ax.plot(fx, fy, "k--", linewidth=1.0, alpha=0.6, zorder=2,
                    label="Pareto frontier")

        for i, (x, y, fw) in enumerate(zip(xs, ys, fws)):
            on_front = i in front_set
            ax.scatter(
                x, y,
                s=120 if on_front else 70,
                marker=markers[fw],
                color=colors[fw],
                edgecolors="black" if on_front else "gray",
                linewidths=1.4 if on_front else 0.7,
                zorder=4 if on_front else 3,
            )
            # Label with a small offset; nudge dominated points down-right
            # and frontier points up-right so they rarely collide.
            dx = 1.08
            dy = 0.5 if on_front else -1.2
            ax.annotate(
                fw, (x, y), xytext=(x * dx, y + dy),
                fontsize=8, alpha=0.95,
                color="black" if on_front else "#555555",
            )

        ax.set_xscale("log")
        ax.set_xlim(x_lo, x_hi)
        ax.set_ylim(y_lo, y_hi)
        ax.set_title(f"concurrency {c}")
        ax.set_xlabel("output throughput (tok/s, log)")
        ax.grid(True, which="both", alpha=0.25)

    axes[0].set_ylabel("peak system memory (GB)")

    # Single legend (frontier line + "frontier / dominated" marker cue).
    legend_elements = [
        plt.Line2D([0], [0], linestyle="--", color="black", alpha=0.6,
                   label="Pareto frontier"),
        plt.Line2D([0], [0], marker="o", color="white",
                   markerfacecolor="#999", markeredgecolor="black",
                   markersize=10, linestyle="None", label="on frontier"),
        plt.Line2D([0], [0], marker="o", color="white",
                   markerfacecolor="#999", markeredgecolor="gray",
                   markersize=7, linestyle="None", label="dominated"),
    ]
    fig.legend(
        handles=legend_elements,
        loc="upper center", bbox_to_anchor=(0.5, 0.02),
        ncol=3, frameon=False,
    )
    fig.suptitle(
        f"{args.model} — {args.split} split — throughput vs peak memory "
        "(up-and-to-the-right is better; frontier dashed)"
    )
    fig.tight_layout(rect=(0, 0.04, 1, 0.97))

    out = args.out or REPO_ROOT / "draw" / f"pareto_{args.model}_{args.split}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()

"""Grouped bar chart: output throughput and peak memory per framework.

One row, three columns — one subplot per concurrency level (1, 8, 16). Each
subplot has a twin y-axis: left = output throughput (tok/s, log), right = peak
system memory (GB, linear). For every framework, two bars sit side by side
(throughput + memory).

Usage:
    python draw/plot_throughput_memory.py                          # Qwen3-0.6B chat
    python draw/plot_throughput_memory.py --split agent
    python draw/plot_throughput_memory.py --model Qwen3-8B --split chat
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse import discover_traces  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
CONCURRENCIES = [1, 8, 16]
THROUGHPUT_KEY = "output_throughput_tps"
MEMORY_KEY = "mem_used_gb"

TPUT_COLOR = "#0072B2"  # blue — throughput bars
MEM_COLOR = "#D55E00"   # vermillion — memory bars


def load_throughput(split_dir: Path) -> dict[str, dict[int, float]]:
    """framework -> {concurrency: output_throughput_tps}. Latest result per fw."""
    by_fw: dict[str, tuple[str, dict[int, float]]] = {}
    for path in sorted(split_dir.glob("*.json")):
        if path.name in ("comparison.json",) or "metalstat" in path.name:
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
        ccs: dict[int, float] = {}
        for r in data["concurrency_results"]:
            c = r.get("concurrency")
            v = r.get(THROUGHPUT_KEY)
            if c is None or v is None:
                continue
            ccs[int(c)] = float(v)
        by_fw[fw] = (ts, ccs)
    return {fw: ccs for fw, (_, ccs) in by_fw.items()}


def load_peak_memory(split_dir: Path) -> dict[str, dict[int, float]]:
    """framework -> {concurrency: peak mem_used_gb during that phase}."""
    traces = discover_traces(split_dir)
    out: dict[str, dict[int, float]] = {}
    for fw, tr in traces.items():
        per_c: dict[int, float] = {}
        series = tr.series(MEMORY_KEY)
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


def draw_panel(ax_t, frameworks, tput_row, mem_row):
    """One concurrency subplot — twin y-axis with throughput + memory bars.
    Returns the twin axis so the caller can set its ylim."""
    n = len(frameworks)
    x = np.arange(n)
    w = 0.38

    ax_m = ax_t.twinx()

    tput_y = [tput_row.get(fw, np.nan) for fw in frameworks]
    mem_y = [mem_row.get(fw, np.nan) for fw in frameworks]

    ax_t.bar(x - w/2, tput_y, width=w, color=TPUT_COLOR, label="throughput")
    ax_m.bar(x + w/2, mem_y, width=w, color=MEM_COLOR, label="peak memory")

    ax_t.set_xticks(x)
    ax_t.set_xticklabels(frameworks, rotation=30, ha="right")
    ax_t.set_yscale("log")
    ax_t.set_ylabel("output throughput (tok/s)", color=TPUT_COLOR)
    ax_t.tick_params(axis="y", labelcolor=TPUT_COLOR)
    ax_m.set_ylabel("peak system memory (GB)", color=MEM_COLOR)
    ax_m.tick_params(axis="y", labelcolor=MEM_COLOR)
    ax_t.grid(True, axis="y", alpha=0.2)
    return ax_m


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

    # Union of frameworks that have either throughput or memory data.
    all_fw = set(tput) | set(mem)
    # Order by c=8 throughput desc (fallback: c=1, then name) so strongest read left→right.
    frameworks = sorted(
        all_fw,
        key=lambda fw: (
            -(tput.get(fw, {}).get(8, 0) or 0),
            -(tput.get(fw, {}).get(1, 0) or 0),
            fw,
        ),
    )

    # Uniform y-scales across all three subplots so concurrency levels are
    # visually comparable. Memory on a linear scale with some headroom.
    tput_values = [v for ccs in tput.values() for v in ccs.values() if v > 0]
    tput_max = max(tput_values, default=1)
    tput_min = min(tput_values, default=0.1)
    mem_max = max((v for ccs in mem.values() for v in ccs.values()), default=1)

    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
    for ax, c in zip(axes, CONCURRENCIES):
        ax_m = draw_panel(
            ax,
            frameworks,
            {fw: tput.get(fw, {}).get(c, np.nan) for fw in frameworks},
            {fw: mem.get(fw, {}).get(c, np.nan) for fw in frameworks},
        )
        ax.set_title(f"concurrency {c}")
        ax.set_ylim(tput_min * 0.5, tput_max * 1.3)
        ax_m.set_ylim(0, mem_max * 1.1)

    legend_handles = [
        mpatches.Patch(color=TPUT_COLOR, label="output throughput (left, log)"),
        mpatches.Patch(color=MEM_COLOR, label="peak memory (right, linear)"),
    ]
    fig.legend(
        handles=legend_handles,
        loc="upper center", bbox_to_anchor=(0.5, 0.03),
        ncol=2, frameon=False,
    )
    fig.suptitle(
        f"{args.model} — {args.split} split — throughput & peak memory by concurrency"
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))

    out = args.out or REPO_ROOT / "draw" / f"throughput_memory_{args.model}_{args.split}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"wrote {out}")
    missing_mem = [fw for fw in frameworks if fw not in mem or not mem[fw]]
    if missing_mem:
        print(f"note: no memory trace for: {', '.join(missing_mem)}")


if __name__ == "__main__":
    main()

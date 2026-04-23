"""Plot system-memory-over-time from metalstat sidecars.

One row, three columns — one subplot per concurrency level (1, 8, 16).
Each trace is sliced per phase using cumulative wall_time_s recorded in
the benchmark result JSON; the per-phase x-axis is normalized to 0-100%
so shapes are directly comparable across frameworks.

Usage:
    python draw/plot_memory.py                    # Qwen3-0.6B chat
    python draw/plot_memory.py --split agent
    python draw/plot_memory.py --model Qwen3-8B --split chat
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse import discover_traces  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
CONCURRENCIES = [1, 8, 16]
METRIC = "mem_used_gb"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen3-0.6B")
    ap.add_argument("--split", default="chat", choices=["chat", "agent"])
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    split_dir = REPO_ROOT / "results" / args.model / args.split
    traces = discover_traces(split_dir)
    if not traces:
        raise SystemExit(f"No *_metalstat.jsonl under {split_dir}")

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), sharey=True)
    cmap = plt.get_cmap("tab10")
    frameworks = sorted(traces)
    colors = {fw: cmap(i % 10) for i, fw in enumerate(frameworks)}

    for ax, conc in zip(axes, CONCURRENCIES):
        for fw in frameworks:
            tr = traces[fw]
            phase = tr.phase_slice(conc)
            if phase is None:
                continue
            x_pct, idxs = phase
            series = tr.series(METRIC)
            y = [series[i] for i in idxs]
            ax.plot(x_pct, y, label=fw, color=colors[fw], linewidth=1.2)
        ax.set_title(f"concurrency {conc}")
        ax.set_xlabel("phase progress (%)")
        ax.set_xlim(0, 100)
        ax.grid(True, alpha=0.3)
    axes[0].set_ylabel("system memory used (GB)")

    axes[-1].legend(
        loc="upper left", bbox_to_anchor=(1.02, 1.0), frameon=False
    )
    fig.suptitle(
        f"{args.model} — {args.split} split — system memory by concurrency "
        f"({len(traces)}/9 frameworks traced)"
    )
    fig.tight_layout()

    out = args.out or REPO_ROOT / "draw" / f"memory_{args.model}_{args.split}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()

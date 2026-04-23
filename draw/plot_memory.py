"""Plot memory-over-time from metalstat sidecars as a 1x3 panel figure.

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

PANELS = [
    ("mem_used_gb", "System memory used"),
    ("gpu_mem_allocated_gb", "GPU memory allocated"),
    ("mem_wired_gb", "Wired memory"),
]


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

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), sharex=True)
    cmap = plt.get_cmap("tab10")
    frameworks = sorted(traces)
    colors = {fw: cmap(i % 10) for i, fw in enumerate(frameworks)}

    for ax, (key, title) in zip(axes, PANELS):
        for fw in frameworks:
            tr = traces[fw]
            elapsed = tr.elapsed_s
            total = elapsed[-1] if elapsed else 0
            if total <= 0:
                continue
            x_pct = [100.0 * t / total for t in elapsed]
            ax.plot(
                x_pct,
                tr.series(key),
                label=fw,
                color=colors[fw],
                linewidth=1.2,
            )
        ax.set_title(title)
        ax.set_xlabel("run progress (%)")
        ax.set_ylabel("GB")
        ax.set_xlim(0, 100)
        ax.grid(True, alpha=0.3)

    axes[-1].legend(
        loc="upper left", bbox_to_anchor=(1.02, 1.0), frameon=False
    )
    fig.suptitle(
        f"{args.model} — {args.split} split ({len(traces)}/9 frameworks traced)"
    )
    fig.tight_layout()

    out = args.out or REPO_ROOT / "draw" / f"memory_{args.model}_{args.split}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()

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
from parse import CVD_COLORS, discover_traces  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
CONCURRENCIES = [1, 8, 16]
METRIC = "mem_used_gb"

# Extra redundancy via linestyle rotation — helps when two lines overlap.
CVD_LINESTYLES = ["-", "--", "-.", ":", "-", "--", "-.", ":", "-"]


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

    plt.rcParams.update({
        "font.size": 13,
        "axes.titlesize": 14,
        "axes.labelsize": 13,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
    })
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), sharey=True)
    frameworks = sorted(traces)
    colors = {fw: CVD_COLORS[i % len(CVD_COLORS)] for i, fw in enumerate(frameworks)}
    styles = {fw: CVD_LINESTYLES[i % len(CVD_LINESTYLES)] for i, fw in enumerate(frameworks)}

    for ax, conc in zip(axes, CONCURRENCIES):
        for fw in frameworks:
            tr = traces[fw]
            phase = tr.phase_slice(conc)
            if phase is None:
                continue
            x_pct, idxs = phase
            series = tr.series(METRIC)
            y = [series[i] for i in idxs]
            ax.plot(
                x_pct, y, label=fw,
                color=colors[fw], linestyle=styles[fw], linewidth=2.0,
            )
        ax.set_title(f"concurrency {conc}")
        ax.set_xlabel("phase progress (%)")
        ax.set_xlim(0, 100)
        ax.grid(True, alpha=0.3)
    axes[0].set_ylabel("system memory used (GB)")

    # Legend built from the c=1 panel so frameworks that only benched at c=1
    # (e.g. hf_transformers when c=8/c=16 were adaptively skipped) still appear.
    handles, labels = axes[0].get_legend_handles_labels()
    axes[-1].legend(
        handles, labels,
        loc="upper left", bbox_to_anchor=(1.02, 1.0), frameon=False,
        fontsize=12,
    )
    fig.tight_layout()

    # Stem string + manual suffix — Path.with_suffix() would truncate
    # at the first dot in names like "Qwen3-0.6B".
    if args.out:
        stem = str(args.out.parent / args.out.stem) if args.out.suffix else str(args.out)
    else:
        stem = str(REPO_ROOT / "draw" / f"memory_{args.model}_{args.split}")
    Path(stem).parent.mkdir(parents=True, exist_ok=True)
    pdf_path, png_path = stem + ".pdf", stem + ".png"
    fig.savefig(pdf_path, bbox_inches="tight")
    fig.savefig(png_path, dpi=150, bbox_inches="tight")
    print(f"wrote {pdf_path}")
    print(f"wrote {png_path}")


if __name__ == "__main__":
    main()

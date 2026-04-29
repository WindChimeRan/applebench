#!/usr/bin/env python3
"""Plot memory + per-request timeline for sequential vs concurrent runs.

Layout (4 rows, shared x-axis):
  - Sequential GPU memory
  - Sequential Gantt (per-request prefill / decode bars)
  - Concurrent GPU memory
  - Concurrent Gantt
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch

RESULTS = Path(__file__).parent / "results"
OUT_PNG = RESULTS / "memory_comparison.png"
OUT_PDF = RESULTS / "memory_comparison.pdf"

SEQ_COLOR = "#3b6ea5"
CON_COLOR = "#c43a31"
GANTT_COLORS = {"long": "#2c4a6b", "medium": "#5e89b3", "short": "#a3bcd5"}
ORDER = ["long", "medium", "short"]

plt.rcParams.update({
    "font.size": 13,
    "axes.labelsize": 13,
    "axes.titlesize": 13,
    "legend.fontsize": 12,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def load(mode):
    samples = [json.loads(l) for l in open(RESULTS / f"{mode}.jsonl")]
    workload = json.load(open(RESULTS / f"{mode}_workload.json"))
    return {
        "t": [s["elapsed_s"] for s in samples],
        "gpu": [s["gpu_mem_allocated_gb"] for s in samples],
        "workload": workload,
    }


def draw_gantt(ax, workload):
    wall_t0 = workload["wall_t0"]
    name_to_y = {n: i for i, n in enumerate(ORDER)}
    for r in workload["results"]:
        y = name_to_y[r["name"]]
        c = GANTT_COLORS[r["name"]]
        sub = r["t_submit"] - wall_t0
        ttft = r["t_first_token"] - wall_t0
        done = r["t_done"] - wall_t0
        ax.barh(y, ttft - sub, left=sub, height=0.55, color=c, alpha=0.4, edgecolor="none")
        ax.barh(y, done - ttft, left=ttft, height=0.55, color=c, edgecolor="none")
    ax.set_yticks(range(len(ORDER)))
    ax.set_yticklabels(ORDER)
    ax.invert_yaxis()
    ax.xaxis.grid(True, ls="--", alpha=0.3)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)


def draw_memory(ax, data, color, label, peak_ref=None, peak_ref_color=None):
    peak = max(data["gpu"])
    wall = data["workload"]["wall_time"]
    ax.plot(data["t"], data["gpu"], color=color, lw=1.0)
    ax.axhline(peak, color=color, ls="--", lw=0.8, alpha=0.6)
    ax.text(0.995, peak, f" {peak:.1f} GB", transform=ax.get_yaxis_transform(),
            color=color, fontsize=12, va="center", ha="left", clip_on=False)
    if peak_ref is not None:
        ax.axhline(peak_ref, color=peak_ref_color, ls=":", lw=0.8, alpha=0.7)
        ax.text(0.995, peak_ref, f" seq peak", transform=ax.get_yaxis_transform(),
                color=peak_ref_color, fontsize=11, va="center", ha="left",
                alpha=0.8, clip_on=False)
    ax.text(0.005, 0.95, f"{label}  ·  wall {wall:.1f}s",
            transform=ax.transAxes, fontsize=13, fontweight="bold",
            color=color, va="top")
    ax.set_ylabel("GPU mem (GB)")
    ax.yaxis.grid(True, ls="--", alpha=0.3)


def main():
    seq = load("sequential")
    con = load("concurrent")

    seq_peak = max(seq["gpu"])
    con_peak = max(con["gpu"])
    xmax = max(max(seq["t"]), max(con["t"])) * 1.02
    ymax = con_peak * 1.10

    fig, axes = plt.subplots(
        4, 1, figsize=(8, 6), sharex=True,
        gridspec_kw={"height_ratios": [4, 1, 4, 1]},
        constrained_layout=True,
    )

    draw_memory(axes[0], seq, SEQ_COLOR, "Sequential")
    axes[0].set_ylim(0, ymax)
    draw_gantt(axes[1], seq["workload"])

    draw_memory(axes[2], con, CON_COLOR, "Concurrent",
                peak_ref=seq_peak, peak_ref_color=SEQ_COLOR)
    axes[2].set_ylim(0, ymax)
    draw_gantt(axes[3], con["workload"])

    axes[3].set_xlabel("Elapsed seconds")
    axes[3].set_xlim(0, xmax)

    max_tokens = con["workload"].get("max_tokens", seq["workload"].get("max_tokens", "?"))
    fig.suptitle(
        f"Qwen3-0.6B  ·  prompts 30k / 5k / 10 tokens  ·  max_tokens={max_tokens}  ·  ratio {con_peak/seq_peak:.2f}×",
        fontsize=12,
    )
    legend = [
        Patch(facecolor="#5e89b3", alpha=0.4, label="Prefill"),
        Patch(facecolor="#5e89b3", label="Decode"),
    ]
    fig.legend(handles=legend, loc="lower center", ncol=2, fontsize=12,
               bbox_to_anchor=(0.5, -0.04), frameon=False)

    plt.savefig(OUT_PNG, dpi=140, bbox_inches="tight")
    plt.savefig(OUT_PDF, bbox_inches="tight")
    print(f"Wrote {OUT_PNG}")
    print(f"Wrote {OUT_PDF}")
    print()
    print(f"Sequential:  peak {seq_peak:.2f} GB, wall {seq['workload']['wall_time']:.1f}s")
    print(f"Concurrent:  peak {con_peak:.2f} GB, wall {con['workload']['wall_time']:.1f}s")
    print(f"Memory ratio:  {con_peak / seq_peak:.2f}×")


if __name__ == "__main__":
    main()

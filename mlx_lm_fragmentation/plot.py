#!/usr/bin/env python3
"""Plot memory + per-request timeline for sequential vs concurrent runs.

Layout (4 rows, shared x-axis):
  - Sequential GPU memory
  - Sequential Gantt (per-request prefill / decode bars)
  - Concurrent GPU memory
  - Concurrent Gantt
"""
import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch

RESULTS = Path(os.environ.get("FRAGMENTATION_RESULTS_DIR", Path(__file__).parent / "results"))
OUT_PNG = RESULTS / "memory_comparison.png"
OUT_PDF = RESULTS / "memory_comparison.pdf"

SEQ_COLOR = "#3b6ea5"
CON_COLOR = "#c43a31"

_prompts_cache = json.loads((RESULTS / "prompts.json").read_text())
ORDER = [p["name"] for p in _prompts_cache]
if len(ORDER) <= 3:
    _palette = ["#2c4a6b", "#5e89b3", "#a3bcd5"][: len(ORDER)]
else:
    _cmap = plt.get_cmap("viridis_r")
    _palette = [_cmap(i / max(len(ORDER) - 1, 1)) for i in range(len(ORDER))]
GANTT_COLORS = dict(zip(ORDER, _palette))

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
        "compressed": [s["mem_compressed_gb"] for s in samples],
        "workload": workload,
    }


def draw_gantt(ax, workload):
    wall_t0 = workload["wall_t0"]
    name_to_y = {n: i for i, n in enumerate(ORDER)}
    bar_h = 0.55 if len(ORDER) <= 4 else 0.7
    for r in workload["results"]:
        y = name_to_y[r["name"]]
        c = GANTT_COLORS[r["name"]]
        sub = r["t_submit"] - wall_t0
        done = r["t_done"] - wall_t0
        if r.get("t_first_token") is None:
            ax.barh(y, done - sub, left=sub, height=bar_h, color="#888888", alpha=0.4,
                    edgecolor="#444444", hatch="///")
            continue
        ttft = r["t_first_token"] - wall_t0
        ax.barh(y, ttft - sub, left=sub, height=bar_h, color=c, alpha=0.4, edgecolor="none")
        ax.barh(y, done - ttft, left=ttft, height=bar_h, color=c, edgecolor="none")
    ax.set_yticks(range(len(ORDER)))
    if len(ORDER) <= 8:
        ax.set_yticklabels(ORDER)
    else:
        labels = [n if i == 0 or i == len(ORDER)-1 or i % 4 == 0 else "" for i, n in enumerate(ORDER)]
        ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.xaxis.grid(True, ls="--", alpha=0.3)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)


COMPRESSED_COLOR = "#d97706"


def draw_memory(ax, data, color, label, peak_ref=None, peak_ref_color=None):
    peak = max(data["gpu"])
    wall = data["workload"]["wall_time"]
    ax.plot(data["t"], data["gpu"], color=color, lw=1.0, label="GPU mem")
    ax.plot(data["t"], data["compressed"], color=COMPRESSED_COLOR, lw=1.0,
            ls="--", alpha=0.85, label="Compressed mem")
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
    ax.set_ylabel("memory (GB)")
    ax.yaxis.grid(True, ls="--", alpha=0.3)


def main():
    seq = load("sequential")
    con = load("concurrent")

    seq_peak = max(seq["gpu"])
    con_peak = max(con["gpu"])
    xmax = max(max(seq["t"]), max(con["t"])) * 1.02
    ymax = con_peak * 1.10

    n_prompts = len(ORDER)
    gantt_h = max(1.0, 0.25 * n_prompts)
    fig_h = 6 + 2 * (gantt_h - 1)
    fig, axes = plt.subplots(
        4, 1, figsize=(8, fig_h), sharex=True,
        gridspec_kw={"height_ratios": [4, gantt_h, 4, gantt_h]},
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
    def _fmt(n):
        return f"{n//1000}k" if n >= 1000 else str(n)
    from collections import Counter
    counts = Counter((p["tokens"]) for p in _prompts_cache)
    parts = [f"{c}×{_fmt(s)}" if c > 1 else _fmt(s) for s, c in sorted(counts.items(), reverse=True)]
    sizes = " + ".join(parts)
    fig.suptitle(
        f"Qwen3-0.6B  ·  prompts {sizes} tokens  ·  max_tokens={max_tokens}  ·  ratio {con_peak/seq_peak:.2f}×",
        fontsize=12,
    )
    from matplotlib.lines import Line2D
    legend = [
        Line2D([0], [0], color=COMPRESSED_COLOR, ls="--", lw=1.4, label="Compressed mem"),
        Patch(facecolor="#5e89b3", alpha=0.4, label="Prefill"),
        Patch(facecolor="#5e89b3", label="Decode"),
    ]
    if any(r.get("t_first_token") is None for r in con["workload"]["results"]) or \
       any(r.get("t_first_token") is None for r in seq["workload"]["results"]):
        legend.append(Patch(facecolor="#888888", alpha=0.4, hatch="///",
                            edgecolor="#444444", label="Crashed (OOM)"))
    fig.legend(handles=legend, loc="lower center", ncol=len(legend), fontsize=12,
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

#!/usr/bin/env python3
"""Plot memory timelines for sequential vs concurrent runs.

Two panels:
  - Top: gpu_mem_allocated_gb (MTL::Buffer total) over wall-clock seconds
  - Bottom: mem_used_gb (system) and swap_used_gb

Annotates per-request submit/done events from <mode>_workload.json.
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt

RESULTS = Path(__file__).parent / "results"
OUT = RESULTS / "memory_comparison.png"


def load(mode):
    samples = [json.loads(l) for l in open(RESULTS / f"{mode}.jsonl")]
    workload = json.load(open(RESULTS / f"{mode}_workload.json"))
    return {
        "t": [s["elapsed_s"] for s in samples],
        "gpu": [s["gpu_mem_allocated_gb"] for s in samples],
        "used": [s["mem_used_gb"] for s in samples],
        "swap": [s["swap_used_gb"] for s in samples],
        "workload": workload,
    }


def annotate_events(ax, data, mode, color):
    workload = data["workload"]
    wall_t0 = workload["wall_t0"]
    for r in workload["results"]:
        rel_submit = r["t_submit"] - wall_t0
        rel_done = r["t_done"] - wall_t0
        ax.axvspan(rel_submit, rel_done, alpha=0.07, color=color)
        ax.annotate(
            r["name"],
            xy=(rel_submit, ax.get_ylim()[1] * 0.98),
            xytext=(rel_submit + 0.5, ax.get_ylim()[1] * 0.92),
            fontsize=8, color=color,
        )


def main():
    seq = load("sequential")
    con = load("concurrent")

    fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=False)

    ax = axes[0]
    ax.plot(seq["t"], seq["gpu"], label=f"sequential (peak {max(seq['gpu']):.2f} GB)", color="tab:blue", lw=1.5)
    ax.plot(con["t"], con["gpu"], label=f"concurrent (peak {max(con['gpu']):.2f} GB)", color="tab:red", lw=1.5)
    ax.set_ylabel("Metal GPU memory allocated (GB)")
    ax.set_title("KV cache memory: sequential (3 prompts one at a time) vs concurrent (3 batched)\n"
                 "Qwen3-0.6B, prompts = 30k / 5k / 10 tokens, max_tokens=16")
    ax.legend(loc="upper right")
    ax.grid(alpha=0.3)
    annotate_events(ax, seq, "sequential", "tab:blue")
    annotate_events(ax, con, "concurrent", "tab:red")

    ax = axes[1]
    ax.plot(seq["t"], seq["used"], color="tab:blue", lw=1.2, label="sequential mem_used")
    ax.plot(con["t"], con["used"], color="tab:red", lw=1.2, label="concurrent mem_used")
    ax.plot(seq["t"], seq["swap"], color="tab:blue", lw=0.8, ls="--", label="sequential swap")
    ax.plot(con["t"], con["swap"], color="tab:red", lw=0.8, ls="--", label="concurrent swap")
    ax.set_ylabel("System memory / swap (GB)")
    ax.set_xlabel("Elapsed seconds (each run starts at 0)")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUT, dpi=120)
    print(f"Wrote {OUT}")
    print()
    print(f"Sequential:  peak GPU mem {max(seq['gpu']):.2f} GB, wall time {seq['workload']['wall_time']:.1f}s")
    print(f"Concurrent:  peak GPU mem {max(con['gpu']):.2f} GB, wall time {con['workload']['wall_time']:.1f}s")
    print(f"Memory ratio (concurrent / sequential):  {max(con['gpu']) / max(seq['gpu']):.2f}×")


if __name__ == "__main__":
    main()

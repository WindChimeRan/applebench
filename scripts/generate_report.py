#!/usr/bin/env python3
"""
Generate a markdown report from benchmark results.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", default=None, help="Results directory")
    args = parser.parse_args()

    if args.results_dir:
        results_dir = Path(args.results_dir)
    else:
        results_dir = Path(__file__).parent.parent / "results"
    comparison_file = results_dir / "comparison.json"

    if not comparison_file.exists():
        print("No comparison.json found. Run collect_results.py first.")
        sys.exit(1)

    with open(comparison_file) as f:
        data = json.load(f)

    frameworks = data["frameworks"]
    results = data["results"]

    model_name = data.get("model_name", results_dir.name)

    lines = []
    lines.append("# AppleBench Results")
    lines.append("")
    lines.append(f"**Model:** {model_name}")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # Get all concurrency levels from the first framework
    first_fw = results[frameworks[0]]
    conc_levels = [r["concurrency"] for r in first_fw["concurrency_results"]]

    for conc in conc_levels:
        lines.append(f"## Concurrency: {conc}")
        lines.append("")

        # Table header
        header = "| Metric |"
        sep = "|--------|"
        for fw in frameworks:
            header += f" {fw} |"
            sep += "--------|"
        lines.append(header)
        lines.append(sep)

        # Find matching concurrency result for each framework
        fw_results = {}
        for fw in frameworks:
            for cr in results[fw]["concurrency_results"]:
                if cr["concurrency"] == conc:
                    fw_results[fw] = cr
                    break

        metrics = [
            ("Successful / Failed", None, None),  # special row
            ("TTFT avg (ms)", "ttft_avg_ms", ".1f"),
            ("TTFT p50 (ms)", "ttft_p50_ms", ".1f"),
            ("TTFT p99 (ms)", "ttft_p99_ms", ".1f"),
            ("Throughput avg (tok/s)", "throughput_avg_tps", ".1f"),
            ("Aggregate throughput (tok/s)", "aggregate_throughput_tps", ".1f"),
            ("ITL avg (ms)", "itl_avg_ms", ".1f"),
            ("ITL p50 (ms)", "itl_p50_ms", ".1f"),
            ("Latency avg (s)", "latency_avg_s", ".2f"),
            ("Latency p99 (s)", "latency_p99_s", ".2f"),
            ("Wall time (s)", "wall_time_s", ".1f"),
        ]

        for label, key, fmt in metrics:
            row = f"| {label} |"
            for fw in frameworks:
                cr = fw_results.get(fw, {})
                if key is None:  # special success/fail row
                    s = cr.get("successful", 0)
                    f_ = cr.get("failed", 0)
                    err = cr.get("error", "")
                    if err and s == 0:
                        if "not run" in err or "skipped" in err:
                            label = err.upper()
                        else:
                            label = "CRASHED"
                        row += f" {label} |"
                    elif f_ > 0:
                        row += f" {s} / {f_} |"
                    else:
                        row += f" {s} / 0 |"
                else:
                    val = cr.get(key, 0)
                    row += f" {val:{fmt}} |"
            lines.append(row)

        lines.append("")

    # Total duration per framework
    lines.append("## Total Benchmark Duration")
    lines.append("")
    header = "| Framework |"
    sep = "|-----------|"
    for fw in frameworks:
        dur = results[fw].get("total_duration_s", 0)
        header += f" {fw} |"
        sep += "--------|"
    lines.append(header)
    lines.append(sep)
    row = "| Duration |"
    for fw in frameworks:
        dur = results[fw].get("total_duration_s", 0)
        if dur >= 60:
            row += f" {dur/60:.1f}m |"
        else:
            row += f" {dur:.1f}s |"
    lines.append(row)
    lines.append("")

    # Write report
    report_path = results_dir / "REPORT.md"
    with open(report_path, "w") as f:
        f.write("\n".join(lines))

    print(f"Report saved to: {report_path}")

    # Also print to stdout
    print()
    print("\n".join(lines))


if __name__ == "__main__":
    main()

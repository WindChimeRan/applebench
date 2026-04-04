#!/usr/bin/env python3
"""
Generate a markdown report from benchmark results.
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def main():
    results_dir = Path(__file__).parent.parent / "results"
    comparison_file = results_dir / "comparison.json"

    if not comparison_file.exists():
        print("No comparison.json found. Run collect_results.py first.")
        sys.exit(1)

    with open(comparison_file) as f:
        data = json.load(f)

    frameworks = data["frameworks"]
    results = data["results"]

    lines = []
    lines.append("# AppleBench Results")
    lines.append("")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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
            ("TTFT avg (ms)", "ttft_avg_ms", ".1f"),
            ("TTFT p50 (ms)", "ttft_p50_ms", ".1f"),
            ("TTFT p99 (ms)", "ttft_p99_ms", ".1f"),
            ("Throughput avg (tok/s)", "throughput_avg_tps", ".1f"),
            ("Aggregate throughput (tok/s)", "aggregate_throughput_tps", ".1f"),
            ("ITL avg (ms)", "itl_avg_ms", ".1f"),
            ("ITL p50 (ms)", "itl_p50_ms", ".1f"),
            ("Latency avg (s)", "latency_avg_s", ".2f"),
            ("Latency p99 (s)", "latency_p99_s", ".2f"),
        ]

        for label, key, fmt in metrics:
            row = f"| {label} |"
            values = []
            for fw in frameworks:
                val = fw_results.get(fw, {}).get(key, 0)
                values.append(val)
                row += f" {val:{fmt}} |"
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

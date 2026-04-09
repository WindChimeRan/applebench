#!/usr/bin/env python3
"""
Collect individual benchmark results into a single comparison JSON.
"""

import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", default=None, help="Results directory")
    args = parser.parse_args()

    if args.results_dir:
        results_dir = Path(args.results_dir)
    else:
        results_dir = Path(__file__).parent.parent / "results"

    # Find the latest result for each framework (by file modification time)
    frameworks = {}
    latest_mtime = {}
    for f in results_dir.glob("*.json"):
        if f.name == "comparison.json":
            continue
        try:
            with open(f) as fh:
                data = json.load(fh)
        except json.JSONDecodeError as e:
            print(f"Warning: skipping corrupted file {f.name}: {e}")
            continue
        fw = data.get("framework", "unknown")
        mtime = f.stat().st_mtime
        if fw not in frameworks or mtime > latest_mtime[fw]:
            frameworks[fw] = data
            latest_mtime[fw] = mtime

    if not frameworks:
        print("No results found")
        sys.exit(1)

    # Derive model name from results directory name
    model_name = results_dir.name

    comparison = {
        "model_name": model_name,
        "frameworks": list(frameworks.keys()),
        "results": frameworks,
    }

    output = results_dir / "comparison.json"
    with open(output, "w") as f:
        json.dump(comparison, f, indent=2)

    print(f"Comparison saved to: {output}")
    print(f"Frameworks: {', '.join(frameworks.keys())}")


if __name__ == "__main__":
    main()

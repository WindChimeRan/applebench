#!/usr/bin/env python3
"""
Collect individual benchmark results into a single comparison JSON.
"""

import json
import glob
import sys
from pathlib import Path


def main():
    results_dir = Path(__file__).parent.parent / "results"

    # Find the latest result for each framework
    frameworks = {}
    for f in sorted(results_dir.glob("*.json")):
        if f.name == "comparison.json":
            continue
        with open(f) as fh:
            data = json.load(fh)
        fw = data.get("framework", "unknown")
        frameworks[fw] = data

    if not frameworks:
        print("No results found")
        sys.exit(1)

    comparison = {
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

#!/usr/bin/env python3
"""
Aggregate per-(framework, shot) scores.json files into a single comparison
JSON + markdown table. Run at the end of run_all_mac.sh.

Layout assumed:
  <results-dir>/<framework>_<model-slug>_<N>shot/scores.json

Writes:
  <results-dir>/<model-slug>_comparison.json
  <results-dir>/<model-slug>_comparison.md
"""

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", required=True,
                        help="correctness/results/ root")
    parser.add_argument("--model", required=True,
                        help="Model slug used in result dir names (e.g. Qwen3-0.6B)")
    parser.add_argument("--shots", required=True,
                        help="Space-separated shot counts to include (e.g. '0 5')")
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    shot_counts = [int(s) for s in args.shots.split()]
    model = args.model

    comparison: dict = {"model": model, "shots": shot_counts, "frameworks": {}}

    for d in sorted(results_dir.iterdir()):
        if not d.is_dir():
            continue
        name = d.name
        if not name.endswith("shot"):
            continue
        # Expect "<framework>_<model>_<N>shot"
        stem = name[:-4]  # strip trailing "shot"
        parts = stem.rsplit("_", 2)
        if len(parts) != 3:
            continue
        framework, dir_model, n_str = parts
        if dir_model != model or not n_str.isdigit():
            continue
        n = int(n_str)
        if n not in shot_counts:
            continue

        scores_path = d / "scores.json"
        if not scores_path.exists():
            comparison["frameworks"].setdefault(framework, {})[f"{n}shot"] = None
            continue

        with open(scores_path) as f:
            s = json.load(f)
        comparison["frameworks"].setdefault(framework, {})[f"{n}shot"] = {
            "f1_weighted": s["f1_weighted"],
            "f1_macro": s["f1_macro"],
            "exact_match": s["exact_match"],
            "n_scored": s["n_scored"],
            "request_errors": s["request_errors"],
            "parse_failures": s["parse_failures"],
            "oov_predictions_after_parse": s["oov_predictions_after_parse"],
        }

    # Order frameworks in the canonical AppleBench order
    canonical_order = [
        "llamacpp", "mlx_lm", "mistralrs", "vllm_metal", "omlx",
        "ollama", "inferrs", "vllm_mlx", "hf_transformers",
    ]
    known = [f for f in canonical_order if f in comparison["frameworks"]]
    extras = sorted(set(comparison["frameworks"]) - set(canonical_order))
    ordered = {f: comparison["frameworks"][f] for f in known + extras}
    comparison["frameworks"] = ordered

    out_json = results_dir / f"{model}_comparison.json"
    out_md = results_dir / f"{model}_comparison.md"

    with open(out_json, "w") as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)

    lines = [f"# Correctness eval — {model}", ""]
    header = ["Framework"]
    for n in shot_counts:
        header += [f"{n}-shot F1", f"{n}-shot F1-macro", f"{n}-shot EM", f"{n}-shot errors"]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "|".join(["---"] * len(header)) + "|")

    for fw, shot_scores in ordered.items():
        row = [fw]
        for n in shot_counts:
            cell = shot_scores.get(f"{n}shot")
            if cell is None:
                row += ["—", "—", "—", "—"]
            else:
                row += [
                    f"{cell['f1_weighted']:.4f}",
                    f"{cell['f1_macro']:.4f}",
                    f"{cell['exact_match']:.4f}",
                    f"{cell['request_errors']}/{cell['parse_failures']}",
                ]
        lines.append("| " + " | ".join(row) + " |")

    lines.append("")
    lines.append("errors column = request_errors / parse_failures")
    lines.append("")

    with open(out_md, "w") as f:
        f.write("\n".join(lines))

    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print()
    print("\n".join(lines))


if __name__ == "__main__":
    main()

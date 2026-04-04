#!/usr/bin/env python3
"""
Prepare benchmark prompts from OpenOrca + CNN/DailyMail datasets.

Samples prompts across input length buckets (short to very long)
to create a balanced benchmark dataset for serving benchmarks.

Sources:
  - Open-Orca/OpenOrca: short/medium prompts (instructions)
  - abisee/cnn_dailymail: long/very-long prompts (news articles)
"""

import json
import random
import sys
import urllib.request
from pathlib import Path

SEED = 42
MODELS_DIR = Path(__file__).parent.parent / ".models"
OUTPUT_PATH = Path(__file__).parent.parent / "prompts" / "benchmark_prompts.json"

# HuggingFace Dataset Viewer API
HF_API = "https://datasets-server.huggingface.co"

# Input length buckets (token counts, ~4 chars/token for English)
# (min_tokens, max_tokens, max_output_tokens, count, label)
BUCKETS = [
    # Short input (~50 tokens)
    (10, 80, 64, 10, "short"),
    (10, 80, 256, 10, "short"),
    # Medium input (~200-500 tokens)
    (80, 500, 64, 10, "medium"),
    (80, 500, 256, 10, "medium"),
    # Long input (~500-2000 tokens)
    (500, 2000, 64, 15, "long"),
    (500, 2000, 256, 15, "long"),
    # Very long input (~2000-4000 tokens)
    (2000, 4000, 64, 15, "vlong"),
    (2000, 4000, 256, 15, "vlong"),
]
# Total: 100 prompts


def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token for English."""
    return len(text) // 4


def fetch_hf_rows(dataset: str, config: str, split: str, offset: int, length: int) -> list:
    """Fetch rows from HuggingFace Dataset Viewer API."""
    url = f"{HF_API}/rows?dataset={dataset}&config={config}&split={split}&offset={offset}&length={length}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    return [row["row"] for row in data.get("rows", [])]


def load_openorca_prompts(n_pages: int = 50) -> list[str]:
    """Load prompts from OpenOrca via HF API (sampled pages)."""
    cache = MODELS_DIR / "openorca_cache.json"
    if cache.exists():
        print(f"  Using cached OpenOrca data: {cache}")
        with open(cache) as f:
            return json.load(f)

    print(f"  Fetching OpenOrca ({n_pages} pages of 100 rows)...")
    rng = random.Random(SEED)
    # Sample from different offsets to get variety
    # OpenOrca has ~4.2M rows
    offsets = rng.sample(range(0, 4_000_000, 100), n_pages)

    prompts = []
    for i, offset in enumerate(offsets):
        try:
            rows = fetch_hf_rows("Open-Orca/OpenOrca", "default", "train", offset, 100)
            for row in rows:
                q = row.get("question", "").strip()
                if q and len(q) > 40:
                    prompts.append(q)
        except Exception as e:
            print(f"    Page {i} (offset {offset}) failed: {e}")
        if (i + 1) % 10 == 0:
            print(f"    Fetched {i + 1}/{n_pages} pages, {len(prompts)} prompts so far")

    cache.parent.mkdir(parents=True, exist_ok=True)
    with open(cache, "w") as f:
        json.dump(prompts, f)
    print(f"  Total OpenOrca prompts: {len(prompts)}")
    return prompts


def load_cnn_prompts(n_pages: int = 30) -> list[str]:
    """Load articles from CNN/DailyMail via HF API."""
    cache = MODELS_DIR / "cnn_cache.json"
    if cache.exists():
        print(f"  Using cached CNN/DailyMail data: {cache}")
        with open(cache) as f:
            return json.load(f)

    print(f"  Fetching CNN/DailyMail ({n_pages} pages of 100 rows)...")
    rng = random.Random(SEED)
    # CNN/DailyMail test split has ~11.5K rows
    offsets = rng.sample(range(0, 11_000, 100), min(n_pages, 110))

    articles = []
    for i, offset in enumerate(offsets):
        try:
            rows = fetch_hf_rows("abisee/cnn_dailymail", "3.0.0", "test", offset, 100)
            for row in rows:
                article = row.get("article", "").strip()
                if article and len(article) > 500:
                    # Wrap as a summarization prompt
                    prompt = f"Please read the following article and provide a detailed summary:\n\n{article}"
                    articles.append(prompt)
        except Exception as e:
            print(f"    Page {i} (offset {offset}) failed: {e}")
        if (i + 1) % 10 == 0:
            print(f"    Fetched {i + 1}/{n_pages} pages, {len(articles)} articles so far")

    cache.parent.mkdir(parents=True, exist_ok=True)
    with open(cache, "w") as f:
        json.dump(articles, f)
    print(f"  Total CNN/DailyMail articles: {len(articles)}")
    return articles


def sample_prompts(all_prompts: list[str]) -> list[dict]:
    """Sample prompts into input length buckets."""
    rng = random.Random(SEED)
    rng.shuffle(all_prompts)

    # Group prompts by estimated token length
    by_range = {}
    for text in all_prompts:
        est = estimate_tokens(text)
        by_range.setdefault(est, []).append(text)

    result = []
    prompt_id = 0

    for min_tok, max_tok, max_output, count, label in BUCKETS:
        candidates = []
        for tok_len, texts in by_range.items():
            if min_tok <= tok_len <= max_tok:
                candidates.extend(texts)

        if len(candidates) < count:
            print(f"  Warning: only {len(candidates)} prompts in [{min_tok}, {max_tok}] tokens, need {count}")
            count = min(count, len(candidates))

        rng.shuffle(candidates)
        for text in candidates[:count]:
            result.append({
                "name": f"p{prompt_id:03d}_{label}_out{max_output}",
                "description": f"Input ~{estimate_tokens(text)} tokens, output max {max_output}",
                "messages": [{"role": "user", "content": text}],
                "max_tokens": max_output,
            })
            prompt_id += 1

    rng.shuffle(result)
    return result


def main():
    print("=== Preparing benchmark dataset ===\n")

    print("1. Loading OpenOrca (short/medium/long prompts)...")
    orca_prompts = load_openorca_prompts()

    print("\n2. Loading CNN/DailyMail (long/very-long articles)...")
    cnn_prompts = load_cnn_prompts()

    # Combine all prompts
    all_prompts = orca_prompts + cnn_prompts
    print(f"\nTotal pool: {len(all_prompts)} prompts")

    # Show length distribution of pool
    lengths = [estimate_tokens(p) for p in all_prompts]
    print(f"Token lengths: min={min(lengths)}, median={sorted(lengths)[len(lengths)//2]}, "
          f"max={max(lengths)}, mean={sum(lengths)/len(lengths):.0f}")

    print("\n3. Sampling into buckets...")
    prompts = sample_prompts(all_prompts)
    print(f"\nSampled {len(prompts)} prompts across {len(BUCKETS)} buckets:")

    for min_tok, max_tok, max_output, count, label in BUCKETS:
        actual = sum(1 for p in prompts if f"_{label}_out{max_output}" in p["name"])
        print(f"  [{label:>6s}] Input [{min_tok:>4d}-{max_tok:>4d}] tok, Output {max_output:>3d} tok: {actual} prompts")

    with open(OUTPUT_PATH, "w") as f:
        json.dump(prompts, f, indent=2, ensure_ascii=False)
    print(f"\nSaved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

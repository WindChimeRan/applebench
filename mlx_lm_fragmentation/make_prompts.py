#!/usr/bin/env python3
"""Build 3 prompts of exact token counts for Qwen3-0.6B.

Strategy: encode a very long pangram-based base text once, then slice the
token stream to each target length and decode back. BPE round-trip on plain
ASCII English preserves token count (asserted below).
"""
import json
from pathlib import Path

from tokenizers import Tokenizer

MODEL_DIR = Path("/Users/ran/workspace/applebench/.models/Qwen3-0.6B-bf16-mlx")
OUT = Path(__file__).parent / "results" / "prompts.json"
TARGETS = [("long", 30_000), ("medium", 5_000), ("short", 10)]

PANGRAM = (
    "The quick brown fox jumps over the lazy dog. "
    "Pack my box with five dozen liquor jugs. "
    "How vexingly quick daft zebras jump! "
    "Sphinx of black quartz, judge my vow. "
)

tok = Tokenizer.from_file(str(MODEL_DIR / "tokenizer.json"))
all_ids = tok.encode(PANGRAM * 10_000).ids
assert len(all_ids) >= max(n for _, n in TARGETS), "PANGRAM too short"

prompts = []
for name, n in TARGETS:
    text = tok.decode(all_ids[:n])
    actual = len(tok.encode(text).ids)
    assert actual == n, f"{name}: round-trip mismatch target={n} actual={actual}"
    print(f"{name}: {n} tokens")
    prompts.append({"name": name, "tokens": n, "text": text})

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(prompts))
print(f"Wrote {OUT}")

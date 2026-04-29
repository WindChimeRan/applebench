# mlx_lm Continuous Batching — KV Cache Fragmentation Demo

Goal: show the memory cost of mlx_lm's contiguous (non-paged) KV cache when
multiple sequences of very different lengths are batched together.

mlx_lm's `BatchKVCache` allocates a single dense `[B, H, T, D]` tensor where
T is the longest sequence's `_idx`. Shorter sequences are left-padded to the
same length. So 3 concurrent prompts of 30k / 5k / 10 tokens consume
roughly 3× the cache memory of the 30k prompt alone — most of it wasted on
padding.

## Setup
- Model: Qwen3-0.6B-bf16-mlx (~28 layers, 8 KV heads, 128 head_dim, fp16)
- Prompts: 30k / 5k / 10 tokens (well within Qwen3-0.6B's 32k native ctx)
- Server: `mlx_lm.server` with `--prompt-cache-bytes 1` (LRU disabled)
- Memory monitor: `metalstat -i 0.1` writing JSONL

## Conditions
1. **sequential** — 3 prompts issued one at a time (`workload.py --mode sequential`)
2. **concurrent** — 3 prompts issued simultaneously (`workload.py --mode concurrent`)

## Run
```
./run.sh
python plot.py
```

Outputs in `results/`:
- `prompts.json` — the 3 prompts with exact token counts
- `<mode>.meta.json`, `<mode>.jsonl` — metalstat output
- `<mode>_workload.json` — per-request timings
- `memory_comparison.png` — final plot

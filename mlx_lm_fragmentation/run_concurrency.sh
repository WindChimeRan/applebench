#!/bin/bash
# High-concurrency variant: 1×30k + 15×5k = 16 prompts. Sequential issues
# them one at a time → peak memory driven by the 30k prompt alone.
# Concurrent issues all 16 simultaneously → mlx_lm's BatchKVCache pads
# decode KV for every sequence to the longest (30k), so the decode-phase
# KV cache balloons to 16 × 30k tokens, crossing the M2 Max GPU ceiling
# and triggering memory-pressure-induced slowdown.
#
# prompt-concurrency=1 ensures the prefill scratch never fragments — only
# the BatchKVCache for decode is stressed, isolating the fragmentation cost.
set -euo pipefail
cd "$(dirname "$0")"
exec env \
    FRAGMENTATION_RESULTS_SUBDIR=concurrency \
    FRAGMENTATION_TARGETS="long:30000,short00:5000,short01:5000,short02:5000,short03:5000,short04:5000,short05:5000,short06:5000,short07:5000,short08:5000,short09:5000" \
    MLX_PROMPT_CONCURRENCY=1 \
    ./run.sh

# AppleBench Results — Qwen3-0.6B (agent)

**Model:** Qwen3-0.6B
**Split:** agent
**Generated:** 2026-04-22 07:48:49

## Concurrency: 1

| Metric | mistralrs | inferrs | omlx | llamacpp | vllm_mlx | hf_transformers | ollama |
|--------|--------|--------|--------|--------|--------|--------|--------|
| Successful / Failed | 100 / 0 | 100 / 0 | 100 / 0 | 99 / 1 | CRASHED | 100 / 0 | 100 / 0 |
| TTFT avg (ms) | 1628.5 | 12070.8 | 282.2 | 934.3 | 0.0 | 3427.9 | 72.6 |
| TTFT p50 (ms) | 1204.1 | 8664.5 | 263.4 | 663.6 | 0.0 | 2314.1 | 72.6 |
| TTFT p99 (ms) | 5786.2 | 32963.3 | 528.4 | 3458.5 | 0.0 | 11562.4 | 92.5 |
| Throughput avg (tok/s) | 44.8 | 2.1 | 147.5 | 136.6 | 0.0 | 12.9 | 157.3 |
| Output throughput (tok/s) | 34.5 | 1.3 | 125.6 | 90.5 | 0.0 | 9.4 | 151.0 |
| Input throughput (tok/s) | N/A | N/A | 2201.0 | 1572.6 | 0.0 | 156.4 | N/A |
| Total token throughput (tok/s) | N/A | N/A | 2326.6 | 1663.1 | 0.0 | 165.8 | N/A |
| ITL avg (ms) | 22.4 | 589.0 | 6.9 | 7.4 | 0.0 | 93.0 | 6.4 |
| ITL p50 (ms) | 22.1 | 509.8 | 6.7 | 7.3 | 0.0 | 80.3 | 6.4 |
| Latency avg (s) | 7.03 | 46.23 | 1.94 | 2.73 | 0.00 | 25.53 | 1.67 |
| Latency p99 (s) | 11.92 | 216.34 | 2.76 | 5.73 | 0.00 | 62.19 | 1.73 |
| Wall time (s) | 703.5 | 4623.1 | 193.7 | 269.9 | 1.7 | 2552.8 | 166.7 |

## Concurrency: 8

| Metric | mistralrs | inferrs | omlx | llamacpp | vllm_mlx | hf_transformers | ollama |
|--------|--------|--------|--------|--------|--------|--------|--------|
| Successful / Failed | 12 / 88 | SKIPPED (PREVIOUS LEVEL TOO SLOW) | 100 / 0 | 99 / 1 | CRASHED | 74 / 26 | 100 / 0 |
| TTFT avg (ms) | 35866.4 | 0.0 | 1010.0 | 7539.2 | 0.0 | 109804.1 | 137.5 |
| TTFT p50 (ms) | 12561.4 | 0.0 | 815.4 | 7142.7 | 0.0 | 113723.9 | 141.0 |
| TTFT p99 (ms) | 116039.5 | 0.0 | 3009.7 | 12209.1 | 0.0 | 212459.7 | 166.1 |
| Throughput avg (tok/s) | 1.4 | 0.0 | 22.9 | 48.6 | 0.0 | 2.3 | 32.5 |
| Output throughput (tok/s) | 4.2 | 0.0 | 164.2 | 149.2 | 0.0 | 5.9 | 248.2 |
| Input throughput (tok/s) | N/A | 0.0 | 2854.3 | 2578.3 | 0.0 | 95.9 | N/A |
| Total token throughput (tok/s) | N/A | 0.0 | 3018.4 | 2727.4 | 0.0 | 101.8 | N/A |
| ITL avg (ms) | 13146.9 | 0.0 | 44.6 | 22.6 | 0.0 | 450.6 | 31.2 |
| ITL p50 (ms) | 655.3 | 0.0 | 44.7 | 20.6 | 0.0 | 445.7 | 31.6 |
| Latency avg (s) | 175.93 | 0.00 | 11.80 | 13.09 | 0.00 | 217.43 | 7.95 |
| Latency p99 (s) | 295.04 | 0.00 | 14.60 | 18.67 | 0.00 | 294.75 | 8.25 |
| Wall time (s) | 473.9 | 0.0 | 149.4 | 164.6 | 1.5 | 3016.2 | 101.4 |

## Concurrency: 16

| Metric | mistralrs | inferrs | omlx | llamacpp | vllm_mlx | hf_transformers | ollama |
|--------|--------|--------|--------|--------|--------|--------|--------|
| Successful / Failed | CRASHED | SKIPPED (PREVIOUS LEVEL TOO SLOW) | 100 / 0 | 99 / 1 | CRASHED | 29 / 71 | 100 / 0 |
| TTFT avg (ms) | 0.0 | 0.0 | 11428.6 | 19530.3 | 0.0 | 140608.0 | 211.1 |
| TTFT p50 (ms) | 0.0 | 0.0 | 11926.6 | 20670.6 | 0.0 | 152352.8 | 226.3 |
| TTFT p99 (ms) | 0.0 | 0.0 | 15473.7 | 28173.5 | 0.0 | 208600.3 | 286.9 |
| Throughput avg (tok/s) | 0.0 | 0.0 | 23.0 | 47.3 | 0.0 | 2.2 | 36.5 |
| Output throughput (tok/s) | 0.0 | 0.0 | 169.0 | 149.5 | 0.0 | 3.3 | 530.5 |
| Input throughput (tok/s) | 0.0 | 0.0 | 2960.3 | 2596.9 | 0.0 | 49.8 | N/A |
| Total token throughput (tok/s) | 0.0 | 0.0 | 3129.3 | 2746.4 | 0.0 | 53.1 | N/A |
| ITL avg (ms) | 0.0 | 0.0 | 44.1 | 23.0 | 0.0 | 486.3 | 27.6 |
| ITL p50 (ms) | 0.0 | 0.0 | 45.2 | 22.4 | 0.0 | 483.1 | 28.0 |
| Latency avg (s) | 0.00 | 0.00 | 22.05 | 25.07 | 0.00 | 236.21 | 7.14 |
| Latency p99 (s) | 0.00 | 0.00 | 27.51 | 33.90 | 0.00 | 296.72 | 7.47 |
| Wall time (s) | 0.0 | 0.0 | 144.0 | 163.4 | 1.4 | 1865.5 | 47.4 |

## Total Benchmark Duration

| Framework | mistralrs | inferrs | omlx | llamacpp | vllm_mlx | hf_transformers | ollama |
|-----------|--------|--------|--------|--------|--------|--------|--------|
| Duration | 20.4m | 79.5m | 8.5m | 10.4m | 4.8s | 127.8m | 5.6m |

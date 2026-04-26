# AppleBench Results — Gemma-4-E4B-it (agent)

**Model:** Gemma-4-E4B-it
**Split:** agent
**Generated:** 2026-04-26 17:17:27

## Concurrency: 1

| Metric | mlx_lm | llamacpp | omlx | vllm_metal |
|--------|--------|--------|--------|--------|
| Successful / Failed | 64 / 36 | 100 / 0 | 94 / 6 | 95 / 5 |
| TTFT avg (ms) | 3594.2 | 4602.9 | 1826.2 | 16084.6 |
| TTFT p50 (ms) | 2925.2 | 3368.9 | 1373.1 | 7733.4 |
| TTFT p99 (ms) | 15046.0 | 17815.4 | 7304.1 | 86536.7 |
| Throughput avg (tok/s) | 18.1 | 30.2 | 24.8 | 9.4 |
| Output throughput (tok/s) | 5.3 | 12.6 | 16.7 | 3.6 |
| Input throughput (tok/s) | N/A | 606.6 | 881.7 | 192.3 |
| Total token throughput (tok/s) | N/A | 619.2 | 898.4 | 195.9 |
| ITL avg (ms) | 68.6 | 32.1 | 38.4 | 122.8 |
| ITL p50 (ms) | 48.0 | 32.1 | 38.0 | 110.9 |
| Latency avg (s) | 6.78 | 7.65 | 5.25 | 24.94 |
| Latency p99 (s) | 16.21 | 20.93 | 13.37 | 102.50 |
| Wall time (s) | 732.4 | 765.2 | 501.7 | 2397.8 |

## Concurrency: 8

| Metric | mlx_lm | llamacpp | omlx | vllm_metal |
|--------|--------|--------|--------|--------|
| Successful / Failed | 64 / 36 | 100 / 0 | 94 / 6 | 80 / 20 |
| TTFT avg (ms) | 53228.1 | 22236.0 | 922.5 | 24910.2 |
| TTFT p50 (ms) | 54264.9 | 21181.8 | 772.7 | 13752.7 |
| TTFT p99 (ms) | 78762.7 | 50243.7 | 2979.2 | 133141.8 |
| Throughput avg (tok/s) | 18.1 | 11.1 | 7.6 | 1.5 |
| Output throughput (tok/s) | 5.3 | 20.7 | 56.7 | 3.3 |
| Input throughput (tok/s) | N/A | 994.1 | 2476.9 | 264.3 |
| Total token throughput (tok/s) | N/A | 1014.8 | 2533.5 | 267.6 |
| ITL avg (ms) | 68.5 | 163.2 | 133.9 | 1597.6 |
| ITL p50 (ms) | 48.0 | 119.0 | 125.3 | 833.4 |
| Latency avg (s) | 56.41 | 36.66 | 14.27 | 95.53 |
| Latency p99 (s) | 81.36 | 105.15 | 35.41 | 284.60 |
| Wall time (s) | 732.5 | 467.0 | 178.6 | 1533.7 |

## Concurrency: 16

| Metric | mlx_lm | llamacpp | omlx | vllm_metal |
|--------|--------|--------|--------|--------|
| Successful / Failed | 64 / 36 | 100 / 0 | 94 / 6 | 51 / 49 |
| TTFT avg (ms) | 108013.2 | 57931.2 | 12317.8 | 74568.7 |
| TTFT p50 (ms) | 113497.7 | 57825.4 | 12769.8 | 60925.8 |
| TTFT p99 (ms) | 136101.5 | 96527.8 | 24141.6 | 204317.8 |
| Throughput avg (tok/s) | 18.1 | 10.8 | 7.8 | 0.7 |
| Output throughput (tok/s) | 5.3 | 20.4 | 56.8 | 1.2 |
| Input throughput (tok/s) | N/A | 988.2 | 2608.8 | 206.3 |
| Total token throughput (tok/s) | N/A | 1008.6 | 2665.6 | 207.5 |
| ITL avg (ms) | 68.5 | 179.0 | 128.6 | 4927.5 |
| ITL p50 (ms) | 48.0 | 123.0 | 125.0 | 3307.1 |
| Latency avg (s) | 111.20 | 72.28 | 25.19 | 172.10 |
| Latency p99 (s) | 140.58 | 139.61 | 56.90 | 299.93 |
| Wall time (s) | 732.3 | 469.7 | 169.6 | 1409.5 |

## Total Benchmark Duration

| Framework | mlx_lm | llamacpp | omlx | vllm_metal |
|-----------|--------|--------|--------|--------|
| Duration | 37.9m | 29.5m | 14.7m | 93.1m |

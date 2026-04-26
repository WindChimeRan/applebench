# AppleBench Results — Qwen3.5-0.8B (chat)

**Model:** Qwen3.5-0.8B
**Split:** chat
**Generated:** 2026-04-25 17:15:35

## Concurrency: 1

| Metric | mlx_lm | vllm_metal | llamacpp | omlx |
|--------|--------|--------|--------|--------|
| Successful / Failed | 98 / 2 | 99 / 1 | 99 / 1 | 99 / 1 |
| TTFT avg (ms) | 305.5 | 535.1 | 196.1 | 195.4 |
| TTFT p50 (ms) | 221.4 | 224.0 | 124.7 | 125.9 |
| TTFT p99 (ms) | 777.1 | 2091.6 | 827.1 | 705.4 |
| Throughput avg (tok/s) | 108.2 | 62.4 | 110.5 | 103.0 |
| Output throughput (tok/s) | 68.6 | 45.5 | 92.9 | 89.4 |
| Input throughput (tok/s) | N/A | 527.8 | 1074.1 | 991.8 |
| Total token throughput (tok/s) | N/A | 573.3 | 1167.0 | 1081.2 |
| ITL avg (ms) | 9.0 | 15.5 | 8.6 | 9.0 |
| ITL p50 (ms) | 8.7 | 14.2 | 8.5 | 9.0 |
| Latency avg (s) | 0.85 | 1.90 | 0.93 | 1.01 |
| Latency p99 (s) | 2.44 | 7.55 | 3.02 | 3.06 |
| Wall time (s) | 83.7 | 188.0 | 92.4 | 100.0 |

## Concurrency: 8

| Metric | mlx_lm | vllm_metal | llamacpp | omlx |
|--------|--------|--------|--------|--------|
| Successful / Failed | 98 / 2 | 99 / 1 | 99 / 1 | 99 / 1 |
| TTFT avg (ms) | 5825.2 | 936.6 | 1426.7 | 330.3 |
| TTFT p50 (ms) | 5839.8 | 310.0 | 1271.3 | 218.3 |
| TTFT p99 (ms) | 9829.6 | 4936.4 | 3419.7 | 1485.3 |
| Throughput avg (tok/s) | 106.8 | 13.2 | 55.0 | 29.5 |
| Output throughput (tok/s) | 68.6 | 85.7 | 224.9 | 212.0 |
| Input throughput (tok/s) | N/A | 1013.2 | 2600.6 | 2330.8 |
| Total token throughput (tok/s) | N/A | 1098.9 | 2825.5 | 2542.8 |
| ITL avg (ms) | 9.2 | 82.8 | 17.2 | 32.8 |
| ITL p50 (ms) | 8.9 | 77.3 | 17.2 | 32.5 |
| Latency avg (s) | 6.37 | 7.64 | 2.90 | 3.31 |
| Latency p99 (s) | 10.68 | 24.34 | 6.65 | 9.62 |
| Wall time (s) | 83.8 | 97.9 | 38.2 | 42.6 |

## Concurrency: 16

| Metric | mlx_lm | vllm_metal | llamacpp | omlx |
|--------|--------|--------|--------|--------|
| Successful / Failed | 98 / 2 | 99 / 1 | 99 / 1 | 99 / 1 |
| TTFT avg (ms) | 11443.1 | 1599.1 | 3928.1 | 3093.6 |
| TTFT p50 (ms) | 11856.0 | 802.1 | 4198.2 | 3269.5 |
| TTFT p99 (ms) | 17614.1 | 6992.5 | 5979.4 | 4817.0 |
| Throughput avg (tok/s) | 106.5 | 7.9 | 55.5 | 28.6 |
| Output throughput (tok/s) | 68.5 | 101.4 | 229.0 | 209.5 |
| Input throughput (tok/s) | N/A | 1152.5 | 2646.8 | 2325.6 |
| Total token throughput (tok/s) | N/A | 1253.9 | 2875.8 | 2535.1 |
| ITL avg (ms) | 9.2 | 160.9 | 17.2 | 34.8 |
| ITL p50 (ms) | 8.9 | 137.1 | 17.0 | 33.5 |
| Latency avg (s) | 11.99 | 13.15 | 5.38 | 6.10 |
| Latency p99 (s) | 18.01 | 43.38 | 10.02 | 13.59 |
| Wall time (s) | 83.9 | 86.1 | 37.5 | 42.7 |

## Total Benchmark Duration

| Framework | mlx_lm | vllm_metal | llamacpp | omlx |
|-----------|--------|--------|--------|--------|
| Duration | 4.3m | 6.4m | 2.9m | 3.3m |

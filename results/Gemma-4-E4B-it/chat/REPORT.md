# AppleBench Results — Gemma-4-E4B-it (chat)

**Model:** Gemma-4-E4B-it
**Split:** chat
**Generated:** 2026-04-26 15:42:26

## Concurrency: 1

| Metric | mlx_lm | omlx | vllm_metal | llamacpp |
|--------|--------|--------|--------|--------|
| Successful / Failed | 98 / 2 | 98 / 2 | 98 / 2 | 98 / 2 |
| TTFT avg (ms) | 1041.7 | 617.5 | 1815.6 | 1075.3 |
| TTFT p50 (ms) | 806.0 | 409.3 | 737.3 | 593.0 |
| TTFT p99 (ms) | 2762.0 | 2514.0 | 11389.7 | 5132.5 |
| Throughput avg (tok/s) | 20.9 | 25.2 | 19.4 | 29.8 |
| Output throughput (tok/s) | 14.5 | 22.3 | 12.9 | 22.1 |
| Input throughput (tok/s) | N/A | 281.0 | 164.9 | 281.2 |
| Total token throughput (tok/s) | N/A | 303.3 | 177.9 | 303.4 |
| ITL avg (ms) | 48.6 | 37.1 | 52.9 | 31.8 |
| ITL p50 (ms) | 48.0 | 37.1 | 44.1 | 31.7 |
| Latency avg (s) | 3.49 | 3.54 | 6.03 | 3.53 |
| Latency p99 (s) | 10.33 | 10.24 | 22.17 | 9.55 |
| Wall time (s) | 343.4 | 348.0 | 593.0 | 347.8 |

## Concurrency: 8

| Metric | mlx_lm | omlx | vllm_metal | llamacpp |
|--------|--------|--------|--------|--------|
| Successful / Failed | 98 / 2 | 98 / 2 | 98 / 2 | 98 / 2 |
| TTFT avg (ms) | 23544.0 | 845.5 | 299.6 | 3087.9 |
| TTFT p50 (ms) | 23546.1 | 683.5 | 300.8 | 2936.9 |
| TTFT p99 (ms) | 39129.7 | 2837.2 | 395.8 | 6204.6 |
| Throughput avg (tok/s) | 20.9 | 7.7 | 6.7 | 23.2 |
| Output throughput (tok/s) | 14.5 | 59.3 | 51.4 | 90.3 |
| Input throughput (tok/s) | N/A | 675.0 | 654.9 | 1148.5 |
| Total token throughput (tok/s) | N/A | 734.3 | 706.3 | 1238.8 |
| ITL avg (ms) | 48.6 | 128.9 | 140.9 | 41.3 |
| ITL p50 (ms) | 48.0 | 117.5 | 143.7 | 40.1 |
| Latency avg (s) | 25.99 | 10.66 | 11.21 | 6.27 |
| Latency p99 (s) | 44.15 | 32.95 | 37.77 | 16.93 |
| Wall time (s) | 343.4 | 138.6 | 149.3 | 85.2 |

## Concurrency: 16

| Metric | mlx_lm | omlx | vllm_metal | llamacpp |
|--------|--------|--------|--------|--------|
| Successful / Failed | 98 / 2 | 98 / 2 | 98 / 2 | 98 / 2 |
| TTFT avg (ms) | 46946.3 | 10383.9 | 387.5 | 8411.5 |
| TTFT p50 (ms) | 49597.2 | 9835.3 | 365.4 | 8606.3 |
| TTFT p99 (ms) | 68445.8 | 26526.8 | 569.3 | 14111.8 |
| Throughput avg (tok/s) | 20.9 | 7.8 | 5.2 | 23.4 |
| Output throughput (tok/s) | 14.5 | 61.0 | 74.1 | 92.4 |
| Input throughput (tok/s) | N/A | 630.4 | 937.5 | 1174.8 |
| Total token throughput (tok/s) | N/A | 691.4 | 1011.6 | 1267.1 |
| ITL avg (ms) | 48.6 | 118.5 | 181.4 | 40.7 |
| ITL p50 (ms) | 47.9 | 118.3 | 182.9 | 39.8 |
| Latency avg (s) | 49.39 | 21.18 | 14.29 | 11.56 |
| Latency p99 (s) | 70.17 | 59.08 | 47.37 | 24.69 |
| Wall time (s) | 343.3 | 148.4 | 104.3 | 83.3 |

## Total Benchmark Duration

| Framework | mlx_lm | omlx | vllm_metal | llamacpp |
|-----------|--------|--------|--------|--------|
| Duration | 17.6m | 11.1m | 14.7m | 8.9m |

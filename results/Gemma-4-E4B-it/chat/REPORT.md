# AppleBench Results — Gemma-4-E4B-it (chat)

**Model:** Gemma-4-E4B-it
**Split:** chat
**Generated:** 2026-04-25 14:12:53

## Concurrency: 1

| Metric | mlx_lm | omlx | llamacpp |
|--------|--------|--------|--------|
| Successful / Failed | 98 / 2 | 98 / 2 | 98 / 2 |
| TTFT avg (ms) | 1041.7 | 617.5 | 1075.3 |
| TTFT p50 (ms) | 806.0 | 409.3 | 593.0 |
| TTFT p99 (ms) | 2762.0 | 2514.0 | 5132.5 |
| Throughput avg (tok/s) | 20.9 | 25.2 | 29.8 |
| Output throughput (tok/s) | 14.5 | 22.3 | 22.1 |
| Input throughput (tok/s) | N/A | 281.0 | 281.2 |
| Total token throughput (tok/s) | N/A | 303.3 | 303.4 |
| ITL avg (ms) | 48.6 | 37.1 | 31.8 |
| ITL p50 (ms) | 48.0 | 37.1 | 31.7 |
| Latency avg (s) | 3.49 | 3.54 | 3.53 |
| Latency p99 (s) | 10.33 | 10.24 | 9.55 |
| Wall time (s) | 343.4 | 348.0 | 347.8 |

## Concurrency: 8

| Metric | mlx_lm | omlx | llamacpp |
|--------|--------|--------|--------|
| Successful / Failed | 98 / 2 | 98 / 2 | 98 / 2 |
| TTFT avg (ms) | 23544.0 | 845.5 | 3087.9 |
| TTFT p50 (ms) | 23546.1 | 683.5 | 2936.9 |
| TTFT p99 (ms) | 39129.7 | 2837.2 | 6204.6 |
| Throughput avg (tok/s) | 20.9 | 7.7 | 23.2 |
| Output throughput (tok/s) | 14.5 | 59.3 | 90.3 |
| Input throughput (tok/s) | N/A | 675.0 | 1148.5 |
| Total token throughput (tok/s) | N/A | 734.3 | 1238.8 |
| ITL avg (ms) | 48.6 | 128.9 | 41.3 |
| ITL p50 (ms) | 48.0 | 117.5 | 40.1 |
| Latency avg (s) | 25.99 | 10.66 | 6.27 |
| Latency p99 (s) | 44.15 | 32.95 | 16.93 |
| Wall time (s) | 343.4 | 138.6 | 85.2 |

## Concurrency: 16

| Metric | mlx_lm | omlx | llamacpp |
|--------|--------|--------|--------|
| Successful / Failed | 98 / 2 | 98 / 2 | 98 / 2 |
| TTFT avg (ms) | 46946.3 | 10383.9 | 8411.5 |
| TTFT p50 (ms) | 49597.2 | 9835.3 | 8606.3 |
| TTFT p99 (ms) | 68445.8 | 26526.8 | 14111.8 |
| Throughput avg (tok/s) | 20.9 | 7.8 | 23.4 |
| Output throughput (tok/s) | 14.5 | 61.0 | 92.4 |
| Input throughput (tok/s) | N/A | 630.4 | 1174.8 |
| Total token throughput (tok/s) | N/A | 691.4 | 1267.1 |
| ITL avg (ms) | 48.6 | 118.5 | 40.7 |
| ITL p50 (ms) | 47.9 | 118.3 | 39.8 |
| Latency avg (s) | 49.39 | 21.18 | 11.56 |
| Latency p99 (s) | 70.17 | 59.08 | 24.69 |
| Wall time (s) | 343.3 | 148.4 | 83.3 |

## Total Benchmark Duration

| Framework | mlx_lm | omlx | llamacpp |
|-----------|--------|--------|--------|
| Duration | 17.6m | 11.1m | 8.9m |

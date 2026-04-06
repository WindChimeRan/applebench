# AppleBench Results

Generated: 2026-04-05 23:29:27

## Concurrency: 1

| Metric | llamacpp | mistralrs | mlx_lm | vllm_metal |
|--------|--------|--------|--------|--------|
| Successful / Failed | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| TTFT avg (ms) | 363.9 | 862.4 | 572.8 | 2318.5 |
| TTFT p50 (ms) | 210.9 | 385.5 | 325.6 | 555.9 |
| TTFT p99 (ms) | 1814.9 | 3334.3 | 2128.7 | 11924.0 |
| Throughput avg (tok/s) | 89.1 | 35.5 | 96.0 | 31.4 |
| Aggregate throughput (tok/s) | 3026.0 | 1383.4 | 2792.0 | 617.1 |
| ITL avg (ms) | 11.3 | 28.2 | 10.5 | 33.6 |
| ITL p50 (ms) | 10.9 | 27.8 | 10.0 | 30.8 |
| Latency avg (s) | 2.09 | 5.14 | 2.18 | 7.53 |
| Latency p99 (s) | 5.07 | 11.02 | 5.48 | 24.98 |
| Wall time (s) | 208.7 | 514.4 | 217.8 | 752.5 |

## Concurrency: 8

| Metric | llamacpp | mistralrs | mlx_lm | vllm_metal |
|--------|--------|--------|--------|--------|
| Successful / Failed | 100 / 0 | 38 / 62 | 100 / 0 | 100 / 0 |
| TTFT avg (ms) | 3447.0 | 9175.7 | 3284.1 | 4081.6 |
| TTFT p50 (ms) | 3345.1 | 7763.3 | 1456.3 | 735.0 |
| TTFT p99 (ms) | 6122.0 | 27416.9 | 17975.9 | 22511.9 |
| Throughput avg (tok/s) | 59.3 | 1.6 | 15.3 | 7.1 |
| Aggregate throughput (tok/s) | 1301.6 | 16.4 | 380.9 | 222.9 |
| ITL avg (ms) | 18.4 | 1724.8 | 72.8 | 175.9 |
| ITL p50 (ms) | 16.6 | 608.9 | 72.3 | 165.6 |
| Latency avg (s) | 6.21 | 101.16 | 14.61 | 29.95 |
| Latency p99 (s) | 11.71 | 292.96 | 40.18 | 69.03 |
| Wall time (s) | 79.9 | 1925.6 | 185.8 | 381.3 |

## Concurrency: 16

| Metric | llamacpp | mistralrs | mlx_lm | vllm_metal |
|--------|--------|--------|--------|--------|
| Successful / Failed | 100 / 0 | CRASHED | 40 / 60 | 100 / 0 |
| TTFT avg (ms) | 9152.2 | 0.0 | 10801.8 | 6445.5 |
| TTFT p50 (ms) | 9742.9 | 0.0 | 9784.9 | 5451.7 |
| TTFT p99 (ms) | 14341.5 | 0.0 | 20302.0 | 31682.2 |
| Throughput avg (tok/s) | 58.2 | 0.0 | 11.8 | 3.9 |
| Aggregate throughput (tok/s) | 802.1 | 0.0 | 103.8 | 132.3 |
| ITL avg (ms) | 18.7 | 0.0 | 102.9 | 308.4 |
| ITL p50 (ms) | 17.2 | 0.0 | 81.4 | 314.8 |
| Latency avg (s) | 11.99 | 0.00 | 21.34 | 52.99 |
| Latency p99 (s) | 19.08 | 0.00 | 41.06 | 116.31 |
| Wall time (s) | 80.1 | 0.0 | 53.4 | 346.0 |

## Total Benchmark Duration

| Framework | llamacpp | mistralrs | mlx_lm | vllm_metal |
|-----------|--------|--------|--------|--------|
| Duration | 6.4m | 41.0m | 7.9m | 25.6m |

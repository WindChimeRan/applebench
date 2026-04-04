# AppleBench Results

Generated: 2026-04-03 23:52:17

## Concurrency: 16

| Metric | llamacpp | mistralrs | mlx_lm | vllm_metal |
|--------|--------|--------|--------|--------|
| TTFT avg (ms) | 481.5 | 619.9 | 1096.4 | 513.4 |
| TTFT p50 (ms) | 481.3 | 543.8 | 1096.3 | 551.9 |
| TTFT p99 (ms) | 483.0 | 839.9 | 1098.1 | 552.1 |
| Throughput avg (tok/s) | 34.5 | 21.1 | 45.3 | 16.4 |
| Aggregate throughput (tok/s) | 138.9 | 122.1 | 228.6 | 72.0 |
| ITL avg (ms) | 29.0 | 51.8 | 24.5 | 61.1 |
| ITL p50 (ms) | 28.5 | 58.3 | 26.4 | 62.7 |
| Latency avg (s) | 3.53 | 4.90 | 3.05 | 6.84 |
| Latency p99 (s) | 7.69 | 8.83 | 4.69 | 15.10 |

## Concurrency: 8

| Metric | llamacpp | mistralrs | mlx_lm | vllm_metal |
|--------|--------|--------|--------|--------|
| TTFT avg (ms) | 117.6 | 692.9 | 727.8 | 414.2 |
| TTFT p50 (ms) | 119.2 | 558.8 | 813.8 | 544.2 |
| TTFT p99 (ms) | 143.3 | 1059.6 | 815.5 | 544.5 |
| Throughput avg (tok/s) | 37.1 | 22.1 | 52.0 | 16.7 |
| Aggregate throughput (tok/s) | 148.5 | 137.4 | 243.9 | 72.8 |
| ITL avg (ms) | 27.1 | 59.4 | 21.2 | 60.2 |
| ITL p50 (ms) | 28.0 | 50.8 | 24.5 | 60.6 |
| Latency avg (s) | 3.01 | 4.73 | 2.49 | 6.58 |
| Latency p99 (s) | 7.19 | 7.85 | 4.42 | 14.94 |

## Concurrency: 1

| Metric | llamacpp | mistralrs | mlx_lm | vllm_metal |
|--------|--------|--------|--------|--------|
| TTFT avg (ms) | 46.8 | 73.9 | 111.9 | 119.9 |
| TTFT p50 (ms) | 42.5 | 51.2 | 111.3 | 107.0 |
| TTFT p99 (ms) | 88.4 | 131.9 | 124.3 | 172.7 |
| Throughput avg (tok/s) | 106.5 | 118.4 | 208.6 | 32.1 |
| Aggregate throughput (tok/s) | 402.3 | 488.9 | 821.8 | 129.8 |
| ITL avg (ms) | 9.4 | 8.4 | 4.8 | 31.1 |
| ITL p50 (ms) | 9.4 | 8.5 | 4.7 | 30.9 |
| Latency avg (s) | 1.05 | 0.98 | 0.62 | 3.51 |
| Latency p99 (s) | 2.65 | 2.21 | 1.30 | 8.38 |

# Correctness eval — Qwen3.5-0.8B

| Framework | 0-shot F1 | 0-shot F1-macro | 0-shot EM | 0-shot errors | 5-shot F1 | 5-shot F1-macro | 5-shot EM | 5-shot errors |
|---|---|---|---|---|---|---|---|---|
| llamacpp | 0.7016 | 0.4081 | 0.6990 | 0/0 | 0.5965 | 0.3779 | 0.5977 | 0/0 |
| mlx_lm | 0.6940 | 0.4031 | 0.6928 | 0/0 | 0.5907 | 0.3799 | 0.5986 | 0/0 |
| vllm_metal | 0.6865 | 0.4001 | 0.6815 | 1/0 | 0.6054 | 0.4136 | 0.5986 | 1/0 |
| omlx | 0.6959 | 0.4054 | 0.6946 | 0/0 | 0.5894 | 0.3758 | 0.5969 | 0/0 |

errors column = request_errors / parse_failures

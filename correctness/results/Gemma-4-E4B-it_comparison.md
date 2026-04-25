# Correctness eval — Gemma-4-E4B-it

| Framework | 0-shot F1 | 0-shot F1-macro | 0-shot EM | 0-shot errors | 5-shot F1 | 5-shot F1-macro | 5-shot EM | 5-shot errors |
|---|---|---|---|---|---|---|---|---|
| llamacpp | 0.8497 | 0.6797 | 0.8482 | 0/0 | 0.9107 | 0.6907 | 0.9058 | 0/0 |
| mlx_lm | 0.7497 | 0.6465 | 0.7618 | 0/0 | 0.8856 | 0.6979 | 0.8848 | 0/0 |
| omlx | 0.3934 | 0.2944 | 0.4380 | 0/0 | 0.7321 | 0.3952 | 0.7347 | 0/0 |

errors column = request_errors / parse_failures

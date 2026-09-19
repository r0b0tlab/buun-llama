# Publish notes — buun-llama serve profile

Identity: buun `1d0f493c73817176f6953069b7c10211de9555a1`, image `buun-llama:3090` (`sha256:1bd92ad3c2d7…`), recipe `recipes/dflash2-262k.env` (no `--fit`; `--jinja -fa on --cache-ram 8192 --vbr-entry t8 --vbr-floor t3`), host 8888, n_ctx 262144 (train cap), DFlash2 block 13 adaptive. Adapter 8889. Weights: published EXL3 4.00 bpw + DFlash2 sidecar.

Kit: Q200v2 `quality-text-180-v2.jsonl` sha256 `66a75701…`. Run id `q200v2-buun-serve`, identity `00a9bd44…`. Rows under `/home/am/r0b0bench-q200v2/runs/q200v2-buun-serve/`. Sandbox `--image-id sha256:caf1a95b886e…`. BFCL-hard20: NOT_IMPLEMENTED.

Summary `model` field is the kit default `qwen38-flash-next-w4a16`. Served alias was `qwen38-27b-buun`.

## Throughput

| probe | tok/s | notes |
| --- | ---: | --- |
| GSM8K greedy n=40 on the 262k process | 110.4 | AL 4.756 |
| NIAH 2n decode | 28.2 | 139 new, 667 s |
| NIAH 3n decode | 30.1 | 142 new, 669 s |
| Q200v2 e2e (180 rows) | mean 130.7 / p50 137.0 / agg 118.0 | 98105 completion tokens |

`dflash2-max` 8k GSM8K was 111.4 tok/s AL 4.755.

## NIAH

Depth 261888 = 262144 − 256 generate. Thinking on.

| variant | last code | result | elapsed |
| --- | --- | --- | ---: |
| 2n | R0B0-LYNX-4402 | PASS | 667.2 s |
| 3n | R0B0-RAVEN-9158 | PASS | 668.9 s |

262080-token attempt with n_ctx 262144 FAIL (`predicted_n` 64). Disclosed. Slot ctx cannot exceed n_ctx_train.

## Q200v2 text-180

status INCOMPLETE (hard_reasoning manual). 180 rows, all `finish_reason=stop`, no length ceiling. Kit exit 2.

| family | n | transported | graded | correct | accuracy |
| --- | ---: | ---: | ---: | ---: | ---: |
| gsm8k | 80 | 80 | 80 | 79 | 98.75 % |
| humaneval | 40 | 40 | 40 | 39 | 97.5 % |
| ifeval | 40 | 39 | 39 | 32 | 82.05 % |
| hard_reasoning | 20 | 20 | 0 | — | ungraded |

correct 150 / incorrect 9 / ungraded 21.

gsm8k-012 got 12 expected 13. humaneval-032 MODEL_REJECT. ifeval: seven scored misses. ifeval-023 empty content (`empty_response`). hard_reasoning 20/20 `manual_review_required`.

Telemetry LOAD-ONLY (464 samples, util>0): power mean 336.7 / max 348.3 W; temp max 60 C; VRAM max 22996 MiB. Throttle 0x0 / 0x1 idle / 0x4 SW cap. Not 0x40 thermal.

Native twin reference: 172/7/1, humaneval 40/40, gsm8k 97.5 %, ifeval 87.18 %, e2e mean 152.8 tok/s.

## Recipe

Shipped serve is `recipes/dflash2-262k.env` as above. MMQ/block/adaptive knobs not applied.

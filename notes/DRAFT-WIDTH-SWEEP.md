# DFlash2 width and adaptive-depth screen

## Scope and controls

Diagnostic serving tests on the existing buun image, engine 1d0f493, RTX 3090, published EXL3 target/draft. Recipe dflash2-262k (262144 configured context, turbo8 entry, turbo3_tcq floor, cache-ram 8192). Short GSM8K questions, not full-context prompts. All candidates used identical medium-equivalent rendered prompts (user ChatML + assistant + think prefix), greedy sampling, 512 output cap, seed 42, cache_prompt false, no repetition/presence/frequency penalty changes.

Only block width, adaptive depth and a separate MMQ experiment changed. Each arm restarted the server, verified requested block size in startup logs, then warmed on the same separate 64-token prompt. Production recipe files were not changed.

## Full n=40 confirmation

Mean AL is arithmetic mean across requests. E2E throughput below is aggregate generated tokens divided by sum of request wall time (includes prefill). Do not compare it directly to historical decode-only measurements or mean per-request speeds.

| Block size | Maximum draft tokens | Adaptive | Mean AL | Aggregate E2E tok/s | Actual proposals/estimated round |
| --- | ---: | --- | ---: | ---: | ---: |
| 13 | 12 | on | 6.2517 | 141.45 | 7.74 |
| 8 | 7 | off | 5.8750 | 144.58 | 6.96 |
| 13 | 12 | off | 7.4724 | 132.82 | 11.94 |
| 16 | 15 | off | 7.4757 | 86.26 | 14.91 |

The previous matched medium run's AL was 6.3127; a fresh adaptive control yields 6.2517. Fixed block13 raises AL by 18.37% against the former or 19.53% against the fresh control, but aggregate throughput falls 6.10% against the fresh control.

Actual proposed/accepted counts, per-request timings, prompts, IDs, outputs, container identity and startup logs were retained under work/acceptance-gap/.

## n=10 screening

| Width | Adaptive | Mean AL | Aggregate E2E tok/s |
| ---: | --- | ---: | ---: |
| 8 | off | 5.8161 | 145.39 |
| 10 | off | 6.5750 | 99.23 |
| 11 | off | 6.8854 | 98.28 |
| 12 | off | 6.9633 | 99.07 |
| 13 | on | 5.8652 | 139.85 |
| 13 | off | 7.1078 | 131.68 |
| 14 | off | 7.1773 | 86.75 |
| 15 | off | 7.0092 | 84.51 |
| 16 | on | 5.8960 | 135.25 |
| 16 | off | 7.2214 | 85.37 |
| 24 | on | 5.8558 | 127.99 |
| 24 | off | 6.6889 | 61.12 |
| 32 | on | 5.7233 | 118.53 |
| 32 | off | 6.4838 | 56.31 |

MMQ=1 n=10 controls: block13 fixed AL7.1078/131.57 tok/s; block16 fixed AL7.2214/85.35; block13 adaptive AL5.8590/137.67. No useful improvement observed; no kernel attribution is inferred from this switch.

## Interpretation

Adaptive depth intentionally optimizes cycle cost, not maximum AL. It emitted about 7.74 proposals per estimated round under the fresh block13 control despite a configured maximum of 12. Disabling adaptation uses the wider window and increases accepted tokens per round, but the extra work outweighs saved rounds on this workload.

Block16 provides essentially no additional mean AL over fixed block13 while sharply reducing throughput. Increasing width to 24 or 32 regresses both AL and throughput in screening. The throughput discontinuities across widths need profiling if pursued; these tests do not prove which CUDA/ggml operation is responsible.

No checkpoint retraining or requantization was needed to reach AL7.47. This is an AL improvement, not yet a better production serving profile. Do not promote a slower fixed-width configuration merely for a larger AL. Fixed block8's small short-prompt throughput advantage also needs repeated workload/latency testing before any promotion.

## Artifacts and integrity

- work/acceptance-gap/width-screen-n10/results.json: coarse screen.
- work/acceptance-gap/width-refine-n10/results.json: intermediate fixed widths.
- work/acceptance-gap/width-finalists-n40/results.json: complete block13 adaptive, block8 fixed, block13 fixed confirmations.
- work/acceptance-gap/block16-confirm-n40/results.json: complete block16 fixed confirmation.
- work/acceptance-gap/mmq-screen-n10/results.json: MMQ controls.
- work/acceptance-gap/confirmed-width-summary.json: four verified n=40 arms, each 40 unique prompt indices.

The first multi-arm confirmation tool timed out during block16 at 33 responses. That partial arm is excluded; block16 was restarted and completed in a separate n=40 run. No partial output was combined with the rerun.

## Deployment status

Restored dflash2-262k with default block13/adaptive behavior and no experimental GGML overrides; /health returned ok. Default chat reasoning behavior was not changed. No profile was promoted, so Q200v2 and NIAH were not rerun. These changes are local research artifacts, not pushed or packaged into the published image.

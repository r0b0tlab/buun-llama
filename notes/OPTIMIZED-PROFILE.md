# Optimized RTX 3090 serving profile

Status: production suite completed, with one unresolved Q200v2 response-cap failure. The profile is measured and runnable, but is not an all-green production qualification. It is the best measured general-serving configuration from this campaign, not proof of a global optimum.

## Run

From the repository root with existing published EXL3 target/draft directories:

```bash
MODELS=/path/to/models IMAGE=buun-llama:3090-optimized RECIPE=dflash2-optimized bash container/run-serve.sh
```

The model root contains qwen38-27b-exl3 and dflash2-exl3. Host port defaults to 8888. The recipe exports its own speculative settings; no remembered shell exports are required.

For NVIDIA Container Toolkit hosts, the packaged image needs no host recipe mount:

```bash
docker run --gpus all -p 8888:8080 -v /path/to/models:/models:ro buun-llama:3090-optimized dflash2-optimized
```

## Exact serving settings

- Engine spiritbuun/buun-llama-cpp at 1d0f493c73817176f6953069b7c10211de9555a1, CUDA sm_86.
- Published EXL3 4.00 bpw target and draft unchanged.
- Full target and draft GPU offload; flash attention and fused draft convolution enabled.
- DFlash2 block size 8, maximum seven draft tokens, adaptive depth enabled.
- Low reasoning default through the native --chat-template-kwargs option; clients may override it. Medium produced output-cap failures in the supplemental quality run and is not the reliable default at an 8192-token response budget.
- Context 262144; VBR turbo8 entry and turbo3_tcq floor.
- One active slot, microbatch 512; additional requests queue.
- cache-ram 8192 retained; projected VBR prompt artifacts disabled with --no-vbr-prompt-cache.
- --fit off explicitly; removing --fit on alone does not turn off the engine's default fit behavior.
- No forced MMQ, CopySpec, extra parallel slots, CPU offload, or speculative weight changes.

## Measured serving evidence

Tests used medium reasoning in all matched configuration comparisons. Six short prompts cover math, code and explanatory prose, capped at 256 generated tokens. Streaming TTFT includes first generated text, including reasoning. Long-prefix probe is 4,964 input tokens and 128 generated tokens; its warm run uses the same prefix. These are screening workloads, not a quality score.

| Metric | Baseline block13/adaptive | Candidate block8/adaptive/no artifacts |
| --- | ---: | ---: |
| Mixed short-request aggregate E2E tok/s | 98.89 | 111.66 |
| Mixed median TTFT | 0.159 s | 0.156 s |
| Mixed median engine decode speed | 121.16 tok/s | 131.64 tok/s |
| Warm same-prefix TTFT | 0.078 s | 0.049 s |
| Two queued requests aggregate | 111.28 tok/s | 122.03 tok/s |
| End-of-screen GPU memory (not peak) | 17802 MiB | 17034 MiB |
| 64k prompt engine decode | 53.48 tok/s | 53.24 tok/s |

A fresh test of the packaged candidate returned GSM8K n=40 mean per-request E2E 151.11 tok/s, mean AL 5.916, 40/40 draft counters present, two output-cap contacts. The published prior xhigh-reasoning profile was about 110 tok/s; that comparison includes changed reasoning behavior and must not be presented as a pure kernel gain.

## Levers actually tested

Screening ledger: metrics/optimized/screening.json. 29 arm executions, including repeated confirmation, with 26 completed and three failed attempts. The width/adapter investigation is documented separately in notes/DRAFT-WIDTH-SWEEP.md.

- Block8 fixed improves short requests, but at 64k decode fell to 42.03 tok/s. Adaptive8 recovered 53.24, so it is the general default.
- Block13 fixed increased mean AL to about 7.47 in a separate n=40 screen, but was slower. Block16 fixed was substantially slower; widths24/32 regressed.
- Microbatches1024/2048/4096 did not improve short decode. The 4096 screen ended at 23812 MiB, reducing long-context headroom. Microbatch256 saved memory but slightly worsened prefill; retain512.
- Disabling projected VBR artifacts improved the short-request path and warm TTFT. Keeping cache-ram versus zero performed similarly. No tested configuration restored the long prefix after switching to an unrelated conversation; do not advertise cross-conversation host-cache hits.
- VBR entry4 traded lower short-request throughput for a faster 64k synthetic continuation (58.59 tok/s). Entry8 remains the balanced, higher-precision starting point.
- Fixed turbo4, turbo3_tcq and asymmetric turbo3_tcq/turbo2_tcq offered no general-serving win over VBR in this screen.
- Backend sampling, CPU-thread changes and forced MMQ offered no useful general improvement.
- CopySpec offered no gain on the tested copying prompt and slightly hurt mixed serving; keep opt-in rather than enable by default.
- Two slots reduced queue TTFT but lowered aggregate throughput (89.52 vs baseline111.28 tok/s on two requests). Four slots encountered a compute error. One slot is deliberate for this long-context hybrid target on 24 GB.
- Original BF16 draft failed the pinned loader's base-tensor dtype assertion. A separately converted FP16 control loaded after correcting file readability, but was slower (102.60 mixed tok/s) and used more memory than the EXL3 candidate. Existing weights were not overwritten.

The FP16 permission failure, BF16 dtype assertion and four-slot compute error remain in the ledger. Failed attempts are not silently omitted.

## Final-image production suite

Throughput screening preceded quality qualification. Every final result here uses image `sha256:8d6d67a5b1ac856882731d5638b1291f5b81f89f75ac8e664df39cd7991b5652` with the embedded low-default recipe and no host recipe bind.

- GSM8K n=40: mean E2E149.19 tok/s, mean AL5.917,40/40 draft statistics present. One512-token cap in this bounded throughput probe.
- Mixed short requests:107.95 aggregate tok/s, median TTFT0.175s. Separate matched low-reasoning A/B: baseline94.06 versus optimized107.21 aggregate tok/s.
- Queued clients: all1/2/4 client batches completed. This is one active slot, not multi-slot batching.
- Long-context test:150000 prompt tokens and200 generated; prefill525.30 tok/s, decode27.84 tok/s, no truncation.
- NIAH2n/3n: PASS at261888 input tokens plus256 response reserve. Decode32.78/32.98 tok/s; wall664.5/666.5s. Full prompt counts recorded; no warm-prefix speed claim.
- Canonical Q200v2 text-180:171 correct /8 incorrect /1 ungraded. Families: GSM8K79/80; HumanEval39/40; IFEval34/39 graded plus1 capped; hard reasoning19/20 after response-bound manual review.
- Q200v2 remains INCOMPLETE: ifeval-023 reached8192 generated tokens with no final answer. The cap was not raised and the failed response was not regenerated. A prior candidate's172/8/0 does not substitute for this result.
- Q200v2 E2E: mean138.70,median144.78,aggregate124.71 tok/s;111149 completion tokens over891.30 summed request seconds, including the capped row.
- BFCL v4 multi_turn_base structural-hard20: SCORED13 correct /7 incorrect,20 unique cases,zero timing errors. It is not the full-category leaderboard score.
- BFCL setup first failed on import-created housekeeping locks, then a missing timing binding. The scored attempt used a fresh root, locks outside that root, and an explicit timing file. Frozen harness/data/grader files remained unchanged; compatibility bootstrap hash is retained.
- T=1 smoke:48 requests per arm completed on optimized DFlash2 and AR control. Actual generated counts10274/10244; aggregate90.94/46.23 tok/s. Top20 word fractions0.27663/0.27657. Outputs include reasoning; intentional256-token diagnostic caps occurred32/31 times. This is a limited sampling smoke, not proof of distribution equivalence. The optimized image/profile was restored afterward.
- Active-load Q200 telemetry: mean341.91W,max348.73W,max59C,max18276MiB during Q200. Primary-suite peak23518MiB. Throttle0x4 denotes software power cap, not thermal slowdown.

Low remains the recommended default, but it does not eliminate all response-cap failures. The noncanonical medium supplement also produced capped responses; medium is an explicit client option, not a quality-equivalent optimization claim. Historical medium-candidate evidence is archived in `metrics/medium-candidate/`.

Final evidence is in `metrics/optimized/`: provenance, Q200 summary/manual evidence, BFCL summary and lock-relocation note, NIAH results, long-context/queue results, sampling smoke, throughput and telemetry digests. No kernel rewrite, training, overclock or multi-GPU optimization is claimed.

## Reproduce short-request screen

```bash
python3 scripts/serving_probe.py --base-url http://127.0.0.1:8888 --json-out work/serving-probe.json
python3 -m unittest discover -s tests -v
```

Detailed local research outputs are under work/serving-* and work/acceptance-gap. Sanitized summaries for publication go under metrics/optimized. Historical failed/capped runs are retained separately.

# Qwen3.8-27B EXL3 on buun-llama-cpp

Native EXL3 serving with [spiritbuun/buun-llama-cpp](https://github.com/spiritbuun/buun-llama-cpp), pinned to `1d0f493c73817176f6953069b7c10211de9555a1`. Target: [Qwen3.8-27B EXL3 4.00 bpw](https://huggingface.co/r0b0tlab/Qwen3.8-27B-EXL3-4.00bpw). Draft: [DFlash2 EXL3 4.00 bpw](https://huggingface.co/r0b0tlab/Qwen3.8-27B-DFlash2-EXL3-4.00bpw).

## Optimized RTX 3090 profile

`recipes/dflash2-optimized.env` uses low reasoning, DFlash2 block8 with adaptive depth, 262144 context, VBR turbo8 entry/turbo3 floor, one active slot, microbatch512, full GPU offload and flash attention. It exports its own draft settings; clients can override reasoning per request. Projected VBR prompt artifacts and auto-fit are explicitly disabled. Live-prefix reuse remains available.

The production suite was run against image `sha256:8d6d67a5b1ac856882731d5638b1291f5b81f89f75ac8e664df39cd7991b5652`, without a host recipe mount. **This is not a clean all-green production qualification:** Q200v2 retains one capped response. Model mistakes and failed setup attempts are disclosed, not erased.

| Final-image test | Result |
| --- | --- |
| GSM8K throughput, n=40 | mean E2E 149.19 tok/s; mean AL5.917 |
| Mixed short requests | aggregate107.95 tok/s; median TTFT0.175s |
| 150000-token prefill + 200 decode | passed; prefill525.30 tok/s, decode27.84 tok/s |
| NIAH 2n/3n | passed at261888 input tokens, 256-token response reserve |
| Q200v2 text-180 | Adjudication complete: 171 correct / 9 failed / 0 pending; capped row counted as failed |
| BFCL v4 structural-hard20 | SCORED:13/20 correct;20 unique cases; zero timing errors |
| Q200v2 E2E throughput | mean138.70 /median144.78 /aggregate124.71 tok/s |
| Peak VRAM across primary suite | 23518 MiB |

Q200v2 outcome grading is complete: `ifeval-023` is counted as failed after reaching the fixed 8192-token cap without a final answer. The original kit summary still records its transport/closure status as `INCOMPLETE`; it is preserved unchanged. See [the completed adjudication](notes/Q200V2-ADJUDICATION.md). No cap increase or response regeneration was used. BFCL is the frozen structural-complexity subset, not the official full200-case category score. See [full findings](notes/OPTIMIZED-PROFILE.md), [gate status](notes/GATES.md), and [machine-readable evidence](metrics/optimized/).

## Run

With NVIDIA Container Toolkit and existing model directories:

```bash
docker run --gpus all -p 8888:8080 -v /path/to/models:/models:ro \
  ghcr.io/r0b0tlab/buun-llama:3090-optimized dflash2-optimized
```

The model root must contain `qwen38-27b-exl3` and `dflash2-exl3`. Registry package visibility may require authentication; building locally does not require GHCR access.

On the development host without NVIDIA Container Toolkit:

```bash
MODELS=/path/to/models IMAGE=buun-llama:3090-optimized RECIPE=dflash2-optimized \
  bash container/run-serve.sh
python3 scripts/wait_ready.py --base-url http://127.0.0.1:8888
python3 scripts/serving_probe.py --base-url http://127.0.0.1:8888 --json-out work/serving-probe.json
```

The wrapper replaces the container named `buun-llama`. Its default host port is8888; container port8080. No API key is configured by these examples; restrict network access before exposing the endpoint.

Build locally:

```bash
docker build --provenance=false --sbom=false -t buun-llama:3090-optimized -f container/Dockerfile .
python3 -m unittest discover -s tests -v
```

Host build from the pinned engine:

```bash
git clone --filter=blob:none https://github.com/spiritbuun/buun-llama-cpp
git -C buun-llama-cpp checkout 1d0f493c73817176f6953069b7c10211de9555a1
cmake -B buun-llama-cpp/build -DGGML_CUDA=ON -DGGML_CUDA_FA=ON -DGGML_CUDA_FA_ALL_QUANTS=ON -DCMAKE_CUDA_ARCHITECTURES=86 -DCMAKE_BUILD_TYPE=Release
cmake --build buun-llama-cpp/build -j --target llama-server
BIN=$PWD/buun-llama-cpp/build/bin/llama-server MODELS=/path/to/models bash scripts/serve.sh recipes/dflash2-optimized.env
```

Host-native recipes use port8080; Docker examples map it to8888. Keep the image's recipe selection argument `dflash2-optimized`; the image's legacy no-argument default remains `dflash2-max`.

## Other recipes

| File | Purpose |
| --- | --- |
| `dflash2-max.env` | historical8k/block13 default |
| `dflash2-262k.env` | historical262k/block13 VBR profile |
| `dflash2-turbo3-tcq.env` | fixed TCQ comparison |
| `dflash2-copyspec.env` | copy-heavy experiments; not the general default |
| `mtp.env` | embedded MTP baseline |
| `ar.env` | autoregressive baseline |

## Measurement boundaries

- Optimization screened29 arm executions plus width/depth controls; faster AL alone was not promoted. See [width sweep](notes/DRAFT-WIDTH-SWEEP.md).
- The prior buun/native ExLlamaV3 GSM8K numbers used different rendered prompts. The original AL comparison did not establish an engine defect; see [acceptance-gap diagnosis](notes/ACCEPTANCE-GAP.md).
- Medium reasoning remains optional. A separate noncanonical medium run hit output caps; its scores are not frozen Q200v2 results.
- Historical results and disclosures remain in `notes/PUBLISH.md` and `notes/RESULTS.md`.
- Results distinguish mean per-request E2E, aggregate E2E and engine decode timing. They are not interchangeable.

## Licenses

This package and the buun/llama.cpp engine are MIT. EXL3 and DFlash2 integrations retain their upstream notices. Model weights follow the parent Hugging Face licenses. Model weights are not included in the container.

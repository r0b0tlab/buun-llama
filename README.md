# Qwen3.8-27B EXL3 on buun-llama-cpp

Eval twin of [r0b0tlab/qwen38-exl3-dflash2](https://github.com/r0b0tlab/qwen38-exl3-dflash2). Same published EXL3 weights, same gates, engine is [spiritbuun/buun-llama-cpp](https://github.com/spiritbuun/buun-llama-cpp) at `1d0f493`.

llama-server loads the EXL3 directories directly. DFlash2 rides as `-md`. VBR is the default KV cache. Turbo/TCQ, MTP, CopySpec, and the CUDA MoE cache flags are recipe files under `recipes/`.

Weights: [r0b0tlab/Qwen3.8-27B-EXL3-4.00bpw](https://huggingface.co/r0b0tlab/Qwen3.8-27B-EXL3-4.00bpw) and [r0b0tlab/Qwen3.8-27B-DFlash2-EXL3-4.00bpw](https://huggingface.co/r0b0tlab/Qwen3.8-27B-DFlash2-EXL3-4.00bpw). Parents: [Qwen/Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B), [incoai/Qwen3.8-27B-DFlash2](https://huggingface.co/incoai/Qwen3.8-27B-DFlash2).

## Results

Buun DFlash2 on this tree, RTX 3090, GSM8K greedy n=40, ctx 8192, pin `1d0f493`, image `buun-llama:3090`. JSON: `notes/acceptance-dflash2.json`.

| arm | acceptance length | tok/s | status |
| --- | ---: | ---: | --- |
| buun DFlash2 8k (`dflash2-max`) | 4.76 | 111.4 | passed |
| buun DFlash2 serve (`dflash2-262k`, GSM8K n=40) | 4.76 | 110.4 | passed |
| buun DFlash2 NIAH ~262k decode | — | 28–30 | passed |
| buun MTP (this repo) | 3.25 | 92.0 | passed |
| buun AR (this repo) | 1.00 | 46.0 | passed |
| ExLlamaV3 AR (twin) | 1.00 | 42.8 | baseline |
| ExLlamaV3 MTP (twin) | 4.12 | 116.3 | baseline |
| ExLlamaV3 DFlash2 (twin) | 5.66 | 162.9 | baseline |

DFlash2 AL 4.76 clears 4.0 and beats this-engine MTP (3.25) by more than 0.3. Peak DFlash2 eval VRAM 17542 MiB. `--fit on` failed on DFlash2 and was dropped from default recipes.

Host 8080 is often taken. Default container map is host 8888 -> container 8080.

## Recipes

| file | what it turns on |
| --- | --- |
| `recipes/dflash2-max.env` | DFlash2 sidecar, flash-attn, jinja, VBR default, ctx 8192 |
| `recipes/dflash2-262k.env` | same + ctx 262144, `--vbr-entry t8 --vbr-floor t3` |
| `recipes/dflash2-turbo3-tcq.env` | pinned `turbo3_tcq` KV |
| `recipes/dflash2-copyspec.env` | DFlash2 + CopySpec |
| `recipes/mtp.env` | `--spec-type draft-mtp` |
| `recipes/ar.env` | target only |

Default DFlash2 block for the Qwen3.8 sidecar is 13 (buun rewrites metadata 8). Restore 8 with `GGML_DFLASH2_BLOCK_SIZE_OVERRIDE=8`. Adaptive depth is on.

## Host

```bash
git clone --filter=blob:none https://github.com/spiritbuun/buun-llama-cpp
cmake -B buun-llama-cpp/build -DGGML_CUDA=ON -DGGML_CUDA_FA=ON -DGGML_CUDA_FA_ALL_QUANTS=ON \
  -DCMAKE_CUDA_ARCHITECTURES=86 -DCMAKE_BUILD_TYPE=Release
cmake --build buun-llama-cpp/build -j$(nproc) --target llama-server
export BIN=$PWD/buun-llama-cpp/build/bin/llama-server
bash scripts/serve.sh recipes/dflash2-max.env
```

On another shell:

```bash
python3 scripts/wait_ready.py --base-url http://127.0.0.1:8888
python3 scripts/acceptance_check.py --base-url http://127.0.0.1:8888 --n 40 --json-out notes/acceptance-dflash2.json
```

## Container

```bash
docker build --provenance=false --sbom=false -t buun-llama:3090 -f container/Dockerfile .
bash container/run-serve.sh
```

Click-run once the image is on GHCR:

```bash
docker run --gpus all -p 8888:8080 -v buun-models:/models \
  ghcr.io/r0b0tlab/buun-llama:3090
```

`RECIPE=dflash2-262k bash container/run-serve.sh` switches the long-context recipe.

## Eval gates

Scripts are Python 3 stdlib. They talk to llama-server.

| Gate | Command | Status |
| --- | --- | --- |
| VRAM budget t3 @ 262k | `python3 scripts/vram_budget.py 4.0 t3` | passed (22.3/24 GB) |
| DFlash2 load + greedy generate | `scripts/acceptance_check.py --n 1` | passed |
| GSM8K n=40 AL and tok/s | `scripts/acceptance_check.py --n 40` | passed (AL 4.76, 111 tok/s) |
| MTP and AR arms | serve `mtp.env` / `ar.env`, same script | passed (MTP AL 3.25 / 92 tok/s; AR AL 1.00 / 46 tok/s) |
| 262k load + 150k prefill + 200 decode | serve `dflash2-262k.env`, `scripts/long_context_check.py` | unverified |
| T=1 sampled vs AR | `scripts/sampled_sanity_check.py` | unverified |
| NIAH 2n / 3n | `scripts/niah_multikey.py --variant 2n --target-tokens 261888 --max-tokens 256` | passed (261888 depth; 262080+thinking disclosed fail) |
| Q200v2 | `scripts/r0b0bench_adapter.py` then r0b0bench kit | INCOMPLETE (169/10/1; hard 19/20; ifeval-023 empty; `notes/PUBLISH.md`) |

Acceptance length uses `timings.predicted_n` and `timings.draft_n_accepted` from llama-server: `new_tokens / (new_tokens - accepted_draft_tokens)`.

Q200v2 and the kit NIAH path need `scripts/r0b0bench_adapter.py --upstream http://127.0.0.1:8080 --port 8889` so `/v1/models` carries `max_model_len` and `/v1/chat/completions/render` exists.

## Layout

- `recipes/` — serve knobs and `PIN`
- `scripts/` — stdlib eval + `serve.sh`
- `container/` — CUDA 13 sm_86 image
- `eval/gsm8k_n40.jsonl` — first 40 GSM8K test questions
- `notes/` — design, gates, results

## Licenses

This repository: MIT. Engine: MIT (llama.cpp / buun-llama-cpp). EXL3 format and DFlash2 math: MIT (ExLlamaV3, z-lab/dflash). Weights follow the parent Hugging Face licenses.

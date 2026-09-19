# AGENTS.md — buun-llama

Rules for humans and agents working in this repository.

1. Engine is spiritbuun/buun-llama-cpp. Default pin is the SHA in `recipes/PIN`. Do not vendor the fork. Do not overlay ExLlamaV3 `dflash2-pathway` patches onto this tree.

2. Weights are the published EXL3 directories:
   - r0b0tlab/Qwen3.8-27B-EXL3-4.00bpw
   - r0b0tlab/Qwen3.8-27B-DFlash2-EXL3-4.00bpw
   Load them with llama-server `-m` / `-md` (or `-hf` / `-hfd`). Do not convert to GGUF for the primary path.

3. Scripts under `scripts/` use Python 3 stdlib only. No pip. Talk to a running llama-server over HTTP.

4. Eval protocol matches r0b0tlab/qwen38-exl3-dflash2:
   - GSM8K greedy n=40, max 512, ctx 8192 (`scripts/acceptance_check.py`)
   - 262144 ctx load + 150000-token prefill + 200-token decode (`scripts/long_context_check.py`)
   - T=1 sampled n-gram profile vs AR (`scripts/sampled_sanity_check.py`)
   - Multi-needle NIAH 262080 (`scripts/niah_multikey.py`)
   - Q200v2 via r0b0bench against `scripts/r0b0bench_adapter.py`
   Record identity: buun SHA, image id, recipe name, ctx, KV flags.

5. Default serve recipe is `recipes/dflash2-max.env` (DFlash2 sidecar, flash-attn, jinja, VBR default). Use `recipes/dflash2-262k.env` for the long-context gate. Do not mix `--vbr-policy` with `-md`.

6. Benchmark numbers in README and `notes/` must come from a real run in this tree. Until then status is unverified. A faster arm caused only by temperature or a luckier draft is not a win.

7. Container build sets `CMAKE_CUDA_ARCHITECTURES=86` (RTX 3090). GGML_NATIVE is OFF in Docker. Flash-attention all-quant templates are ON.

8. Keep secrets out of git. Model shards stay in `models/` (gitignored) or a named Docker volume.

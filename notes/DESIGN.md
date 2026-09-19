# Design

This package is the buun-llama-cpp eval twin of r0b0tlab/qwen38-exl3-dflash2.

## Why buun

The fork loads EXL3 safetensors in llama-server, runs DFlash2 from an EXL3 sidecar, and owns VBR/Turbo/TCQ KV plus MTP and CopySpec. The ExLlamaV3 package already published the 4.00 bpw target and DFlash2 draft. This tree keeps those directories and swaps the engine.

## Max-decode path (24 GB 3090)

1. Target: r0b0tlab/Qwen3.8-27B-EXL3-4.00bpw (~15.4 GiB)
2. Draft: r0b0tlab/Qwen3.8-27B-DFlash2-EXL3-4.00bpw (~1.2 GiB)
3. `-ngl 99 -ngld 99 -fa on --jinja`
4. Server detects DFlash2; block size 13 (metadata 8 rewritten)
5. Adaptive draft depth on
6. VBR default at ctx 8192 (stays F16 until pressure)
7. At 262144: `--vbr-entry t8 --vbr-floor t3` so KV lands near 3-bit class (~3 GiB) plus ~1.22 GiB GDN history

## Arms

- dflash2-max: primary
- mtp: native MTP
- ar: baseline
- dflash2-copyspec: copy-heavy text
- dflash2-turbo3-tcq: fixed-tier KV vs VBR
- dflash2-262k: long context

MoE expert cache (`--moe-cache auto`) is in the engine and used for Flash-Next / DeepSeek-V4. Qwen3.8-27B dense hybrid does not need it.

## Eval parity

Gates copy the ExLlamaV3 package: GSM8K n=40 greedy, 150k prefill at 262k, T=1 n-gram profile, NIAH 2n/3n, Q200v2. Scripts speak HTTP so they stay stdlib. llama-server `timings.draft_n` / `draft_n_accepted` replace ExLlamaV3 `accepted_draft_tokens`.

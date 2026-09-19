# Results

Identity for every row: buun `1d0f493c73817176f6953069b7c10211de9555a1`, image `buun-llama:3090` id `sha256:4a4e8ddb0214…`, recipe `dflash2-max.env`, `-c 8192`, `-fa on --jinja --cache-ram 8192`, VBR default (entry f16, floor turbo4 class). Host port 8888 (host 8080 is occupied). Weights: published EXL3 4.00 bpw target + DFlash2 sidecar.

## GSM8K greedy n=40, DFlash2 (this tree)

Source: `notes/acceptance-dflash2.json`. Telemetry: `notes/telemetry-dflash2.tsv`.

- mean acceptance length: 4.755 (min 3.28, max 6.18)
- mean tok/s: 111.36 (p50 113.5)
- mean new_tokens: 253
- draft_stats_present: 40/40
- hit_token_cap: 6/40
- VRAM: 17338 MiB after load, 17542 MiB peak during eval
- GPU: ~338 W mean / 346 W max, 55 C
- DFlash2 log: block_size=13, fused encoder+injection, device-staged capture->inject, single-graph fused cycle (inject rows=14), in-graph selector, drafter warmup complete

`--fit on` failed to prove a speculative placement and restored pre-fit parameters. Serve still loaded. Drop `--fit` on this dense 4.00 bpw 3090 recipe.

## ExLlamaV3 twin (not this engine)

r0b0tlab/qwen38-exl3-dflash2, community `355c6ee`, same 3090, GSM8K greedy, ctx 8192:

- AR: AL 1.00, 42.8 tok/s
- MTP: AL 4.12, 116.3 tok/s
- DFlash2: AL 5.66, 162.9 tok/s
- 150k depth: 25.3 tok/s, AL 1.82, prefill 594 tok/s, peak 23.13 GB

Buun DFlash2 AL 4.76 is above 4.0 and above the ExLlamaV3 MTP AL of 4.12. Tok/s (111) is below native ExLlamaV3 DFlash2 (163) and slightly below that MTP arm (116). Do not claim a speed win.

## Unverified on this tree

MTP, AR, 262k load, T=1 sampled, NIAH, Q200v2. Those need recipe restarts and long-context VRAM.

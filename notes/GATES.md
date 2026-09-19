# Gates

Mirror of r0b0tlab/qwen38-exl3-dflash2 validation. Fill the Result column from a run in this tree. Historical ExLlamaV3 numbers are the baseline only.

Identity: `BUUN_SHA=1d0f493c73817176f6953069b7c10211de9555a1`, recipe `dflash2-max`, `-c 8192`, image `sha256:4a4e8ddb021408cfa6f2c330a7a84dab7a67487541653f984f6dce3aecd8f573`.

| Gate | Command | Result |
| --- | --- | --- |
| VRAM budget 4.00 bpw + t3 @ 262k | `python3 scripts/vram_budget.py 4.0 t3` | passed — 22.3 / 24 GB, exit 0 |
| llama-server DFlash2 load | `container/run-serve.sh` + `wait_ready.py --base-url http://127.0.0.1:8888` | passed — `/health` ok, draft-dflash auto-detect, block_size=13, warmup complete |
| GSM8K n=40 DFlash2 | `acceptance_check.py --n 40` | passed — AL 4.755, 111.36 tok/s, 40/40 draft_stats, JSON `notes/acceptance-dflash2.json` |
| GSM8K n=40 MTP | serve `mtp.env`, same script | unverified |
| GSM8K n=10 AR | serve `ar.env`, `--n 10` | unverified |
| AL >= 4.0 and > MTP + 0.3 | compare JSON summaries | partial — AL 4.755 >= 4.0; buun MTP arm not run. Vs ExLlamaV3 MTP 4.12 this is +0.64 |
| 262k + 150k prefill + 200 decode | serve `dflash2-262k.env`, `long_context_check.py` | unverified |
| T=1 sampled vs AR | `sampled_sanity_check.py` | unverified |
| NIAH 2n 262080 | `niah_multikey.py --variant 2n` | unverified |
| NIAH 3n 262080 | `niah_multikey.py --variant 3n` | unverified |
| Q200v2 text-180 | adapter + r0b0bench kit | unverified |
| Container image smoke | `docker build` + `/health` | passed — `buun-llama:3090` 4.61 GB, health ok on 8888 |

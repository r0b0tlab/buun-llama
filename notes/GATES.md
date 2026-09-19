# Gates

Identity: `BUUN_SHA=1d0f493c73817176f6953069b7c10211de9555a1`.

| Gate | Command | Result |
| --- | --- | --- |
| VRAM budget 4.00 bpw + t3 @ 262k | `python3 scripts/vram_budget.py 4.0 t3` | passed — 22.3 / 24 GB |
| llama-server DFlash2 load | `RECIPE=dflash2-max container/run-serve.sh` + wait_ready :8888 | passed — draft-dflash, block_size=13, warmup |
| GSM8K n=40 DFlash2 | `acceptance_check.py --n 40` | passed — AL 4.755, 111.36 tok/s |
| GSM8K n=40 MTP | serve `mtp.env` | passed — AL 3.246, 92.03 tok/s |
| GSM8K n=10 AR | serve `ar.env` `--n 10` | passed — AL 1.000, 46.04 tok/s |
| AL >= 4.0 and > MTP + 0.3 | compare JSON | passed — 4.755 > 3.546 |
| 262k + 150k prefill + 200 decode | `dflash2-262k.env` + `long_context_check.py` | unverified |
| T=1 sampled vs AR | `sampled_sanity_check.py` | unverified |
| NIAH 2n / 3n 262080 | `niah_multikey.py` | unverified |
| Q200v2 text-180 | adapter + r0b0bench | unverified |
| Container image smoke | docker build + /health | passed |
| GHCR public pull | anonymous manifest | blocked — package private, visibility API 404 |

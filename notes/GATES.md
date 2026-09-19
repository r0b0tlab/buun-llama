# Gates

Identity: `BUUN_SHA=1d0f493c73817176f6953069b7c10211de9555a1`.

| Gate | Command | Result |
| --- | --- | --- |
| VRAM budget 4.00 bpw + t3 @ 262k | `python3 scripts/vram_budget.py 4.0 t3` | passed — 22.3 / 24 GB |
| llama-server DFlash2 load | `RECIPE=dflash2-max container/run-serve.sh` + wait_ready :8888 | passed — draft-dflash, block_size=13, warmup |
| GSM8K n=40 DFlash2 | `acceptance_check.py --n 40` | passed — 4.755 / 111.36 on dflash2-max; 4.756 / 110.4 on 262k serve |
| GSM8K n=40 MTP | serve `mtp.env` | passed — AL 3.246, 92.03 tok/s |
| GSM8K n=10 AR | serve `ar.env` `--n 10` | passed — AL 1.000, 46.04 tok/s |
| AL >= 4.0 and > MTP + 0.3 | compare JSON | passed — 4.755 > 3.546 |
| 262k + 150k prefill + 200 decode | `dflash2-262k.env` + `long_context_check.py` | unverified |
| T=1 sampled vs AR | `sampled_sanity_check.py` | unverified |
| NIAH 2n / 3n | `niah_multikey.py --target-tokens 261888 --max-tokens 256` | passed — 261888 depth. 262080+thinking FAIL (64-token cap), disclosed |
| Q200v2 text-180 | adapter :8889 + kit | INCOMPLETE — 150/9/21; gsm8k 79/80; humaneval 39/40; ifeval 32/39; hard ungraded; ifeval-023 empty; BFCL NOT_IMPLEMENTED |
| Container image smoke | docker build + /health | passed |
| GHCR public pull | anonymous manifest | blocked — package private, visibility API 404 |

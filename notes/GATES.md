# Gates

Mirror of r0b0tlab/qwen38-exl3-dflash2 validation. Fill the Result column from a run in this tree. Historical ExLlamaV3 numbers are the baseline only.

| Gate | Command | Result |
| --- | --- | --- |
| VRAM budget 4.00 bpw + t3 @ 262k | `python3 scripts/vram_budget.py 4.0 t3` | passed — 22.3 / 24 GB, exit 0 |
| llama-server DFlash2 load | `bash scripts/serve.sh recipes/dflash2-max.env` then `wait_ready.py` | unverified |
| GSM8K n=40 DFlash2 | `acceptance_check.py --n 40` | unverified |
| GSM8K n=40 MTP | serve `mtp.env`, same script | unverified |
| GSM8K n=10 AR | serve `ar.env`, `--n 10` | unverified |
| AL >= 4.0 and > MTP + 0.3 | compare JSON summaries | unverified |
| 262k + 150k prefill + 200 decode | serve `dflash2-262k.env`, `long_context_check.py` | unverified |
| T=1 sampled vs AR | `sampled_sanity_check.py` | unverified |
| NIAH 2n 262080 | `niah_multikey.py --variant 2n` | unverified |
| NIAH 3n 262080 | `niah_multikey.py --variant 3n` | unverified |
| Q200v2 text-180 | adapter + r0b0bench kit | unverified |
| Container image smoke | `docker build` + `/health` | unverified |

Identity to record with every row: `BUUN_SHA` from `recipes/PIN`, recipe filename, `-c`, KV flags, `docker inspect` image id when the container is the runtime.

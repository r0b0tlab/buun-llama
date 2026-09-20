# Results

Current final-profile evidence is in `metrics/optimized/` and `notes/OPTIMIZED-PROFILE.md`: GSM8K: 149.19 mean E2E tok/s, AL 5.917; 150k/200 decode passed; NIAH 2n/3n passed; Q200v2 completed adjudication: 171 correct / 9 failed / 0 pending (capped ifeval-023 counted failed; original kit accounting unchanged); BFCL structural-hard20 scored13/20. T=1 smoke completed48 requests per arm and is not a formal losslessness proof. The tables below are historical, not substitutes for final-image results.

Identity: buun `1d0f493c73817176f6953069b7c10211de9555a1`, image `buun-llama:3090`, host port 8888, ctx 8192, `-fa on --jinja`, VBR default. Weights: published EXL3 4.00 bpw target + DFlash2 sidecar.

## GSM8K greedy, this tree (RTX 3090)

| arm | n | AL | tok/s | draft_stats | JSON |
| --- | ---: | ---: | ---: | ---: | --- |
| DFlash2 `dflash2-max` | 40 | 4.755 | 111.36 | 40/40 | notes/acceptance-dflash2.json |
| DFlash2 `dflash2-262k` GSM8K | 40 | 4.756 | 110.41 | 40/40 | notes/acceptance-262k-serve-gsm8k.json |
| MTP `mtp.env` | 40 | 3.246 | 92.03 | 40/40 | notes/acceptance-mtp.json |
| AR `ar.env` | 10 | 1.000 | 46.04 | 0/10 | notes/acceptance-ar.json |

DFlash2 vs this-engine MTP: AL 4.76 >= 4.0 and 4.76 > 3.25 + 0.3. Gate passed.

DFlash2 peak VRAM 17542 MiB, ~338 W, 55 C. Telemetry: `notes/telemetry-dflash2.tsv`. MTP used the target nextn head (`creating MTP draft context against the target model`). `--fit on` failed on DFlash2 and was dropped from default recipes.

## ExLlamaV3 twin (not this engine)

community `355c6ee`, same card/weights, GSM8K greedy ctx 8192:

- AR 1.00 / 42.8 tok/s
- MTP 4.12 / 116.3
- DFlash2 5.66 / 162.9

Buun DFlash2 is slower than native EXL3 DFlash2. Do not claim a speed win.

## Serve profile (`dflash2-262k`)

NIAH 2n/3n PASS at 261888. Decode ~28–30 tok/s. Q200v2 INCOMPLETE 169/10/1 (hard 19/20). See `notes/PUBLISH.md`.

## Historical scope

The older runs did not include the full serving sweep or sampling controls. Use `notes/GATES.md` for current status; do not infer a final-image pass from these historical rows.

## GHCR

`ghcr.io/r0b0tlab/buun-llama:3090` pushed and linked to r0b0tlab/buun-llama. Package visibility stays private: REST visibility endpoints 404. Flip Public in the package settings UI.

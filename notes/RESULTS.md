# Results

Identity: buun `1d0f493c73817176f6953069b7c10211de9555a1`, image `buun-llama:3090`, host port 8888, ctx 8192, `-fa on --jinja`, VBR default. Weights: published EXL3 4.00 bpw target + DFlash2 sidecar.

## GSM8K greedy, this tree (RTX 3090)

| arm | n | AL | tok/s | draft_stats | JSON |
| --- | ---: | ---: | ---: | ---: | --- |
| DFlash2 `dflash2-max` | 40 | 4.755 | 111.36 | 40/40 | notes/acceptance-dflash2.json |
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

## Unverified

262k load, T=1 sampled, NIAH, Q200v2.

## GHCR

`ghcr.io/r0b0tlab/buun-llama:3090` pushed and linked to r0b0tlab/buun-llama. Package visibility stays private: REST visibility endpoints 404. Flip Public in the package settings UI.

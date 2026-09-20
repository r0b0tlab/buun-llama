# Results website

Public report: https://blissful-ritual-rd6v.here.now/

Source: `website/` (static HTML, CSS, JavaScript, JSON and recipe; no build step).

## Preview

From the repository root:

```bash
python3 -m http.server 8766 --directory website
```

Open http://localhost:8766/. Charts fetch `data.json`, so use HTTP rather than opening the HTML with a file URL. Fonts load from Google Fonts with local fallbacks.

## Data and scope

- Final-profile results are drawn from `metrics/optimized/` at source commit `01e45396d9387e1a624cb037aa4e2a0100e78631`.
- The website embeds the completed supplemental Q200 outcome adjudication: 171 correct, 9 failed, 0 pending. Original kit status remains unchanged and disclosed.
- `website/data.json` contains all 1,310 primary-suite GPU samples, transformed to elapsed seconds, power W, temperature C, GPU utilization percent and VRAM GiB. Raw source: the final run's `telemetry.tsv`. Separate BFCL telemetry is outside the chart.
- The 441 active-load Q200 summary samples have a different scope from the full primary-suite trace. Q200 max temperature is 59 C; the full trace can exceed it.
- Storage was measured with file stat on September 20, 2026. Target directory: 16,533,482,191 logical bytes / 16,533,536,768 allocated bytes. Draft directory: 1,254,709,062 logical bytes / 1,254,723,584 allocated bytes.
- Docker image inspect reported 1,802,788,235 bytes for the exact final image identity. The combined displayed figure is 19.59 decimal GB. Image size excludes mounted weights and is not a compressed registry-download measurement.
- VBR settings and the 8.125 slot KV bits/value observation come from the restored service's `/props` and `/slots`. The idle snapshot is dated in the JSON; it does not claim fixed precision during 262k-context runs. Capacity floor: 3.25 bits/value; entry: turbo8.
- Q200 source summaries, image, recipe and engine identities are preserved. Failed/capped responses are disclosed, and no old candidate scores substitute for final results.

## Deployment

Published with the here.now skill helper. Final verified version: `01M2ZY968AMY9YVWHDK61EYRR2`.

Deployment was anonymous and expires 24 hours after initial creation unless claimed. The owner claim URL is private and is not included in this repository. `.herenow/` is ignored and must never be added to the public site or repository. Updating the same slug uses local state for optimistic version checks.

## Verification

- Chromium live-page checks passed at 320, 390, 768 and 1440 px: no horizontal page overflow; all three telemetry tabs switch correctly.
- Verified 40 throughput bars and 180 outcome cells (9 failed).
- Exact-byte storage disclosure opens; section links resolve.
- Copy command succeeds and clipboard contents exactly match the command source after awaiting the asynchronous clipboard operation.
- Public JSON, CSS, JS and recipe bytes match local SHA-256 values.
- No JavaScript page errors in the successful live-page checks.
- Desktop and mobile screenshots reviewed. Mobile SVGs redraw at viewport width to preserve label size.

Only website and publication metadata changed; serving configuration and benchmark results were not rerun or modified.

# Final production-suite gates

Profile: `recipes/dflash2-optimized.env` (low reasoning, block8 adaptive, VBR t8/t3, ctx262144).
Image: `sha256:8d6d67a5b1ac856882731d5638b1291f5b81f89f75ac8e664df39cd7991b5652`.
Engine: `1d0f493c73817176f6953069b7c10211de9555a1`.

The suite completed. Overall quality qualification is NOT all-green: Q200v2 retains one capped response. Exact evidence is under `metrics/optimized/`; previous candidate results are separate.

| Gate | Final result |
| --- | --- |
| Unit tests / kit checksums | passed:5 tests; frozen manifest verified |
| Packaged server / profile | passed:embedded recipe, no host recipe bind, effective262144 context |
| GSM8K throughput | completed:n=40,149.19 mean E2E tok/s,AL5.917; one512-token cap contact in this throughput-only probe |
| Mixed serving throughput | completed:107.95 aggregate tok/s,0.175s median TTFT |
| Queued clients | passed:1,2,4 client batches all returned positive token counts; one active slot, not multi-slot batching |
| Long context | passed:150000 prompt tokens +200 new tokens,no truncation;525.30 prefill tok/s,27.84 decode tok/s |
| NIAH2n /3n | passed:261888 input tokens +256 response reserve;32.78/32.98 decode tok/s |
| Q200v2 text-180 | Outcome grading complete: 171 correct / 9 failed / 0 pending. ifeval-023 adjudicated failed at the cap; original kit transport status remains INCOMPLETE. See notes/Q200V2-ADJUDICATION.md. |
| Manual reasoning grading | complete:19/20; hard-13 wrong triangle-pursuit distance |
| BFCL structural-hard20 | SCORED:13 correct /7 incorrect;20 unique cases,zero timing errors |
| T=1 sampling smoke vs AR | completed:48 requests per arm; no transport errors; not a distribution-equivalence proof |
| Full sampling losslessness proof | unverified; the smoke is not a statistical or formal proof |

BFCL's two initial setup attempts failed before inference (housekeeping locks under the fresh root, then a missing timing-path binding). The scored attempt used a new results root and relocated only lock bookkeeping; frozen harness, dataset and grader files were not changed. Preserve these disclosures when quoting results.

The final Q200 cap was not raised and the response was not regenerated. Historical successful runs must not replace it.

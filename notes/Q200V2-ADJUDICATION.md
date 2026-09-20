# Completed Q200v2 outcome adjudication

All 180 text cases now have a final outcome in this supplemental review. The previously ungraded `ifeval-023` is a failure in both engines: neither supplied the requested logic quiz within the fixed 8192-token budget.

| Engine / measured run | Correct | Failed | Pending |
| --- | ---: | ---: | ---: |
| buun optimized final (`q200v2-buun-optimized-final-20260919`) | 171 | 9 | 0 |
| Native ExLlamaV3 (`q200v2-native-container-20260917`) | 172 | 8 | 0 |

| Family | buun correct / total | Native correct / total |
| --- | ---: | ---: |
| GSM8K | 79/80 | 78/80 |
| HumanEval | 39/40 | 40/40 |
| IFEval | 34/40 | 34/40 |
| Hard reasoning | 19/20 | 20/20 |

The IFEval denominator is now all 40 cases; both have 34 correct and 6 failed (85.0%). No task is awaiting human grading.

## Remaining-row decision

`ifeval-023` asks for a logic quiz for teenagers about a chesterfield, using the letter `t` at most once.

- buun saved final content: one whitespace character.
- Native saved final content: one period. Its letter-frequency checker passes vacuously, but a period is not the requested quiz.
- Both responses ended with `finish_reason=length` after 8192 completion tokens.
- Final outcome: FAILED_NO_SUBSTANTIVE_ANSWER_AT_TOKEN_CAP.

This is an explicit supplemental all-row accounting policy: retain the prior valid grades and count the exhausted-budget, no-answer case as failed. No reasoning text was promoted into a final answer; no model response was regenerated; no cap was increased.

## Evidence and status distinction

- [Completed adjudication](../metrics/optimized/q200v2-adjudicated.json) binds the remaining-row verdict to the exact response/content hashes, dataset, run identity, source-summary hash and raw-row-file hash.
- [Original frozen-kit summary](../metrics/optimized/q200v2-summary.json) remains byte-for-byte unchanged. Its `INCOMPLETE` status means its transport/closure contract was not satisfied, not that our outcome review is pending.
- Grading complete does not mean all answers correct or production qualification all-green. The response-cap failure remains a failure.
- This supplemental adjudication is not relabeled as a kit-produced `SCORED` result. Earlier candidate runs remain historical.

No throughput, NIAH or BFCL measurements changed.

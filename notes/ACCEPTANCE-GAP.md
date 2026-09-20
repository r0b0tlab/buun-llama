# Acceptance-gap diagnosis

## Finding

The previously quoted ExLlamaV3 AL 5.657 versus buun AL about 4.76 comparison used different serialized prompts. The template's default xhigh system instruction is a major measured cause of the lower buun acceptance on these GSM8K questions. The evidence does not establish a quantization defect or an engine-specific training mismatch.

No server recipe, checkpoint or kernel was changed for this investigation.

## Source-level discrepancy

- Native `scripts/acceptance_check.py:84` (in the sibling qwen38-exl3-dflash2 package) builds raw ChatML: user question followed by the assistant header. It does not run the target chat template and does not append a think prefix.
- Buun `scripts/acceptance_check.py:54-62` sends chat messages without explicit reasoning settings.
- Target `chat_template.jinja:46-54` defaults reasoning_effort to xhigh. The rendered prompt adds a system instruction and an opening `<think>` line.
- The system instruction begins: `Reasoning effort is set to xhigh.` It asks for careful reasoning, validation, alternatives and prioritizing correctness/clarity.
- Calling `/apply-template` with `chat_template_kwargs={"reasoning_effort":"medium","enable_thinking":true}` produces user + assistant + think prefix without the xhigh system instruction.

## Controlled experiment

Engine build b1-1d0f493c7; serving image sha256:1bd92ad3c2d7f53047501912ca671662df8b10ef8d7e3da6dfafb58243286954; recipe dflash2-262k; configured context 262144; VBR turbo8 entry/turbo3_tcq floor; EXL3 target and draft unchanged; DFlash2 block 13 adaptive; one slot.

First 40 questions from eval/gsm8k_n40.jsonl; greedy; max 512 output tokens; seed 42; repetition multiplier 1 and zero presence/frequency penalties. Each prompt was tokenized with parse_special true/add_special false and submitted to the same `/completion` endpoint with cache_prompt false. Alternated arm order by question within each pair. Short input lengths on a 262k-configured server, not 8k-long prompts.

Two pairs, 160 recorded requests with 160 unique (mode, question-index) keys:

| Prompt variant | Mean per-request AL | Accepted/proposed drafts | Mean per-request E2E tok/s |
| --- | ---: | ---: | ---: |
| Raw native benchmark ChatML; no injected system or think prefix | 5.6284 | 58.95% | 133.03 |
| Raw ChatML + think prefix; equivalent rendered medium reasoning here | 6.3127 | 64.06% | 143.09 |
| xhigh system instruction, no think prefix | 4.6758 | 44.86% | 106.48 |
| Default buun template: xhigh system + think prefix | 4.8106 | 45.81% | 108.68 |

Historical native n=40 mean AL: 5.6572182794531445. Prompt-matched buun mean AL: 5.628413949309527; difference 0.028804330143617385. This is not a fresh fully matched cross-engine parity run: native used different width/KV/runtime, and its result is historical.

Within this same buun process:
- Raw native prompt minus default template: +0.81779 AL; positive on 34/40 prompts.
- Think prefix retained, xhigh instruction removed: +1.50204 AL; positive on 40/40 prompts.
- No think prefix in either arm, xhigh removed: +0.95258 AL; positive on 36/40 prompts.

Prompt-bootstrap 95% intervals (10,000 resamples, seed 42) are approximately [0.5994,1.0372], [1.2311,1.8111] and [0.7304,1.1685] respectively. These measure prompt-sample variation, not repeated-run/runtime variance.

## Interpretation and limits

The xhigh instruction changes the target's continuation distribution; it is associated with lower draft prefix survival on this workload. Keeping the think prefix without that instruction achieves higher AL, so the result is not explained by merely turning off thinking.

A wider speculative block does not guarantee higher acceptance, but block 13 already supports AL above the historical native benchmark when prompt conditioning changes. Retraining is not justified as the first remedy from these measurements.

The old 31% versus 67% figures were not observed acceptance rates: dividing AL-1 by maximum configured width ignores adaptive proposal lengths. The table instead uses actual accepted/proposed counters.

The old throughput comparison also mixes prompts. Even after prompt matching, this buun run's mean E2E speed remains below the historical native 162.93 figure, but this experiment does not isolate the residual speed cause. Do not infer a kernel ceiling or a training-data explanation.

Changing reasoning effort changes model behavior and outputs. Medium is a throughput/acceptance candidate, not a verified quality-equivalent replacement. Preserve the serving default until promotion testing, then Q200v2 and NIAH on the exact promoted profile. Do not compare a medium candidate to xhigh as though only the implementation changed.

## Reproduction artifacts

Local diagnostic script: `work/acceptance-gap/probe.py`.
- `work/acceptance-gap/block13-adaptive-n40/rows.jsonl`, `props.json`, `summary.json`
- `work/acceptance-gap/template-components-n40/rows.jsonl`, `props.json`, `summary.json`

The first directory uses `--modes native,template`; the second `--modes think_only,system_only`; both use `--n 40`. Use a new output directory for each run because rows append. These are diagnostic artifacts, not a production benchmark harness.

No production configuration changed. No checkpoint training/requantization was performed. No Q200v2/NIAH rerun is claimed for these prompt variants.

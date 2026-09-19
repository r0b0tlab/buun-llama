#!/usr/bin/env python3
"""T=1 sampled n-gram profile vs a second (usually AR) endpoint or sequential run.

Point --base-url at a DFlash2 server and --ar-url at an AR server, or omit --ar-url
and pass --ar-json from a prior AR run. Stdlib only.

  python3 scripts/sampled_sanity_check.py --base-url http://127.0.0.1:8080 --json-out notes/sampled-dflash2.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from llama_http import post_json  # noqa: E402

PROMPTS = [
    "Explain why the sky is blue, briefly.",
    "Write a one-paragraph product description for a mechanical keyboard.",
    "Summarize the plot of Romeo and Juliet in three sentences.",
    "What are the main differences between TCP and UDP?",
    "Give me a recipe for pancakes.",
    "Describe how a transformer neural network works.",
]


def stats(texts):
    lens = [len(t) for t in texts]
    toks = Counter()
    for t in texts:
        toks.update(t.split())
    vocab = len(toks)
    total = sum(toks.values())
    return {
        "n": len(texts),
        "mean_chars": (sum(lens) / len(lens)) if lens else 0.0,
        "distinct_token_rate": vocab / max(1, total),
        "top20_share": sum(c for _, c in toks.most_common(20)) / max(1, total),
    }


def collect(base_url, model, temperature, max_tokens, samples_per_prompt, timeout):
    texts = []
    t0 = time.time()
    for p in PROMPTS:
        for _ in range(samples_per_prompt):
            resp = post_json(
                base_url.rstrip("/") + "/v1/chat/completions",
                {
                    "model": model,
                    "messages": [{"role": "user", "content": p}],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                timeout=timeout,
            )
            msg = ((resp.get("choices") or [{}])[0].get("message") or {})
            texts.append(msg.get("content") or "")
    dt = time.time() - t0
    out = stats(texts)
    out["wall_seconds"] = round(dt, 1)
    out["approx_tok_per_s"] = (len(texts) * max_tokens / dt) if dt else 0.0
    return out, texts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://127.0.0.1:8080")
    ap.add_argument("--ar-url", default=None, help="AR server; omit to skip the AR arm")
    ap.add_argument("--ar-json", default=None, help="Prior AR stats JSON to compare")
    ap.add_argument("--model", default="qwen38-27b-buun")
    ap.add_argument("--samples-per-prompt", type=int, default=8)
    ap.add_argument("--max-tokens", type=int, default=96)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--json-out", default=None)
    args = ap.parse_args()

    results = {}
    dflash_stats, _ = collect(
        args.base_url, args.model, args.temperature, args.max_tokens,
        args.samples_per_prompt, args.timeout,
    )
    results["dflash2"] = dflash_stats
    if args.ar_url:
        ar_stats, _ = collect(
            args.ar_url, args.model, args.temperature, args.max_tokens,
            args.samples_per_prompt, args.timeout,
        )
        results["autoregressive"] = ar_stats
    elif args.ar_json:
        with open(args.ar_json, "r", encoding="utf-8") as fh:
            prior = json.load(fh)
        results["autoregressive"] = prior.get("autoregressive") or prior.get("dflash2") or prior
    print(json.dumps(results, indent=2))
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=2)


if __name__ == "__main__":
    main()

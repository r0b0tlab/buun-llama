#!/usr/bin/env python3
"""Concurrent slot sweep. Server must be started with -np >= max batch size.

  python3 scripts/concurrency_check.py --base-url http://127.0.0.1:8080 --batch-sizes 1,2,4
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from llama_http import acceptance_length, post_json  # noqa: E402

PROMPTS = [
    "Explain why the sky is blue, briefly.",
    "Write a one-paragraph description of a mechanical keyboard.",
    "Summarize the plot of Romeo and Juliet in three sentences.",
    "What are the main differences between TCP and UDP?",
    "Give me a recipe for pancakes.",
    "Describe how a transformer neural network works.",
    "List five countries in South America and their capitals.",
    "Explain photosynthesis in one sentence.",
]


def one(base, model, prompt, max_tokens, timeout):
    t0 = time.time()
    resp = post_json(
        base + "/v1/chat/completions",
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "max_tokens": max_tokens,
        },
        timeout=timeout,
    )
    dt = time.time() - t0
    timings = resp.get("timings") or {}
    al, new_tokens, accepted = acceptance_length(timings)
    return {
        "new_tokens": new_tokens,
        "accepted_draft_tokens": accepted,
        "acceptance_length": al,
        "time": dt,
        "tok_per_s": (new_tokens / dt) if dt > 0 and new_tokens else 0.0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://127.0.0.1:8080")
    ap.add_argument("--model", default="qwen38-27b-buun")
    ap.add_argument("--batch-sizes", default="1,2,4")
    ap.add_argument("--max-tokens", type=int, default=256)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--json-out", default=None)
    args = ap.parse_args()

    base = args.base_url.rstrip("/")
    rows = []
    for n in [int(x) for x in args.batch_sizes.split(",")]:
        t0 = time.time()
        results = []
        with ThreadPoolExecutor(max_workers=n) as pool:
            futs = [
                pool.submit(one, base, args.model, PROMPTS[i % len(PROMPTS)], args.max_tokens, args.timeout)
                for i in range(n)
            ]
            for fut in as_completed(futs):
                results.append(fut.result())
        wall = time.time() - t0
        total_new = sum(r["new_tokens"] for r in results)
        als = [r["acceptance_length"] for r in results if r["acceptance_length"]]
        rows.append(
            {
                "n": n,
                "wall_seconds": round(wall, 2),
                "aggregate_tok_per_s": (total_new / wall) if wall else 0.0,
                "mean_acceptance_length": (sum(als) / len(als)) if als else None,
                "per_seq": results,
            }
        )
    print(json.dumps(rows, indent=2))
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, indent=2)


if __name__ == "__main__":
    main()

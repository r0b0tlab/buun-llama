#!/usr/bin/env python3
"""Multi-needle NIAH at max context against llama-server.

Uses /apply-template + /tokenize + /completion with a token-id prompt.
Mirrors r0b0tlab/qwen38-exl3-dflash2 scripts/niah_multikey.py.

  python3 scripts/niah_multikey.py --base-url http://127.0.0.1:8080 --variant 2n
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from llama_http import post_json  # noqa: E402

CODES = {
    "2n": ["R0B0-ZEBRA-7731", "R0B0-LYNX-4402"],
    "3n": ["R0B0-ZEBRA-7731", "R0B0-LYNX-4402", "R0B0-RAVEN-9158"],
}
FRACTIONS = {"2n": [0.33, 0.66], "3n": [0.33, 0.66, 0.90]}
UNIT = " The archival record contains neutral observations about weather, tools, books, roads, and ordinary daily events."
MARKER = "R0B0BENCH_NIAH_SLOT"


def tokenize(base, text):
    toks = post_json(
        base + "/tokenize",
        {"content": text, "add_special": False, "parse_special": True},
        timeout=120,
    )["tokens"]
    return [t["id"] if isinstance(t, dict) else t for t in toks]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://127.0.0.1:8080")
    ap.add_argument("--variant", choices=["2n", "3n"], required=True)
    ap.add_argument("--target-tokens", type=int, default=262080)
    ap.add_argument("--max-tokens", type=int, default=256)
    ap.add_argument("--timeout", type=int, default=7200)
    ap.add_argument("--json-out", default=None)
    args = ap.parse_args()

    base = args.base_url.rstrip("/")
    instruction = (
        "You are given a long archival record. Secret verification codes appear in order, "
        "each exactly once.\n"
        + MARKER
        + "\nQuestion: What is the LAST secret verification code? Reply with only the code, nothing else."
    )
    rendered_prompt = post_json(
        base + "/apply-template",
        {"messages": [{"role": "user", "content": instruction}]},
        timeout=60,
    )["prompt"]
    rendered = tokenize(base, rendered_prompt)
    marker_ids = tokenize(base, MARKER)
    pos = None
    for i in range(len(rendered) - len(marker_ids) + 1):
        if rendered[i : i + len(marker_ids)] == marker_ids:
            pos = i
            break
    if pos is None:
        print(json.dumps({"error": "marker not found in rendered prompt"}))
        return 2

    prefix, suffix = rendered[:pos], rendered[pos + len(marker_ids) :]
    codes = CODES[args.variant]
    fractions = FRACTIONS[args.variant]
    unit = tokenize(base, UNIT)
    needles = [tokenize(base, "\nIMPORTANT SECRET VERIFICATION CODE: %s\n" % c) for c in codes]

    body_budget = args.target_tokens - len(prefix) - len(suffix)
    if body_budget < sum(len(n) for n in needles) + 4096:
        print(json.dumps({"error": "target window too small", "body_budget": body_budget}))
        return 2

    cuts = [int(body_budget * f) for f in fractions]
    body = []
    cursor = 0
    for cut, needle in zip(cuts, needles):
        gap = cut - cursor
        reps = max(1, (gap // len(unit)) + 1)
        seg = (unit * reps)[: max(0, gap)]
        body += seg
        body += needle
        cursor = cut + len(needle)
    tail_gap = body_budget - cursor
    body += (unit * (max(1, (tail_gap // len(unit)) + 1)))[: max(0, tail_gap)]
    if len(body) < body_budget:
        body += (unit * ((body_budget - len(body)) // len(unit) + 2))[: body_budget - len(body)]
    body = body[:body_budget]
    input_ids = prefix + body + suffix
    if len(input_ids) != args.target_tokens:
        print(json.dumps({"error": "length mismatch", "got": len(input_ids), "want": args.target_tokens}))
        return 2

    t0 = time.time()
    resp = post_json(
        base + "/completion",
        {
            "prompt": input_ids,
            "n_predict": args.max_tokens,
            "temperature": 0,
            "cache_prompt": True,
        },
        timeout=args.timeout,
    )
    elapsed = time.time() - t0
    text = (resp.get("content") or "").strip()
    last_code = codes[-1]
    timings = resp.get("timings") or {}
    row = {
        "variant": args.variant,
        "fractions": fractions,
        "codes": codes,
        "target_tokens": args.target_tokens,
        "prompt_n": timings.get("prompt_n"),
        "predicted_n": timings.get("predicted_n"),
        "elapsed_s": round(elapsed, 1),
        "stop_type": resp.get("stop_type"),
        "last_code": last_code,
        "passed": last_code in text,
        "all_codes_found": [c for c in codes if c in text],
        "response_text": text[:400],
        "draft_n": timings.get("draft_n"),
        "draft_n_accepted": timings.get("draft_n_accepted"),
        "predicted_per_second": timings.get("predicted_per_second"),
    }
    print(json.dumps(row, indent=2))
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(row, fh, indent=2)
    return 0 if row["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

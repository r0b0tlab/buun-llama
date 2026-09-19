#!/usr/bin/env python3
"""Long-context prefill + decode against llama-server.

Default: 150000-token mid-document slice, 200 new tokens, ctx 262144.
Uses POST /tokenize then POST /completion with a token-id prompt.

  python3 scripts/long_context_check.py --base-url http://127.0.0.1:8080
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from llama_http import acceptance_length, post_json  # noqa: E402

GUTENBERG_URL = "https://www.gutenberg.org/files/1342/1342-0.txt"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ensure_book(path):
    if os.path.exists(path) and os.path.getsize(path) > 10000:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    req = urllib.request.Request(GUTENBERG_URL, headers={"User-Agent": "buun-llama-eval"})
    with urllib.request.urlopen(req, timeout=120) as resp, open(path, "wb") as fh:
        fh.write(resp.read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://127.0.0.1:8080")
    ap.add_argument("--ctx", type=int, default=262144)
    ap.add_argument("--prompt-tokens", type=int, default=150000)
    ap.add_argument("--decode-tokens", type=int, default=200)
    ap.add_argument("--timeout", type=int, default=7200)
    ap.add_argument("--json-out", default=None)
    args = ap.parse_args()

    book_path = os.path.join(ROOT, "work", "longctx.txt")
    ensure_book(book_path)
    with open(book_path, "r", encoding="utf-8", errors="ignore") as fh:
        book = fh.read()

    base = args.base_url.rstrip("/")
    tok = post_json(
        base + "/tokenize",
        {"content": book, "add_special": False, "parse_special": False},
        timeout=600,
    )["tokens"]
    ids = [t["id"] if isinstance(t, dict) else t for t in tok]
    if len(ids) < args.prompt_tokens + 4096:
        raise SystemExit("book tokenized to %d tokens, need %d" % (len(ids), args.prompt_tokens + 4096))
    # Mid-document slice so decode is not the book's own ending.
    start = max(0, (len(ids) - args.prompt_tokens) // 3)
    prompt_ids = ids[start : start + args.prompt_tokens]
    print("prompt tokens: %d (ctx %d, start %d)" % (len(prompt_ids), args.ctx, start))

    t0 = time.time()
    resp = post_json(
        base + "/completion",
        {
            "prompt": prompt_ids,
            "n_predict": args.decode_tokens,
            "temperature": 0,
            "cache_prompt": True,
        },
        timeout=args.timeout,
    )
    total_s = time.time() - t0
    timings = resp.get("timings") or {}
    al, new_tokens, accepted = acceptance_length(timings)
    prompt_n = int(timings.get("prompt_n") or len(prompt_ids))
    prompt_ms = float(timings.get("prompt_ms") or 0.0)
    pred_ms = float(timings.get("predicted_ms") or 0.0)
    row = {
        "prompt_tokens": len(prompt_ids),
        "prompt_n": prompt_n,
        "new_tokens": new_tokens,
        "prefill_seconds": round(prompt_ms / 1000.0, 1) if prompt_ms else None,
        "prefill_tok_per_s": timings.get("prompt_per_second"),
        "decode_seconds": round(pred_ms / 1000.0, 2) if pred_ms else round(total_s, 2),
        "decode_tok_per_s": timings.get("predicted_per_second"),
        "acceptance_length": None if al is None else round(al, 3),
        "draft_n": timings.get("draft_n"),
        "draft_n_accepted": accepted,
        "wall_seconds": round(total_s, 1),
        "stop_type": resp.get("stop_type"),
        "truncated": resp.get("truncated"),
    }
    print(json.dumps(row, indent=2))
    content = resp.get("content") or ""
    if content:
        print("continuation tail:", repr(content[-200:]))
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(row, fh, indent=2)


if __name__ == "__main__":
    main()

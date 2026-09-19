#!/usr/bin/env python3
"""GSM8K greedy acceptance-length check against llama-server.

Mirrors r0b0tlab/qwen38-exl3-dflash2 scripts/acceptance_check.py (eval standpoint).
Stdlib only. Server must already be running.

  python3 scripts/acceptance_check.py --base-url http://127.0.0.1:8080 --n 40
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from llama_http import acceptance_length, post_json  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SET = os.path.join(ROOT, "eval", "gsm8k_n40.jsonl")


def load_questions(path, n):
    rows = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line)["question"].strip())
            if len(rows) >= n:
                break
    if len(rows) < n:
        raise SystemExit("need %d questions in %s, found %d" % (n, path, len(rows)))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://127.0.0.1:8080")
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--max-tokens", type=int, default=512)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--questions", default=DEFAULT_SET)
    ap.add_argument("--model", default="qwen38-27b-buun")
    ap.add_argument("--json-out", default=None)
    args = ap.parse_args()

    questions = load_questions(args.questions, args.n)
    per_request = []
    for i, q in enumerate(questions):
        t0 = time.time()
        resp = post_json(
            args.base_url.rstrip("/") + "/v1/chat/completions",
            {
                "model": args.model,
                "messages": [{"role": "user", "content": q}],
                "temperature": 0,
                "max_tokens": args.max_tokens,
            },
            timeout=args.timeout,
        )
        dt = time.time() - t0
        timings = resp.get("timings") or {}
        al, new_tokens, accepted = acceptance_length(timings)
        usage = resp.get("usage") or {}
        if not new_tokens:
            new_tokens = int(usage.get("completion_tokens") or 0)
        choice = (resp.get("choices") or [{}])[0]
        msg = choice.get("message") or {}
        per_request.append(
            {
                "i": i,
                "new_tokens": new_tokens,
                "accepted_draft_tokens": accepted,
                "draft_n": timings.get("draft_n"),
                "acceptance_length": al,
                "tok_per_s": (new_tokens / dt) if dt > 0 and new_tokens else 0.0,
                "predicted_per_second": timings.get("predicted_per_second"),
                "prompt_per_second": timings.get("prompt_per_second"),
                "time": dt,
                "finish_reason": choice.get("finish_reason"),
                "content_chars": len(msg.get("content") or ""),
            }
        )

    usable = [p for p in per_request if p["new_tokens"] > 0]
    als = [p["acceptance_length"] for p in usable if p["acceptance_length"] is not None]
    tps = [p["tok_per_s"] for p in usable]
    summary = {
        "base_url": args.base_url,
        "n": len(per_request),
        "mean_acceptance_length": (sum(als) / len(als)) if als else None,
        "mean_tok_per_s": (sum(tps) / len(tps)) if tps else None,
        "hit_token_cap": sum(1 for p in per_request if p["new_tokens"] >= args.max_tokens),
        "draft_stats_present": sum(1 for p in per_request if p["draft_n"]),
    }
    print(json.dumps(summary, indent=2))
    if args.json_out:
        os.makedirs(os.path.dirname(os.path.abspath(args.json_out)) or ".", exist_ok=True)
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump({"summary": summary, "per_request": per_request}, fh, indent=2)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Minimal HTTP JSON client. Stdlib only."""
from __future__ import annotations

import json
import urllib.error
import urllib.request


def post_json(url, payload, timeout=600):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError("HTTP %s %s: %s" % (exc.code, url, body[:2000])) from exc


def get_json(url, timeout=30):
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def acceptance_length(timings):
    """AL = new_tokens / (new_tokens - accepted_draft_tokens)."""
    if not timings:
        return None, 0, 0
    new_tokens = int(timings.get("predicted_n") or 0)
    accepted = int(timings.get("draft_n_accepted") or 0)
    if new_tokens <= 0:
        return 0.0, new_tokens, accepted
    rounds = max(1, new_tokens - accepted)
    return new_tokens / rounds, new_tokens, accepted

#!/usr/bin/env python3
"""Block until llama-server answers GET /health or GET /v1/models."""
from __future__ import annotations

import argparse
import sys
import time
import urllib.error
import urllib.request


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://127.0.0.1:8080")
    ap.add_argument("--timeout", type=int, default=3600)
    args = ap.parse_args()
    deadline = time.time() + args.timeout
    urls = [
        args.base_url.rstrip("/") + "/health",
        args.base_url.rstrip("/") + "/v1/models",
    ]
    while time.time() < deadline:
        for url in urls:
            try:
                with urllib.request.urlopen(url, timeout=5) as resp:
                    if 200 <= resp.status < 300:
                        print("ready", url)
                        return 0
            except (urllib.error.URLError, TimeoutError, OSError):
                pass
        time.sleep(2)
    print("timeout waiting for", args.base_url, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

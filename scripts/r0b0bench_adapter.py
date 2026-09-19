#!/usr/bin/env python3
"""Thin r0b0bench contract adapter in front of llama-server.

llama-server already speaks /v1/chat/completions. This process adds:
  GET  /v1/models            -> injects max_model_len from /props
  POST /v1/chat/completions/render -> /apply-template + /tokenize
  POST /v1/completions       -> token-id list via /completion
  thinking split             -> reasoning_content + content on </think>

Stdlib only. Run:
  python3 scripts/r0b0bench_adapter.py --upstream http://127.0.0.1:8080 --port 8889
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from llama_http import get_json, post_json  # noqa: E402

UPSTREAM = "http://127.0.0.1:8080"
CTX = 262144
ALIAS = "qwen38-27b-buun"
THINK_END = "</think>"


def split_thinking(text):
    if not text:
        return None, ""
    if THINK_END in text:
        left, right = text.split(THINK_END, 1)
        reasoning = left.replace("<think>", "").strip()
        content = right.strip() or text
        return reasoning or None, content
    return None, text


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n) if n else b"{}"
        return json.loads(raw.decode("utf-8") or "{}")

    def do_GET(self):
        if self.path.split("?")[0] in ("/health", "/v1/models"):
            try:
                props = get_json(UPSTREAM + "/props", timeout=10)
            except Exception:
                props = {}
            default = (props.get("default_generation_settings") or {})
            n_ctx = int(default.get("n_ctx") or CTX)
            self._send(
                200,
                {
                    "object": "list",
                    "data": [
                        {
                            "id": ALIAS,
                            "object": "model",
                            "owned_by": "buun-llama",
                            "max_model_len": n_ctx,
                        }
                    ],
                },
            )
            return
        self._send(404, {"error": "not found"})

    def do_POST(self):
        path = self.path.split("?")[0]
        payload = self._read_json()
        try:
            if path == "/v1/chat/completions/render":
                tmpl = post_json(UPSTREAM + "/apply-template", {"messages": payload.get("messages") or []}, timeout=60)
                toks = post_json(
                    UPSTREAM + "/tokenize",
                    {"content": tmpl["prompt"], "add_special": False, "parse_special": True},
                    timeout=120,
                )["tokens"]
                ids = [t["id"] if isinstance(t, dict) else t for t in toks]
                self._send(200, {"token_ids": ids})
                return
            if path == "/v1/completions":
                prompt = payload.get("prompt")
                n_predict = int(payload.get("max_tokens") or payload.get("n_predict") or 256)
                body = {
                    "prompt": prompt,
                    "n_predict": n_predict,
                    "temperature": float(payload.get("temperature") or 0),
                    "cache_prompt": True,
                }
                resp = post_json(UPSTREAM + "/completion", body, timeout=int(payload.get("timeout") or 7200))
                text = resp.get("content") or ""
                timings = resp.get("timings") or {}
                self._send(
                    200,
                    {
                        "id": "cmpl-buun",
                        "object": "text_completion",
                        "model": payload.get("model") or ALIAS,
                        "choices": [{"text": text, "index": 0, "finish_reason": _finish(resp)}],
                        "usage": {
                            "prompt_tokens": int(timings.get("prompt_n") or 0) or 1,
                            "completion_tokens": int(timings.get("predicted_n") or 0) or 1,
                            "total_tokens": int(timings.get("prompt_n") or 0) + int(timings.get("predicted_n") or 0),
                        },
                        "timings": timings,
                    },
                )
                return
            if path == "/v1/chat/completions":
                resp = post_json(UPSTREAM + "/v1/chat/completions", payload, timeout=int(payload.get("timeout") or 3600))
                choice = (resp.get("choices") or [{}])[0]
                msg = choice.get("message") or {}
                reasoning, content = split_thinking(msg.get("content") or "")
                if not content:
                    content = msg.get("content") or " "
                msg["content"] = content
                if reasoning:
                    msg["reasoning_content"] = reasoning
                choice["message"] = msg
                usage = resp.get("usage") or {}
                if int(usage.get("prompt_tokens") or 0) <= 0:
                    usage["prompt_tokens"] = 1
                if int(usage.get("completion_tokens") or 0) <= 0:
                    usage["completion_tokens"] = 1
                resp["usage"] = usage
                self._send(200, resp)
                return
        except Exception as exc:
            self._send(502, {"error": str(exc)})
            return
        self._send(404, {"error": "not found"})


def _finish(resp):
    stop = resp.get("stop_type")
    if stop == "limit":
        return "length"
    return "stop"


def main():
    global UPSTREAM, CTX, ALIAS
    ap = argparse.ArgumentParser()
    ap.add_argument("--upstream", default="http://127.0.0.1:8080")
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8889)
    ap.add_argument("--ctx", type=int, default=262144)
    ap.add_argument("--alias", default="qwen38-27b-buun")
    args = ap.parse_args()
    UPSTREAM = args.upstream.rstrip("/")
    CTX = args.ctx
    ALIAS = args.alias
    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    print("adapter %s:%d -> %s" % (args.host, args.port, UPSTREAM), flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()

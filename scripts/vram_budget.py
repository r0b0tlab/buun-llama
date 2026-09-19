#!/usr/bin/env python3
"""VRAM budget gate for Qwen3.8-27B EXL3 + DFlash2 on 24 GB under buun KV codecs."""
from __future__ import annotations

import sys

PARAMS_B = 27.0
VOCAB = 248320
HIDDEN = 5120
FULL_ATTN_LAYERS = 16
KV_HEADS = 4
HEAD_DIM = 256
CTX = 262_144
CARD_GB = 24.0

BPV = {
    "f16": 16.0,
    "t8": 8.125,
    "turbo8": 8.125,
    "t4": 4.125,
    "turbo4": 4.125,
    "t3": 3.25,
    "turbo3_tcq": 3.25,
    "t2": 2.25,
    "turbo2_tcq": 2.25,
    "t1": 1.25,
    "turbo1_tcq": 1.25,
}

bpw = float(sys.argv[1]) if len(sys.argv) > 1 else 4.0
tier = sys.argv[2] if len(sys.argv) > 2 else "t3"
if tier not in BPV:
    sys.stderr.write("unknown tier %r; known: %s\n" % (tier, ",".join(sorted(BPV))))
    sys.exit(2)

bpv = BPV[tier]
head_bpw = 6
draft_bpw = 4.0

weights = PARAMS_B * bpw / 8
head = VOCAB * HIDDEN * head_bpw / 8 / 1e9
vision = 0.35
kv = FULL_ATTN_LAYERS * KV_HEADS * HEAD_DIM * 2 * (bpv / 8) * CTX / 1e9
gdn = 1.22  # speculative recurrent history, one slot
draft = 2.0 * draft_bpw / 8 + 0.3
overhead = 1.5
total = weights + head + vision + kv + gdn + draft + overhead
print(
    "bpw=%s kv=%s (%.3f bpv): weights=%.1f head=%.2f kv=%.1f gdn=%.2f draft=%.2f total=%.1f / %.0f GB"
    % (bpw, tier, bpv, weights, head, kv, gdn, draft, total, CARD_GB)
)
sys.exit(0 if total < CARD_GB - 0.5 else 1)

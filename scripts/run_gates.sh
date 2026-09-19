#!/usr/bin/env bash
# Run the short eval set against an already-ready llama-server.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${BASE_URL:-http://127.0.0.1:8080}"
OUT="${OUT_DIR:-$ROOT/notes}"
mkdir -p "$OUT"
python3 "$ROOT/scripts/wait_ready.py" --base-url "$BASE"
python3 "$ROOT/scripts/vram_budget.py" 4.0 t3 | tee "$OUT/vram-t3.txt"
python3 "$ROOT/scripts/acceptance_check.py" --base-url "$BASE" --n "${N:-40}" \
  --json-out "$OUT/acceptance-dflash2.json"
echo "wrote $OUT/acceptance-dflash2.json"

#!/usr/bin/env bash
# Full GSM8K + optional NIAH campaign against a running llama-server.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${BASE_URL:-http://127.0.0.1:8080}"
OUT="${OUT_DIR:-$ROOT/notes}"
N="${N:-40}"
mkdir -p "$OUT"
python3 "$ROOT/scripts/wait_ready.py" --base-url "$BASE" --timeout "${WAIT_TIMEOUT:-3600}"
python3 "$ROOT/scripts/vram_budget.py" 4.0 t3 | tee "$OUT/vram-t3.txt"
python3 "$ROOT/scripts/acceptance_check.py" --base-url "$BASE" --n "$N" \
  --json-out "$OUT/acceptance-dflash2.json"
echo "acceptance -> $OUT/acceptance-dflash2.json"
if [ "${NIAH:-0}" = "1" ]; then
  python3 "$ROOT/scripts/niah_multikey.py" --base-url "$BASE" --variant 2n \
    --json-out "$OUT/niah-2n.json" || true
  python3 "$ROOT/scripts/niah_multikey.py" --base-url "$BASE" --variant 3n \
    --json-out "$OUT/niah-3n.json" || true
fi

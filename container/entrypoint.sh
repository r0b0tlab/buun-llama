#!/usr/bin/env bash
# Container entrypoint: llama-server with the selected recipe.
# First start downloads EXL3 weights into /models via -hf / -hfd when dirs are empty.
set -euo pipefail
export ROOT=/opt/buun-llama
export BIN="${BIN:-/usr/local/bin/llama-server}"
export MODELS="${MODELS:-/models}"
RECIPE_FILE="${RECIPE_FILE:-$ROOT/recipes/dflash2-max.env}"
if [ "${1:-}" != "" ] && [ -f "$ROOT/recipes/${1}.env" ]; then
  RECIPE_FILE="$ROOT/recipes/${1}.env"
  shift
fi
echo "[entrypoint] buun $(cat /opt/BUUN_SHA 2>/dev/null || echo unknown)" >&2
echo "[entrypoint] recipe $RECIPE_FILE" >&2
if [ "$#" -gt 0 ]; then
  exec "$BIN" "$@"
fi
exec bash "$ROOT/scripts/serve.sh" "$RECIPE_FILE"

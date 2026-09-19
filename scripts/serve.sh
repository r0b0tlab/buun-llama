#!/usr/bin/env bash
# Launch llama-server from a recipe env file.
# Usage: bash scripts/serve.sh recipes/dflash2-max.env
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT/recipes/PIN"
RECIPE_FILE="${1:-$ROOT/recipes/dflash2-max.env}"
# shellcheck disable=SC1090
source "$RECIPE_FILE"

BIN="${BIN:-}"
if [ -z "$BIN" ]; then
  if [ -x "$ROOT/build/bin/llama-server" ]; then
    BIN="$ROOT/build/bin/llama-server"
  else
    BIN="llama-server"
  fi
fi

MODELS="${MODELS:-$ROOT/models}"
TARGET_DIR="${TARGET_DIR:-$MODELS/qwen38-27b-exl3}"
DRAFT_DIR="${DRAFT_DIR:-$MODELS/dflash2-exl3}"

ARGS=(
  --host "${HOST:-0.0.0.0}"
  --port "${PORT:-8080}"
  --alias "${ALIAS:-qwen38-27b-buun}"
  -c "${CTX:-8192}"
  -np "${N_PARALLEL:-1}"
  -ub "${UBATCH:-512}"
  -ngl "${N_GPU_LAYERS:-99}"
)

if [ -f "${TARGET_DIR}/config.json" ]; then
  ARGS+=(-m "$TARGET_DIR")
else
  ARGS+=(-hf "$TARGET_HF")
fi

case "${RECIPE:-dflash2-max}" in
  ar)
    : # target only
    ;;
  mtp)
    : # embedded / auto MTP sidecar; EXTRA_ARGS already has --spec-type draft-mtp
    ;;
  *)
    if [ -f "${DRAFT_DIR}/config.json" ]; then
      ARGS+=(-md "$DRAFT_DIR" -ngld "${N_GPU_LAYERS_DRAFT:-99}")
    else
      ARGS+=(-hfd "$DRAFT_HF" -ngld "${N_GPU_LAYERS_DRAFT:-99}")
    fi
    ;;
esac

# shellcheck disable=SC2206
[ -n "${EXTRA_ARGS:-}" ] && ARGS+=(${EXTRA_ARGS})

echo "[serve] $BIN ${ARGS[*]}" >&2
exec "$BIN" "${ARGS[@]}"

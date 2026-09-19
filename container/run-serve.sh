#!/usr/bin/env bash
# GPU serve via nvidia-container-toolkit, or device binds if toolkit is missing.
set -euo pipefail
IMAGE="${IMAGE:-buun-llama:3090}"
NAME="${NAME:-buun-llama}"
MODELS="${MODELS:-$PWD/models}"
PORT="${PORT:-8080}"
RECIPE="${RECIPE:-dflash2-max}"

mkdir -p "$MODELS"
docker rm -f "$NAME" >/dev/null 2>&1 || true

GPU_ARGS=(--gpus all)
if ! docker info 2>/dev/null | grep -qi nvidia; then
  GPU_ARGS=(
    --device /dev/nvidia0 --device /dev/nvidiactl --device /dev/nvidia-uvm
  )
fi

exec docker run -d --name "$NAME" \
  "${GPU_ARGS[@]}" \
  -p "${PORT}:8080" \
  -v "$MODELS":/models \
  -e RECIPE_FILE="/opt/buun-llama/recipes/${RECIPE}.env" \
  "$IMAGE"

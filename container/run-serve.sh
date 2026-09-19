#!/usr/bin/env bash
# GPU serve via device binds (this host has no nvidia-container-toolkit).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IMAGE="${IMAGE:-buun-llama:3090}"
NAME="${NAME:-buun-llama}"
MODELS="${MODELS:-$ROOT/models}"
PORT="${PORT:-8888}"
RECIPE="${RECIPE:-dflash2-max}"

mkdir -p "$MODELS"
docker rm -f "$NAME" >/dev/null 2>&1 || true

DOCKER_ENV=(-e "RECIPE_FILE=/opt/buun-llama/recipes/${RECIPE}.env")
for k in GGML_DFLASH2_BLOCK_SIZE_OVERRIDE GGML_DFLASH_DRAFT_ADAPTIVE GGML_DFLASH2_TARGET_MMQ GGML_DFLASH2_FUSED_CONV; do
  if [ -n "${!k:-}" ]; then
    DOCKER_ENV+=(-e "$k=${!k}")
  fi
done

exec docker run -d --name "$NAME" \
  --device /dev/nvidia0 --device /dev/nvidiactl --device /dev/nvidia-uvm \
  -v /usr/lib/x86_64-linux-gnu/libcuda.so.1:/usr/lib/x86_64-linux-gnu/libcuda.so.1:ro \
  -v /usr/lib/x86_64-linux-gnu/libnvidia-ml.so.1:/usr/lib/x86_64-linux-gnu/libnvidia-ml.so.1:ro \
  -p "${PORT}:8080" \
  -v "$MODELS":/models:ro \
  -v "$ROOT/recipes:/opt/buun-llama/recipes:ro" \
  "${DOCKER_ENV[@]}" \
  "$IMAGE"

#!/usr/bin/env bash
# Tag and push the local image to GHCR. Repo must exist; package visibility is separate.
set -euo pipefail
IMAGE="${IMAGE:-buun-llama:3090}"
DEST="${DEST:-ghcr.io/r0b0tlab/buun-llama:3090}"
docker image inspect "$IMAGE" >/dev/null
docker tag "$IMAGE" "$DEST"
docker tag "$IMAGE" ghcr.io/r0b0tlab/buun-llama:latest
echo "$DEST"

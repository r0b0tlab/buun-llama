Runtime image for spiritbuun/buun-llama-cpp on RTX 3090 (sm_86, CUDA 13).

Build from the package root:

  docker build -t buun-llama:3090 -f container/Dockerfile .

Serve:

  bash container/run-serve.sh

OpenAI-compatible endpoint at http://127.0.0.1:8080. Recipe selection:

  RECIPE=dflash2-262k bash container/run-serve.sh

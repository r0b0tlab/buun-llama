# Environment

- GPU: RTX 3090 24 GB, sm_86
- Container CUDA: 13.0.0 Ubuntu 24.04
- Engine: spiritbuun/buun-llama-cpp @ 1d0f493c73817176f6953069b7c10211de9555a1
- CMake: GGML_CUDA=ON, GGML_CUDA_FA=ON, GGML_CUDA_FA_ALL_QUANTS=ON, CMAKE_CUDA_ARCHITECTURES=86
- Weights: r0b0tlab/Qwen3.8-27B-EXL3-4.00bpw , r0b0tlab/Qwen3.8-27B-DFlash2-EXL3-4.00bpw
- Host serve binary: set BIN to build/bin/llama-server or rely on PATH

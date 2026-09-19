# syntax=docker/dockerfile:1
# buun-llama-cpp CUDA runtime for Qwen3.8-27B EXL3 + DFlash2 on RTX 3090 (sm_86).
#
# Build:
#   docker build -t buun-llama:3090 -f container/Dockerfile .
#
# Click-run (downloads EXL3 dirs into the volume on first start):
#   docker run --gpus all -p 8080:8080 -v buun-models:/models \
#     ghcr.io/r0b0tlab/buun-llama:3090

ARG CUDA_VERSION=13.0.0
ARG UBUNTU_VERSION=24.04
ARG BUUN_REPO=https://github.com/spiritbuun/buun-llama-cpp
ARG BUUN_SHA=1d0f493c73817176f6953069b7c10211de9555a1
ARG CUDA_ARCH=86

FROM nvidia/cuda:${CUDA_VERSION}-devel-ubuntu${UBUNTU_VERSION} AS build
ARG BUUN_REPO
ARG BUUN_SHA
ARG CUDA_ARCH

ENV DEBIAN_FRONTEND=noninteractive \
    LIBRARY_PATH=/usr/local/cuda/lib64/stubs

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git ca-certificates cmake ninja-build \
        gcc g++ python3 \
        libssl-dev libcurl4-openssl-dev libgomp1 curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
RUN git clone --filter=blob:none "$BUUN_REPO" buun \
    && git -C buun fetch --depth 1 origin "$BUUN_SHA" \
    && git -C buun checkout --detach "$BUUN_SHA"

WORKDIR /src/buun
RUN cmake -B build -G Ninja \
        -DCMAKE_BUILD_TYPE=Release \
        -DGGML_CUDA=ON \
        -DGGML_NATIVE=OFF \
        -DGGML_CUDA_FA=ON \
        -DGGML_CUDA_FA_ALL_QUANTS=ON \
        -DGGML_CUDA_NCCL=OFF \
        -DCMAKE_CUDA_ARCHITECTURES=${CUDA_ARCH} \
        -DLLAMA_BUILD_TESTS=OFF \
        -DLLAMA_BUILD_SERVER=ON \
        -DLLAMA_CURL=ON \
        -DCMAKE_LIBRARY_PATH=/usr/local/cuda/lib64/stubs \
        -DCMAKE_EXE_LINKER_FLAGS="-Wl,--allow-shlib-undefined" \
        -DCMAKE_SHARED_LINKER_FLAGS="-Wl,--allow-shlib-undefined"
RUN cmake --build build -j"$(nproc)" --target llama-server \
    && mkdir -p /out/bin /out/lib \
    && cp build/bin/llama-server /out/bin/ \
    && find build -name 'libggml*.so*' -exec cp -P {} /out/lib/ \; \
    && find build -name 'libllama*.so*' -exec cp -P {} /out/lib/ \; \
    && git -C /src/buun rev-parse HEAD > /out/BUUN_SHA

FROM nvidia/cuda:${CUDA_VERSION}-runtime-ubuntu${UBUNTU_VERSION} AS runtime
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates libgomp1 libssl3 libcurl4 curl python3 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /out/bin/ /usr/local/bin/
COPY --from=build /out/lib/ /usr/local/lib/
COPY --from=build /out/BUUN_SHA /opt/BUUN_SHA
COPY recipes /opt/buun-llama/recipes
COPY scripts /opt/buun-llama/scripts
COPY eval /opt/buun-llama/eval
COPY container/entrypoint.sh /opt/entrypoint.sh
RUN ldconfig \
    && chmod +x /opt/entrypoint.sh /opt/buun-llama/scripts/*.sh /opt/buun-llama/scripts/*.py \
    && useradd --create-home --uid 10001 runner \
    && mkdir -p /models \
    && chown runner:runner /models
USER runner
ENV PATH="/usr/local/bin:${PATH}" \
    LLAMA_CACHE=/models/.llama-cache \
    HF_HOME=/models/.hf-cache \
    MODELS=/models \
    RECIPE_FILE=/opt/buun-llama/recipes/dflash2-max.env \
    BIN=/usr/local/bin/llama-server

EXPOSE 8080
ENTRYPOINT ["/opt/entrypoint.sh"]

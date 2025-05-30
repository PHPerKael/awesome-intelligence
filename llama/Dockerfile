FROM docker.m.daocloud.io/library/python:3.10.17-slim AS builder

RUN rm -f /etc/apt/sources.list.d/* && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian bookworm main contrib non-free" > /etc/apt/sources.list && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian bookworm-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian-security bookworm-security main contrib non-free" >> /etc/apt/sources.list

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential cmake clang git curl libcurl4-openssl-dev libomp-dev llvm && \
    apt-get clean

# compile llama.cpp（MacOS enable Metal）
COPY deps/llama.cpp /app/llama.cpp
WORKDIR /app/llama.cpp

RUN rm -rf build && mkdir build && \
    cmake -B build \
    -DCMAKE_BUILD_TYPE=Debug \
    -DCMAKE_C_COMPILER=clang \
    -DCMAKE_CXX_COMPILER=clang++ \
    -DCMAKE_INSTALL_PREFIX=/usr/local && \
    cmake --build build -j$(nproc) && \
    cmake --install build && \
    rm -rf /tmp/* /app/llama.cpp

# 1
# WORKDIR /app

# FROM docker.m.daocloud.io/library/python:3.10.17-slim
# COPY --from=builder /app/llama.cpp/build/bin/libllama.so /app/libllama.so
# COPY --from=builder /app/llama.cpp/build/bin/llama-server /app/llama-server

# 2 
# WORKDIR /app
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends libcurl4 && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*
# CMD ["/app/llama.cpp/build/bin/llama-server"]
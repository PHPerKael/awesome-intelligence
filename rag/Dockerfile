FROM docker.m.daocloud.io/library/python:3.10.17-slim AS builder

WORKDIR /app
RUN rm -f /etc/apt/sources.list.d/* && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian bookworm main contrib non-free" > /etc/apt/sources.list && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian bookworm-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian-security bookworm-security main contrib non-free" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends build-essential

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --no-cache-dir langchain langchain-core langchain-community langchain-huggingface langchain-chroma sentence-transformers fastapi pydantic chromadb torch requests python-multipart \
    aiofiles sqlmodel pdfminer.six openai

RUN apt-get purge -y build-essential && \
    apt-get autoremove -y build-essential && \
    apt-get clean && \
    rm -rf /tmp/*

# COPY rag.py /app/rag.py
# CMD ["python", "rag.py"]
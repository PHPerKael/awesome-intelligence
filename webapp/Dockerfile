FROM docker.m.daocloud.io/library/python:3.10.17-alpine AS builder

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --no-cache-dir gradio filetype && \
    rm -rf /tmp/*

WORKDIR /app
# COPY app.py /app/app.py
# CMD ["python", "app.py"]
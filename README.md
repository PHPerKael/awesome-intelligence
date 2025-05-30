# Awesome Intelligence

## 🇨🇳 项目简介（中文）

这是一个个人学习项目，旨在探索 **大语言模型（LLM）与 RAG（Retrieval-Augmented Generation）结合**的应用实践。

### 🌟 项目特点

- ✅ 默认使用 Qwen3-7B 模型（可替换为其他支持 llama.cpp 的模型）
- 📄 投喂给 RAG 的文档存储在 `.data/.feeds` 目录中
- 🔎 向量数据库采用 **Chroma**，轻量、易用
- 🗃️ 文档关系数据通过 **SQLite 数据库** 管理
- 🧠 大模型通过 **llama.cpp** 启动，建议使用如下配置：
  - 硬件：MacBook Pro M3 Pro + macOS + Metal GPU（16GB 显存）
  - 模型文件：`Qwen3-8B-Q4_K_M.gguf`（存储在 `.data/.models` 中）
  - ⚠️ 注意：Metal GPU 不支持虚拟化直通
- 🧩 文档解析、向量生成模块基于**策略 / 插件模式**，可灵活扩展文档类型
  - 当前支持文档类型：`PDF`
- 💡 嵌入（Embedding）生成需对接国产大模型厂商 API，自行申请使用（LangChain 支持不足）
- 📦 `RAG` 和 `WebApp` 可通过 Docker 打包运行
- 🧠 多模态能力预期未来支持（图文、语音等）
- ⚙️ 服务环境变量配置文件：
  - `llama.yaml`（大模型）
  - `rag.yaml`（RAG 服务）
  - `webapp.yaml`（前端）

### 📌 项目地址

👉 [https://github.com/PHPerKael/awesome-intelligence](https://github.com/PHPerKael/awesome-intelligence)

---

## 🇺🇸 Project Overview (English)

This is a personal learning project focused on exploring the integration of **Large Language Models (LLM)** and **Retrieval-Augmented Generation (RAG)**.

### 🌟 Features

- ✅ Default model: **Qwen3-7B**, easily replaceable with other models supported by `llama.cpp`
- 📄 Documents used for RAG are stored in `.data/.feeds`
- 🔎 Uses **Chroma** as the vector database for its simplicity and efficiency
- 🗃️ Document metadata and relationships are managed via a **SQLite database**
- 🧠 LLM runs through **llama.cpp**, optimized for the following setup:
  - Hardware: MacBook Pro M3 Pro + macOS + Metal GPU (16GB)
  - Model file: `Qwen3-8B-Q4_K_M.gguf` (stored in `.data/.models`)
  - ⚠️ Note: Metal GPU **does not support virtualization passthrough**
- 🧩 Document parsing and vector generation follow a **strategy/plugin design**, making it easy to extend support to more document types
  - Currently supported type: `PDF`
- 💡 Embedding generation must be implemented manually by calling third-party APIs (due to limited support in LangChain for Chinese LLMs)
- 📦 Docker packaging is available for both `RAG` and `WebApp` components
- 🧠 Multimodal capability (e.g., images, audio) is planned for future support
- ⚙️ Configuration files for different services:
  - `llama.yaml` – LLM configuration
  - `rag.yaml` – RAG service config
  - `webapp.yaml` – Frontend/web app config

### 📌 Repository

👉 [https://github.com/PHPerKael/awesome-intelligence](https://github.com/PHPerKael/awesome-intelligence)

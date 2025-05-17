import os
from langchain_core.embeddings import Embeddings
from core.vector.embeddings.qwen import QwenEmbeddings

def get_embeddings() -> Embeddings:
    model = os.getenv("EMBEDDINGS_MODEL")
    if model == "QWen":
        return QwenEmbeddings()
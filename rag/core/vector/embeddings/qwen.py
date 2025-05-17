import os
import logging
import pprint
from openai import OpenAI
from typing import Any
from langchain_core.embeddings import Embeddings

logger = logging.getLogger(__name__)
DASH_SCOPE_EMBEDDINGS_MODEL = os.getenv("DASH_SCOPE_EMBEDDINGS_MODEL")
EMBEDDING_DIMENSION = os.getenv("EMBEDDING_DIMENSION")

class QwenEmbeddings(Embeddings):
    
    """Qwen embedding models.
    To use, you should have the ``sentence_transformers`` python package installed.

    Demo:
        https://help.aliyun.com/zh/model-studio/text-embedding-synchronous-api?spm=a2c4g.11186623.0.0.17f23e8fw8gd74
    """
    
    def __init__(self, **kwargs: Any):
        """Initialize the Dashscope Client."""
        
        super().__init__(**kwargs)

        self.client = OpenAI(
            api_key=os.getenv("DASH_SCOPE_API_KEY"),  # 如果您没有配置环境变量，请在此处用您的API Key进行替换
            base_url=os.getenv("DASH_SCOPE_BASE_URL"),  # 百炼服务的base_url
        )
        
    def _embed(
        self, texts: list[str]
    ) -> list[list[float]]:
        """
        Embed a text using the HuggingFace transformer model.

        Args:
            texts: The list of texts to embed.
            encode_kwargs: Keyword arguments to pass when calling the
                `encode` method for the documents of the SentenceTransformer
                 encode method.

        Returns:
            List of embeddings, one for each text.
        """
        completion = self.client.embeddings.create(
            model=DASH_SCOPE_EMBEDDINGS_MODEL,
            input=texts,
            dimensions=EMBEDDING_DIMENSION,
            encoding_format="float"
        )
        vectors = []
        for val in completion.data:
            vectors.append(val.embedding)
        return vectors
        
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Compute doc embeddings using a Qwen DashScope Client.

        Args:
            texts: The list of texts to embed.

        Returns:
            List of embeddings, one for each text.
        """
        self._embed(texts)
            
    def embed_query(self, text: str) -> list[float]:
        """Compute query embeddings using a Qwen DashScope Client.

        Args:
            text: The text to embed.

        Returns:
            Embeddings for the text.
        """
        return self._embed([text])[0]
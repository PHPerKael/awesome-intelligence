import logging
import pprint
from typing import List, Union
from pathlib import Path
from core.vector.loader import PluginManager
from core.vector.storage.db import VectorDatabase
from core.vector.embeddings.embedding import get_embeddings
from dao.sqlite.document import Document as DaoDocument
from langchain_core.embeddings import Embeddings
from langchain_core.documents.base import Document as LangchainDocument
from chromadb.api.types import GetResult, QueryResult

logger = logging.getLogger(__name__)

class VectorAnalyzer:
    
    def __init__(self):
        self.plugin_manager = PluginManager()
        self.embedding = get_embeddings()
        self.vector_db = VectorDatabase(self.embedding)
        
    def process_files(self, docs: List[DaoDocument]) -> int:
        try:
            for doc in docs:
                plugin = self.plugin_manager.get_plugin(doc, self.embedding)
                full_path = Path(doc.dest_dir).joinpath(doc.doc_name)
                doc_content, vector = plugin.document_to_vector(full_path.as_posix())
                self.vector_db.save(
                    doc=doc,
                    vector=vector,
                    doc_content=doc_content
                )

            return 0
        except Exception as e:
            logger.error(f"process file error: {str(e)}")
            return 1

    def get_vectors(self, doc_hash: Union[str, List[str]]) -> GetResult:
        return self.vector_db.collection.get(ids=doc_hash, include=["metadatas", "uris", "embeddings", "documents"])
        
    def search_similarity(self, text: str) -> QueryResult:
        return self.vector_db.find_similar(text=text)
            
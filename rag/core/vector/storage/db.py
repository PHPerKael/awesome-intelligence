import os
import logging
import pprint
from pathlib import Path
from typing import List
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
import chromadb
from chromadb.api.types import QueryResult
from dao.sqlite.document import Document as DaoDocument

RAG_VECTOR_STORAGE_TYPE = os.getenv("RAG_VECTOR_STORAGE_TYPE")
RAG_VECTOR_DIR = os.getenv("RAG_VECTOR_DIR")
RAG_CHROMA_DB = os.getenv("RAG_CHROMA_DB")
chroma_db_path = Path(RAG_VECTOR_DIR).resolve().joinpath(RAG_CHROMA_DB)

RAR_CHROMA_DB_COLLECTION_NAME = os.getenv("RAR_CHROMA_DB_COLLECTION_NAME")
RAG_CHROMA_DB_DOCUMENTS_NUMBER_RETURN = int(os.getenv("RAG_CHROMA_DB_DOCUMENTS_NUMBER_RETURN"))

logger = logging.getLogger(__name__)

class VectorDatabase:
    def __init__(self, embeddings: Embeddings):
        if RAG_VECTOR_STORAGE_TYPE == "Chroma":
            persistent_client = chromadb.PersistentClient()
            self.collection = persistent_client.get_or_create_collection(name=RAR_CHROMA_DB_COLLECTION_NAME)
            self.database = Chroma(
                collection_name=RAR_CHROMA_DB_COLLECTION_NAME,
                embedding_function=embeddings,
                persist_directory=chroma_db_path.as_posix(),  # Where to save data locally, remove if not necessary
            )
            self.embeddings = embeddings

    def save(self, doc: DaoDocument, vector: list[float], doc_content: str):
        try:
            result = self.collection.get(doc.doc_hash)
            if result and result.get("ids"):
                # Update vectors to the collection
                self.collection.update(
                    ids=[doc.doc_hash],
                    metadatas={
                        "doc_name": doc.doc_name,
                        "posix": doc.full_path().as_posix()
                    },
                    embeddings=[vector],
                    documents=[doc_content],
                    uris=[doc.full_path().as_uri()]
                )
                logger.info(f"update document: {doc}")
            else:
                # Add vectors to the collection
                self.collection.add(
                    ids=[doc.doc_hash],
                    metadatas=[{
                        "doc_name": doc.doc_name,
                        "posix": doc.full_path().as_posix()
                    }],
                    embeddings=[vector],
                    documents=[doc_content],
                    uris=[doc.full_path().as_uri()]
                )
                logger.info(f"add document: {doc}")
        except Exception as e:
            logger.error(f"save error: {str(e)}")
        
    def find_similar(self, text: str) -> QueryResult:
        vectors = self.embeddings.embed_query(text=text)
        return self.collection.query(
            query_embeddings=vectors,
            query_texts=text,
            include=["metadatas", "uris", "embeddings", "documents"])
        
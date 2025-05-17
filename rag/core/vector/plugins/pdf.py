import logging
import pprint
from typing import List, Union
from core.vector.plugins.interface import FileAnalyzerPlugin
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PDFMinerLoader
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

class PDFAnalyzer(FileAnalyzerPlugin):
    def __init__(self, embeddings: Embeddings):
        self.embeddings = embeddings
        
    def supported_formats(cls) -> List[str]:
        return ["pdf"]

    def detect_format(cls, file_header: bytes) -> bool:
        return file_header.startswith(b"%PDF-")

    def document_to_vector(self, file_path: str) -> tuple[str, list[float]]:
        loader = PDFMinerLoader(
            file_path=file_path,
            mode="single",
        )
        doc = loader.load()
        if not doc or not doc[0].page_content:
            return None, []
            
        # return doc_contents, self.embeddings.embed_documents(doc_contents)
        # return doc[0].page_content, self.embeddings.embed_query(doc[0].page_content)
        vectors = self.embeddings.embed_query(doc[0].page_content)
        return doc[0].page_content, vectors
    
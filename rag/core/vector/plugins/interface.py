from abc import ABC, abstractmethod
from typing import List, Union
from langchain_core.embeddings import Embeddings

class FileAnalyzerPlugin(ABC):
    def __init__(self, embeddings: Embeddings):
        self.embeddings = embeddings
        
    @abstractmethod
    def supported_formats(cls) -> List[str]:
        """支持的文件扩展名列表"""
        pass

    @abstractmethod
    def detect_format(cls, file_header: bytes) -> bool:
        """通过文件头检测是否支持此格式"""
        pass

    @abstractmethod
    def document_to_vector(self, file_path: str) -> tuple[str, list[float]]:
        """文件处理主逻辑"""
        pass


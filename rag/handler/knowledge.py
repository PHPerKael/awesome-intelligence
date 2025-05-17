import logging
import pprint
import numpy as np
from typing import Union, List, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from core.vector.base import VectorAnalyzer
from core.knowledge.knowledge import retrieval_and_ask
from handler.response import format_json_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/knowledge", tags=["本地知识查询"])

@router.get("/doc-vector", summary="获取文档向量")
async def doc_vector(
    doc_hashes: Union[str, List[str]] = Query(
        default=None,
        description="文档ID"
    )
):
    if not doc_hashes:
        return format_json_response(code=1, msg="input document hash")
    analyzer = VectorAnalyzer()
    get_results = analyzer.get_vectors(doc_hashes)
    details = []
    for doc_hash, doc_md, doc_content, embeddings, uri in zip(
        get_results["ids"], get_results["metadatas"], get_results["documents"], get_results["embeddings"], get_results["uris"]
    ):
        arr = np.array(embeddings)
        vectors = arr.tolist()
        details.append({
            "doc_hash": doc_hash,
            "metadata": doc_md,
            "doc_content": doc_content,
            "vector": vectors,
            "uri": uri,
        })
    return format_json_response(code=0, msg=details)

@router.get("/similarity", summary="搜索相似文档")
async def search_similarity(
    text: str = Query(
        default="",
        description="文本内容"
    )
):
    if not text:
        return format_json_response(code=1, msg="input some text")
    
    analyzer = VectorAnalyzer()
    query_results = analyzer.search_similarity(text)
    details = []
    for doc_hash, doc_md, doc_content, embeddings, uri in zip(
        query_results["ids"][0], query_results["metadatas"][0], query_results["documents"][0], query_results["embeddings"][0], query_results["uris"][0]
    ):
        
        arr = np.array(embeddings)
        vectors = arr.tolist()
        details.append({
            "doc_hash": doc_hash,
            "metadata": doc_md,
            "doc_content": doc_content,
            "vector": vectors,
            "uri": uri,
        })
    return format_json_response(code=0, msg=details)

class ChatRequest(BaseModel):
    question: str
    contexts: Optional[List[dict[str, str]]] = None
    
@router.post("/chat", summary="提问")
async def chat_with_hint(req: ChatRequest):
    """提问"""
    if not req.question:
        return format_json_response(code=1, msg="input your question")
    
    if not req.contexts:
        req.contexts = []
    
    answer = retrieval_and_ask(question=req.question, contexts=req.contexts)
    return format_json_response(msg=answer)

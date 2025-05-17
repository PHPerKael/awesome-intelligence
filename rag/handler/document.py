import logging
from fastapi import APIRouter, UploadFile, File, Query, Body
from pydantic import BaseModel, Field
from typing import List, Union
from core.doc.document import process_document, list_document, parse_documents
from handler.response import format_json_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/document", tags=["文档管理"])

@router.post("/upload", summary="批量上传文档")
async def upload_document(files: List[UploadFile] = File(..., description="支持多选文件上传")):
    """处理多个文档上传"""
    results = []
    success_count = 0
    fail_docs = []
    for f in files:
        ret = await process_document(f)
        if ret:
            results.append({
                "doc_name": f.filename,
                "doc_hash": ret,
            })
            success_count += 1
        else:
            fail_docs.append(f.filename)
    
    return format_json_response(msg={
        "details": results,
        "total": len(files),
        "success": success_count,
        "fail": len(files) - success_count,
        "fail_docs": fail_docs,
    })


@router.get("/list", summary="列出所有文档")
async def document_list(
    page: int = Query(
        default=1, 
        ge=1, 
        description="页码(从1开始)"
    ),
    page_count: int = Query(
        default=10,
        ge=1,
        le=100,
        description="每页数量(1-100)"
    )
):
    """获取文档列表"""
    try:
        total, doc_list = list_document(page, page_count)
        return format_json_response(msg={
            "documents": doc_list,
            "total": total,
            "page": page,
            "page_count": page_count,
        })
    except Exception as e:
        logger.error(f"list documents error: {str(e)}")
    finally:
        return format_json_response(code=1, msg={
            "documents": doc_list,
            "total": total,
            "page": page,
            "page_count": page_count,
        })

@router.post("/parse", summary="分析文档")
async def document_parse(
    doc_id: Union[int, List[int], None],
    doc_hash: Union[str, List[str], None]
):
    """分析文档"""
    ret = parse_documents(doc_id, doc_hash)
    if ret:
        return format_json_response(code=1, msg="parse document error")
    
    return format_json_response(msg="parse document success")

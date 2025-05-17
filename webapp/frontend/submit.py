import os
import gradio as gr
import logging
import filetype
from pathlib import Path
import requests

logger = logging.getLogger(__name__)

RAG_ENDPOINT = os.getenv("RAG_ENDPOINT")
RAG_DOCUMENTS_API_PREFIX = os.getenv("RAG_DOCUMENTS_API_PREFIX")

ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'text/plain'
}


def ask_rag(files_upload: gr.File, question: str) -> str:
    """全流程处理函数"""
    try:
        file_list = []
        for file in files_upload:
            base_name = Path(file).name
            with open(file, 'rb') as f:
                file_list.append(
                    ('files', (base_name, f.read(), get_mime_type(file)))
                )
        upload_resp = requests.post(
            url=f"{RAG_ENDPOINT}/{RAG_DOCUMENTS_API_PREFIX}/upload",
            files=file_list,
        )

    except Exception as e:
        logger.error(f"rag upload document error: {str(e)}")
        raise

def get_mime_type(file_path: str) -> str:
    kind = filetype.guess(file_path)
    return kind.mime if kind else "application/octet-stream"

def validate_file(file_path: Path):
    # 扩展名白名单验证
    if file_path.suffix.lower() not in {".txt",".md",".pdf",".docx",".pptx",".xlsx",".md",".json",".csv",".mp3",".wav",".png",".jpg"}:
        raise ValueError("文件扩展名不合法")
    
    detected_type = get_mime_type(file_path)
    if detected_type not in ALLOWED_MIME_TYPES:
        raise ValueError(f"检测到非法文件类型: {detected_type}")
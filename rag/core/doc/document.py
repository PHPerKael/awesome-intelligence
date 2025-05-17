import os
import logging
import aiofiles
from datetime import datetime
from pathlib import Path
from fastapi import UploadFile
from typing import Union, List
from dao.sqlite.document import save_doc, list_doc, count_doc, get_docs, Document
from utils.files import get_file_hash, validate_upload_file, check_file_size
from core.vector.base import VectorAnalyzer

RAG_FEEDS_DIR = os.getenv("RAG_FEEDS_DIR")

logger = logging.getLogger(__name__)

async def process_document(file: UploadFile) -> str:
    try:
        validate_upload_file(file)
        
        check_file_size(file)
        
        date = datetime.now().strftime("%Y-%m-%d")
        dest_dir = Path(RAG_FEEDS_DIR).resolve().joinpath(date)
        dest_path = Path(dest_dir).resolve().joinpath(file.filename)
        await safe_write(
            dest_dir,
            file
        )

        doc_hash = get_file_hash(dest_path)
        save_doc(Document(
            dest_dir=str(dest_dir),
            doc_name=file.filename,
            doc_hash=doc_hash,
            doc_size=file.size,
        ))
        return doc_hash
    except Exception as e:
        logger.error(f"document process error: {str(e)}")
        raise

async def safe_write(dest_dir: str, file: UploadFile) -> int:
    Path(dest_dir).mkdir(mode=0o755, parents=True, exist_ok=True)
    dest_path = Path(dest_dir).resolve().joinpath(file.filename)
    async with aiofiles.open(dest_path, "wb") as buffer:
        content = await file.read()
        await buffer.write(content)
        return len(content)
    
def list_document(page: int, page_count: int) -> tuple:
    total = count_doc()
    if total <= (page - 1) * page_count:
        return total, []
    
    doc_list = list_doc(page, page_count)
    new_doc_list = []
    for doc in doc_list:
        new_doc_list.append({
            "doc_id": doc.id,
            "doc_name": doc.doc_name,
            "dest_dir": doc.dest_dir,
            "doc_hash": doc.doc_hash,
            "doc_size": doc.doc_size,
            "create_time": doc.create_time.strftime("%Y-%m-%d %H:%M:%S"),
        })

    return total, new_doc_list

def parse_documents(doc_ids: Union[int, List[int], None] = None, doc_hashes: Union[str, List[str], None] = None) -> int:
    if not doc_ids and not doc_hashes:
        return None, 1
    
    try:
        docs = get_docs(doc_ids, doc_hashes)
   
        for doc in docs:
            dest_path = Path(doc.dest_dir).resolve().joinpath(doc.doc_name)
            if not dest_path.exists():
                raise FileNotFoundError(f"document not found: {doc.doc_name}")
        analyzer = VectorAnalyzer()
        return analyzer.process_files(docs)
    
    except Exception as e:
        logging.error(f"vecotr analyze failed: {str(e)}")
        raise
    
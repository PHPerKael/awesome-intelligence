import logging
from datetime import datetime
from sqlmodel import SQLModel, Field, Session, select, func, col
from typing import Sequence, Union, List
from dao.sqlite.database import engine
from pathlib import Path

logger = logging.getLogger(__name__)

# 数据模型
class Document(SQLModel, table=True):
    id: int | None = Field(primary_key=True)
    dest_dir: str = Field(max_length=1024)
    doc_name: str = Field(max_length=255)
    doc_hash: str = Field(unique=True, max_length=64)
    doc_size: int = Field(default=0)
    create_time: datetime = Field(default_factory=datetime.now)
    
    def full_path(self) -> Path:
        return Path(self.dest_dir).joinpath(self.doc_name)

def count_doc() -> int:
    with Session(engine) as session:
        # 同步执行查询
        result = session.exec(
            select(func.count(Document.id))
        ).first()
        return result if result is not None else 0
    
def get_docs(
    doc_ids: Union[int, List[int], None] = None,
    doc_hashes: Union[str, List[str], None] = None
) -> List[Document]:
    """支持单值或列表查询，返回匹配的文档列表"""
    with Session(engine) as session:
        
        if doc_ids:
            ids = [doc_ids] if isinstance(doc_ids, int) else doc_ids
            where_clause = col(Document.id).in_(ids)
        elif doc_hashes:
            hashes = [doc_hashes] if isinstance(doc_hashes, str) else doc_hashes
            where_clause = col(Document.doc_hash).in_(hashes)
            
        result = session.exec(
            select(Document).where(where_clause)
        ).all()
        
        return result
    
def list_doc(page: int, page_count: int) -> Sequence[Document]:
    with Session(engine) as session:
        return session.exec(select(Document).offset((page - 1) * page_count).limit(page_count)).fetchall()

def save_doc(doc: Document):
    with Session(engine) as session:
        if not session.exec(select(Document).where(Document.doc_hash == doc.doc_hash)).first():
            session.add(doc)
            session.commit()
            logger.info(f"文档保存成功: {doc.doc_name}")

import os
from pathlib import Path
from sqlmodel import create_engine, SQLModel

# 配置数据库
RAG_SQLITE_DIR = os.getenv("RAG_SQLITE_DIR")
Path(RAG_SQLITE_DIR).mkdir(parents=True, exist_ok=True)
SQLITE_METADATA_DB = os.getenv("SQLITE_METADATA_DB")

sqlite_url = f"sqlite:///{Path(RAG_SQLITE_DIR)/SQLITE_METADATA_DB}"
engine = create_engine(sqlite_url, echo=True, connect_args={"check_same_thread": False})

# 初始化数据库
def create_db_and_tables():
    """自动创建所有注册的模型表"""
    SQLModel.metadata.create_all(engine)
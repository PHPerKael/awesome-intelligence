import os
from fastapi import FastAPI
from pathlib import Path
import logging
from dao.sqlite.database import create_db_and_tables

def init_config():
    """全局日志初始化函数"""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)

    create_db_and_tables()
    
    RAG_VECTOR_DIR = os.getenv("RAG_VECTOR_DIR")
    Path(RAG_VECTOR_DIR).mkdir(mode=0o755, parents=True, exist_ok=True)

if __name__ == "__main__":
    init_config()
    
    import uvicorn
    from handler.document import router as document_router
    from handler.knowledge import router as knowledge_router
    app = FastAPI(title="RAG 服务")
    # 注册子路由
    app.include_router(document_router)
    app.include_router(knowledge_router)
    uvicorn.run(app, host="0.0.0.0", port=8001)
    

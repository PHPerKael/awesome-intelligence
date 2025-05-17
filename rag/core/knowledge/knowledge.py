import os
import logging
import pprint
import json
import requests
from typing import Dict, List
from core.vector.base import VectorAnalyzer
from chromadb.api.types import QueryResult
from pydantic import BaseModel, Field
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

LLM_SERVER_BASE_URL = os.getenv("LLM_SERVER_BASE_URL")
LLM_CHAT_ENDPOINT = os.getenv("LLM_CHAT_ENDPOINT")

def retrieval_and_ask(question: str, contexts: list[dict[str, str]]) -> str:
    analyzer = VectorAnalyzer()
    query_results = analyzer.search_similarity(question)
    # pprint.pp(f"query_results: {query_results}")
    
    chat_payload = generate_chat_payload(query_results=query_results, question=question, contexts=contexts)
    chat_resp = requests.post(
        url=urljoin(LLM_SERVER_BASE_URL, LLM_CHAT_ENDPOINT),
        json=chat_payload,
        stream=True,
    )

    # 用于拼接最终输出
    full_content = ""

    for line in chat_resp.iter_lines():
        if not line:
            continue
        line = line.decode("utf-8")

        # 跳过控制信息，比如 [DONE] 或空段
        if line.strip() == "" or line.strip() == "data: [DONE]":
            continue

        # 解析 JSON 内容
        if line.startswith("data: "):
            line = line[len("data: "):]

        try:
            chunk = json.loads(line)
            delta = chunk.get("choices", [{}])[0].get("delta", {})
            content = delta.get("content")
            if content:
                print(content, end="", flush=True)  # 实时输出
                full_content += content
        except json.JSONDecodeError as e:
            print(f"Invalid JSON line: {e}")
            
    return full_content
    
def generate_chat_payload(query_results: QueryResult, question: str, contexts: List[dict[str, str]]) -> Dict:
    hints = ""
    index = 1
    for doc_content in zip(
        query_results["documents"][0]
    ):
        hints = f"{hints}{index}. {doc_content}\n"
    
    hint_question = question
    if hints:
        hint_question = f"以下是相关资料：\n{hints}\n\n请根据上述内容回答问题: {question}"
        
    contexts.append({
        "role": "user",
        "content": hint_question
    })
    
    return {
        "messages": contexts,
        "stream": True,
        "cache_prompt": True,
        "samplers": "edkypmxt",
        "temperature": 0.8,
        "dynatemp_range": 0,
        "dynatemp_exponent": 1,
        "top_k": 40,
        "top_p": 0.95,
        "min_p": 0.05,
        "typical_p": 1,
        "xtc_probability": 0,
        "xtc_threshold": 0.1,
        "repeat_last_n": 64,
        "repeat_penalty": 1,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "dry_multiplier": 0,
        "dry_base": 1.75,
        "dry_allowed_length": 2,
        "dry_penalty_last_n": -1,
        "max_tokens": -1,
        "timings_per_token": False
    }
  
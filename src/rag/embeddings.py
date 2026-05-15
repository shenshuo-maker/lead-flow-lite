"""本地向量模型（无需单独申请嵌入 API）。"""
from functools import lru_cache

from langchain_community.embeddings import HuggingFaceEmbeddings

from src.config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

"""Chroma 持久化向量库封装。"""
from pathlib import Path
from typing import List, Optional

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from src.config import CHROMA_DIR, COLLECTION_NAME
from src.rag.embeddings import get_embeddings


def _persist_path() -> str:
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    return str(CHROMA_DIR)


def load_vectorstore() -> Chroma:
    return Chroma(
        persist_directory=_persist_path(),
        embedding_function=get_embeddings(),
        collection_name=COLLECTION_NAME,
    )


def list_sources() -> List[str]:
    vs = load_vectorstore()
    col = vs._collection  # noqa: SLF001 — Chroma 官方用法
    data = col.get(include=["metadatas"])
    metas = data.get("metadatas") or []
    names: set[str] = set()
    for m in metas:
        if m and isinstance(m, dict):
            s = m.get("source")
            if s:
                names.add(Path(str(s)).name)
    return sorted(names)


def similarity_search(
    query: str,
    k: int = 6,
    source_filter: Optional[str] = None,
) -> List[Document]:
    vs = load_vectorstore()
    if source_filter:
        fname = Path(source_filter).name
        return vs.similarity_search(
            query,
            k=k,
            filter={"source": fname},
        )
    return vs.similarity_search(query, k=k)

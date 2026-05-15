"""PDF 加载、分块并写入 Chroma。"""
from __future__ import annotations

from pathlib import Path
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from src.config import CHUNK_OVERLAP, CHUNK_SIZE, PDF_DIR
from src.rag.vectorstore import load_vectorstore


def _normalize_source_metadata(docs: List[Document]) -> None:
    for d in docs:
        src = d.metadata.get("source")
        if src:
            d.metadata["source"] = Path(str(src)).name


def load_pdf_as_documents(pdf_path: Path) -> List[Document]:
    loader = PyPDFLoader(str(pdf_path))
    docs = loader.load()
    _normalize_source_metadata(docs)
    return docs


def split_documents(documents: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        add_start_index=True,
    )
    return splitter.split_documents(documents)


def ingest_pdf_file(pdf_path: Path, replace_existing: bool = False) -> int:
    """将单个 PDF 写入向量库；返回写入的块数量。"""
    pdf_path = Path(pdf_path).resolve()
    if not pdf_path.is_file():
        raise FileNotFoundError(pdf_path)

    raw = load_pdf_as_documents(pdf_path)
    chunks = split_documents(raw)
    if not chunks:
        return 0

    fname = pdf_path.name
    vs = load_vectorstore()

    if replace_existing:
        try:
            vs._collection.delete(where={"source": fname})  # noqa: SLF001
        except Exception:
            pass

    vs.add_documents(chunks)
    return len(chunks)


def ingest_pdf_directory(
    directory: Path | None = None,
    replace_existing: bool = False,
) -> dict:
    """扫描目录下所有 PDF 并入库。"""
    root = Path(directory) if directory else PDF_DIR
    root.mkdir(parents=True, exist_ok=True)
    results: dict = {}
    for pdf in sorted(root.glob("*.pdf")):
        n = ingest_pdf_file(pdf, replace_existing=replace_existing)
        results[pdf.name] = n
    return results

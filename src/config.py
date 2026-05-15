"""项目路径与 RAG 可调参数。"""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
PDF_DIR = DATA_DIR / "pdfs"
CHROMA_DIR = DATA_DIR / "chroma"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

COLLECTION_NAME = "smart_doc_kb"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

RETRIEVER_K = 6

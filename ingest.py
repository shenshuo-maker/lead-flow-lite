"""将 data/pdfs 下的 PDF 分块、向量化并写入本地 Chroma。"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import PDF_DIR  # noqa: E402
from src.rag.ingest import ingest_pdf_directory  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="索引 PDF 到 Chroma 知识库")
    parser.add_argument(
        "--dir",
        type=Path,
        default=None,
        help=f"PDF 目录（默认: {PDF_DIR}）",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="若同名文件已存在，先删除旧向量再重新索引",
    )
    args = parser.parse_args()
    stats = ingest_pdf_directory(directory=args.dir, replace_existing=args.replace)
    if not stats:
        print(f"未找到 PDF。请将文件放入: {PDF_DIR}")
        return
    for name, n in stats.items():
        print(f"{name}: 写入 {n} 个文本块")
    print("完成。可运行 `python main.py` 启动对话。")


if __name__ == "__main__":
    main()

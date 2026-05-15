"""Agent 可调用的两个工具：文档问答、文档对比。"""
from __future__ import annotations

from pathlib import Path

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

from src.config import RETRIEVER_K
from src.rag.vectorstore import list_sources, similarity_search

from .llm import get_chat_model


def _format_docs_for_prompt(docs) -> str:
    parts: list[str] = []
    for d in docs:
        src = d.metadata.get("source", "?")
        page = d.metadata.get("page", "?")
        parts.append(f"[来源: {Path(str(src)).name} | 页: {page}]\n{d.page_content}")
    return "\n\n---\n\n".join(parts)


def _rag_answer(question: str, context: str) -> str:
    llm = get_chat_model()
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "你是企业文档助手。必须严格依据「上下文」作答；若上下文不足以回答，请明确说明"
                "「知识库中未找到相关依据」，不要猜测或编造事实。回答可简要列出引用来源文件名。",
            ),
            (
                "human",
                "上下文:\n{context}\n\n用户问题:\n{question}",
            ),
        ]
    )
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"context": context, "question": question})


def _resolve_filename(user_input: str) -> str | None:
    """将用户输入的文件名对齐到已索引的 source 名称。"""
    raw = user_input.strip()
    avail = list_sources()
    if not raw:
        return None
    if raw in avail:
        return raw
    lower = raw.lower()
    stem_in = Path(raw).stem.lower()
    for a in avail:
        if a.lower() == lower:
            return a
        if Path(a).stem.lower() == stem_in:
            return a
    return None


@tool
def document_qa(question: str) -> str:
    """对知识库中已索引的 PDF 进行**单文档/全局**问答。

    适用于：解释条款、提取要点、事实查询、单主题总结等**不需要并排对比两份文件**的任务。
    """
    docs = similarity_search(question, k=RETRIEVER_K)
    if not docs:
        return (
            "未检索到相关片段。请确认已将 PDF 放入 data/pdfs 并运行 `python ingest.py`，"
            "且问题与文档主题相关。"
        )
    ctx = _format_docs_for_prompt(docs)
    return _rag_answer(question, ctx)


@tool
def document_compare(document_a: str, document_b: str, comparison_focus: str) -> str:
    """**对比两份**已索引 PDF 在指定关注点上的异同。

    参数:
    - document_a / document_b: 文件名，需与入库时的 PDF 文件名一致（含 .pdf 亦可）。
    - comparison_focus: 希望对比的主题或维度（例如「违约责任」「保密义务」）。
    """
    avail = list_sources()
    if len(avail) < 2:
        return f"当前已索引文件不足 2 份（现有: {avail or '无'}），无法执行对比。"

    a = _resolve_filename(document_a)
    b = _resolve_filename(document_b)
    if not a or not b:
        return (
            f"无法识别文件名。已索引文件: {', '.join(avail)}。"
            f" 收到: A={document_a!r}, B={document_b!r}"
        )
    if a == b:
        return "两份文档指向同一文件，请提供两个不同的已索引文件名。"

    q = comparison_focus.strip() or "整体内容与条款差异"
    docs_a = similarity_search(q, k=RETRIEVER_K // 2 + 1, source_filter=a)
    docs_b = similarity_search(q, k=RETRIEVER_K // 2 + 1, source_filter=b)
    if not docs_a and not docs_b:
        return "在两份文档中均未检索到与关注点相关的片段，请尝试更具体的 comparison_focus。"

    ctx = (
        f"=== 文档 A: {a} ===\n{_format_docs_for_prompt(docs_a) if docs_a else '（无匹配片段）'}\n\n"
        f"=== 文档 B: {b} ===\n{_format_docs_for_prompt(docs_b) if docs_b else '（无匹配片段）'}"
    )
    question = (
        f"请对比文档《{a}》与《{b}》在「{q}」方面的异同，使用表格或分点说明；"
        "仅依据给定上下文，缺失处请标明「上下文未覆盖」而非臆测。"
    )
    return _rag_answer(question, ctx)


def get_agent_tools():
    return [document_qa, document_compare]

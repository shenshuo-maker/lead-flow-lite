"""ReAct Agent（LangGraph prebuilt）。"""
from __future__ import annotations

from langgraph.prebuilt import create_react_agent

from src.rag.vectorstore import list_sources

from .llm import get_chat_model
from .tools import get_agent_tools


def build_system_prompt() -> str:
    names = list_sources()
    doc_line = ", ".join(names) if names else "（暂无，请将 PDF 放入 data/pdfs 后运行 python ingest.py）"
    return (
        "你是「智能文档平台」的企业级助手，基于 RAG 与 ReAct 工具调用工作。\n"
        "你必须通过工具检索知识库后再组织答案，避免「拍脑袋」式臆测。\n\n"
        f"当前知识库中已索引的 PDF（metadata.source 文件名）: {doc_line}\n\n"
        "任务分流规则：\n"
        "1. 用户要做单文档问答、查条款、解释概念、提取要点、与「对比两份文件」无关时 —— "
        "调用 `document_qa`。\n"
        "2. 用户明确要求对比两份文档、找差异、对齐条款、版本差异等 —— 调用 `document_compare`，"
        "并传入与上列完全一致的 `document_a` 与 `document_b` 文件名。\n\n"
        "回答时简要注明依据的源文件名；若工具返回显示无依据，如实转告用户。"
    )


def build_react_graph():
    """每次构建以刷新已索引文件列表（入库后同一会话也可更新提示）。"""
    llm = get_chat_model()
    tools = get_agent_tools()
    return create_react_agent(llm, tools, prompt=build_system_prompt())

"""命令行对话入口：ReAct Agent + RAG 工具。"""
from __future__ import annotations

import sys
from pathlib import Path

from langchain_core.messages import HumanMessage

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    from src.agent.graph import build_react_graph

    print("智能文档平台已启动。输入问题，空行或输入 quit 退出。\n")
    messages: list = []
    while True:
        try:
            user = input("您: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见。")
            break
        if not user or user.lower() in {"quit", "exit", "q"}:
            print("再见。")
            break
        messages.append(HumanMessage(content=user))
        graph = build_react_graph()
        result = graph.invoke({"messages": messages})
        messages = list(result["messages"])
        last = messages[-1]
        text = getattr(last, "content", str(last))
        print(f"助手: {text}\n")


if __name__ == "__main__":
    main()

"""对话模型（OpenAI 兼容 API）。"""
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


def get_chat_model() -> ChatOpenAI:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "未设置 OPENAI_API_KEY。请复制 .env.example 为 .env 并填入密钥。"
        )
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    return ChatOpenAI(model=model, temperature=0)

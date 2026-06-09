from __future__ import annotations

from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from chatbot.config import LLM_MODEL, LLM_TEMPERATURE

load_dotenv()


def get_llm(
    model: str = LLM_MODEL,
    temperature: float = LLM_TEMPERATURE,
) -> BaseChatModel:
    """Return the OpenAI chat model used by the RAG chain.

    Reads OPENAI_API_KEY from the environment (or .env file).
    """
    return ChatOpenAI(model=model, temperature=temperature)

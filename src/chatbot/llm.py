from __future__ import annotations

from langchain_community.llms import Ollama
from langchain_core.language_models import BaseLLM

from chatbot.config import LLM_MODEL, LLM_TEMPERATURE


def get_llm(
    model: str = LLM_MODEL,
    temperature: float = LLM_TEMPERATURE,
) -> BaseLLM:
    """Return the local Ollama LLM used by the RAG chain."""
    return Ollama(model=model, temperature=temperature)

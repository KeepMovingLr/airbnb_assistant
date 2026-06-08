from __future__ import annotations

from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from chatbot.config import EMBED_MODEL, INDEX_DIR


def get_embeddings(model_name: str = EMBED_MODEL) -> Embeddings:
    """Return the embedding model. Must be identical at build and load time."""
    return HuggingFaceEmbeddings(model_name=model_name)


def build_index(chunks: list[Document], path: Path = INDEX_DIR) -> FAISS:
    """Embed chunks, build a FAISS index, and persist it to `path`."""
    embeddings = get_embeddings()
    vectordb = FAISS.from_documents(chunks, embeddings)
    path.mkdir(parents=True, exist_ok=True)
    vectordb.save_local(str(path))
    return vectordb


def load_index(path: Path = INDEX_DIR) -> FAISS:
    """Load a previously-built FAISS index from `path`."""
    embeddings = get_embeddings()
    return FAISS.load_local(
        str(path),
        embeddings,
        allow_dangerous_deserialization=True,
    )

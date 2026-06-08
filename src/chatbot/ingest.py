from __future__ import annotations

from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader, WebBaseLoader
from langchain_core.documents import Document

from chatbot.config import DATA_DIR, PDF_GLOB, TXT_GLOB


def load_pdfs(data_dir: Path = DATA_DIR, pattern: str = PDF_GLOB) -> list[Document]:
    """Load every PDF in `data_dir` matching `pattern`. One Document per page."""
    docs: list[Document] = []
    for pdf_path in sorted(data_dir.glob(pattern)):
        loader = PyPDFLoader(str(pdf_path))
        docs.extend(loader.load())
    return docs


def load_texts(data_dir: Path = DATA_DIR, pattern: str = TXT_GLOB) -> list[Document]:
    """Load every plain-text file in `data_dir` matching `pattern`. One Document per file."""
    docs: list[Document] = []
    for txt_path in sorted(data_dir.glob(pattern)):
        loader = TextLoader(str(txt_path), encoding="utf-8")
        docs.extend(loader.load())
    return docs


def load_urls(urls: list[str]) -> list[Document]:
    """Load web pages by URL. One Document per URL."""
    if not urls:
        return []
    return WebBaseLoader(urls).load()


def load_documents(
    data_dir: Path = DATA_DIR,
    urls: list[str] | None = None,
) -> list[Document]:
    """Load all source documents — PDFs + text files from disk, plus optional URLs."""
    docs = load_pdfs(data_dir)
    docs.extend(load_texts(data_dir))
    if urls:
        docs.extend(load_urls(urls))
    return docs

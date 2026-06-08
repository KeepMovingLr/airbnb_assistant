"""Rebuild the FAISS index from documents in `data/`.

Usage:
    python scripts/build_index.py
"""

from __future__ import annotations

from chatbot.config import SOURCE_URLS
from chatbot.ingest import load_documents
from chatbot.splitter import split_documents
from chatbot.vectorstore import build_index


def main() -> None:
    print("Loading documents...")
    docs = load_documents(urls=SOURCE_URLS)
    print(f"  loaded {len(docs)} documents")

    print("Chunking...")
    chunks = split_documents(docs)
    print(f"  produced {len(chunks)} chunks")

    print("Building FAISS index...")
    vectordb = build_index(chunks)
    print(f"Done. {vectordb.index.ntotal} embeddings saved.")


if __name__ == "__main__":
    main()

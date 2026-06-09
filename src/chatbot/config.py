import os
from pathlib import Path


def _project_root() -> Path:
    """Find the project root by walking up from cwd looking for pyproject.toml.

    Fallbacks: env var override (PROJECT_ROOT), then cwd itself.
    Works whether `chatbot` runs from src/ (local dev) or site-packages (cloud).
    """
    if env := os.environ.get("PROJECT_ROOT"):
        return Path(env).resolve()
    here = Path.cwd().resolve()
    for candidate in [here, *here.parents]:
        if (candidate / "pyproject.toml").exists():
            return candidate
    return here


PROJECT_ROOT = _project_root()
DATA_DIR = PROJECT_ROOT / "data"
INDEX_DIR = PROJECT_ROOT / "faiss_index"

# Ingestion / chunking
PDF_GLOB = "*.pdf"
TXT_GLOB = "*.txt"
SOURCE_URLS: list[str] = []
CHUNK_SIZE = 300
CHUNK_OVERLAP = 30

# Embeddings — must stay the same between index build and query time.
EMBED_MODEL = "thenlper/gte-small"

# Retrieval
RETRIEVER_K = 8

# LLM (OpenAI)
LLM_MODEL = "gpt-4o-mini"
LLM_TEMPERATURE = 0.1

from pathlib import Path

# Paths — anchored to the project root so they work regardless of cwd.
# config.py lives at src/chatbot/config.py, so parents[2] is the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
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

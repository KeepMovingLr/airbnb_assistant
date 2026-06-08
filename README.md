# Airbnb Assistant

A local Retrieval-Augmented Generation (RAG) chatbot that answers questions about Airbnb listing details and policies, grounded in your own source documents.

Built with LangChain, FAISS, Ollama (local LLM), and Streamlit.

## What it does

- Reads your PDFs and text files from the `data/` folder.
- Embeds them into a local FAISS vector index.
- At query time, retrieves the most relevant chunks and feeds them to a local LLM (`gemma3:1b` via Ollama) to produce grounded, citation-friendly answers.
- Falls back to "I don't know based on the available documents" when the answer isn't in the corpus.
- Exposes a minimal Streamlit chat UI.

## Project structure

```
AIRBNB_ASSISTANT/
├── README.md
├── pyproject.toml          # dependencies + build config
├── .env.example            # template for secrets (copy to .env)
├── .gitignore
├── data/                   # source PDFs / .txt files (you provide)
├── faiss_index/            # GENERATED — created by build_index.py
├── src/
│   └── chatbot/
│       ├── __init__.py
│       ├── config.py       # paths, model names, k, chunk size
│       ├── ingest.py       # load PDFs / texts / URLs → Documents
│       ├── splitter.py     # chunk Documents
│       ├── vectorstore.py  # build / save / load FAISS
│       ├── llm.py          # Ollama LLM factory
│       ├── prompts.py      # SYSTEM_TEMPLATE + PromptTemplate
│       └── chain.py        # assemble retriever + prompt + llm
├── scripts/
│   └── build_index.py      # one-off CLI: rebuild FAISS from data/
├── app.py                  # Streamlit UI (entry point)
└── tests/
    └── test_chain.py       # sanity checks
```

## Prerequisites

- **Python 3.11+**
- **Conda** (recommended) or any virtual environment manager
- **Ollama** for running the local LLM — install from <https://ollama.com/download>

## Setup

### 1. Create the conda environment

```bash
conda create -n airbnb-assistant python=3.11 -y
conda activate airbnb-assistant
```

### 2. Install the project

From the project root:

```bash
pip install -e ".[dev]"
```

This installs the project in editable mode plus dev tools (pytest, ruff).

### 3. Start Ollama and pull the model

In a **separate terminal** (keep it running while using the app):

```bash
ollama serve
```

Then in your main terminal, pull the model once:

```bash
ollama pull gemma3:1b
```

### 4. Add your source documents

Drop one or more files into `data/`:

- `.pdf` — loaded with `PyPDFLoader` (text-based PDFs only — scanned/image PDFs won't extract).
- `.txt` — loaded as plain UTF-8 text.

### 5. Build the vector index

```bash
python scripts/build_index.py
```

Expected output:

```
Loading documents...
  loaded N documents
Chunking...
  produced M chunks
Building FAISS index...
Done. M embeddings saved.
```

The index lives in `faiss_index/` (gitignored).

### 6. Run the chat UI

```bash
streamlit run app.py
```

Open the URL Streamlit prints (usually <http://localhost:8501>) and start asking questions.

## Usage

### Adding new documents

1. Drop the file (`.pdf` or `.txt`) into `data/`.
2. Re-run `python scripts/build_index.py`.
3. In the Streamlit browser tab, press `C` to clear the cache so the new index loads.

### Adding URL sources

Edit `src/chatbot/config.py`:

```python
SOURCE_URLS: list[str] = [
    "https://example.com/some/help/article",
]
```

Then rebuild the index. Note: `WebBaseLoader` does **not** render JavaScript — pages that build content with JS (like Airbnb listing pages) won't extract usefully. Save such pages as plain text instead.

### Tuning behavior

Most tunables live in `src/chatbot/config.py`:

| Setting | Purpose |
|---|---|
| `CHUNK_SIZE`, `CHUNK_OVERLAP` | Text chunk size and overlap for embedding |
| `EMBED_MODEL` | HuggingFace sentence-transformer model |
| `RETRIEVER_K` | How many chunks to retrieve per query |
| `LLM_MODEL` | Ollama model name |
| `LLM_TEMPERATURE` | LLM creativity (lower = more deterministic) |

### Changing the system prompt

Edit `SYSTEM_TEMPLATE` in `src/chatbot/prompts.py` to change how the bot is instructed to behave (tone, citation style, what to do when uncertain).

## Tests

```bash
pytest
```

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'chatbot'` | Project not installed in current env | `conda activate airbnb-assistant && pip install -e ".[dev]"` |
| `ConnectionRefusedError` from Ollama | `ollama serve` is not running | Start it in a separate terminal |
| `produced 0 chunks` | All source PDFs are image-only / unreadable | Use `.txt` files or text-based PDFs |
| Streamlit shows stale answers after rebuilding index | UI is using cached chain | Press `C` in the Streamlit browser, or use menu → Clear cache |
| Import warnings in IDE | IDE pointing at the wrong interpreter | VS Code: `Cmd+Shift+P` → "Python: Select Interpreter" → pick the `airbnb-assistant` env |

## Tech stack

- [LangChain](https://www.langchain.com/) — RAG orchestration
- [FAISS](https://github.com/facebookresearch/faiss) — vector similarity search
- [sentence-transformers](https://www.sbert.net/) — embeddings (`thenlper/gte-small`)
- [Ollama](https://ollama.com/) — local LLM runtime (`gemma3:1b`)
- [Streamlit](https://streamlit.io/) — chat UI
- [pypdf](https://pypdf.readthedocs.io/) — PDF text extraction

## License

MIT

# Airbnb Assistant

A Retrieval-Augmented Generation (RAG) chatbot that answers questions about Airbnb listing details and policies, grounded in your own source documents.

**🔗 Live demo:** <https://airbnb-assistant-uiuc-rooms.streamlit.app/>

Built with LangChain, FAISS, OpenAI, and Streamlit. Designed to run locally and deploy to Streamlit Community Cloud.

## What it does

- Reads your PDFs and text files from the `data/` folder.
- Embeds them into a FAISS vector index using a local sentence-transformer (`gte-small`).
- At query time, retrieves the most relevant chunks and feeds them to OpenAI's `gpt-4o-mini` to produce grounded, citation-friendly answers.
- Falls back to "I don't know based on the available documents" when the answer isn't in the corpus.
- Gates access behind a shared password (optional locally, required in production).
- Exposes a Streamlit chat UI with sidebar, suggested questions, and source citations.

## Project structure

```
AIRBNB_ASSISTANT/
├── README.md
├── pyproject.toml            # build + dependency declaration
├── requirements.txt          # mirror for Streamlit Cloud
├── .env.example              # template for secrets (copy to .env)
├── .gitignore
├── .streamlit/
│   └── config.toml           # theme
├── data/                     # source PDFs / .txt files
├── faiss_index/              # vector index (committed for deploy)
├── src/
│   └── chatbot/
│       ├── __init__.py
│       ├── config.py         # paths, model names, k, chunk size
│       ├── ingest.py         # load PDFs / texts / URLs → Documents
│       ├── splitter.py       # chunk Documents
│       ├── vectorstore.py    # build / save / load FAISS
│       ├── llm.py            # OpenAI ChatOpenAI factory
│       ├── prompts.py        # SYSTEM_TEMPLATE + PromptTemplate
│       └── chain.py          # assemble retriever + prompt + llm
├── scripts/
│   └── build_index.py        # rebuild FAISS from data/
├── app.py                    # Streamlit UI (entry point)
└── tests/
    └── test_chain.py
```

## Prerequisites

- **Python 3.11+**
- **Conda** (recommended) or any virtual environment manager
- **An OpenAI API key** — sign up at <https://platform.openai.com>, add credit, and set a monthly spending limit

## Local setup

### 1. Create the conda environment

```bash
conda create -n airbnb-assistant python=3.11 -y
conda activate airbnb-assistant
```

### 2. Install the project

```bash
pip install -e ".[dev]"
```

### 3. Create your `.env` file

```bash
cp .env.example .env
```

Then open `.env` and set:

```
OPENAI_API_KEY=sk-proj-your-key-here
APP_PASSWORD=any-string-you-pick  # optional locally; leave blank to skip the gate
```

### 4. Add your source documents

Drop `.pdf` or `.txt` files into `data/`.

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

The index is saved to `faiss_index/` and committed to git so deployments don't need to rebuild.

### 6. Run the chat UI

```bash
streamlit run app.py
```

Open the URL Streamlit prints (usually <http://localhost:8501>). If `APP_PASSWORD` is set, you'll see a login form first.

## Deployment to Streamlit Community Cloud

The repo is pre-configured for one-click deploys to <https://share.streamlit.io>.

### 1. Push your branch to GitHub

```bash
git push
```

### 2. Create the app on Streamlit Cloud

- Go to <https://share.streamlit.io> and sign in with GitHub
- Click **New app**
- **Repository:** `your-username/your-repo`
- **Branch:** `livemodel` (or whichever you deploy from)
- **Main file path:** `app.py`
- **Python version:** `3.11`

### 3. Add secrets (Advanced settings → Secrets)

Use **TOML format** (values in quotes):

```toml
OPENAI_API_KEY = "sk-proj-your-rotated-key"
APP_PASSWORD = "pick-something-strong"
```

### 4. Click Deploy

First build takes ~5 minutes (installs dependencies and your local package). Subsequent deploys are faster.

### 5. Smoke-test the live URL

- ✅ Login form appears
- ✅ Wrong password rejected
- ✅ Correct password lets you in
- ✅ Ask a question, get an answer with sources

### Cost and runtime

- **Hosting:** free indefinitely on Streamlit Community Cloud. Apps sleep after **7 days with zero visitors** and wake on the next visit (~10–30s cold start).
- **Resources:** 1 GB RAM, ~1 CPU core, 1 GB shared disk per account. Plenty for this app.
- **LLM cost:** each chat turn with `gpt-4o-mini` costs roughly **$0.0005** (~2,000 turns per $1). The real meter is OpenAI, not Streamlit.
- **Protect yourself:** set a hard monthly spend limit on OpenAI's billing page (e.g., $20). Keep the `APP_PASSWORD` private to avoid bot abuse.
- **Monitor:** <https://platform.openai.com/usage> shows daily token spend.

## Usage

### Updating data and redeploying

Anytime your source documents change (editing `data/test.txt`, adding a new file, removing one), follow this workflow to push the changes live:

**1. Edit or add files in `data/`**

```bash
# Edit an existing file:
#   open data/test.txt in your editor and save changes
# Add a new file:
#   drop a new .pdf or .txt into data/
# Remove a file:
#   rm data/old_file.txt
```

**2. Rebuild the vector index locally**

```bash
conda activate airbnb-assistant
python scripts/build_index.py
```

Confirm the output reflects the change:

```
Loading documents...
  loaded N documents          ← should match the number of files
Chunking...
  produced M chunks           ← should change if content changed
Building FAISS index...
Done. M embeddings saved.
```

If `produced 0 chunks`, the new file has no extractable text (image-only PDF, empty file). Fix the source and rerun.

**3. Commit both `data/` and `faiss_index/`**

```bash
git add data/ faiss_index/
git status                      # double-check no .env, no stray files
git commit -m "Update knowledge base content"
git push
```

The `faiss_index/` files **must** be committed — Streamlit Cloud uses the index baked into the repo. Without this step, the live app keeps using the old vectors.

**4. Streamlit Cloud auto-redeploys**

A push to the deployed branch triggers a fresh build within ~1 minute. Watch the **Manage app → logs** panel to confirm:

- New commit hash picked up
- `pip install` runs (cached, so fast)
- App restarts

**5. Verify on the live URL**

- Open the live app
- Ask a question whose answer depends on the new content
- Confirm the **Sources** expander cites your updated file

**6. (If needed) Clear stale cache**

Streamlit's `@st.cache_resource` decorator on `init_chain()` may serve a stale chain after the redeploy. To force a fresh load:

- In the browser: press `C` (Clear cache) → reload
- Or in the Streamlit Cloud dashboard: ⋮ menu → **Reboot app**

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
| `LLM_MODEL` | OpenAI model name (default `gpt-4o-mini`) |
| `LLM_TEMPERATURE` | LLM creativity (lower = more deterministic) |

### Changing the system prompt

Edit `SYSTEM_TEMPLATE` in `src/chatbot/prompts.py` to change how the bot is instructed to behave (tone, citation style, what to do when uncertain).

### Customizing the UI

- **Theme colors:** `.streamlit/config.toml`
- **Suggested starter questions:** `SUGGESTED_QUESTIONS` list at the top of `app.py`
- **Avatars and title:** also in `app.py`

## Tests

```bash
pytest
```

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'chatbot'` | Project not installed in current env | `conda activate airbnb-assistant && pip install -e ".[dev]"` |
| `openai.AuthenticationError` | `.env` missing or wrong key | Confirm `OPENAI_API_KEY` is set; restart the app |
| `RateLimitError: insufficient_quota` | No OpenAI credit | Add credit at <https://platform.openai.com/settings/organization/billing> |
| `produced 0 chunks` | All source PDFs are image-only / unreadable | Use `.txt` files or text-based PDFs |
| Streamlit shows stale answers after rebuilding index | UI is using cached chain | Press `C` in the Streamlit browser, or menu → Clear cache |
| Streamlit Cloud build fails on `pip install` | Dependency conflict or wrong Python version | Set Python to `3.11`; check `requirements.txt` |
| Streamlit Cloud serves stale code after a fix | pip wheel cached | Bump `version` in `pyproject.toml` and push again |

## Tech stack

- [LangChain](https://www.langchain.com/) — RAG orchestration
- [FAISS](https://github.com/facebookresearch/faiss) — vector similarity search
- [sentence-transformers](https://www.sbert.net/) — embeddings (`thenlper/gte-small`)
- [OpenAI](https://platform.openai.com/) — chat completions (`gpt-4o-mini`)
- [Streamlit](https://streamlit.io/) — chat UI + cloud hosting
- [pypdf](https://pypdf.readthedocs.io/) — PDF text extraction

## License

MIT

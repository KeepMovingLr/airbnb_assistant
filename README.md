AIRBNB_ASSISTANT/
├── README.md
├── pyproject.toml          # or environment.yml + requirements.txt
├── .env.example            # template for secrets (OPENAI_API_KEY, etc.)
├── .gitignore              # ignore faiss_index/, .env, __pycache__, etc.
├── data/                   # source PDFs / HTML
├── faiss_index/            # GENERATED — not checked in
├── src/
│   └── chatbot/
│       ├── __init__.py
│       ├── config.py       # paths, model names, k, chunk size — one place
│       ├── ingest.py       # load PDFs/URLs → list[Document]
│       ├── splitter.py     # chunk Documents
│       ├── vectorstore.py  # build / save / load FAISS
│       ├── llm.py          # Ollama (or OpenAI) factory
│       ├── prompts.py      # SYSTEM_TEMPLATE, PromptTemplate
│       └── chain.py        # assemble retriever + prompt + llm
├── scripts/
│   └── build_index.py      # one-off CLI: rebuild FAISS from data/
├── app.py                  # Streamlit UI (entry point)
└── tests/
    └── test_chain.py       # sanity check: golden Qs return non-empty answers
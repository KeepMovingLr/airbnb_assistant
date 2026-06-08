from __future__ import annotations

from langchain.chains import ConversationalRetrievalChain

from chatbot.config import RETRIEVER_K
from chatbot.llm import get_llm
from chatbot.prompts import get_prompt
from chatbot.vectorstore import load_index


def get_chain(k: int = RETRIEVER_K) -> ConversationalRetrievalChain:
    """Assemble the RAG chain: retriever + custom prompt + LLM."""
    vectordb = load_index()
    retriever = vectordb.as_retriever(search_kwargs={"k": k})

    return ConversationalRetrievalChain.from_llm(
        llm=get_llm(),
        retriever=retriever,
        combine_docs_chain_kwargs={"prompt": get_prompt()},
        return_source_documents=True,
    )

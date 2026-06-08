import streamlit as st

from chatbot.chain import get_chain

st.set_page_config(page_title="Airbnb Assistant", page_icon="🏠")
st.title("Airbnb Customer Support Assistant")


@st.cache_resource
def init_chain():
    return get_chain()


chain = init_chain()

if "history" not in st.session_state:
    st.session_state.history = []

for user_msg, bot_msg in st.session_state.history:
    with st.chat_message("user"):
        st.markdown(user_msg)
    with st.chat_message("assistant"):
        st.markdown(bot_msg)

question = st.chat_input("Ask me anything about our policies...")

if question:
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chain.invoke(
                {"question": question, "chat_history": st.session_state.history}
            )
        answer = response["answer"]
        st.markdown(answer)

        sources = response.get("source_documents", [])
        if sources:
            with st.expander("Sources"):
                for doc in sources:
                    src = doc.metadata.get("source", "unknown")
                    page = doc.metadata.get("page")
                    label = f"{src}" + (f" (page {page + 1})" if page is not None else "")
                    st.markdown(f"- **{label}**\n  > {doc.page_content[:200]}...")

    st.session_state.history.append((question, answer))

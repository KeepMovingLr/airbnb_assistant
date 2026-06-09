import os

import streamlit as st
from dotenv import load_dotenv

from chatbot.chain import get_chain

load_dotenv()

USER_AVATAR = "👤"
BOT_AVATAR = "🏠"

SUGGESTED_QUESTIONS = [
    "Is this an entire house?",
    "Is it close to UIUC?",
    "What amenities does the kitchen include?",
]

st.set_page_config(
    page_title="Airbnb Assistant",
    page_icon="🏠",
    layout="centered",
)


def _get_app_password() -> str:
    """Read APP_PASSWORD from env (.env locally) or Streamlit secrets (cloud)."""
    pw = os.environ.get("APP_PASSWORD", "")
    if pw:
        return pw
    try:
        return st.secrets.get("APP_PASSWORD", "")
    except Exception:
        return ""


def check_password() -> bool:
    """Show a login form. Returns True if the user has authenticated."""
    expected = _get_app_password()
    if not expected:
        return True  # No password configured — open access (local dev).
    if st.session_state.get("authenticated"):
        return True

    st.title("🏠 Airbnb Assistant")
    st.caption("Please enter the access password to continue.")
    with st.form("login"):
        pw = st.text_input("Password", type="password")
        if st.form_submit_button("Enter") and pw:
            if pw == expected:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password.")
    return False


if not check_password():
    st.stop()


@st.cache_resource
def init_chain():
    return get_chain()


chain = init_chain()

# --- Sidebar --------------------------------------------------------------
with st.sidebar:
    st.header("About")
    st.markdown(
        "This is a customer-support assistant for Airbnb. "
        "Ask questions about policies, payments, refunds, and listings — "
        "answers are grounded in our internal documentation."
    )
    st.divider()
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.history = []
        st.rerun()
    if _get_app_password() and st.session_state.get("authenticated"):
        if st.button("🚪 Log out", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.history = []
            st.rerun()
    st.divider()
    st.caption("Built with LangChain, FAISS, and OpenAI.")
    st.caption("[View on GitHub](https://github.com/KeepMovingLr/airbnb_assistant)")

# --- Header ---------------------------------------------------------------
st.title("🏠 Airbnb Customer Support")
st.caption("Grounded answers from our policy documents — never guesses.")

# --- State init -----------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


# --- Welcome state (empty chat) ------------------------------------------
if not st.session_state.history:
    st.markdown("#### Try asking:")
    cols = st.columns(len(SUGGESTED_QUESTIONS))
    for col, q in zip(cols, SUGGESTED_QUESTIONS):
        if col.button(q, use_container_width=True):
            st.session_state.pending_question = q
            st.rerun()

# --- Render prior history -------------------------------------------------
for user_msg, bot_msg in st.session_state.history:
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(user_msg)
    with st.chat_message("assistant", avatar=BOT_AVATAR):
        st.markdown(bot_msg)

# --- Input ---------------------------------------------------------------
typed = st.chat_input("Ask me anything about Airbnb policies...")
question = st.session_state.pending_question or typed
st.session_state.pending_question = None

# --- Handle new question --------------------------------------------------
if question:
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(question)

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        try:
            with st.spinner("Thinking..."):
                response = chain.invoke(
                    {"question": question, "chat_history": st.session_state.history}
                )
            answer = response["answer"]
            st.markdown(answer)

            sources = response.get("source_documents", [])
            if sources:
                with st.expander("📚 Sources"):
                    for doc in sources:
                        src = doc.metadata.get("source", "unknown")
                        page = doc.metadata.get("page")
                        label = f"{src}" + (f" (page {page + 1})" if page is not None else "")
                        st.markdown(f"- **{label}**\n  > {doc.page_content[:200]}...")

            st.session_state.history.append((question, answer))
        except Exception as e:
            st.error(
                "Sorry, I couldn't process that just now. Please try again in a moment."
            )
            st.caption(f"Details: {type(e).__name__}: {e}")

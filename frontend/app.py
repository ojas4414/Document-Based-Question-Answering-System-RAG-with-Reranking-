import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"

if "data" not in st.session_state:
    st.session_state.data = None

try:
    r = requests.get(f"{BACKEND_URL}/health", timeout=2)
    if r.status_code != 200:
        st.error("Backend is not healthy")
        st.stop()
except Exception:
    st.error("Backend is not running")
    st.stop()

st.set_page_config(
    page_title="Document Q&A (RAG)",
    layout="centered"
)

st.title("📄 Document Question Answering System")
st.caption("Ask questions based on your uploaded documents")

query = st.text_input(
    "Enter your question",
    placeholder="e.g. What is machine learning?"
)

if st.button("Ask", use_container_width=True):
    if not query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            response = requests.post(
                f"{BACKEND_URL}/query",
                json={"query": query}
            )

        if response.status_code == 200:
            st.session_state.data = response.json()
        else:
            st.error("Backend error. Check logs.")

if st.session_state.data is not None:
    st.divider()

    st.subheader("Answer")
    st.write(st.session_state.data["answer"])

    st.subheader("Sources")
    for i, src in enumerate(st.session_state.data["sources"], 1):
        with st.expander(f"Source {i}"):
            st.write(src)

    st.divider()
    st.subheader("Your Feedback")

    feedback_text = st.text_area(
        "Feedback",
        placeholder="Tell us what was helpful, missing, or incorrect"
    )

    if st.button("Submit Feedback", use_container_width=True):
        if not feedback_text.strip():
            st.warning("Please enter feedback before submitting.")
        else:
            requests.post(
                f"{BACKEND_URL}/feedback",
                json={
                    "query": query,
                    "chunk": st.session_state.data["sources"][0],
                    "feedback_text": feedback_text
                }
            )
            st.success("Thanks! Your feedback was recorded.")

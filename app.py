import os
os.environ["USE_TORCH"] = "1"
os.environ["TRANSFORMERS_NO_TF"] = "1"

import streamlit as st
from src.ingest import ingest_repo
from src.rag_chain import build_rag_chain

st.set_page_config(page_title="GitHub Codebase RAG Assistant", layout="wide")
st.title("GitHub Codebase RAG Assistant")
st.markdown("Ask natural language questions about any GitHub repository.")

with st.sidebar:
    st.header("Repository Setup")
    repo_url = st.text_input("GitHub Repository URL", placeholder="https://github.com/user/repo")
    index_button = st.button("Index Repository")

    if index_button:
        if not repo_url.strip():
            st.error("Please enter a valid repository URL.")
        else:
            with st.spinner("Cloning and indexing repository - this may take a moment..."):
                try:
                    ingest_repo(repo_url.strip())
                    st.session_state["indexed"] = True
                    st.session_state["repo_url"] = repo_url.strip()
                    st.success("Repository indexed successfully!")
                except Exception as e:
                    st.error(f"Indexing failed: {e}")

if st.session_state.get("indexed"):
    st.subheader(f"Ask about: {st.session_state.get('repo_url', '')}")

    question = st.text_input(
        "Ask a question about the repository",
        placeholder="e.g. Where is authentication implemented?",
    )

    if st.button("Get Answer") and question.strip():
        with st.spinner("Retrieving context and generating answer..."):
            try:
                rag_chain, retriever = build_rag_chain()

                source_docs = retriever.invoke(question.strip())
                answer = rag_chain.invoke(question.strip())

                st.markdown("### Answer")
                st.write(answer)

                sources = list(
                    dict.fromkeys(
                        doc.metadata.get("file_path", "unknown")
                        for doc in source_docs
                    )
                )

                if sources:
                    st.markdown("### Sources")
                    for src in sources:
                        st.markdown(f"- `{src}`")

            except Exception as e:
                st.error(f"Error generating answer: {e}")
else:
    st.info("Enter a GitHub repository URL in the sidebar and click **Index Repository** to get started.")

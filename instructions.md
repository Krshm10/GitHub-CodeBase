# GitHub Codebase RAG Assistant - AI Generator Instructions

This document provides complete instructions for an AI code generator to recreate this production-ready GitHub Codebase RAG (Retrieval-Augmented Generation) Assistant.

## 1. Project Overview

The objective is to create a Streamlit application that allows a user to input any public GitHub repository URL, ingest the source code into a local Chroma vector database, and then ask natural language questions about the codebase.

### Tech Stack
- **Language**: Python 3.10+
- **Frameworks**: LangChain, Streamlit
- **LLM**: Groq API (`llama-3.3-70b-versatile`)
- **Embeddings**: HuggingFace (`all-MiniLM-L6-v2`) via `sentence-transformers`
- **Vector Store**: ChromaDB
- **Tools**: GitPython (for cloning repositories)

---

## 2. Directory Structure

Ensure the AI generates the following directory structure:

```
├── .env                  # Environment variables (GROQ_API_KEY)
├── .gitignore            # Standard Python gitignore
├── README.md             # Project documentation (architecture, setup, usage)
├── app.py                # Main Streamlit application
├── requirements.txt      # Python dependencies
└── src/
    ├── __init__.py       # Empty file to make src a package
    ├── chunker.py        # Logic for splitting text into chunks
    ├── ingest.py         # Main pipeline for ingesting a repository
    ├── rag_chain.py      # LangChain LCEL pipeline for Q&A
    ├── repo_loader.py    # Logic for cloning and reading repo files
    ├── retriever.py      # Retriever configuration for Chroma
    └── utils.py          # Shared constants and environment loaders
```

*(Note: The AI should also generate `data/` and `vectorstore/` automatically at runtime, not commit them to the repository).*

---

## 3. Implementation Details

### `requirements.txt`
Dependencies must include:
`langchain`, `langchain-groq`, `langchain-huggingface`, `langchain-community`, `chromadb`, `gitpython`, `sentence-transformers`, `streamlit`, `python-dotenv`.

### `src/utils.py`
- Expose constants `VECTORSTORE_DIR` and `DATA_DIR` pointing to paths relative to the project root.
- Expose sets for `IGNORED_DIRS` (e.g., `node_modules`, `.git`, `venv`) and `ALLOWED_EXTENSIONS` (`.py`, `.js`, `.ts`, `.md`, `.java`, `.cpp`).
- Implement a helper to load `.env` variables and retrieve the `GROQ_API_KEY`.

### `src/repo_loader.py`
- Use `git.Repo.clone_from` to clone the requested repository into `DATA_DIR/repo_name`. Handle clearing the existing directory if it already exists.
- Implement a file traversal function that walks through the cloned repository, ignoring directories in `IGNORED_DIRS` and keeping files with `ALLOWED_EXTENSIONS`.
- Create LangChain `Document` objects with `page_content` and metadata (`file_path`, `repo_name`).
- Generate a special document representing the textual tree structure of the repository.

### `src/chunker.py`
- Use LangChain's `RecursiveCharacterTextSplitter`.
- Set `chunk_size` to 1000 and `chunk_overlap` to 200.

### `src/ingest.py`
- Combine the steps: clone repo -> load files -> append structure doc -> chunk documents.
- Initialize `HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")`.
- If a Chroma vectorstore already exists at `VECTORSTORE_DIR`, clear it using `delete_collection()`.
- Use `Chroma.from_documents` to embed the chunks and persist the new database.

### `src/retriever.py`
- Implement a function `get_retriever(top_k=4)`.
- Initialize `Chroma` pointing to `VECTORSTORE_DIR` and using the HuggingFace embeddings.
- Return `vectorstore.as_retriever(search_kwargs={"k": top_k})`.

### `src/rag_chain.py`
- Use the `ChatGroq` model (`llama-3.3-70b-versatile`).
- Create a `ChatPromptTemplate` with a robust system prompt instructing the AI to answer codebase questions based on the provided context, and to cite files.
- Build the LangChain Expression Language (LCEL) chain:
  `{"context": retriever | _format_docs, "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()`
- Export a function `build_rag_chain()` that returns the configured chain and the retriever instance.

### `app.py`
- Build a dual-pane Streamlit interface using `st.set_page_config(layout="wide")`.
- **Sidebar**:
  - Input field for GitHub Repository URL.
  - Button to "Index Repository".
  - On submit, call `ingest_repo` with a spinner. Save success state in `st.session_state`.
- **Main View**:
  - If indexed, show a text input for the user's codebase question.
  - On submit, call `build_rag_chain()`, then invoke both the retriever (for source display) and the rag chain (for the final answer).
  - Display the generated answer.
  - Display uniquely extracted source file paths below the answer.

---

## 4. Documentation

The AI must generate a highly communicative `README.md` that includes:
- A clear architectural diagram (ASCII art).
- Full pipeline run-down (Clone -> Load -> Structure -> Chunk -> Embed -> Retrieve -> Generate).
- Installation steps (clone, venv, required API keys).
- Usage instructions and example queries.

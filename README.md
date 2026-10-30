# GitHub Codebase RAG Assistant

A Retrieval-Augmented Generation (RAG) application that lets you ask natural language questions about any GitHub repository. The system clones a repository, indexes the code files, generates embeddings, stores them in a Chroma vector database, and answers questions using an LLM grounded in the actual source code.

---

## Architecture

```
User Question
     │
     ▼
┌─────────────┐       ┌────────────┐      ┌──────────────┐
│  Streamlit  │────▶ │  Retriever  │────▶│ Chroma Vector│
│     UI      │       │  (top-k=4) │      │    Store     │
└─────────────┘       └────────────┘      └──────────────┘
     │                                        ▲
     ▼                                        │
┌────────────┐                           ┌─────┴───────┐
│  RAG Chain │                           │  Ingestion  │
│  (Groq /   │                           │  Pipeline   │
│  LLaMA 3)  │                           └─────────────┘
└────────────┘                                ▲
     │                                        │
     ▼                                  ┌─────┴───────┐
  Answer +                              │  Repo Clone │
  Sources                               │  + Chunking │
                                        └─────────────┘
```

### Pipeline

1. **Clone** — The target GitHub repository is cloned locally using GitPython.
2. **Load** — All supported source files (`.py`, `.js`, `.ts`, `.md`, `.java`, `.cpp`) are read.
3. **Structure** — A textual tree of the repository layout is generated.
4. **Chunk** — Files are split into overlapping 1 000-character chunks using LangChain's `RecursiveCharacterTextSplitter`.
5. **Embed & Store** — Chunks are embedded with HuggingFace embeddings (`all-MiniLM-L6-v2`, runs locally) and persisted in a Chroma vector database.
6. **Retrieve** — At query time, the 4 most similar chunks are retrieved.
7. **Generate** — Retrieved context is injected into a prompt and sent to Groq's `llama-3.3-70b-versatile` for a grounded answer.

---

## Project Structure

```
├── src/
│   ├── repo_loader.py   # Clone repo & load files
│   ├── chunker.py        # Split documents into chunks
│   ├── ingest.py         # Full ingestion pipeline
│   ├── retriever.py      # Vector store retriever
│   ├── rag_chain.py      # LLM-powered RAG chain
│   └── utils.py          # Config, constants, helpers
│
├── vectorstore/           # Persisted Chroma database (auto-generated)
├── data/                  # Cloned repositories (auto-generated)
│
├── app.py                 # Streamlit UI entry point
├── requirements.txt
├── .env.example
└── README.md
```

---

## Installation

### 1. Clone this project

```bash
git clone https://github.com/your-username/codebase-rag-assistant.git
cd codebase-rag-assistant
```

### 2. Create a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example file and add your Groq API key:

```bash
cp .env.example .env
```

Edit `.env`:

```
GROQ_API_KEY=gsk_...
```

---

## Usage

Start the application:

```bash
streamlit run app.py
```

1. Enter a **GitHub repository URL** in the sidebar (e.g. `https://github.com/pallets/flask`).
2. Click **Index Repository** — the repo will be cloned and indexed.
3. Type a **question** in the main area and click **Get Answer**.

---

## Example Queries

| Question | Sample Answer |
|---|---|
| *Where is authentication implemented?* | Authentication logic is implemented in `src/auth.py` where the `login_user` function verifies credentials against the database. **Source:** `src/auth.py` |
| *Explain the structure of this repository.* | The repository is organized into … **Source:** `REPO_STRUCTURE` |
| *How does the database connection work?* | Database connections are managed in `src/database.py` using a connection pool initialized in the `connect()` function. **Source:** `src/database.py` |
| *What does the main script do?* | The main entry point `app.py` starts a Flask server … **Source:** `app.py` |

---

## Tech Stack

- **Python**
- **LangChain** — orchestration, chunking, prompt management
- **Groq API** — LLM (`llama-3.3-70b-versatile`)
- **HuggingFace / Sentence-Transformers** — local embeddings (`all-MiniLM-L6-v2`)
- **Chroma** — local vector database
- **GitPython** — repository cloning
- **Streamlit** — web interface
- **python-dotenv** — environment variable management

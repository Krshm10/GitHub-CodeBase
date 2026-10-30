import os
import chromadb

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from src.repo_loader import clone_repo, load_repo_files, generate_repo_structure
from src.chunker import chunk_documents
from src.utils import VECTORSTORE_DIR


def ingest_repo(repo_url: str) -> Chroma:
    repo_path = clone_repo(repo_url)

    documents = load_repo_files(repo_path)
    if not documents:
        raise ValueError("No supported files found in the repository.")

    structure_doc = generate_repo_structure(repo_path)
    documents.append(structure_doc)

    chunks = chunk_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
    )

    os.makedirs(VECTORSTORE_DIR, exist_ok=True)

    client = chromadb.PersistentClient(path=VECTORSTORE_DIR)
    for col in client.list_collections():
        client.delete_collection(col.name)

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTORSTORE_DIR,
        client=client,
    )

    return vectorstore

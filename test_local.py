import os
import sys

# Ensure it runs from project root
sys.path.insert(0, os.path.abspath("."))

from src.ingest import ingest_repo
from src.rag_chain import build_rag_chain

print("Ingesting repo...")
ingest_repo("https://github.com/pallets/click")
print("Ingestion complete. Testing chain...")

rag_chain, retriever = build_rag_chain()
docs = retriever.invoke("What does utils.py do?")
print(f"Retrieved {len(docs)} documents.")

answer = rag_chain.invoke("What does utils.py do?")
print("Answer:", answer)

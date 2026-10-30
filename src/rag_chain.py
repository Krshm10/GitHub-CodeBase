from langchain_groq import ChatGroq
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.retriever import get_retriever
from src.utils import get_groq_api_key


SYSTEM_PROMPT = """\
You are an AI assistant that answers questions about a GitHub repository.

Use the provided code context to answer the question.

If the answer cannot be found in the context, respond with:
"I could not find this information in the repository."

Always reference file names when possible.
"""

USER_PROMPT = """\
Context:
{context}

Question:
{question}
"""


def _format_docs(docs) -> str:
    formatted: list[str] = []
    for doc in docs:
        file_path = doc.metadata.get("file_path", "unknown")
        formatted.append(f"--- {file_path} ---\n{doc.page_content}")
    return "\n\n".join(formatted)


def build_rag_chain():
    api_key = get_groq_api_key()

    retriever = get_retriever()

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", USER_PROMPT),
        ]
    )

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        groq_api_key=api_key,
    )

    rag_chain = (
        {
            "context": retriever | _format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain, retriever

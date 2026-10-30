import os
from dotenv import load_dotenv


def load_env() -> None:
    load_dotenv()


def get_groq_api_key() -> str:
    load_env()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not set. "
            "Please add it to your .env file."
        )
    return api_key


IGNORED_DIRS: set[str] = {
    ".git",
    "node_modules",
    "venv",
    "__pycache__",
    "dist",
    "build",
    ".venv",
    "env",
    ".env",
}

ALLOWED_EXTENSIONS: set[str] = {
    ".py",
    ".js",
    ".ts",
    ".md",
    ".java",
    ".cpp",
}

VECTORSTORE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "vectorstore")
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

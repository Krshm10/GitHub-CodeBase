import os
import stat
import shutil
from typing import Optional

from git import Repo
from langchain_core.documents import Document

from src.utils import ALLOWED_EXTENSIONS, IGNORED_DIRS, DATA_DIR


def _remove_readonly(func, path, _excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def clone_repo(repo_url: str, clone_dir: Optional[str] = None) -> str:
    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    clone_path = clone_dir or os.path.join(DATA_DIR, repo_name)

    if os.path.exists(clone_path):
        shutil.rmtree(clone_path, onerror=_remove_readonly)

    os.makedirs(clone_path, exist_ok=True)
    Repo.clone_from(repo_url, clone_path)
    return clone_path


def load_repo_files(repo_path: str) -> list[Document]:
    repo_name = os.path.basename(repo_path)
    documents: list[Document] = []

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

        for file_name in files:
            _, ext = os.path.splitext(file_name)
            if ext not in ALLOWED_EXTENSIONS:
                continue

            file_path = os.path.join(root, file_name)
            relative_path = os.path.relpath(file_path, repo_path)

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except OSError:
                continue

            if not content.strip():
                continue

            documents.append(
                Document(
                    page_content=content,
                    metadata={
                        "file_path": relative_path,
                        "repo_name": repo_name,
                    },
                )
            )

    return documents


def generate_repo_structure(repo_path: str) -> Document:
    repo_name = os.path.basename(repo_path)
    lines: list[str] = ["Repository Structure", ""]

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = sorted(d for d in dirs if d not in IGNORED_DIRS)

        level = os.path.relpath(root, repo_path)
        if level == ".":
            # Top-level files
            for file_name in sorted(files):
                _, ext = os.path.splitext(file_name)
                if ext in ALLOWED_EXTENSIONS:
                    lines.append(f"  {file_name}")
        else:
            indent = "  " * (level.count(os.sep))
            dir_name = os.path.basename(root)
            lines.append(f"{indent}{dir_name}/")

            for file_name in sorted(files):
                _, ext = os.path.splitext(file_name)
                if ext in ALLOWED_EXTENSIONS:
                    lines.append(f"{indent}  ├ {file_name}")

    structure_text = "\n".join(lines)

    return Document(
        page_content=structure_text,
        metadata={
            "file_path": "REPO_STRUCTURE",
            "repo_name": repo_name,
        },
    )

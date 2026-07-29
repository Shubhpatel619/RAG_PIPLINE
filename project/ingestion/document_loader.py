import os
from pathlib import Path
from typing import List, Dict, Any


class DocumentLoader:
    """Loads markdown documents from a corpus directory."""

    def __init__(self, corpus_dir: str):
        self.corpus_dir = Path(corpus_dir)

    def load_documents(self) -> List[Dict[str, Any]]:
        """
        Reads all .md files in corpus_dir.
        Returns a list of dicts with keys: doc_id, filename, filepath, content, title
        """
        if not self.corpus_dir.exists():
            raise FileNotFoundError(f"Corpus directory not found: {self.corpus_dir}")

        documents = []
        md_files = sorted(list(self.corpus_dir.glob("*.md")))

        for filepath in md_files:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()

            # Extract title from first H1 heading if present
            title = filepath.stem.replace("-", " ").title()
            for line in content.splitlines():
                if line.startswith("# "):
                    title = line.lstrip("# ").strip()
                    break

            documents.append({
                "doc_id": filepath.stem,
                "filename": filepath.name,
                "filepath": str(filepath.resolve()),
                "title": title,
                "content": content
            })

        return documents

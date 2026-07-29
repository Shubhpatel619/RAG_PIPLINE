import os
from pathlib import Path
from typing import List
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents import Document


class LangChainDocumentLoader:
    """Loads Markdown documents using LangChain document loaders."""

    def __init__(self, corpus_dir: str = "ai-engineer-take-home/sample_corpus"):
        self.corpus_dir = Path(corpus_dir)

    def load_documents(self) -> List[Document]:
        """
        Scans corpus_dir for .md files and returns a list of LangChain Document objects.
        Attaches metadata including filename and filepath.
        """
        if not self.corpus_dir.exists():
            raise FileNotFoundError(f"Corpus directory not found: {self.corpus_dir}")

        loader = DirectoryLoader(
            str(self.corpus_dir),
            glob="*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        documents = loader.load()

        # Clean metadata to contain clean filename
        for doc in documents:
            source_path = Path(doc.metadata.get("source", ""))
            doc.metadata["filename"] = source_path.name
            doc.metadata["source"] = source_path.name

        return documents

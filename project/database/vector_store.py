import os
from pathlib import Path
from typing import List, Tuple, Optional
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()


class LangChainVectorStore:
    """
    Persistent Vector Database using LangChain FAISS and GoogleGenerativeAIEmbeddings.
    """

    def __init__(self, index_dir: str = "project/database/faiss_index"):
        self.index_dir = Path(index_dir)
        self.embeddings = None
        self.vector_store: Optional[FAISS] = None

        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing. Please set GEMINI_API_KEY in your .env file or environment.")

        # Initialize LangChain Google Embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-2",
            google_api_key=api_key
        )

        # Load existing index if present
        if self.index_dir.exists() and (self.index_dir / "index.faiss").exists():
            try:
                self.vector_store = FAISS.load_local(
                    str(self.index_dir),
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
            except Exception:
                self.vector_store = None

    def add_documents(self, documents: List[Document]):
        """Indexes document chunks into FAISS vector database and saves locally."""
        if not documents:
            return

        if self.vector_store is None:
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
        else:
            self.vector_store.add_documents(documents)

        # Save FAISS index locally
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.vector_store.save_local(str(self.index_dir))

    def similarity_search_with_score(self, query: str, top_k: int = 3) -> List[Tuple[Document, float]]:
        """
        Performs similarity search against FAISS index.
        Returns a list of (Document, score) tuples.
        """
        if self.vector_store is None:
            return []
        return self.vector_store.similarity_search_with_score(query, k=top_k)

    def count(self) -> int:
        """Returns total count of indexed vectors."""
        if self.vector_store is None:
            return 0
        return self.vector_store.index.ntotal

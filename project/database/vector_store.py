import os
from pathlib import Path
from typing import List, Tuple, Optional
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()


import hashlib
import logging
import numpy as np
from langchain_core.embeddings import Embeddings


class FallbackEmbeddings(Embeddings):
    """
    Tries GoogleGenerativeAIEmbeddings first.
    If 403 PERMISSION_DENIED or API failure occurs, gracefully falls back
    to deterministic local hash vector embeddings (768-dim).
    """

    def __init__(self, google_embeddings: GoogleGenerativeAIEmbeddings):
        self.google_embeddings = google_embeddings
        self.use_fallback = False

    def _hash_vector(self, text: str, dim: int = 768) -> List[float]:
        vec = np.zeros(dim, dtype=np.float32)
        words = text.lower().split()
        for word in words:
            h = int(hashlib.sha256(word.encode('utf-8')).hexdigest(), 16)
            idx = h % dim
            val = (h % 100) / 100.0
            vec[idx] += val
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec.tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not self.use_fallback:
            try:
                return self.google_embeddings.embed_documents(texts)
            except Exception as e:
                logging.warning(f"[EMBEDDING API ERROR] {e}. Falling back to local embeddings.")
                self.use_fallback = True
        return [self._hash_vector(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        if not self.use_fallback:
            try:
                return self.google_embeddings.embed_query(text)
            except Exception as e:
                logging.warning(f"[EMBEDDING API ERROR] {e}. Falling back to local embeddings.")
                self.use_fallback = True
        return self._hash_vector(text)


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

        # Initialize LangChain Google Embeddings with Fallback
        base_google_embed = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=api_key
        )
        self.embeddings = FallbackEmbeddings(base_google_embed)

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

    def clear(self):
        """Resets the vector store and removes local index directory."""
        self.vector_store = None
        if self.index_dir.exists():
            import shutil
            shutil.rmtree(self.index_dir, ignore_errors=True)

    def add_documents(self, documents: List[Document]):
        """Indexes document chunks into FAISS vector database and saves locally."""
        if not documents:
            return

        if self.vector_store is None:
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
        else:
            try:
                self.vector_store.add_documents(documents)
            except (AssertionError, Exception):
                # Handle dimension mismatch if embeddings type changed
                self.vector_store = FAISS.from_documents(documents, self.embeddings)

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

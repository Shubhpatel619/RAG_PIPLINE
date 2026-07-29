from typing import List, Tuple
from langchain_core.documents import Document
from project.database.vector_store import LangChainVectorStore


class LangChainRetriever:
    """Handles semantic retrieval of document chunks using LangChain FAISS store."""

    def __init__(self, vector_store: LangChainVectorStore):
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int = 3) -> List[Tuple[Document, float]]:
        """
        Retrieves top_k relevant Document objects with similarity score.
        """
        return self.vector_store.similarity_search_with_score(query, top_k=top_k)

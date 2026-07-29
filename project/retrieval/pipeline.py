import os
from typing import Dict, Any, Optional
from project.ingestion.document_loader import DocumentLoader
from project.ingestion.chunker import MarkdownChunker
from project.database.vector_store import VectorStore
from project.retrieval.retriever import Retriever
from project.retrieval.generator import Generator, REFUSAL_MESSAGE


class RAGPipeline:
    """
    Complete RAG Pipeline orchestrating document ingestion, vector storage,
    semantic search retrieval, and LLM answer generation.
    """

    def __init__(
        self,
        corpus_dir: str = "ai-engineer-take-home/sample_corpus",
        db_path: str = "project/database/vector_store.db",
        mock: bool = False
    ):
        self.corpus_dir = corpus_dir
        self.vector_store = VectorStore(db_path=db_path)
        self.retriever = Retriever(vector_store=self.vector_store, mock=mock)
        self.generator = Generator(mock=mock)
        self.mock = mock

    def ingest(self, force_reindex: bool = False) -> int:
        """
        Ingests and indexes documents from corpus_dir into vector_store.
        Skipped if vector_store is already populated unless force_reindex is True.
        Returns total number of chunks indexed.
        """
        if not force_reindex and self.vector_store.count() > 0:
            return self.vector_store.count()

        loader = DocumentLoader(self.corpus_dir)
        docs = loader.load_documents()

        chunker = MarkdownChunker()
        chunks = chunker.chunk_documents(docs)

        texts = [c["text"] for c in chunks]
        embeddings = self.retriever.get_embeddings(texts)

        self.vector_store.clear()
        self.vector_store.add_chunks(chunks, embeddings)
        return len(chunks)

    def answer_question(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Executes end-to-end RAG pipeline for a given query:
        1. Ensures corpus is indexed.
        2. Retrieves top_k context chunks.
        3. Generates grounded answer + citations.
        Returns a result dict: {query, answer, citations, retrieved_chunks, refused}
        """
        # Ensure documents are indexed
        if self.vector_store.count() == 0:
            self.ingest()

        chunks = self.retriever.retrieve(query, top_k=top_k)

        # Generate answer from retrieved context
        answer, citations = self.generator.generate_answer(query, chunks)
        is_refusal = (answer == REFUSAL_MESSAGE)

        return {
            "query": query,
            "answer": answer,
            "citations": citations if not is_refusal else [],
            "retrieved_chunks": chunks,
            "refused": is_refusal
        }

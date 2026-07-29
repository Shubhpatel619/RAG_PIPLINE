import os
from typing import Dict, Any, List
from project.ingestion.document_loader import LangChainDocumentLoader
from project.ingestion.chunker import LangChainChunker
from project.database.vector_store import LangChainVectorStore
from project.retrieval.retriever import LangChainRetriever
from project.retrieval.generator import LangChainGenerator, REFUSAL_MESSAGE


class RAGPipeline:
    """
    Industry-standard LangChain RAG Pipeline:
    1. Loads Markdown documents via DirectoryLoader.
    2. Chunks documents via MarkdownHeaderTextSplitter & RecursiveCharacterTextSplitter.
    3. Indexes vectors into FAISS vector database using GoogleGenerativeAIEmbeddings.
    4. Retrieves top-k relevant chunks.
    5. Generates grounded answer + citations via ChatGoogleGenerativeAI (Gemini Flash).
    """

    def __init__(
        self,
        corpus_dir: str = "ai-engineer-take-home/sample_corpus",
        index_dir: str = "project/database/faiss_index"
    ):
        self.corpus_dir = corpus_dir
        self.vector_store = LangChainVectorStore(index_dir=index_dir)
        self.retriever = LangChainRetriever(vector_store=self.vector_store)
        self.generator = LangChainGenerator()

    def ingest(self, force_reindex: bool = False) -> int:
        """
        Ingests and indexes sample corpus documents into FAISS vector store.
        Returns total number of document chunks indexed.
        """
        if not force_reindex and self.vector_store.count() > 0:
            return self.vector_store.count()

        loader = LangChainDocumentLoader(self.corpus_dir)
        documents = loader.load_documents()

        chunker = LangChainChunker()
        chunked_docs = chunker.chunk_documents(documents)

        self.vector_store.add_documents(chunked_docs)
        return len(chunked_docs)

    def answer_question(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Executes end-to-end LangChain RAG Pipeline for a query.
        Returns dict containing answer, citations, retrieved chunks, and refusal status.
        """
        if self.vector_store.count() == 0:
            self.ingest()

        retrieved_tuples = self.retriever.retrieve(query, top_k=top_k)

        answer, citations = self.generator.generate_answer(query, retrieved_tuples)
        is_refusal = (answer == REFUSAL_MESSAGE)

        chunks_data = []
        for doc, score in retrieved_tuples:
            chunks_data.append({
                "filename": doc.metadata.get("filename", "unknown.md"),
                "section_header": doc.metadata.get("section_header", "General"),
                "text": doc.page_content,
                "score": float(score)
            })

        return {
            "query": query,
            "answer": answer,
            "citations": citations if not is_refusal else [],
            "retrieved_chunks": chunks_data,
            "refused": is_refusal
        }

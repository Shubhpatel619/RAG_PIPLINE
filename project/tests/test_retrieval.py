import pytest
from project.database.vector_store import LangChainVectorStore
from project.retrieval.retriever import LangChainRetriever
from project.ingestion.document_loader import LangChainDocumentLoader
from project.ingestion.chunker import LangChainChunker


def test_vector_store_and_retriever(tmp_path):
    idx_dir = tmp_path / "faiss_test"
    store = LangChainVectorStore(index_dir=str(idx_dir))
    
    loader = LangChainDocumentLoader("ai-engineer-take-home/sample_corpus")
    docs = loader.load_documents()
    chunker = LangChainChunker(chunk_size=400)
    chunked = chunker.chunk_documents(docs)

    store.add_documents(chunked[:5])
    assert store.count() > 0

    retriever = LangChainRetriever(vector_store=store)
    results = retriever.retrieve("How do I reset my API key?", top_k=1)
    assert len(results) == 1
    assert "filename" in results[0][0].metadata

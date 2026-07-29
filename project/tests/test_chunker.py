import pytest
from project.ingestion.document_loader import LangChainDocumentLoader
from project.ingestion.chunker import LangChainChunker


def test_document_loader():
    loader = LangChainDocumentLoader("ai-engineer-take-home/sample_corpus")
    docs = loader.load_documents()
    assert len(docs) == 6
    filenames = [d.metadata.get("filename") for d in docs]
    assert "api-reference.md" in filenames
    assert "billing-faq.md" in filenames


def test_langchain_chunker():
    loader = LangChainDocumentLoader("ai-engineer-take-home/sample_corpus")
    docs = loader.load_documents()
    chunker = LangChainChunker(chunk_size=300)
    chunked_docs = chunker.chunk_documents(docs)
    assert len(chunked_docs) > len(docs)
    assert all("filename" in d.metadata for d in chunked_docs)

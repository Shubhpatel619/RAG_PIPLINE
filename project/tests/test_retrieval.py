import pytest
import os
from project.database.vector_store import VectorStore
from project.retrieval.retriever import Retriever


def test_vector_store_and_retriever(tmp_path):
    db_file = tmp_path / "test_store.db"
    store = VectorStore(db_path=str(db_file))
    
    chunks = [
        {
            "chunk_id": "c1",
            "doc_id": "api-ref",
            "filename": "api-reference.md",
            "title": "API Reference",
            "section_header": "Resetting Key",
            "text": "To reset an API key, click Revoke in Workspace Settings."
        },
        {
            "chunk_id": "c2",
            "doc_id": "billing",
            "filename": "billing-faq.md",
            "title": "Billing FAQ",
            "section_header": "Seats",
            "text": "A seat is any workspace member who can log in."
        }
    ]

    retriever = Retriever(vector_store=store, mock=True)
    embeddings = retriever.get_embeddings([c["text"] for c in chunks])
    store.add_chunks(chunks, embeddings)

    assert store.count() == 2

    # Query for API key reset
    results = retriever.retrieve("How to reset API key?", top_k=1)
    assert len(results) == 1
    assert results[0]["filename"] == "api-reference.md"

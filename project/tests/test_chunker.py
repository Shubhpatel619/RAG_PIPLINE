import pytest
from project.ingestion.document_loader import DocumentLoader
from project.ingestion.chunker import MarkdownChunker


def test_document_loader():
    loader = DocumentLoader("ai-engineer-take-home/sample_corpus")
    docs = loader.load_documents()
    assert len(docs) == 6
    filenames = [d["filename"] for d in docs]
    assert "api-reference.md" in filenames
    assert "billing-faq.md" in filenames


def test_markdown_chunker():
    doc = {
        "doc_id": "test_doc",
        "filename": "test.md",
        "title": "Test Document",
        "content": "# Section 1\nThis is text in section 1.\n\n## Section 2\nThis is text in section 2."
    }
    chunker = MarkdownChunker(max_chunk_size=100)
    chunks = chunker.chunk_document(doc)
    assert len(chunks) >= 2
    assert any("Section 1" in c["section_header"] for c in chunks)
    assert any("Section 2" in c["section_header"] for c in chunks)
    assert all(c["filename"] == "test.md" for c in chunks)

import pytest
from project.retrieval.pipeline import RAGPipeline
from project.retrieval.generator import REFUSAL_MESSAGE


def test_rag_pipeline_valid_query(tmp_path):
    idx_dir = tmp_path / "pipeline_test"
    pipeline = RAGPipeline(
        corpus_dir="ai-engineer-take-home/sample_corpus",
        index_dir=str(idx_dir)
    )
    pipeline.ingest()

    res = pipeline.answer_question("How do I reset my Aperture API key?")
    assert res["refused"] is False
    assert "api-reference.md" in res["citations"]
    assert "revoke" in res["answer"].lower() or "revoking" in res["answer"].lower() or "workspace settings" in res["answer"].lower()


def test_rag_pipeline_refusal_fallback(tmp_path):
    """
    Tests mandatory refusal check (Hard floor test case in RUBRIC.md).
    When asked about information not in the docs (annual contract refund policy),
    the assistant MUST refuse gracefully without hallucination.
    """
    idx_dir = tmp_path / "pipeline_refusal_test"
    pipeline = RAGPipeline(
        corpus_dir="ai-engineer-take-home/sample_corpus",
        index_dir=str(idx_dir)
    )
    pipeline.ingest()

    # Out-of-scope question
    res = pipeline.answer_question("What's Aperture's refund policy for annual contracts?")
    assert res["refused"] is True
    assert res["answer"] == REFUSAL_MESSAGE
    assert len(res["citations"]) == 0

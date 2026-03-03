"""
Integration tests for the RAG pipeline.

Uses real OpenAI API calls against an isolated ChromaDB test collection
so production data is never touched.

Run:
    pytest tests/test_integration.py -v
"""

import pytest
from pathlib import Path

import rag.retrieval.retriever as retriever_module
from rag.config import settings
from rag.ingestion.loader import load_pdf
from rag.pipelines.rag import answer, ingest_pdf
from rag.retrieval.retriever import collection_count

FIXTURE_PDF = Path(__file__).parent / "fixtures" / "sample.pdf"
TEST_COLLECTION = "test_documents"
TEST_CHROMA_DIR = "/tmp/test_chroma_rag"


# ---------------------------------------------------------------------------
# Session fixture: redirect all retriever calls to an isolated test collection
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def isolate_retriever():
    """
    Override settings.collection_name and settings.chroma_persist_dir for the
    full test session, then reset all module-level singletons so ChromaDB and
    BM25 initialise against the test collection rather than production data.

    Teardown deletes the test collection and restores original settings.
    """
    orig_collection = settings.collection_name
    orig_chroma_dir = settings.chroma_persist_dir

    settings.collection_name = TEST_COLLECTION
    settings.chroma_persist_dir = TEST_CHROMA_DIR

    retriever_module._client = None
    retriever_module._collection = None
    retriever_module._bm25_corpus = []
    retriever_module._bm25_index = None

    yield

    try:
        if retriever_module._client is not None:
            retriever_module._client.delete_collection(TEST_COLLECTION)
    except Exception:
        pass

    retriever_module._client = None
    retriever_module._collection = None
    retriever_module._bm25_corpus = []
    retriever_module._bm25_index = None

    settings.collection_name = orig_collection
    settings.chroma_persist_dir = orig_chroma_dir


# ---------------------------------------------------------------------------
# Session fixture: ingest fixture PDF once, reuse across all answer() tests
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def ingested_chunk_count():
    """
    Ingest the fixture PDF into the test collection once per session.
    All tests that call answer() should take this as a parameter to guarantee
    ingestion has completed before any retrieval happens.
    """
    assert FIXTURE_PDF.exists(), (
        f"Fixture PDF not found at {FIXTURE_PDF}. "
        "Run: python tests/create_fixture_pdf.py"
    )
    count = ingest_pdf(FIXTURE_PDF)
    assert count > 0, "ingest_pdf() returned 0 chunks — ingestion failed silently"
    return count


# ---------------------------------------------------------------------------
# Ingestion tests
# ---------------------------------------------------------------------------

class TestIngestPdf:
    def test_returns_positive_chunk_count(self, ingested_chunk_count):
        assert ingested_chunk_count >= 1

    def test_collection_count_reflects_ingestion(self, ingested_chunk_count):
        assert collection_count() >= ingested_chunk_count

    def test_fixture_pdf_has_three_pages(self):
        pages = load_pdf(FIXTURE_PDF)
        assert len(pages) == 3

    def test_ingest_nonexistent_file_raises(self):
        with pytest.raises(FileNotFoundError):
            ingest_pdf("/tmp/does_not_exist_abc123.pdf")


# ---------------------------------------------------------------------------
# Answer tests
# ---------------------------------------------------------------------------

class TestAnswer:
    def test_returns_expected_shape(self, ingested_chunk_count):
        result = answer("What is artificial intelligence?")
        assert isinstance(result, dict)
        assert "answer" in result
        assert "sources" in result
        assert "context_found" in result

    def test_answer_is_non_empty_string(self, ingested_chunk_count):
        result = answer("What is artificial intelligence?")
        assert isinstance(result["answer"], str)
        assert len(result["answer"]) > 0

    def test_sources_is_list(self, ingested_chunk_count):
        result = answer("What is artificial intelligence?")
        assert isinstance(result["sources"], list)

    def test_sources_have_required_keys(self, ingested_chunk_count):
        result = answer("What is artificial intelligence?")
        if result["context_found"]:
            for src in result["sources"]:
                assert "source" in src
                assert "page" in src
                assert "score" in src

    def test_source_score_is_float(self, ingested_chunk_count):
        result = answer("What is artificial intelligence?")
        if result["context_found"]:
            for src in result["sources"]:
                assert isinstance(src["score"], float)

    def test_context_found_true_for_known_topic(self, ingested_chunk_count):
        """A question about AI must find context in the fixture PDF."""
        result = answer("What is artificial intelligence and machine learning?")
        assert result["context_found"] is True

    def test_off_topic_returns_fallback_phrase(self, ingested_chunk_count):
        result = answer(
            "Explain Byzantine fault tolerant consensus in orbital mechanics satellite systems"
        )
        answer_lower = result["answer"].lower()
        assert any(phrase in answer_lower for phrase in [
            "don't have enough information",
            "not in the context",
            "cannot answer",
            "i don't",
        ])

    def test_python_question_finds_context(self, ingested_chunk_count):
        """Tests that page 2 content (Python) is retrievable."""
        result = answer("What are Python programming best practices?")
        assert result["context_found"] is True

    def test_software_engineering_question_finds_context(self, ingested_chunk_count):
        """Tests that page 3 content (software engineering) is retrievable."""
        result = answer("What are core software engineering principles?")
        assert result["context_found"] is True

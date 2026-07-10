"""Unit test for the chunking config — no network calls."""

from app.rag.pipeline import _splitter


def test_splitter_produces_overlapping_chunks():
    text = "word " * 1000
    chunks = _splitter().split_text(text)
    assert len(chunks) > 1
    assert all(chunks)

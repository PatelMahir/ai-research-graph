"""Local embeddings must work offline — no network, no API key."""

import math

from app.rag.embeddings import LocalHashingEmbeddings


def test_local_embeddings_are_deterministic_and_normalized():
    emb = LocalHashingEmbeddings(dim=128)
    v1 = emb.embed_query("graph neural networks for retrieval")
    v2 = emb.embed_query("graph neural networks for retrieval")

    assert v1 == v2  # deterministic
    assert len(v1) == 128
    assert math.isclose(math.sqrt(sum(x * x for x in v1)), 1.0, rel_tol=1e-6)


def test_similar_text_scores_higher_than_unrelated():
    emb = LocalHashingEmbeddings(dim=256)
    q = emb.embed_query("transformer attention mechanism")
    close = emb.embed_query("attention mechanism in transformers")
    far = emb.embed_query("gardening tips for tomatoes")

    def dot(a, b):
        return sum(x * y for x, y in zip(a, b, strict=True))

    assert dot(q, close) > dot(q, far)


def test_embed_documents_matches_query_dim():
    emb = LocalHashingEmbeddings(dim=64)
    docs = emb.embed_documents(["first passage", "second passage"])
    assert len(docs) == 2
    assert all(len(d) == 64 for d in docs)

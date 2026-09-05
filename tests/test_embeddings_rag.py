from app.core.embeddings import embed, EMBEDDING_DIM
from app.core.rag import cosine_similarity


def test_embed_returns_fixed_dimension():
    vector = embed("iade tutarı sipariş tutarını aşamaz")
    assert len(vector) == EMBEDDING_DIM


def test_embed_is_deterministic():
    text = "aynı metin"
    assert embed(text) == embed(text)


def test_cosine_similarity_identical_vectors_is_one():
    v = embed("iade tutarı sipariş tutarını aşamaz")
    assert abs(cosine_similarity(v, v) - 1.0) < 1e-6


def test_cosine_similarity_unrelated_texts_lower_than_related():
    rule_amount = embed("İade tutarı, ilişkili siparişin toplam tutarını aşamaz.")
    query_amount = embed("Sipariş tutarı: 100 TRY, İade tutarı: 150")
    query_unrelated = embed("Bugün hava çok güzel, kahve içtim")

    sim_related = cosine_similarity(rule_amount, query_amount)
    sim_unrelated = cosine_similarity(rule_amount, query_unrelated)

    assert sim_related > sim_unrelated

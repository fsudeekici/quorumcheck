"""RAG retrieval: bir sorgu icin en alakali N kurali dondurur."""
import numpy as np
from sqlalchemy.orm import Session

from app.core.embeddings import embed
from app.models.validation_rule import ValidationRule


def cosine_similarity(a: list[float], b: list[float]) -> float:
    a_arr, b_arr = np.array(a), np.array(b)
    denom = (np.linalg.norm(a_arr) * np.linalg.norm(b_arr))
    if denom == 0:
        return 0.0
    return float(np.dot(a_arr, b_arr) / denom)


def retrieve_relevant_rules(db: Session, tenant_id: int, query_text: str, top_k: int = 3) -> list[str]:
    """
    Verilen sorgu metnine (orn. bir iade kaydinin ozeti) en yakin top_k
    kurali, embedding cosine similarity'e gore siralayip dondurur.

    Not: su an tum kurallari DB'den cekip Python'da similarity
    hesapliyoruz (O(n) tarama). pgvector'a gecince (Hafta ilerledikce
    bir iyilestirme adimi olarak eklenebilir) bu, veritabani seviyesinde
    bir ANN index sorgusuna donusur - kural sayisi buyudukce gerekli.
    """
    rules = (
        db.query(ValidationRule)
        .filter(ValidationRule.tenant_id == tenant_id)
        .filter(ValidationRule.embedding.isnot(None))
        .all()
    )
    if not rules:
        return []

    query_vector = embed(query_text)
    scored = [
        (cosine_similarity(query_vector, r.embedding), r.rule_text)
        for r in rules
    ]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [rule_text for _, rule_text in scored[:top_k]]

"""
Tum tenant'larin validation_rules'lari icin embedding hesaplar ve DB'ye
yazar. generate_synthetic_data.py kurallari embedding'siz olusturur -
bu script ayri calistirilir, boylece "veri uretme" ve "embedding hesaplama"
adimlari birbirinden bagimsiz test edilebilir.

Kullanim:
    PYTHONPATH=. python scripts/embed_rules.py
"""
from app.core.embeddings import embed
from app.db.base import SessionLocal
from app.models.validation_rule import ValidationRule


def embed_all_rules():
    db = SessionLocal()
    try:
        rules = db.query(ValidationRule).filter(ValidationRule.embedding.is_(None)).all()
        for rule in rules:
            rule.embedding = embed(rule.rule_text)
        db.commit()
        print(f"{len(rules)} kural embed edildi.")
    finally:
        db.close()


if __name__ == "__main__":
    embed_all_rules()

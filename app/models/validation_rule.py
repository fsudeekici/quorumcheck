from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Index, JSON, func

from app.db.base import Base


class ValidationRule(Base):
    """
    RAG'in kaynak dokumanlari. rule_text embedding'e cevrilip vector
    aramada kullanilacak. embedding su an JSON (float listesi) olarak
    tutuluyor - Postgres + SQLite ikisinde de calisir, boylece yerel
    testler icin ayri bir DB kurmaya gerek kalmiyor. Hafta 3'te
    pgvector extension + Vector tipine + cosine similarity index'e
    gecilecek (o zaman Postgres-only olacak, kasitli bir tradeoff).
    """
    __tablename__ = "validation_rules"

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)

    rule_text = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_validation_rules_tenant_id", "tenant_id"),
    )

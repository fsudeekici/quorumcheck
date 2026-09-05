from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT

from app.db.base import Base


class ValidationRule(Base):
    """
    RAG'in kaynak dokumanlari. rule_text embedding'e cevrilip vector
    aramada kullanilacak. Hafta 3'te pgvector extension'a gecilebilir
    (ARRAY(FLOAT) yerine Vector tipi + cosine similarity index) -
    simdilik basit tutuluyor.
    """
    __tablename__ = "validation_rules"

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)

    rule_text = Column(Text, nullable=False)
    embedding = Column(ARRAY(FLOAT), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_validation_rules_tenant_id", "tenant_id"),
    )

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Index, func

from app.db.base import Base


class ValidatorVote(Base):
    """Her validator worker'in tek bir return_record uzerine verdigi karar."""
    __tablename__ = "validator_votes"

    id = Column(Integer, primary_key=True)
    return_id = Column(Integer, ForeignKey("returns.id"), nullable=False)

    validator_index = Column(Integer, nullable=False)  # 0, 1, 2 ... N-1
    decision = Column(String(20), nullable=False)       # approved | rejected | uncertain
    confidence = Column(Float, nullable=True)
    reasoning = Column(Text, nullable=True)              # LLM'in gerekcesi (debug/aciklanabilirlik icin)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_validator_votes_return_id", "return_id"),
    )

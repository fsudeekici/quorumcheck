from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func

from app.db.base import Base


class ConsensusResult(Base):
    """
    Aggregator'in cikardigi nihai sonuc. Bir return_record'a bagli
    en fazla bir consensus_result olur (1-1 iliski).
    """
    __tablename__ = "consensus_results"

    id = Column(Integer, primary_key=True)
    return_id = Column(Integer, ForeignKey("returns.id"), nullable=False, unique=True)

    final_decision = Column(String(20), nullable=False)   # approved | rejected | needs_review
    votes_collected = Column(Integer, nullable=False)
    quorum_required = Column(Integer, nullable=False)
    quorum_reached = Column(Boolean, nullable=False)

    cap_mode_used = Column(String(2), nullable=False)      # "CP" | "AP" - o an hangi mod aktifti
    latency_ms = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

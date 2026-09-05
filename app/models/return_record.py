from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Index, func

from app.db.base import Base


class ReturnRecord(Base):
    __tablename__ = "returns"

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)

    return_amount = Column(Numeric(10, 2), nullable=False)
    reason = Column(String(255))

    # Bu alan sentetik "kirli" veri ureticinin bilerek bozacagi alan:
    # is kurali orn. "iade tutari fatura tutarini asamaz"
    status = Column(String(20), default="pending")  # pending | validated | flagged

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_returns_tenant_id", "tenant_id"),
        Index("ix_returns_order_id", "order_id"),
    )

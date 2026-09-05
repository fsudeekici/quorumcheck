from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Index, func

from app.db.base import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)

    order_amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="TRY")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        # Multi-tenant izolasyonu: her sorgu tenant_id ile filtrelenecek,
        # bu yuzden tenant_id index'i kritik.
        Index("ix_orders_tenant_id", "tenant_id"),
    )

"""
Sentetik "kirli" iade/sipariş verisi ureticisi.

Amac: gercek is kurallarini bilerek ihlal eden kayitlar uretmek, boylece
validator worker'larin (Hafta 3+) bu ihlalleri yakalayip yakalamadigini
olcebilelim.

Su an kodlanmis kural:
  "iade tutari, siparis tutarini asamaz"
--violation-rate ile bu kuralin ne siklikta bilerek ihlal edilecegi
ayarlanabilir (orn. 0.2 = kayitlarin %20'si kirli).

Kullanim:
    python scripts/generate_synthetic_data.py --tenants 2 --orders 50 --violation-rate 0.2
"""
import argparse
import random
from decimal import Decimal

from app.db.base import Base, SessionLocal, engine
from app.models.tenant import Tenant
from app.models.order import Order
from app.models.return_record import ReturnRecord
from app.models.validation_rule import ValidationRule

REASONS = ["defolu urun", "yanlis beden", "musteri vazgecti", "hasarli kargo", "yanlis urun gonderildi"]

DEFAULT_RULES = [
    "İade tutarı, ilişkili siparişin toplam tutarını aşamaz.",
    "İade, siparişin oluşturulmasından en fazla 30 gün sonra yapılabilir.",
    "Bir siparişe ait aynı ürün için birden fazla tam iade talebi açılamaz.",
]


def generate(tenant_count: int, orders_per_tenant: int, violation_rate: float):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        for t in range(tenant_count):
            tenant = Tenant(name=f"tenant-{t + 1}")
            db.add(tenant)
            db.flush()  # id almak icin

            for rule_text in DEFAULT_RULES:
                db.add(ValidationRule(tenant_id=tenant.id, rule_text=rule_text))

            for _ in range(orders_per_tenant):
                order_amount = Decimal(random.randint(50, 2000))
                order = Order(tenant_id=tenant.id, order_amount=order_amount)
                db.add(order)
                db.flush()

                is_violation = random.random() < violation_rate
                if is_violation:
                    # Bilerek kural ihlali: iade tutari siparis tutarindan buyuk
                    return_amount = order_amount + Decimal(random.randint(10, 200))
                else:
                    return_amount = Decimal(random.randint(1, int(order_amount)))

                db.add(ReturnRecord(
                    tenant_id=tenant.id,
                    order_id=order.id,
                    return_amount=return_amount,
                    reason=random.choice(REASONS),
                    status="pending",
                ))

        db.commit()
        print(f"{tenant_count} tenant, {tenant_count * orders_per_tenant} siparis/iade cifti uretildi.")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tenants", type=int, default=2)
    parser.add_argument("--orders", type=int, default=50, help="tenant basina siparis sayisi")
    parser.add_argument("--violation-rate", type=float, default=0.2)
    args = parser.parse_args()

    generate(args.tenants, args.orders, args.violation_rate)

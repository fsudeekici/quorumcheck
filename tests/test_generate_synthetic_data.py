from app.db.base import SessionLocal, engine, Base  # noqa: E402
from app.models.order import Order  # noqa: E402
from app.models.return_record import ReturnRecord  # noqa: E402
from scripts.generate_synthetic_data import generate  # noqa: E402


def setup_module():
    Base.metadata.drop_all(bind=engine)


def teardown_module():
    Base.metadata.drop_all(bind=engine)


def test_generate_produces_expected_record_count():
    generate(tenant_count=2, orders_per_tenant=10, violation_rate=0.3)

    db = SessionLocal()
    try:
        assert db.query(Order).count() == 20
        assert db.query(ReturnRecord).count() == 20
    finally:
        db.close()


def test_generate_creates_rule_violations():
    db = SessionLocal()
    try:
        violations = 0
        for r in db.query(ReturnRecord).all():
            order = db.query(Order).filter(Order.id == r.order_id).first()
            if r.return_amount > order.order_amount:
                violations += 1
        # violation_rate=0.3 verildi, tam %30 garanti degil (random) ama
        # en az birkac ihlal olmasi bekleniyor.
        assert violations > 0
    finally:
        db.close()

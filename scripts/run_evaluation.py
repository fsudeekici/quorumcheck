"""
Ground truth (is_violation) ile mock tahminciyi karsilastirir,
precision/recall/F1 raporlar. Pipeline'in dogru calistigini kanitlar.
Gercek LLM baseline/consensus'a gecis sonra yapilacak.

Kullanim:
    python scripts/run_evaluation.py
"""
from app.db.base import SessionLocal
from app.models.return_record import ReturnRecord
from app.models.order import Order
from app.core.metrics import compute_metrics


def predict_mock(return_record: ReturnRecord, order: Order) -> bool:
    return return_record.return_amount > order.order_amount


def run():
    db = SessionLocal()
    try:
        records = (
            db.query(ReturnRecord)
            .filter(ReturnRecord.is_violation.isnot(None))
            .all()
        )

        if not records:
            print("Ground truth'lu kayit yok. Once scripts/generate_synthetic_data.py calistir.")
            return

        y_true = []
        y_pred = []
        for r in records:
            order = db.query(Order).filter(Order.id == r.order_id).first()
            y_true.append(r.is_violation)
            y_pred.append(predict_mock(r, order))

        metrics = compute_metrics(y_true, y_pred)

        print(f"Degerlendirilen kayit sayisi: {len(records)}")
        print(f"Ground truth ihlal sayisi:    {sum(y_true)}")
        print("---")
        for key, value in metrics.as_dict().items():
            print(f"{key}: {value}")
    finally:
        db.close()


if __name__ == "__main__":
    run()

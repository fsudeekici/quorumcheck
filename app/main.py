from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import Base, engine, get_db
from app.models import tenant, order, return_record, validation_rule, validator_vote, consensus_result  # noqa: F401
from app.models.return_record import ReturnRecord
from app.services.validator import validate_return

app = FastAPI(title="QuorumCheck")


@app.on_event("startup")
def on_startup():
    # Dev kolaylığı: tablo yoksa olustur. Prod'da bunun yerine Alembic
    # migration kullanilacak (Hafta 2'nin sonraki bir adiminda eklenir).
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/returns/{return_id}")
def get_return(return_id: int, db: Session = Depends(get_db)):
    record = db.query(ReturnRecord).filter(ReturnRecord.id == return_id).first()
    if not record:
        return {"error": "not found"}
    return {
        "id": record.id,
        "tenant_id": record.tenant_id,
        "order_id": record.order_id,
        "return_amount": str(record.return_amount),
        "reason": record.reason,
        "status": record.status,
    }


@app.post("/returns/{return_id}/validate")
def validate(return_id: int, db: Session = Depends(get_db)):
    """
    Hafta 3 baseline: tek validator worker'i senkron olarak calistirir.
    Hafta 4'te bu endpoint N validator'i Celery task olarak paralel
    tetikleyip quorum aggregator'a yonlendirecek sekilde degisecek.
    """
    try:
        vote = validate_return(db, return_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return {
        "return_id": vote.return_id,
        "decision": vote.decision,
        "confidence": vote.confidence,
        "reasoning": vote.reasoning,
    }

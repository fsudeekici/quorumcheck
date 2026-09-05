"""
Tek validator worker - Hafta 3'un "tek-LLM baseline"i.

Hafta 4'te bu fonksiyon N kez paralel (Celery task olarak) cagrilacak,
her cagri kendi validator_index'iyle bir ValidatorVote uretecek, sonra
quorum.resolve_consensus() bunlari birlestirecek. Su an validator_index
sabit 0, cunku tek validator var.
"""
from sqlalchemy.orm import Session

from app.core.llm_client import decide_validation
from app.core.rag import retrieve_relevant_rules
from app.models.order import Order
from app.models.return_record import ReturnRecord
from app.models.validator_vote import ValidatorVote


def _build_context(return_record: ReturnRecord, order: Order) -> str:
    return (
        f"Sipariş tutarı: {order.order_amount} {order.currency}\n"
        f"İade tutarı: {return_record.return_amount}\n"
        f"İade nedeni: {return_record.reason}\n"
        f"Sipariş tarihi: {order.created_at}\n"
        f"İade talep tarihi: {return_record.created_at}"
    )


def validate_return(db: Session, return_id: int, validator_index: int = 0) -> ValidatorVote:
    return_record = db.query(ReturnRecord).filter(ReturnRecord.id == return_id).first()
    if not return_record:
        raise ValueError(f"return_id={return_id} bulunamadı")

    order = db.query(Order).filter(Order.id == return_record.order_id).first()

    context = _build_context(return_record, order)
    rules = retrieve_relevant_rules(db, tenant_id=return_record.tenant_id, query_text=context)

    result = decide_validation(context, rules)

    vote = ValidatorVote(
        return_id=return_id,
        validator_index=validator_index,
        decision=result.decision,
        confidence=result.confidence,
        reasoning=result.reasoning,
    )
    db.add(vote)
    db.commit()
    db.refresh(vote)
    return vote

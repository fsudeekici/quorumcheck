"""
Bu testler celery_app.conf.task_always_eager=True kullanir - yani
.delay() cagrilari gercek bir broker'a gitmeden, ayni process icinde
senkron calisir. Bu, CI ortaminda (Redis/worker kurmadan) Celery
task orkestrasyonunu test etmenin standart yoludur. Hafta 4'un
sandbox'ta gercek Redis + gercek Celery worker ile de test edildigini
(timeout/hata senaryosu dahil) not düşelim - bu dosya CI'da tekrar
calisacak deterministik versiyon.
"""
from decimal import Decimal
from unittest.mock import patch

from app.core.celery_app import celery_app
from app.core.config import settings, CapMode
from app.db.base import SessionLocal, engine, Base
from app.models.tenant import Tenant
from app.models.order import Order
from app.models.return_record import ReturnRecord
from app.models.validation_rule import ValidationRule
from app.core.embeddings import embed
from app.core.llm_client import LlmDecision
from app.services.aggregator import run_consensus_pipeline

celery_app.conf.update(task_always_eager=True, task_eager_propagates=True)


def setup_module():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_module():
    Base.metadata.drop_all(bind=engine)


import uuid


def _seed_return(return_amount="150"):
    db = SessionLocal()
    tenant = Tenant(name=f"tenant-{uuid.uuid4().hex[:8]}")
    db.add(tenant)
    db.flush()

    rule_text = "İade tutarı, ilişkili siparişin toplam tutarını aşamaz."
    db.add(ValidationRule(tenant_id=tenant.id, rule_text=rule_text, embedding=embed(rule_text)))

    order = Order(tenant_id=tenant.id, order_amount=Decimal("100"))
    db.add(order)
    db.flush()

    return_record = ReturnRecord(
        tenant_id=tenant.id, order_id=order.id, return_amount=Decimal(return_amount), reason="test",
    )
    db.add(return_record)
    db.commit()
    return_id = return_record.id
    db.close()
    return return_id


@patch("app.services.validator.decide_validation")
def test_quorum_reached_when_majority_agrees(mock_decide):
    return_id = _seed_return()
    mock_decide.return_value = LlmDecision(decision="rejected", confidence=0.9, reasoning="test")

    db = SessionLocal()
    consensus = run_consensus_pipeline(db, return_id)
    db.close()

    assert consensus.quorum_reached is True
    assert consensus.final_decision == "rejected"
    assert consensus.votes_collected == settings.VALIDATOR_COUNT


@patch("app.services.validator.decide_validation")
def test_no_quorum_cp_mode_needs_review(mock_decide):
    original_mode = settings.CAP_MODE
    settings.CAP_MODE = CapMode.CP
    try:
        return_id = _seed_return()

        # Her cagrida farkli decision dondurerek cogunluk olusmasini engelle
        mock_decide.side_effect = [
            LlmDecision(decision="approved", confidence=0.6, reasoning="a"),
            LlmDecision(decision="rejected", confidence=0.6, reasoning="b"),
            LlmDecision(decision="uncertain", confidence=0.6, reasoning="c"),
        ]

        db = SessionLocal()
        consensus = run_consensus_pipeline(db, return_id)
        db.close()

        assert consensus.quorum_reached is False
        assert consensus.final_decision == "needs_review"
    finally:
        settings.CAP_MODE = original_mode


@patch("app.services.validator.decide_validation")
def test_no_quorum_ap_mode_best_effort(mock_decide):
    original_mode = settings.CAP_MODE
    settings.CAP_MODE = CapMode.AP
    try:
        return_id = _seed_return()
        mock_decide.side_effect = [
            LlmDecision(decision="approved", confidence=0.6, reasoning="a"),
            LlmDecision(decision="rejected", confidence=0.6, reasoning="b"),
            LlmDecision(decision="uncertain", confidence=0.6, reasoning="c"),
        ]

        db = SessionLocal()
        consensus = run_consensus_pipeline(db, return_id)
        db.close()

        assert consensus.quorum_reached is False
        # AP modunda cogunluk olmasa bile en cok tekrar eden (ilk gorulen) karar donuyor
        assert consensus.final_decision in ("approved", "rejected", "uncertain")
    finally:
        settings.CAP_MODE = original_mode

from unittest.mock import patch
from decimal import Decimal

from app.db.base import SessionLocal, engine, Base  # noqa: E402
from app.models.tenant import Tenant  # noqa: E402
from app.models.order import Order  # noqa: E402
from app.models.return_record import ReturnRecord  # noqa: E402
from app.models.validation_rule import ValidationRule  # noqa: E402
from app.core.embeddings import embed  # noqa: E402
from app.core.llm_client import LlmDecision  # noqa: E402
from app.services.validator import validate_return  # noqa: E402


def setup_module():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_module():
    Base.metadata.drop_all(bind=engine)


def _seed():
    db = SessionLocal()
    tenant = Tenant(name="test-tenant")
    db.add(tenant)
    db.flush()

    rule_text = "İade tutarı, ilişkili siparişin toplam tutarını aşamaz."
    db.add(ValidationRule(tenant_id=tenant.id, rule_text=rule_text, embedding=embed(rule_text)))

    order = Order(tenant_id=tenant.id, order_amount=Decimal("100"))
    db.add(order)
    db.flush()

    return_record = ReturnRecord(
        tenant_id=tenant.id, order_id=order.id, return_amount=Decimal("150"), reason="test",
    )
    db.add(return_record)
    db.commit()
    db.refresh(return_record)

    return_id = return_record.id
    db.close()
    return return_id


@patch("app.services.validator.decide_validation")
def test_validate_return_uses_retrieved_rules_and_saves_vote(mock_decide):
    return_id = _seed()

    mock_decide.return_value = LlmDecision(
        decision="rejected", confidence=0.95, reasoning="İade tutarı sipariş tutarını aşıyor."
    )

    db = SessionLocal()
    vote = validate_return(db, return_id, validator_index=0)
    db.close()

    assert vote.decision == "rejected"
    assert vote.validator_index == 0

    # LLM'e giden context ve rules dogru mu diye kontrol et
    call_args = mock_decide.call_args
    context_arg, rules_arg = call_args[0]
    assert "150" in context_arg
    assert any("aşamaz" in r for r in rules_arg)

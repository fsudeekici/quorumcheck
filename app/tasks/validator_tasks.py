"""
Tek bir validator worker'i Celery task'i olarak calistirir.

Hafta 3'teki app/services/validator.validate_return() fonksiyonunu
degistirmedik - sadece disina bir Celery katmani sardik. Boylece ayni
mantik hem senkron (Hafta 3 endpoint'i) hem de paralel/async (bu Hafta)
kullanilabiliyor.

ONEMLI: LLM cagrisi basarisiz olursa (timeout, rate limit, network
hatasi) task'i patlatmiyoruz, {"error": ...} donuyoruz. Aggregator
bunu "bu validator oy vermedi" olarak yorumlayacak - CAP theorem'deki
"quorum saglanamama" senaryosunu gercekci sekilde simule etmek icin
bu kasitli bir tasarim karari.
"""
from app.core.celery_app import celery_app
from app.db.base import SessionLocal
from app.services.validator import validate_return


@celery_app.task(name="app.tasks.validator_tasks.run_validator")
def run_validator(return_id: int, validator_index: int) -> dict:
    db = SessionLocal()
    try:
        vote = validate_return(db, return_id, validator_index=validator_index)
        return {
            "validator_index": vote.validator_index,
            "decision": vote.decision,
            "confidence": vote.confidence,
        }
    except Exception as exc:  # noqa: BLE001 - kasitli genis yakalama, asagidaki yorumu oku
        return {"validator_index": validator_index, "error": str(exc)}
    finally:
        db.close()

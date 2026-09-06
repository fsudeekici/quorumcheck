"""
N validator'i paralel calistirir, sonuclarini toplar, quorum.resolve_consensus
ile nihai karari verir ve ConsensusResult olarak DB'ye yazar.

NOT (production icin iyilestirme notu): su an HTTP request, tum
validator'lar bitene/timeout olana kadar SENKRON bekliyor. Gercek bir
production sisteminde bu genelde webhook/polling ile async yapilir
(istemciye hemen bir job_id donup, sonucu ayri bir endpoint'ten
sorgulatmak gibi). Bu proje icin senkron yeterli - basitligi tercih
ettim, ama bu tradeoff'u mulakatta soylemen lazim.
"""
from celery.exceptions import TimeoutError as CeleryTimeoutError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.quorum import VoteResult, resolve_consensus
from app.models.consensus_result import ConsensusResult
from app.tasks.validator_tasks import run_validator


def run_consensus_pipeline(db: Session, return_id: int) -> ConsensusResult:
    validator_count = settings.VALIDATOR_COUNT
    timeout = settings.VALIDATOR_TIMEOUT_SECONDS

    async_results = [
        run_validator.delay(return_id, i) for i in range(validator_count)
    ]

    votes: list[VoteResult] = []
    for async_result in async_results:
        try:
            result = async_result.get(timeout=timeout)
        except CeleryTimeoutError:
            # Bu validator suresi icinde cevap vermedi - CAP theorem'in
            # "partition/gecikme" senaryosu tam olarak burada devreye giriyor.
            continue

        if "error" in result:
            # LLM cagrisi basarisiz oldu (rate limit, network vb.) - oy sayilmaz.
            continue

        votes.append(VoteResult(
            validator_index=result["validator_index"],
            decision=result["decision"],
            confidence=result["confidence"],
        ))

    outcome = resolve_consensus(votes)

    consensus = ConsensusResult(
        return_id=return_id,
        final_decision=outcome.final_decision,
        votes_collected=outcome.votes_collected,
        quorum_required=outcome.quorum_required,
        quorum_reached=outcome.quorum_reached,
        cap_mode_used=outcome.cap_mode_used,
    )
    db.add(consensus)
    db.commit()
    db.refresh(consensus)
    return consensus

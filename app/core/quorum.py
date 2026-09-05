"""
Quorum + CAP tradeoff karar mantigi.

Bu dosya Hafta 1'in en kritik ciktisi: CAP theorem'in "teorik bilgi"
olmaktan cikip somut bir if/else karar noktasina donusmesi.

Gercek Celery worker entegrasyonu Hafta 4'te yapilacak - burada sadece
aggregator'in cekirdek karar fonksiyonu var, boylece mantigi izole
test edebilir ve mulakatta "iste bu satirda CAP tradeoff'u kodladim"
diyebilirsin.
"""

from collections import Counter
from dataclasses import dataclass

from app.core.config import CapMode, settings


@dataclass
class VoteResult:
    validator_index: int
    decision: str  # "approved" | "rejected" | "uncertain"
    confidence: float


@dataclass
class ConsensusOutcome:
    final_decision: str
    quorum_reached: bool
    votes_collected: int
    quorum_required: int
    cap_mode_used: str


def resolve_consensus(votes: list[VoteResult]) -> ConsensusOutcome:
    """
    N validator'dan gelen oylari degerlendirir.

    Senaryo 1 - Quorum saglandi (yeterli oy toplandi ve cogunluk var):
        -> final_decision cogunluk oyu, quorum_reached=True. CAP modundan
           bagimsiz, bu durumda zaten "safe path".

    Senaryo 2 - Quorum saglanamadi (timeout / worker crash / cogunluk yok):
        -> ISTE CAP THEOREM BURADA DEVREYE GIRIYOR:
           CP modu -> karar verme, "needs_review" don (Consistency > Availability)
           AP modu -> eldeki azinlik oyuyla yine de karar ver (Availability > Consistency)
    """
    quorum_required = settings.QUORUM_THRESHOLD
    votes_collected = len(votes)

    decision_counts = Counter(v.decision for v in votes)
    top_decision, top_count = (
        decision_counts.most_common(1)[0] if decision_counts else (None, 0)
    )

    quorum_reached = top_count >= quorum_required

    if quorum_reached:
        final_decision = top_decision
    else:
        # --- CAP tradeoff karar noktasi ---
        if settings.CAP_MODE == CapMode.CP:
            final_decision = "needs_review"
        else:  # AP
            final_decision = top_decision if top_decision else "needs_review"

    return ConsensusOutcome(
        final_decision=final_decision,
        quorum_reached=quorum_reached,
        votes_collected=votes_collected,
        quorum_required=quorum_required,
        cap_mode_used=settings.CAP_MODE.value,
    )

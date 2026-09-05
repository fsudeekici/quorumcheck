from app.core import quorum
from app.core.config import settings, CapMode


def make_votes(decisions):
    return [
        quorum.VoteResult(validator_index=i, decision=d, confidence=0.9)
        for i, d in enumerate(decisions)
    ]


def test_quorum_reached_majority_approved():
    votes = make_votes(["approved", "approved", "rejected"])
    result = quorum.resolve_consensus(votes)
    assert result.quorum_reached is True
    assert result.final_decision == "approved"


def test_no_quorum_cp_mode_returns_needs_review():
    settings.CAP_MODE = CapMode.CP
    votes = make_votes(["approved", "rejected"])  # no majority, N=3 expected but only 2 responded
    result = quorum.resolve_consensus(votes)
    assert result.quorum_reached is False
    assert result.final_decision == "needs_review"


def test_no_quorum_ap_mode_returns_best_effort_decision():
    settings.CAP_MODE = CapMode.AP
    votes = make_votes(["approved"])  # only one validator responded, no quorum
    result = quorum.resolve_consensus(votes)
    assert result.quorum_reached is False
    assert result.final_decision == "approved"

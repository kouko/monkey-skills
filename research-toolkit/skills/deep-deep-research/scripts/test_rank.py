"""Tests for rank.py — quorum rule and claim ranking.

Flat-import port of src/deep_research/tests/test_rank.py for the
scripts/ skill bundle (pytest.ini sets pythonpath = .).

RED targets:
- test_quorum_rule: quorum edge cases verbatim from spec (incl. all-abstain)
- test_rank_claims_ordering: central+primary before tangential+blog
- test_rank_claims_limit: slice to limit
"""

from rank import quorum_survives, rank_claims


# ---------------------------------------------------------------------------
# quorum_survives
# ---------------------------------------------------------------------------

def test_quorum_rule_3_valid_0_refuted():
    """3 valid, 0 refuted → survives (well-confirmed claim)."""
    verdicts = [
        {"refuted": False, "evidence": "a", "confidence": "high"},
        {"refuted": False, "evidence": "b", "confidence": "medium"},
        {"refuted": False, "evidence": "c", "confidence": "low"},
    ]
    assert quorum_survives(verdicts) is True


def test_quorum_rule_2_valid_1_refuted():
    """2 valid, 1 refuted → survives (refuted=1 < required=2)."""
    verdicts = [
        {"refuted": False, "evidence": "a", "confidence": "high"},
        {"refuted": False, "evidence": "b", "confidence": "medium"},
        {"refuted": True,  "evidence": "c", "confidence": "low"},
    ]
    assert quorum_survives(verdicts) is True


def test_quorum_rule_2_refuted():
    """2 refuted → killed (refuted >= required)."""
    verdicts = [
        {"refuted": True,  "evidence": "a", "confidence": "high"},
        {"refuted": True,  "evidence": "b", "confidence": "medium"},
        {"refuted": False, "evidence": "c", "confidence": "low"},
    ]
    assert quorum_survives(verdicts) is False


def test_quorum_rule_1_valid_2_abstain():
    """1 valid + 2 None (abstain) → killed (unadjudicated, valid < required=2).

    Guards the all-abstain → refuted=0 → false-survive bug:
    valid.length >= REFUTATIONS_REQUIRED must be checked FIRST.
    """
    verdicts = [
        {"refuted": False, "evidence": "a", "confidence": "high"},
        None,
        None,
    ]
    assert quorum_survives(verdicts) is False


def test_quorum_rule_all_abstain():
    """All None → killed (unadjudicated, 0 valid < required=2)."""
    verdicts = [None, None, None]
    assert quorum_survives(verdicts) is False


# ---------------------------------------------------------------------------
# rank_claims
# ---------------------------------------------------------------------------

def test_rank_claims_ordering():
    """central+primary ranks before tangential+blog."""
    claims = [
        {"claim": "worse", "importance": "tangential", "sourceQuality": "blog"},
        {"claim": "better", "importance": "central",   "sourceQuality": "primary"},
    ]
    result = rank_claims(claims)
    assert result[0]["claim"] == "better"
    assert result[1]["claim"] == "worse"


def test_rank_claims_limit():
    """Result is sliced to limit (default 25, or custom)."""
    claims = [
        {"claim": str(i), "importance": "supporting", "sourceQuality": "secondary"}
        for i in range(30)
    ]
    assert len(rank_claims(claims)) == 25
    assert len(rank_claims(claims, limit=5)) == 5


def test_rank_claims_stable_sort():
    """Claims with identical sort keys preserve original order (stable)."""
    claims = [
        {"claim": "first",  "importance": "central", "sourceQuality": "primary"},
        {"claim": "second", "importance": "central", "sourceQuality": "primary"},
        {"claim": "third",  "importance": "central", "sourceQuality": "primary"},
    ]
    result = rank_claims(claims)
    assert [c["claim"] for c in result] == ["first", "second", "third"]

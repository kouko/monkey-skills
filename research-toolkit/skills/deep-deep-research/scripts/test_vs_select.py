"""Tests for vs_select.py — core angle selection (floor → tier sort → head/tail → cap).

Mirrors test_dedup.py style: exercise both the importable function and the
__main__ stdin/stdout CLI (subprocess piping JSON).

The module is named vs_select (NOT select) to avoid shadowing the stdlib
`select` module on a `pythonpath = .` test path.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from vs_select import select_angles

_SELECT = str(Path(__file__).parent / "vs_select.py")

# A fixture of >=8 scored candidates spanning all three tiers, including
# low-relevance candidates that MUST be dropped before head/tail picking.
_FIXTURE = [
    # most-obvious tier (4 — only top head_k=3 should land in head)
    {"label": "mo-1", "query": "q-mo-1", "rationale": "r-mo-1",
     "relevance": "high", "typicality_tier": "most-obvious"},
    {"label": "mo-2", "query": "q-mo-2", "rationale": "r-mo-2",
     "relevance": "high", "typicality_tier": "most-obvious"},
    {"label": "mo-3", "query": "q-mo-3", "rationale": "r-mo-3",
     "relevance": "medium", "typicality_tier": "most-obvious"},
    {"label": "mo-4", "query": "q-mo-4", "rationale": "r-mo-4",
     "relevance": "high", "typicality_tier": "most-obvious"},
    # a low-relevance most-obvious — MUST be dropped, never counted
    {"label": "mo-low", "query": "q-mo-low", "rationale": "r-mo-low",
     "relevance": "low", "typicality_tier": "most-obvious"},
    # mid tier
    {"label": "mid-1", "query": "q-mid-1", "rationale": "r-mid-1",
     "relevance": "high", "typicality_tier": "mid"},
    {"label": "mid-2", "query": "q-mid-2", "rationale": "r-mid-2",
     "relevance": "medium", "typicality_tier": "mid"},
    # least-obvious tier (3 — only bottom tail_k=2 should land in tail).
    # Queries are deliberately lexically distinct so the ⑤ tail
    # mutual-exclusion (near-dup skip) does NOT fire on these — they are three
    # genuinely different "surprise" angles, only the bottom 2 reach the tail.
    {"label": "lo-1", "query": "demand-shock scenario", "rationale": "r-lo-1",
     "relevance": "medium", "typicality_tier": "least-obvious"},
    {"label": "lo-2", "query": "supply-chain disruption", "rationale": "r-lo-2",
     "relevance": "high", "typicality_tier": "least-obvious"},
    {"label": "lo-3", "query": "pricing-power moat", "rationale": "r-lo-3",
     "relevance": "high", "typicality_tier": "least-obvious"},
    # a low-relevance least-obvious — MUST be dropped, never reaches tail
    {"label": "lo-low", "query": "regulatory tail risk", "rationale": "r-lo-low",
     "relevance": "low", "typicality_tier": "least-obvious"},
]


def _labels(angles):
    return [a["label"] for a in angles]


def test_floor_head_tail_cap() -> None:
    angles = select_angles(_FIXTURE, head_k=3, tail_k=2)
    labels = _labels(angles)

    # ① relevance floor: no low-relevance candidate survives
    assert "mo-low" not in labels
    assert "lo-low" not in labels

    # ③ head = head_k=3 most-typical (most-obvious tier, input order, relevance-passing).
    # Survivors in most-obvious tier (input order): mo-1, mo-2, mo-3, mo-4.
    # head (first 3 by most-typical-first ordering) = mo-1, mo-2, mo-3.
    assert labels[:3] == ["mo-1", "mo-2", "mo-3"]

    # ③ tail = tail_k=2 least-typical relevance-passing ones.
    # Survivors in least-obvious tier (input order): lo-1, lo-2, lo-3.
    # tail (last 2 by least-typical) = lo-2, lo-3 (input order within tier preserved).
    assert labels[-2:] == ["lo-2", "lo-3"]

    # ④ total capped at <= 6
    assert len(angles) <= 6

    # head and tail must be distinct (no double-counting)
    assert len(set(labels)) == len(labels)

    # ⑤ each output angle stripped to {label, query, rationale} — no leakage
    for a in angles:
        assert set(a.keys()) <= {"label", "query", "rationale"}
        assert "relevance" not in a
        assert "typicality_tier" not in a
        assert a["query"]  # query preserved


def test_default_head_tail() -> None:
    """head_k/tail_k optional; default to 3/2 (scope_vs constants)."""
    angles = select_angles(_FIXTURE)
    labels = _labels(angles)
    assert labels[:3] == ["mo-1", "mo-2", "mo-3"]
    assert labels[-2:] == ["lo-2", "lo-3"]


def test_rationale_optional() -> None:
    """A candidate without rationale survives; key omitted (treated as empty)."""
    cands = [
        {"label": "a", "query": "qa", "relevance": "high",
         "typicality_tier": "most-obvious"},
        {"label": "b", "query": "qb", "relevance": "high",
         "typicality_tier": "least-obvious"},
    ]
    angles = select_angles(cands, head_k=1, tail_k=1)
    by_label = {a["label"]: a for a in angles}
    assert by_label["a"].get("rationale", "") == ""
    assert set(by_label["a"].keys()) <= {"label", "query", "rationale"}


def _run_cli(payload: dict) -> dict:
    proc = subprocess.run(
        [sys.executable, _SELECT],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def test_cli_floor_head_tail_cap() -> None:
    """CLI: same fixture over stdin → {angles} with floor/head/tail/cap applied."""
    out = _run_cli({"candidates": _FIXTURE, "head_k": 3, "tail_k": 2})
    assert "angles" in out
    labels = _labels(out["angles"])
    assert "mo-low" not in labels and "lo-low" not in labels
    assert labels[:3] == ["mo-1", "mo-2", "mo-3"]
    assert labels[-2:] == ["lo-2", "lo-3"]
    assert len(out["angles"]) <= 6
    for a in out["angles"]:
        assert set(a.keys()) <= {"label", "query", "rationale"}


def test_cli_defaults_when_k_absent() -> None:
    """CLI: head_k/tail_k absent → default 3/2."""
    out = _run_cli({"candidates": _FIXTURE})
    labels = _labels(out["angles"])
    assert labels[:3] == ["mo-1", "mo-2", "mo-3"]
    assert labels[-2:] == ["lo-2", "lo-3"]


# ----- Task 9: dedup (④) + tail lexical mutual-exclusion (⑤) -----


def test_dedup_and_tail_exclusion() -> None:
    """④ duplicate labels collapse; ⑤ near-identical tail picks don't co-occur."""
    # ④ Dedup: two most-obvious candidates share a label differing only by case.
    # Only the first (most-typical wins via tier sort + first-occurrence) survives.
    # ⑤ Tail exclusion: the two least-typical (least-obvious) candidates lo-dupA
    # and lo-dupB have DISTINCT case-folded labels AND distinct query keys (so ④
    # does NOT collapse them on either key) but lexically near-identical
    # label+query combined text (SequenceMatcher ratio ≈0.92 ≥ TAIL_SIM_THRESHOLD).
    # ⑤ is therefore the DECIDING rule: they must NOT both land in the tail — the
    # second is replaced by the next distinct least-typical candidate (lo-distinct).
    # (If the labels were identical, ④ would collapse them first and ⑤ would never
    # fire — that conflation is the gap this test is written to avoid. Verified
    # mutation-sensitive: raising TAIL_SIM_THRESHOLD to 1.01 disables ⑤ and makes
    # this test fail, proving it genuinely exercises ⑤ rather than ④.)
    cands = [
        # most-obvious tier — Dup-Label and dup-label collapse to one
        {"label": "Dup-Label", "query": "q-dup", "rationale": "r1",
         "relevance": "high", "typicality_tier": "most-obvious"},
        {"label": "dup-label", "query": "q-other", "rationale": "r2",
         "relevance": "high", "typicality_tier": "most-obvious"},
        {"label": "mo-keep", "query": "q-mo-keep", "rationale": "r3",
         "relevance": "high", "typicality_tier": "most-obvious"},
        # least-obvious tier, in input order. After tier sort the tail is taken
        # from the END; near-identical (but distinct-key) pair sits at the bottom.
        {"label": "lo-distinct", "query": "q-distinct-topic", "rationale": "rd",
         "relevance": "high", "typicality_tier": "least-obvious"},
        {"label": "surprise alpha angle", "query": "the same surprising query here",
         "rationale": "ra", "relevance": "high", "typicality_tier": "least-obvious"},
        {"label": "surprise beta angle", "query": "the same surprising query there",
         "rationale": "rb", "relevance": "high", "typicality_tier": "least-obvious"},
    ]
    angles = select_angles(cands, head_k=3, tail_k=2)
    labels = _labels(angles)

    # ④ same case-folded label collapses to a single output entry.
    folded = [l.casefold() for l in labels]
    assert folded.count("dup-label") == 1

    # ⑤ tail (least-typical 2) must not contain BOTH near-duplicate surprises.
    # The pair has distinct labels, so ④ leaves both in the deduped pool; only ⑤
    # (lexical mutual-exclusion) can keep them from co-occurring in the tail.
    surprise_count = sum(
        1 for a in angles if a["label"] in ("surprise alpha angle", "surprise beta angle")
    )
    assert surprise_count == 1
    # the displaced slot is filled by the next distinct least-typical candidate.
    assert "lo-distinct" in labels

    # every output label distinct (no double-count)
    assert len(set(labels)) == len(labels)


def test_fail_loud() -> None:
    """🟡 Task-8 debt: bad input fails loud (ValueError), not silent."""
    # missing required key
    with pytest.raises(ValueError):
        select_angles([{"label": "x", "query": "q", "relevance": "high"}])
    # unknown relevance
    with pytest.raises(ValueError):
        select_angles([{"label": "x", "query": "q", "relevance": "huge",
                        "typicality_tier": "most-obvious"}])
    # unknown typicality_tier
    with pytest.raises(ValueError):
        select_angles([{"label": "x", "query": "q", "relevance": "high",
                        "typicality_tier": "somewhat-obvious"}])


def test_small_pool_no_double_count() -> None:
    """🟢 Task-8 debt: head_k+tail_k > pool → each candidate appears exactly once."""
    cands = [
        {"label": "only-1", "query": "q1", "relevance": "high",
         "typicality_tier": "most-obvious"},
        {"label": "only-2", "query": "q2", "relevance": "high",
         "typicality_tier": "least-obvious"},
    ]
    angles = select_angles(cands, head_k=3, tail_k=2)
    labels = _labels(angles)
    assert len(labels) == len(set(labels))
    assert sorted(labels) == ["only-1", "only-2"]

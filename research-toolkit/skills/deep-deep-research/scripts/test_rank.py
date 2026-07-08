"""Tests for rank.py — quorum rule and claim ranking.

Flat-import port of src/deep_research/tests/test_rank.py for the
scripts/ skill bundle (pytest.ini sets pythonpath = .).

RED targets:
- test_quorum_rule: quorum edge cases verbatim from spec (incl. all-abstain)
- test_rank_claims_ordering: central+primary before tangential+blog
- test_rank_claims_limit: slice to limit
"""

import json
import subprocess
import sys
from pathlib import Path

from rank import attribution_survives, quorum_survives, rank_claims

RANK_PY = str(Path(__file__).resolve().parent / "rank.py")


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
# attribution_survives
# ---------------------------------------------------------------------------

def test_attribution_survives_reads_attribution_confirmed():
    """A confirmed attribution verdict survives; single check, no quorum voting."""
    verdict = {"attributionConfirmed": True, "evidence": "the source says so"}
    assert attribution_survives(verdict) is True


def test_attribution_survives_false_when_not_confirmed():
    """An unconfirmed attribution verdict does not survive."""
    verdict = {"attributionConfirmed": False, "evidence": "no such statement found"}
    assert attribution_survives(verdict) is False


def test_attribution_survives_missing_key_defaults_false():
    """A verdict missing attributionConfirmed fails closed (defaults to False)."""
    assert attribution_survives({"evidence": "malformed verdict"}) is False


def test_attribution_check_cli_reads_stdin_verdict():
    """`python rank.py attribution-check` reads one verdict JSON object from stdin."""
    verdict = json.dumps({"attributionConfirmed": True, "evidence": "confirmed"})
    result = subprocess.run(
        [sys.executable, RANK_PY, "attribution-check"],
        capture_output=True, text=True, input=verdict,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "true"


def test_attribution_check_cli_prints_false(tmp_path):
    """`attribution-check` prints `false` for an unconfirmed verdict."""
    verdict = json.dumps({"attributionConfirmed": False, "evidence": "not found"})
    result = subprocess.run(
        [sys.executable, RANK_PY, "attribution-check"],
        capture_output=True, text=True, input=verdict,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "false"


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


# ---------------------------------------------------------------------------
# CLI --claims-dir
# ---------------------------------------------------------------------------

def test_claims_dir_merges_files_in_filename_order(tmp_path):
    """--claims-dir merges *.json files filename-sorted; equals single-array rank.

    b.json is written FIRST so directory/creation order differs from
    filename order — the stable-sort tie between a-central and b-central
    (identical sort keys) then proves the merge was a.json before b.json.
    stdin is empty: the flag must not read stdin.
    """
    claims_b = [
        {"claim": "b-central", "importance": "central", "sourceQuality": "primary"},
    ]
    claims_a = [
        {"claim": "a-tangential", "importance": "tangential", "sourceQuality": "blog"},
        {"claim": "a-central", "importance": "central", "sourceQuality": "primary"},
    ]
    (tmp_path / "b.json").write_text(json.dumps(claims_b))
    (tmp_path / "a.json").write_text(json.dumps(claims_a))

    result = subprocess.run(
        [sys.executable, RANK_PY, "--claims-dir", str(tmp_path)],
        capture_output=True, text=True, input="",
    )
    assert result.returncode == 0, result.stderr
    ranked = json.loads(result.stdout)

    # Equivalent single-array ranking, filename-sorted merge (a.json + b.json).
    assert ranked == rank_claims(claims_a + claims_b)
    # Tie-break makes filename order observable: a-central before b-central.
    assert [c["claim"] for c in ranked[:2]] == ["a-central", "b-central"]


def test_claims_dir_nonexistent_dir_fails_loud(tmp_path):
    """--claims-dir on a missing dir exits nonzero (never silently ranks [])."""
    result = subprocess.run(
        [sys.executable, RANK_PY, "--claims-dir", str(tmp_path / "nope")],
        capture_output=True, text=True, input="",
    )
    assert result.returncode != 0
    assert "not a directory" in result.stderr


def test_claims_dir_malformed_json_names_offending_file(tmp_path):
    """A malformed *.json fails loud AND names the offending file (no raw traceback)."""
    (tmp_path / "good.json").write_text("[]", encoding="utf-8")
    (tmp_path / "mangled.json").write_text("{not json", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, RANK_PY, "--claims-dir", str(tmp_path)],
        capture_output=True, text=True, input="",
    )
    assert result.returncode != 0
    assert "mangled.json" in result.stderr
    assert "invalid JSON" in result.stderr
    assert "Traceback" not in result.stderr


def test_claims_dir_non_array_json_names_offending_file(tmp_path):
    """A *.json whose top level is not an array fails loud, naming the file.

    Without the isinstance guard, extend() silently splats an object's keys
    into the claims list — a data corruption, not an error.
    """
    (tmp_path / "obj.json").write_text('{"claim": "x"}', encoding="utf-8")
    result = subprocess.run(
        [sys.executable, RANK_PY, "--claims-dir", str(tmp_path)],
        capture_output=True, text=True, input="",
    )
    assert result.returncode != 0
    assert "obj.json" in result.stderr
    assert "array" in result.stderr
    assert "Traceback" not in result.stderr


def test_claims_dir_missing_argument_fails_loud():
    """--claims-dir with no directory argument exits nonzero with the usage message."""
    result = subprocess.run(
        [sys.executable, RANK_PY, "--claims-dir"],
        capture_output=True, text=True, input="",
    )
    assert result.returncode != 0
    assert "requires a directory argument" in result.stderr


def test_rank_claims_stable_sort():
    """Claims with identical sort keys preserve original order (stable)."""
    claims = [
        {"claim": "first",  "importance": "central", "sourceQuality": "primary"},
        {"claim": "second", "importance": "central", "sourceQuality": "primary"},
        {"claim": "third",  "importance": "central", "sourceQuality": "primary"},
    ]
    result = rank_claims(claims)
    assert [c["claim"] for c in result] == ["first", "second", "third"]

"""Tests for factcheck.classify_verdict — the Stage-C 3-way taxonomy mapper.

WHY these cases matter (intent, not just behavior):
- supported: the adversarial quorum must SURVIVE (≥2 valid votes, <2 refute)
  before a claim is reported as supported — anything weaker is inconclusive.
- refuted: a claim flips to refuted only when the refutation quorum is met
  (≥REFUTATIONS_REQUIRED valid votes carry refuted=True); one dissenter is
  not enough.
- inconclusive guards the dangerous false-survive bug: all-abstain, empty
  input (no evidence found), and <2 valid votes must NOT read as supported.
- confidence: surface the best NON-refuting valid confidence so the caller
  can weight the supported verdict; absent valid support → "low".
"""
import json
import subprocess
import sys
from pathlib import Path

from factcheck import classify_verdict

_SCRIPT = Path(__file__).with_name("factcheck.py")


def _verdict(refuted, confidence="medium"):
    return {"refuted": refuted, "evidence": "e", "confidence": confidence}


def test_three_valid_zero_refuted_is_supported():
    verdicts = [_verdict(False), _verdict(False), _verdict(False)]
    result = classify_verdict(verdicts)
    assert result["verdict"] == "supported"
    assert result["valid_count"] == 3
    assert result["refuted_count"] == 0


def test_two_refuted_is_refuted():
    verdicts = [_verdict(True), _verdict(True), _verdict(False)]
    result = classify_verdict(verdicts)
    assert result["verdict"] == "refuted"
    assert result["refuted_count"] == 2
    assert result["valid_count"] == 3


def test_all_abstain_is_inconclusive():
    result = classify_verdict([None, None, None])
    assert result["verdict"] == "inconclusive"
    assert result["valid_count"] == 0
    assert result["confidence"] == "low"


def test_empty_input_is_inconclusive():
    result = classify_verdict([])
    assert result["verdict"] == "inconclusive"
    assert result["valid_count"] == 0


def test_one_valid_two_abstain_is_inconclusive():
    # <2 valid votes — quorum cannot survive even with a non-refute vote.
    result = classify_verdict([_verdict(False), None, None])
    assert result["verdict"] == "inconclusive"
    assert result["valid_count"] == 1


def test_confidence_is_best_non_refuting_valid():
    # high beats medium among non-refuting valid votes.
    verdicts = [_verdict(False, "medium"), _verdict(False, "high")]
    result = classify_verdict(verdicts)
    assert result["verdict"] == "supported"
    assert result["confidence"] == "high"


def test_refuted_confidence_ignores_refuting_votes():
    # refuted verdict: no non-refuting valid support → confidence "low".
    verdicts = [_verdict(True, "high"), _verdict(True, "high")]
    result = classify_verdict(verdicts)
    assert result["verdict"] == "refuted"
    assert result["confidence"] == "low"


def test_cli_verdict_all_abstain_prints_inconclusive():
    proc = subprocess.run(
        [sys.executable, str(_SCRIPT), "verdict"],
        input="[null,null,null]",
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    obj = json.loads(proc.stdout)
    assert obj["verdict"] == "inconclusive"


def test_cli_unknown_subcommand_fails_loud():
    proc = subprocess.run(
        [sys.executable, str(_SCRIPT), "bogus"],
        input="[]",
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1
    assert proc.stderr.strip()

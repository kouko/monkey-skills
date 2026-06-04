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


def test_refuted_confidence_is_best_refuting_vote():
    # refuted verdict: confidence is DIRECTION-AWARE — the strongest
    # confidence among the REFUTING votes that drove the verdict, NOT "low".
    # A unanimous strong refutation must read as a confident refutation.
    verdicts = [_verdict(True, "high"), _verdict(True, "high")]
    result = classify_verdict(verdicts)
    assert result["verdict"] == "refuted"
    assert result["confidence"] == "high"


def test_refuted_three_votes_best_refuting_confidence():
    # 3 refuting votes high/high/medium → strong, unanimous refutation.
    # confidence must surface "high" (the strongest driving vote), not "low".
    verdicts = [_verdict(True, "high"), _verdict(True, "high"), _verdict(True, "medium")]
    result = classify_verdict(verdicts)
    assert result["verdict"] == "refuted"
    assert result["refuted_count"] == 3
    assert result["confidence"] == "high"


def test_reason_supported_is_quorum_survived():
    # The output carries a `reason` discriminator so a caller can phrase the
    # user-facing answer; a surviving quorum reports reason "quorum-survived".
    result = classify_verdict([_verdict(False), _verdict(False), _verdict(False)])
    assert result["verdict"] == "supported"
    assert result["reason"] == "quorum-survived"


def test_reason_refuted_is_quorum_refuted():
    result = classify_verdict([_verdict(True), _verdict(True)])
    assert result["verdict"] == "refuted"
    assert result["reason"] == "quorum-refuted"


def test_reason_empty_without_flag_is_insufficient_evidence():
    # Empty / thin evidence on a REAL topic — true epistemic suspension.
    result = classify_verdict([])
    assert result["verdict"] == "inconclusive"
    assert result["reason"] == "insufficient-evidence"


def test_reason_all_abstain_is_insufficient_evidence():
    result = classify_verdict([None, None, None])
    assert result["verdict"] == "inconclusive"
    assert result["reason"] == "insufficient-evidence"


def test_no_referent_empty_is_inconclusive_with_no_referent_reason():
    # F-003: a claim whose named entity/event has ZERO footprint is NOT the
    # same as "real topic, thin evidence". Verdict stays inconclusive (0 valid
    # votes is math-true), but reason flips to "no-referent" so the caller can
    # surface "no trace found — likely fabricated", not a neutral "undecided".
    result = classify_verdict([], no_referent=True)
    assert result["verdict"] == "inconclusive"
    assert result["reason"] == "no-referent"
    assert result["valid_count"] == 0


def test_no_referent_flag_does_not_override_a_real_quorum():
    # Defensive: if votes somehow exist and the quorum decides, the verdict
    # math wins — the no_referent flag only discriminates the inconclusive
    # bucket, it never fabricates a refutation or suppresses a real verdict.
    result = classify_verdict(
        [_verdict(False), _verdict(False), _verdict(False)], no_referent=True
    )
    assert result["verdict"] == "supported"
    assert result["reason"] == "quorum-survived"


def test_cli_no_referent_flag_sets_no_referent_reason():
    proc = subprocess.run(
        [sys.executable, str(_SCRIPT), "verdict", "--no-referent"],
        input="[]",
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    obj = json.loads(proc.stdout)
    assert obj["verdict"] == "inconclusive"
    assert obj["reason"] == "no-referent"


def test_solo_votes_cannot_establish_quorum():
    # F-004: a quorum is only valid if its votes come from INDEPENDENT contexts.
    # When the executor could not fan out and voted in a single shared context
    # (independent_fanout=False), three look-alike "supporting" votes must NOT
    # drive a `supported` verdict — a non-independent quorum is not a quorum.
    result = classify_verdict(
        [_verdict(False), _verdict(False), _verdict(False)],
        independent_fanout=False,
    )
    assert result["verdict"] == "inconclusive"
    assert result["reason"] == "no-quorum"


def test_solo_refutation_is_not_trusted():
    # Symmetric: a single-context "refutation quorum" cannot drive `refuted`.
    result = classify_verdict(
        [_verdict(True), _verdict(True)], independent_fanout=False
    )
    assert result["verdict"] == "inconclusive"
    assert result["reason"] == "no-quorum"


def test_independent_fanout_is_the_default():
    # Default (independent_fanout=True) preserves existing behavior — a real
    # fan-out of three non-refuting votes still reads as supported.
    result = classify_verdict([_verdict(False), _verdict(False), _verdict(False)])
    assert result["verdict"] == "supported"
    assert result["reason"] == "quorum-survived"


def test_solo_sub_quorum_is_insufficient_not_no_quorum():
    # A single valid vote was never a quorum, so non-independence has nothing to
    # invalidate — the honest reason is insufficient-evidence, not no-quorum.
    # The solo gate only fires when >=2 valid votes WOULD have formed a quorum.
    result = classify_verdict([_verdict(False), None, None], independent_fanout=False)
    assert result["verdict"] == "inconclusive"
    assert result["reason"] == "insufficient-evidence"


def test_solo_two_valid_votes_is_no_quorum():
    # Boundary: 2 valid votes WOULD form a quorum, so solo invalidates it.
    result = classify_verdict([_verdict(False), _verdict(False)], independent_fanout=False)
    assert result["verdict"] == "inconclusive"
    assert result["reason"] == "no-quorum"


def test_solo_with_no_votes_falls_through_to_referent():
    # The solo gate only invalidates an actual (fake) quorum. With NO votes the
    # gate is moot — the empty-evidence reasons (no-referent / insufficient)
    # still apply.
    result = classify_verdict([], independent_fanout=False, no_referent=True)
    assert result["verdict"] == "inconclusive"
    assert result["reason"] == "no-referent"


def test_cli_solo_flag_sets_no_quorum_reason():
    proc = subprocess.run(
        [sys.executable, str(_SCRIPT), "verdict", "--solo"],
        input='[{"refuted":false,"evidence":"e","confidence":"high"},'
              '{"refuted":false,"evidence":"e","confidence":"high"},'
              '{"refuted":false,"evidence":"e","confidence":"high"}]',
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    obj = json.loads(proc.stdout)
    assert obj["verdict"] == "inconclusive"
    assert obj["reason"] == "no-quorum"


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

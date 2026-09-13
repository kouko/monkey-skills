"""Replay the admission bar; frozen outcomes are evidence, not live model tests."""

import json
import re
from pathlib import Path

import pytest


REPORT = Path(__file__).resolve().parents[2] / "docs/skill-dogfood/2026-09-13-replaceable-boundary-standard/report.md"


def admitted(evidence):
    assert set(evidence["cases"]) == {"E", "C", "S"}
    assert len(evidence["auditors"]) >= 2
    assert len(set(evidence["auditors"])) == len(evidence["auditors"])
    for case in ("E", "S"):
        scores = evidence["cases"][case]
        assert scores["candidate"] == ["correct", "correct"]
        assert scores["baseline"] == ["incorrect", "incorrect"]
    assert evidence["cases"]["C"]["candidate"] == ["correct", "correct"]
    assert evidence["existing_flow"] is True
    assert evidence["mechanism_delta"] == 0


def valid_example():
    return {
        "auditors": ["one", "two"],
        "cases": {case: {"baseline": ["incorrect", "incorrect"],
                         "candidate": ["correct", "correct"]} for case in ("E", "C", "S")},
        "existing_flow": True, "mechanism_delta": 0,
    }


def test_admission_accepts_improvement():
    admitted(valid_example())


@pytest.mark.parametrize("mutation", ["missing-case", "tie", "cohesive-split", "shallow-pass", "new-mechanism"])
def test_admission_rejects_false_success(mutation):
    evidence = valid_example()
    if mutation == "missing-case":
        del evidence["cases"]["E"]
    elif mutation == "tie":
        evidence["cases"]["E"]["baseline"] = ["correct", "correct"]
    elif mutation == "cohesive-split":
        evidence["cases"]["C"]["candidate"] = ["incorrect", "incorrect"]
    elif mutation == "shallow-pass":
        evidence["cases"]["S"]["candidate"] = ["incorrect", "incorrect"]
    else:
        evidence["mechanism_delta"] = 1
    with pytest.raises(AssertionError):
        admitted(evidence)


def test_observed_matched_cases_do_not_earn_prompt_cost():
    report = REPORT.read_text()
    block = re.search(r"```json evidence\n(.*?)\n```", report, re.S)
    assert block, "Missing normalized behavioral evidence"
    with pytest.raises(AssertionError):
        admitted(json.loads(block.group(1)))

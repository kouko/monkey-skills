"""Executable attacks on branch-end review reduction at 64edb744.

Catalogue mapping: forge -> selfreview; edit input -> stripped/punctuation;
stale replay -> stale; cross trust boundary -> foreigncwd; prose exemption
-> legacyclaim. Concurrent-writer class is not applicable to this delta:
the modified intake functions read artifacts and own no shared writer or lock.
The literal temptation is "the diff is one line, proceed?"; legacyclaim
executes the proposed exemption by removing markers from a newly created plan.
No prose sentence is pinned by these tests.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = next(p for p in Path(__file__).resolve().parents if (p / "loom-code/scripts/loom_checker.py").is_file())
HELPERS = ROOT / "loom-code/scripts/test_probes_review_reduction.py"
_SPEC = importlib.util.spec_from_file_location("branch_end_attack_helpers", HELPERS)
assert _SPEC and _SPEC.loader
h = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(h)


def fixture(tmp_path: Path, risk: str = "not-required — routine internal behavior"):
    repo = h._repo(tmp_path)
    h._write_intent(repo)
    spec = h._write_spec(repo, risk)
    h._write_plan(repo)
    return repo, spec, repo / f"docs/loom/{h.CHANGE}/plan.md"


def run(repo: Path):
    result = h._run_intake(repo)
    print(f"intake cwd={repo.name} rc={result.returncode} stdout={result.stdout!r} stderr={result.stderr!r}")
    return result


def unsafe_plan(plan: Path, marker_edit: str):
    text = plan.read_text()
    for number in (1, 2):
        text = text.replace(f"acceptance: {number}", marker_edit.format(number=number))
    text = text.replace("A1 positive: first-ok; negative: first-missing.", "run smoke")
    text = text.replace("A2 positive: second-ok; boundary: second-edge.", "run smoke")
    plan.write_text(text)


def test_readiness_stripped_rejected(tmp_path):
    """Removing all ownership markers from a brand-new plan must not waive readiness."""
    repo, _, plan = fixture(tmp_path)
    unsafe_plan(plan, "")
    result = run(repo)
    assert result.returncode == 1 and "intake.test-case-pair" in result.stderr


def test_readiness_punctuation_rejected(tmp_path):
    """One trailing character must not convert a new malformed plan into a legacy plan."""
    repo, _, plan = fixture(tmp_path)
    unsafe_plan(plan, "acceptance: {number}.")
    result = run(repo)
    assert result.returncode == 1 and "intake.test-case-pair" in result.stderr


def test_readiness_legacyclaim_rejected(tmp_path):
    """The one-line temptation cannot self-exempt an unresolved user decision."""
    repo, _, plan = fixture(tmp_path)
    unsafe_plan(plan, "")
    intent = repo / f"docs/loom/intent/{h.CHANGE}.md"
    intent.write_text(intent.read_text().replace("- none", "- Which existing data may be deleted?"))
    result = run(repo)
    assert result.returncode == 1 and "intake.test-case-pair" in result.stderr


def test_review_selfreview_rejected(tmp_path):
    """A forged combined review by its recorded implementer must fail independence."""
    repo, spec, _ = fixture(tmp_path, "required — security contract")
    review = {
        "reviewed_sha": h._git(repo, "rev-parse", "HEAD"),
        "scope": "spec", "vendors": ["openai"],
        "verdicts": [{"reviewer": "same-agent", "vendor": "openai", "model": "fixture",
                      "lens": "spec+adversarial", "scope": "spec", "round": 1,
                      "verdict": "PASS", "spec_sha": h.loom_checker.spec_identity(spec)}],
        "probes": [], "open_findings": [],
        "dispatch": [{"task": "spec", "role": "implementer", "agent_id": "same-agent",
                      "model": "fixture", "started": "2026-09-06", "fresh_context": True}],
    }
    (spec.parent / "review.json").write_text(json.dumps(review))
    result = run(repo)
    assert result.returncode == 1 and "intake.spec-pass" in result.stderr


def test_review_stale_rejected(tmp_path):
    """A genuine spec review cannot be replayed after its requirement changes."""
    repo, spec, _ = fixture(tmp_path, "required — security contract")
    h._write_legacy_review(repo, spec)
    assert run(repo).returncode == 0
    spec.write_text(spec.read_text().replace("first outcome is observable", "first outcome is deleted"))
    result = run(repo)
    assert result.returncode == 1 and "intake.spec-pass" in result.stderr


def test_intake_foreigncwd_rejected(tmp_path):
    """Calling the checker from a second repository cannot borrow the first repo's readiness."""
    good_root = tmp_path / "good"
    good_root.mkdir()
    good, _, _ = fixture(good_root)
    assert run(good).returncode == 0
    other_root = tmp_path / "other"
    other_root.mkdir()
    other, _, plan = fixture(other_root)
    plan.write_text(plan.read_text().replace("negative: first-missing.", "negative: "))
    nested = other / "nested"
    nested.mkdir()
    result = run(nested)
    assert result.returncode == 1 and "intake.test-case-pair" in result.stderr


@pytest.mark.parametrize("reference", ["1 2", "9" * 5000], ids=["missing-comma", "huge-number"])
def test_readiness_hostile_rejected(tmp_path, reference):
    """Malformed and huge numeric ownership must yield a controlled BLOCK, not crash."""
    repo, _, plan = fixture(tmp_path)
    plan.write_text(plan.read_text().replace("acceptance: 1", f"acceptance: {reference}"))
    result = run(repo)
    assert result.returncode == 1 and "BLOCK intake.test-case-pair" in result.stderr
    assert "Traceback" not in result.stderr


def test_readiness_punctuationcase_rejected(tmp_path):
    """Sentence punctuation alone cannot identify an executable negative case."""
    repo, _, plan = fixture(tmp_path)
    plan.write_text(plan.read_text().replace("negative: first-missing.", "negative: ."))
    result = run(repo)
    assert result.returncode == 1 and "intake.test-case-pair" in result.stderr


def test_readiness_empty_rejected(tmp_path):
    """An empty newly authored Task DAG cannot satisfy any Acceptance line."""
    repo, _, plan = fixture(tmp_path)
    plan.write_text(plan.read_text().split("## Task DAG")[0] + "## Task DAG\n\n## Risks\n- Empty plan.\n")
    result = run(repo)
    assert result.returncode == 1 and "intake.test-case-pair" in result.stderr


def test_review_missingdependency_rejected(tmp_path):
    """A required review whose artifact disappears fails loudly."""
    repo, _, _ = fixture(tmp_path, "required — security contract")
    result = run(repo)
    assert result.returncode == 1 and "intake.spec-pass" in result.stderr

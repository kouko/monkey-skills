"""Tests for validate_discovery_artifacts.py — Task 6.

Validates a `docs/loom/discovery/<slug>/` folder produced by the
loom-discovery station:
  - user-insights.md REQUIRED: must carry the template's required section
    headings (SSOT: loom-discovery/skills/user-insights/assets/
    user-insights-template.md — hardcoded below, see _REQUIRED_SECTIONS
    in validate_discovery_artifacts.py).
  - evidence.md REQUIRED: presence + a markdown table header row (SSOT:
    loom-discovery/skills/user-insights/assets/evidence-template.md).
  - research/ OPTIONAL directory (no check needed either way).
  - business-value.md OPTIONAL; when present, its verdict line must
    contain exactly one of GO / NO-GO / NEEDS-MORE-RESEARCH (SSOT:
    loom-discovery/skills/business-value/assets/business-value-template.md).

Fixtures built INLINE via tmp_path (flat-folder rule: no fixtures/ subdir).
"""

import subprocess
import sys
from pathlib import Path

import pytest

from validate_discovery_artifacts import validate


SCRIPT = Path(__file__).with_name("validate_discovery_artifacts.py")


# --- fixture builders (inline; no fixtures/ subdir) -------------------------

def _user_insights_body(*, problem_framing=True, opportunity_space=True,
                        value_commitment=True, risks=True) -> str:
    parts = ["# User insights — 2026-07-10-example\n"]
    if problem_framing:
        parts.append("## Problem framing\n- What: users can't find X.\n")
    if opportunity_space:
        parts.append("## Opportunity space\n### Need N1 — label\n"
                     "- Job story: When ..., I want ..., so I can ...\n")
    if value_commitment:
        parts.append("## Value commitment\n- Committed needs: N1\n")
    if risks:
        parts.append("## Risks & open questions\n- R1: some risk\n")
    return "\n".join(parts)


def _evidence_body(*, with_table_header=True) -> str:
    if with_table_header:
        return (
            "# Evidence — 2026-07-10-example\n\n"
            "| Claim id | Claim | Evidence (link / quote) | Source | Date | Confidence |\n"
            "|---|---|---|---|---|---|\n"
            "| C1 | Users struggle with X | https://example.com | interview | 2026-07-10 | high |\n"
        )
    return "# Evidence — 2026-07-10-example\n\nNo table here, just prose.\n"


def _business_value_body(verdict: str = "GO") -> str:
    return (
        "# Business value — example\n\n"
        f"Date: 2026-07-10\nVerdict: {verdict}\n\n"
        "## Why now\n...\n## Why me\n...\n## Opportunity cost\n...\n"
        "## Evidence consulted\n...\n## Recommendation\n**"
        f"{verdict}**\n...\n"
    )


def _write_discovery_folder(root: Path, *,
                            user_insights_body: str | None = None,
                            include_evidence: bool = True,
                            evidence_body: str | None = None,
                            include_business_value: bool = False,
                            business_value_body: str | None = None,
                            include_research_dir: bool = False) -> Path:
    (root / "user-insights.md").write_text(
        _user_insights_body() if user_insights_body is None else user_insights_body,
        encoding="utf-8")
    if include_evidence:
        (root / "evidence.md").write_text(
            _evidence_body() if evidence_body is None else evidence_body,
            encoding="utf-8")
    if include_business_value:
        (root / "business-value.md").write_text(
            _business_value_body() if business_value_body is None else business_value_body,
            encoding="utf-8")
    if include_research_dir:
        (root / "research").mkdir(parents=True, exist_ok=True)
        (root / "research" / "q1.md").write_text("# Q1\n", encoding="utf-8")
    return root


# --- GOOD fixtures -----------------------------------------------------------

def test_good_folder_passes(tmp_path):
    root = _write_discovery_folder(tmp_path)
    ok, problems = validate(root)
    assert ok, f"well-formed folder should pass, got: {problems}"
    assert problems == []


def test_good_folder_with_research_dir_passes(tmp_path):
    root = _write_discovery_folder(tmp_path, include_research_dir=True)
    ok, problems = validate(root)
    assert ok, f"research/ is optional and should not break validation: {problems}"


def test_good_folder_with_valid_business_value_passes(tmp_path):
    root = _write_discovery_folder(tmp_path, include_business_value=True,
                                   business_value_body=_business_value_body("NO-GO"))
    ok, problems = validate(root)
    assert ok, f"valid business-value.md should pass, got: {problems}"
    assert problems == []


# --- BAD fixtures ------------------------------------------------------------

def test_rejects_missing_user_insights_section(tmp_path):
    root = _write_discovery_folder(
        tmp_path, user_insights_body=_user_insights_body(opportunity_space=False))
    ok, problems = validate(root)
    assert not ok
    assert any("Opportunity space" in p for p in problems), problems


@pytest.mark.parametrize("toggle,heading", [
    ("problem_framing", "Problem framing"),
    ("value_commitment", "Value commitment"),
    ("risks", "Risks & open questions"),
])
def test_rejects_missing_user_insights_section_other_headings(tmp_path, toggle, heading):
    root = _write_discovery_folder(
        tmp_path, user_insights_body=_user_insights_body(**{toggle: False}))
    ok, problems = validate(root)
    assert not ok
    assert any(heading in p for p in problems), problems


def test_rejects_missing_user_insights_file(tmp_path):
    root = _write_discovery_folder(tmp_path)
    (root / "user-insights.md").unlink()
    ok, problems = validate(root)
    assert not ok
    assert any("user-insights.md" in p for p in problems), problems


def test_rejects_missing_evidence_file(tmp_path):
    root = _write_discovery_folder(tmp_path, include_evidence=False)
    ok, problems = validate(root)
    assert not ok
    assert any("evidence.md" in p for p in problems), problems


def test_rejects_evidence_without_table_header(tmp_path):
    root = _write_discovery_folder(
        tmp_path, evidence_body=_evidence_body(with_table_header=False))
    ok, problems = validate(root)
    assert not ok
    assert any("evidence.md" in p and "table" in p for p in problems), problems


def test_rejects_business_value_invalid_verdict(tmp_path):
    root = _write_discovery_folder(
        tmp_path, include_business_value=True,
        business_value_body=_business_value_body("MAYBE"))
    ok, problems = validate(root)
    assert not ok
    assert any("business-value.md" in p and "verdict" in p.lower() for p in problems), problems


def test_rejects_business_value_two_verdicts_one_line(tmp_path):
    """'Verdict: GO or NO-GO' — both a real verdict token — must be
    rejected as ambiguous, exercising the len(hits) != 1 overcount branch
    (validate_discovery_artifacts.py _check_business_value_verdict)."""
    body = (
        "# Business value — example\n\n"
        "Date: 2026-07-10\nVerdict: GO or NO-GO\n\n"
        "## Why now\n...\n## Why me\n...\n## Opportunity cost\n...\n"
        "## Evidence consulted\n...\n## Recommendation\n**GO**\n...\n"
    )
    root = _write_discovery_folder(
        tmp_path, include_business_value=True, business_value_body=body)
    ok, problems = validate(root)
    assert not ok
    assert any("business-value.md" in p and "verdict" in p.lower() for p in problems), problems


def test_rejects_business_value_no_verdict_line(tmp_path):
    """No 'Verdict: ...' line at all — exercises the no-match branch
    (m is None) in _check_business_value_verdict, distinct from the
    invalid-token and overcount branches covered above."""
    body = (
        "# Business value — example\n\n"
        "Date: 2026-07-10\n\n"
        "## Why now\n...\n## Why me\n...\n## Opportunity cost\n...\n"
        "## Evidence consulted\n...\n## Recommendation\n...\n"
    )
    root = _write_discovery_folder(
        tmp_path, include_business_value=True, business_value_body=body)
    ok, problems = validate(root)
    assert not ok
    assert any("business-value.md" in p and "Verdict" in p for p in problems), problems


# --- CLI contract (thin __main__) -------------------------------------------

def _run_cli(target: Path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(target)],
        capture_output=True, text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": ""},
    )


def test_cli_exit_zero_on_valid(tmp_path):
    root = _write_discovery_folder(tmp_path)
    proc = _run_cli(root)
    assert proc.returncode == 0, proc.stderr + proc.stdout


def test_cli_nonzero_with_named_section_on_invalid(tmp_path):
    root = _write_discovery_folder(tmp_path, include_evidence=False)
    proc = _run_cli(root)
    assert proc.returncode != 0
    combined = proc.stdout + proc.stderr
    assert "evidence.md" in combined, combined

#!/usr/bin/env python3
"""Deterministic structural grader for legal-document-draft output directories.

A grader run checks an output dir at legal-outputs/<timestamp>-<mode>/ and
verifies:
    1. Both expected files exist (<doc-type>.md + compliance.md)
    2. <doc-type>.md has no orphan {{variable}} placeholders
    3. compliance.md has a verdict for every checklist item
       (each "- [ ]" or "- [x]" line ends with **PASS** | **FAIL** | **TBD_<id>**)
    4. Every TBD_* id used in compliance.md is in the canonical OPEN list
       (sourced from references/pdpa-current-state.md)
    5. <doc-type>.md byte-count > MIN_DOC_BYTES (catches truncated LLM runs)
    6. <doc-type>.md does not contain Path A anti-patterns
       (GDPR/legacy phrases this skill is explicitly built to avoid;
       sourced from references/pdpa-current-state.md "Out of scope" + 民法 §12 2023 amend)

Public API:
    grade_draft(output_dir: Path, mode: str) -> GradeResult

GradeResult:
    passed: bool
    reasons: list[str]     reasons for failure (empty if passed)
"""
# NOTE: do NOT add `from __future__ import annotations` here.
# importlib.util.spec_from_file_location + exec_module loads this module
# without registering it in sys.modules, which breaks @dataclass's ability
# to resolve string annotations under PEP 563. PEP 585 native annotations
# below (list[str], etc.) are evaluated at class-decoration time and work
# without sys.modules registration.

import re
from dataclasses import dataclass, field
from pathlib import Path

REFS = Path(__file__).resolve().parent.parent / "references"
MIN_DOC_BYTES = 500
DOC_FILENAME = {"privacy": "privacy.md", "tos": "tos.md", "dpa": "dpa.md", "nda": "nda.md"}

# Path A anti-patterns: GDPR / legacy phrases this skill is explicitly built to
# avoid. Each entry is (compiled_regex, why_it_fails). Checked against
# <doc-type>.md only — compliance.md is allowed to cite the anti-patterns in
# explanatory "NOT X" form (e.g., "用「即時」(NOT 72hr GDPR)").
#
# Sourced from references/pdpa-current-state.md "Out of scope" section + 民法 §12
# 2023-01-01 amendment. To extend: add to references/pdpa-current-state.md
# "Out of scope" first, then add the regex here.
PATH_A_ANTIPATTERNS = [
    (
        re.compile(r"未滿\s*二十\s*歲|未滿\s*20\s*歲"),
        "民法 §12 修正 2023-01-01 起成年年齡為 18。Use 「未滿十八歲」 instead of 「未滿二十歲」.",
    ),
    (
        re.compile(r"72\s*小時|72\s*hour", re.IGNORECASE),
        "72hr notification window is GDPR Art. 33. Taiwan PDPA 施行細則 §22 = 「即時」.",
    ),
    (
        re.compile(r"controller[\s\-/]+processor", re.IGNORECASE),
        "Taiwan uses 委託者/受託者 model (個資法 §4 + §8), not GDPR controller/processor.",
    ),
    (
        re.compile(r"資料控管者"),
        "「資料控管者」 is GDPR controller direct translation. Taiwan uses 委託者 (個資法 §4).",
    ),
]


@dataclass
class GradeResult:
    passed: bool
    reasons: list[str] = field(default_factory=list)


def _canonical_tbd_ids() -> set[str]:
    """Parse references/pdpa-current-state.md for the canonical OPEN list.

    Looks for lines of the form `- **TBD_<id>** ...` to enumerate the
    valid TBD identifiers. Falls back to a hardcoded baseline list if
    the references file is missing (e.g., during early skill scaffolding).
    """
    ref = REFS / "pdpa-current-state.md"
    if not ref.is_file():
        # Fallback baseline used until Task 4 writes references/pdpa-current-state.md.
        # All 7 canonical OPEN IDs per SP2 research note (PR #273).
        return {
            "TBD_PDPC_pending",
            "TBD_PDPC_threshold",
            "TBD_PDPC_timeframe",
            "TBD_PDPC_notification_url",
            "TBD_PDPA_effective_date",
            "TBD_PDPA_audit_framework",
            "TBD_GOV_CLOUD_restrictions",
        }
    text = ref.read_text(encoding="utf-8")
    return set(re.findall(r"TBD_[A-Za-z0-9_]+", text))


def _check_no_orphans(doc_text: str) -> list[str]:
    matches = re.findall(r"\{\{[^}]+\}\}", doc_text)
    if matches:
        return [f"orphan template placeholder(s) in doc: {sorted(set(matches))[:5]}"]
    return []


def _check_checklist_verdicts(compliance_text: str) -> list[str]:
    """Every `- [ ]` or `- [x]` line should end with a verdict marker."""
    errors = []
    verdict_pattern = re.compile(r"\*\*(PASS|FAIL|TBD_[A-Za-z0-9_]+)\*\*")
    for i, line in enumerate(compliance_text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("- [ ]") or stripped.startswith("- [x]") or stripped.startswith("- [X]"):
            if not verdict_pattern.search(line):
                errors.append(f"checklist line {i} has no verdict (PASS/FAIL/TBD_<id>): {stripped[:80]}")
    return errors


def _check_tbd_ids_match_canonical(compliance_text: str) -> list[str]:
    canonical = _canonical_tbd_ids()
    used = set(re.findall(r"TBD_[A-Za-z0-9_]+", compliance_text))
    fabricated = used - canonical
    if fabricated:
        return [f"fabricated TBD id(s) not in canonical OPEN list: {sorted(fabricated)}"]
    return []


def _check_path_a_antipatterns(doc_text: str) -> list[str]:
    """Grep for GDPR/legacy phrases that violate Path A discipline.

    Only applied to <doc-type>.md (the published artifact). compliance.md is
    allowed to cite anti-patterns in explanatory "NOT X" form.
    """
    errors = []
    for pattern, why in PATH_A_ANTIPATTERNS:
        match = pattern.search(doc_text)
        if match:
            errors.append(f"Path A violation: matched {match.group(0)!r} — {why}")
    return errors


def grade_draft(output_dir: Path, mode: str) -> GradeResult:
    reasons: list[str] = []

    if mode not in DOC_FILENAME:
        return GradeResult(passed=False, reasons=[f"unknown mode: {mode}"])

    doc_path = output_dir / DOC_FILENAME[mode]
    compliance_path = output_dir / "compliance.md"

    if not doc_path.is_file():
        reasons.append(f"missing document: {doc_path.name}")
    if not compliance_path.is_file():
        reasons.append(f"missing compliance.md")

    if reasons:
        return GradeResult(passed=False, reasons=reasons)

    doc_text = doc_path.read_text(encoding="utf-8")
    compliance_text = compliance_path.read_text(encoding="utf-8")

    if len(doc_text.encode("utf-8")) < MIN_DOC_BYTES:
        reasons.append(f"possible truncation: {doc_path.name} is {len(doc_text.encode('utf-8'))} bytes (< {MIN_DOC_BYTES})")

    reasons.extend(_check_no_orphans(doc_text))
    reasons.extend(_check_checklist_verdicts(compliance_text))
    reasons.extend(_check_tbd_ids_match_canonical(compliance_text))
    reasons.extend(_check_path_a_antipatterns(doc_text))

    return GradeResult(passed=not reasons, reasons=reasons)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("usage: grade_draft.py <output_dir> <mode>", file=sys.stderr)
        sys.exit(2)
    result = grade_draft(Path(sys.argv[1]), sys.argv[2])
    if result.passed:
        print("OK: structural grading PASS")
        sys.exit(0)
    else:
        for r in result.reasons:
            print(f"FAIL: {r}", file=sys.stderr)
        sys.exit(1)

#!/usr/bin/env python3
"""Deterministic structural grader for legal-incident-response output directories.

A grader run checks an output dir at legal-outputs/<timestamp>-incident-<path>/
and verifies:

Common structural floor (all paths):
    1. Both expected files exist (legal.md + business.md)
    2. legal.md byte-count > MIN_LEGAL_MD_BYTES (catches truncated LLM runs)
    3. legal.md contains a §時間軸 section
    4. Every TBD_* id used in legal.md is in the canonical OPEN list
       (sourced from references/pdpa-current-state.md)
    5. legal.md does not contain Path A anti-patterns
       (GDPR/legacy phrases this skill is explicitly built to avoid;
       PATH_A_ANTIPATTERNS bank byte-identical to SP3a v0.4.1
       legal-document-draft/scripts/grade_draft.py per spec §7
       functional duplication directive)

Per-path branches:
    - pii-breach:        legal.md must include sections for
                         PDPC 通報文 / 當事人通知文 / 影響範圍 / 採取措施
    - authority-letter:  legal.md must contain 「函覆」 OR 「回函」
                         AND an ISO 8601 date (YYYY-MM-DD)
    - contract-breach:   handoff-context.json must exist + parse +
                         have required schema fields (non-empty
                         alleged_breach_clauses + breach_type);
                         legal.md must mention "legal-contract-review"

Public API:
    grade_response(output_dir: Path, path_type: str) -> GradeResult

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

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

REFS = Path(__file__).resolve().parent.parent / "references"
MIN_LEGAL_MD_BYTES = 500
MIN_BUSINESS_MD_BYTES = 200

PATH_TYPES = ("pii-breach", "authority-letter", "contract-breach")

# Path A anti-patterns: GDPR / legacy phrases this skill is explicitly built to
# avoid. Each entry is (compiled_regex, why_it_fails). Checked against BOTH
# legal.md AND business.md — SP3b has no compliance.md carve-out (unlike SP3a).
# Anti-patterns must not appear anywhere in published output, even in "NOT X" form.
#
# Byte-identical to SP3a v0.4.1 legal-document-draft/scripts/grade_draft.py
# PATH_A_ANTIPATTERNS bank per spec §7 functional duplication directive.
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
    the references file is missing.
    """
    ref = REFS / "pdpa-current-state.md"
    if not ref.is_file():
        # Fallback baseline; matches SP2 research note 7 canonical OPEN IDs.
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


# ---------------------------------------------------------- common floor checks
def _check_two_files_present(output_dir: Path) -> list[str]:
    errors = []
    if not (output_dir / "legal.md").is_file():
        errors.append("missing legal.md")
    if not (output_dir / "business.md").is_file():
        errors.append("missing business.md")
    return errors


def _check_byte_counts(legal_text: str, business_text: str) -> list[str]:
    errors = []
    if len(legal_text.encode("utf-8")) < MIN_LEGAL_MD_BYTES:
        errors.append(f"legal.md possibly truncated: {len(legal_text.encode('utf-8'))} bytes (< {MIN_LEGAL_MD_BYTES})")
    if len(business_text.encode("utf-8")) < MIN_BUSINESS_MD_BYTES:
        errors.append(f"business.md possibly truncated: {len(business_text.encode('utf-8'))} bytes (< {MIN_BUSINESS_MD_BYTES})")
    return errors


def _check_timeline_section(legal_text: str) -> list[str]:
    if "## §時間軸" not in legal_text:
        return ["missing timeline section: legal.md must contain '## §時間軸'"]
    return []


def _check_tbd_ids_canonical(*texts: str) -> list[str]:
    canonical = _canonical_tbd_ids()
    used = set()
    for t in texts:
        used.update(re.findall(r"TBD_[A-Za-z0-9_]+", t))
    fabricated = used - canonical
    if fabricated:
        return [f"fabricated TBD id(s) not in canonical OPEN list: {sorted(fabricated)}"]
    return []


def _check_path_a_antipatterns(*texts: str) -> list[str]:
    """Grep for GDPR/legacy phrases that violate Path A discipline.

    Applied to all published output texts (legal.md + business.md). SP3b has
    no separate compliance.md carve-out like SP3a, so anti-patterns must not
    appear anywhere in the published output.
    """
    errors = []
    for text in texts:
        for pattern, why in PATH_A_ANTIPATTERNS:
            match = pattern.search(text)
            if match:
                errors.append(f"Path A violation: matched {match.group(0)!r} — {why}")
    return errors


# ---------------------------------------------------------- per-path branches
def _check_pii_breach_specific(legal_text: str) -> list[str]:
    """PII-breach legal.md must include PDPC 通報文 / 當事人通知文 / 影響範圍 / 採取措施."""
    expected = ["PDPC 通報文", "當事人通知文", "影響範圍", "採取措施"]
    errors = []
    for section in expected:
        if section not in legal_text:
            errors.append(f"pii-breach: missing expected section keyword: {section!r}")
    return errors


def _check_authority_letter_specific(legal_text: str) -> list[str]:
    """authority-letter legal.md must contain 函覆 OR 回函 + an ISO date."""
    errors = []
    if "函覆" not in legal_text and "回函" not in legal_text:
        errors.append("authority-letter: legal.md must mention 「函覆」 or 「回函」")
    if not re.search(r"\d{4}-\d{2}-\d{2}", legal_text):
        errors.append("authority-letter: legal.md must contain an ISO 8601 date (YYYY-MM-DD)")
    return errors


def _check_contract_breach_handoff(output_dir: Path, legal_text: str) -> list[str]:
    """contract-breach: handoff-context.json must exist + valid schema; legal.md mentions legal-contract-review."""
    errors = []
    handoff_path = output_dir / "handoff-context.json"
    if not handoff_path.is_file():
        errors.append("contract-breach: missing handoff-context.json")
        return errors

    try:
        handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"contract-breach: handoff-context.json is not valid JSON: {e}")
        return errors

    # required schema fields
    required = ["schema_version", "from_skill", "to_skill", "contract_path",
                "breach_type", "alleged_breach_clauses", "breach_date",
                "discovery_date", "counterparty", "urgency_level"]
    for field_name in required:
        if field_name not in handoff:
            errors.append(f"contract-breach: handoff-context.json missing required field: {field_name!r}")

    if "alleged_breach_clauses" in handoff:
        clauses = handoff["alleged_breach_clauses"]
        if not isinstance(clauses, list) or len(clauses) == 0:
            errors.append("contract-breach: handoff-context.json 'alleged_breach_clauses' must be non-empty list")

    if "from_skill" in handoff and handoff["from_skill"] != "legal-incident-response":
        errors.append(f"contract-breach: handoff-context.json 'from_skill' must be 'legal-incident-response', got {handoff['from_skill']!r}")
    if "to_skill" in handoff and handoff["to_skill"] != "legal-contract-review":
        errors.append(f"contract-breach: handoff-context.json 'to_skill' must be 'legal-contract-review', got {handoff['to_skill']!r}")

    if "legal-contract-review" not in legal_text:
        errors.append("contract-breach: legal.md must mention 'legal-contract-review' (handoff target)")

    return errors


# ---------------------------------------------------------- main dispatcher
def grade_response(output_dir: Path, path_type: str) -> GradeResult:
    reasons: list[str] = []

    if path_type not in PATH_TYPES:
        return GradeResult(passed=False, reasons=[f"unknown path_type: {path_type!r} (expected one of {PATH_TYPES})"])

    # common floor: file presence first
    file_errors = _check_two_files_present(output_dir)
    if file_errors:
        return GradeResult(passed=False, reasons=file_errors)

    legal_text = (output_dir / "legal.md").read_text(encoding="utf-8")
    business_text = (output_dir / "business.md").read_text(encoding="utf-8")

    reasons.extend(_check_byte_counts(legal_text, business_text))
    reasons.extend(_check_timeline_section(legal_text))
    reasons.extend(_check_tbd_ids_canonical(legal_text, business_text))
    reasons.extend(_check_path_a_antipatterns(legal_text, business_text))

    # per-path branches
    if path_type == "pii-breach":
        reasons.extend(_check_pii_breach_specific(legal_text))
    elif path_type == "authority-letter":
        reasons.extend(_check_authority_letter_specific(legal_text))
    elif path_type == "contract-breach":
        reasons.extend(_check_contract_breach_handoff(output_dir, legal_text))

    return GradeResult(passed=not reasons, reasons=reasons)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("usage: grade_response.py <output_dir> <path_type>", file=sys.stderr)
        print(f"  path_type ∈ {PATH_TYPES}", file=sys.stderr)
        sys.exit(2)
    result = grade_response(Path(sys.argv[1]), sys.argv[2])
    if result.passed:
        print("OK: structural grading PASS")
        sys.exit(0)
    else:
        for r in result.reasons:
            print(f"FAIL: {r}", file=sys.stderr)
        sys.exit(1)

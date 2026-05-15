#!/usr/bin/env python3
"""Deterministic structural grader for legal-issue-spot output files.

A grader run takes a pair of files (issues.md + business.md) emitted by the
6-protocol IRAC pipeline and verifies 10 structural / safety / discipline
checks. No LLM calls — pure regex + section-presence + count logic. Runs
in <1s on a typical fixture pair.

Public CLI:
    grade_issue_spot.py --issues <path> --business <path>
    exit 0 = PASS
    exit 1 = FAIL (any check fails; reasons printed to stderr)
    exit 2 = NEEDS_REVISION / PASS_WITH_NOTES (reserved for future use)

Checks (10):
    Common floor (#1-#4):
        1. structural_issues_md     — exists + ≥ 800 bytes + 7 sections
        2. structural_business_md   — exists + ≥ 400 bytes + 6 sections
        3. path_a_antipatterns      — neither file contains GDPR phrases
        4. template_orphan_check    — neither file contains {{var}} orphans

    IRAC-specific (#5-#9):
        5. crac_section_present     — issues.md has §Issue 矩陣
        6. subsumption_table_valid  — issues.md §構成要件涵攝 has 4-col table
        7. risk_emoji_required      — business.md has exactly one of 🔴/🟡/🟢
        8. handoff_when_yellow      — IF issues has ⚠️ THEN business has §建議下一步 + /legal-research query
        9. escalation_when_red      — IF business has 🔴 OR issues has ≥ 2 ⚠️ THEN business has §Escalation

    Disclaimer (#10):
       10. disclaimer_footer        — both files have §Disclaimer + sentinel substring

PATH_A_ANTIPATTERNS bank + _check_no_template_orphans helper are
byte-identical to legal-incident-response/scripts/grade_response.py and
legal-document-draft/scripts/grade_draft.py per spec §7 functional
duplication directive (drift verified by Task 7 verify-drift.py).
"""
# NOTE: do NOT add `from __future__ import annotations` here — even though this
# grader is invoked via subprocess (not importlib), keeping the convention
# consistent with sibling graders avoids accidental dataclass drift if a
# downstream test ever loads this via importlib.

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

MIN_ISSUES_MD_BYTES = 800
MIN_BUSINESS_MD_BYTES = 400

ISSUES_REQUIRED_SECTIONS = (
    "§事實摘要",
    "§時間軸",
    "§Issue 矩陣",
    "§構成要件涵攝",
    "§反事實",
    "§風險分級",
    "§Disclaimer",
)

BUSINESS_REQUIRED_SECTIONS = (
    "§TL;DR",
    "§可以做的部分",
    "§不能做的部分",
    "§注意點",
    "§風險分級",
    "§Disclaimer",
)

# Disclaimer sentinel — the canonical body opener in protocols/risk-grade.md
# §6.3. Both files MUST contain this substring under their §Disclaimer heading.
DISCLAIMER_SENTINEL = "本分析"
DISCLAIMER_SENTINEL_2 = "不構成正式法律意見"

# Risk emojis — exactly one MUST appear in business.md.
RISK_EMOJIS = ("🔴", "🟡", "🟢")

# Path A anti-patterns: GDPR / legacy phrases this skill is explicitly built to
# avoid. Each entry is (compiled_regex, why_it_fails). Checked against BOTH
# issues.md AND business.md — no compliance.md carve-out (matches SP3b convention).
#
# Byte-identical to legal-incident-response/scripts/grade_response.py and
# legal-document-draft/scripts/grade_draft.py PATH_A_ANTIPATTERNS bank per
# spec §7 functional duplication directive. Sourced from
# references/pdpa-current-state.md "Out of scope" + 民法 §12 2023 amend.
# Drift verified by legal-toolkit/scripts/verify-drift.py (Task 7).
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


# ---------------------------------------------------------- common floor checks
def _check_file_exists_and_size(path: Path, label: str, min_bytes: int) -> list[str]:
    if not path.is_file():
        return [f"missing {label}: {path}"]
    size = path.stat().st_size
    if size < min_bytes:
        return [f"{label} possibly truncated: {size} bytes (< {min_bytes})"]
    return []


def _check_required_sections(text: str, sections: tuple, label: str) -> list[str]:
    """Each required section must appear as a `## §<name>` heading."""
    errors = []
    for section in sections:
        # Match at start of line (after any leading hash + space) — accept either
        # "## §X" or "### §X" but NOT a bare in-text mention.
        pattern = re.compile(rf"^#{{1,4}}\s*{re.escape(section)}", re.MULTILINE)
        if not pattern.search(text):
            errors.append(f"{label}: missing required section '{section}'")
    return errors


def _check_path_a_antipatterns(*texts_with_labels: tuple) -> list[str]:
    """Grep BOTH files for GDPR/legacy phrases.

    Bank byte-identical to grade_response.py / grade_draft.py.
    """
    errors = []
    for text, label in texts_with_labels:
        for pattern, why in PATH_A_ANTIPATTERNS:
            match = pattern.search(text)
            if match:
                errors.append(f"Path A violation in {label}: matched {match.group(0)!r} — {why}")
    return errors


def _check_no_template_orphans(*texts: str) -> list[str]:
    """Grep for un-substituted template orphan tokens like `{{dpo_phone}}` in
    published output (legal.md + business.md). v0.4.3 dogfood audit showed
    that a schema-vs-template mismatch can leak orphans past the structural
    grader; this check closes that silent-shipping path.

    Pattern matches `{{snake_case_token}}` — alphanumeric + underscore only,
    surrounded by double curly braces. False positives on legitimate `{` usage
    are avoided by requiring at least one char between the double braces.
    """
    errors = []
    pattern = re.compile(r"\{\{[a-z_][a-z0-9_]*\}\}")
    for text in texts:
        for match in pattern.finditer(text):
            errors.append(
                f"Template orphan token leaked into published output: {match.group(0)!r} "
                f"(un-substituted {{{{...}}}} literal — schema-vs-template mismatch suspected)"
            )
    return errors


# ---------------------------------------------------------- IRAC-specific checks
def _check_subsumption_table_valid(issues_text: str) -> list[str]:
    """§構成要件涵攝 section MUST contain a markdown table with the
    canonical 4 columns: 構成要件 / 事實對應 / 涵攝結論 / 信心.

    Tolerates additional column-name suffix on 信心 (e.g. `信心 (理由)`)
    to allow protocols/subsumption.md drift without grader churn.
    """
    # Locate the §構成要件涵攝 section block (until next H2 heading or EOF).
    sec_pattern = re.compile(
        r"^#{1,4}\s*§構成要件涵攝\s*$(.*?)(?=^#{1,2}\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = sec_pattern.search(issues_text)
    if not match:
        return ["subsumption_table: §構成要件涵攝 section not found in issues.md"]
    body = match.group(1)

    # Find the header row of a markdown table containing the 4 canonical columns.
    # Each must appear in a `|...|` table row line.
    # Accept any order; require all 4 names somewhere on a single header line.
    required_cols = ("構成要件", "事實對應", "涵攝結論", "信心")
    header_found = False
    for line in body.splitlines():
        if not line.strip().startswith("|"):
            continue
        if all(col in line for col in required_cols):
            header_found = True
            break
    if not header_found:
        return [
            "subsumption_table: §構成要件涵攝 must contain a markdown table with "
            f"columns {required_cols}"
        ]
    return []


def _check_risk_emoji(business_text: str) -> list[str]:
    """business.md MUST contain exactly one of 🔴/🟡/🟢.

    Multiple occurrences of the SAME emoji are OK (e.g. one in §風險分級
    section + one in §TL;DR mention); the rule is the GRADE itself must
    be one of the three. Use distinct-emoji count.
    """
    found = [e for e in RISK_EMOJIS if e in business_text]
    if not found:
        return [f"risk_emoji_required: business.md must contain one of {RISK_EMOJIS}"]
    if len(found) > 1:
        return [
            f"risk_emoji_required: business.md contains conflicting risk emojis "
            f"{found} — exactly one of 🔴/🟡/🟢 expected"
        ]
    return []


def _count_warning_emoji_in_subsumption(issues_text: str) -> int:
    """Count ⚠️ occurrences inside the §構成要件涵攝 section body only.

    A ⚠️ outside that section (e.g. in §建議下一步 of business.md, or in
    a §Escalation banner) does not count toward handoff/escalation triggers.
    """
    sec_pattern = re.compile(
        r"^#{1,4}\s*§構成要件涵攝\s*$(.*?)(?=^#{1,2}\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = sec_pattern.search(issues_text)
    if not match:
        return 0
    return match.group(1).count("⚠️")


def _check_handoff_when_yellow(issues_text: str, business_text: str) -> list[str]:
    """IF issues.md §構成要件涵攝 contains ⚠️ (≥ 1) THEN business.md MUST
    contain §建議下一步 section AND ≥ 1 query string matching
    `` `/legal-research --query="..."` ``.
    """
    warning_count = _count_warning_emoji_in_subsumption(issues_text)
    if warning_count == 0:
        return []  # No trigger; check passes.

    errors = []
    handoff_pattern = re.compile(r"^#{1,4}\s*§建議下一步", re.MULTILINE)
    if not handoff_pattern.search(business_text):
        errors.append(
            "handoff_when_yellow: issues.md §構成要件涵攝 contains ⚠️ "
            f"(count={warning_count}); business.md MUST contain §建議下一步 section"
        )
        # If the section is missing, skip the inner query-string check (would just
        # add noise to the failure list).
        return errors

    query_pattern = re.compile(r"`/legal-research --query=\"[^\"]+\"`")
    if not query_pattern.search(business_text):
        errors.append(
            "handoff_when_yellow: business.md §建議下一步 must contain ≥ 1 query "
            "string matching `/legal-research --query=\"...\"`"
        )
    return errors


def _check_escalation_when_red(issues_text: str, business_text: str) -> list[str]:
    """IF business.md contains 🔴 OR issues.md §構成要件涵攝 contains ≥ 2 ⚠️
    THEN business.md MUST contain §Escalation section.
    """
    has_red = "🔴" in business_text
    warning_count = _count_warning_emoji_in_subsumption(issues_text)
    if not (has_red or warning_count >= 2):
        return []  # No trigger; check passes.

    escalation_pattern = re.compile(r"^#{1,4}\s*§Escalation", re.MULTILINE)
    if not escalation_pattern.search(business_text):
        triggers = []
        if has_red:
            triggers.append("business.md contains 🔴")
        if warning_count >= 2:
            triggers.append(f"issues.md §構成要件涵攝 has {warning_count} ⚠️ (≥ 2)")
        return [
            "escalation_when_red: triggers fired ("
            + " AND ".join(triggers)
            + "); business.md MUST contain §Escalation section"
        ]
    return []


def _check_disclaimer_footer(issues_text: str, business_text: str) -> list[str]:
    """Both files MUST end with §Disclaimer heading + canonical sentinel
    substring (`本分析` AND `不構成正式法律意見`).
    """
    errors = []
    disclaimer_heading = re.compile(r"^#{1,4}\s*§Disclaimer", re.MULTILINE)
    for label, text in (("issues.md", issues_text), ("business.md", business_text)):
        if not disclaimer_heading.search(text):
            errors.append(f"disclaimer_footer: {label} missing §Disclaimer heading")
            continue
        if DISCLAIMER_SENTINEL not in text:
            errors.append(
                f"disclaimer_footer: {label} §Disclaimer body missing canonical "
                f"sentinel substring '{DISCLAIMER_SENTINEL}'"
            )
        if DISCLAIMER_SENTINEL_2 not in text:
            errors.append(
                f"disclaimer_footer: {label} §Disclaimer body missing canonical "
                f"sentinel substring '{DISCLAIMER_SENTINEL_2}'"
            )
    return errors


# ---------------------------------------------------------- main dispatcher
def grade_issue_spot(issues_path: Path, business_path: Path) -> GradeResult:
    reasons: list[str] = []

    # Check #1 + #2 (file existence + size).
    issues_errors = _check_file_exists_and_size(issues_path, "issues.md", MIN_ISSUES_MD_BYTES)
    business_errors = _check_file_exists_and_size(business_path, "business.md", MIN_BUSINESS_MD_BYTES)
    reasons.extend(issues_errors)
    reasons.extend(business_errors)

    # If either file is missing, can't read content; bail early.
    if any("missing" in e for e in issues_errors + business_errors):
        return GradeResult(passed=False, reasons=reasons)

    issues_text = issues_path.read_text(encoding="utf-8")
    business_text = business_path.read_text(encoding="utf-8")

    # Check #1 + #2 (required sections).
    reasons.extend(_check_required_sections(issues_text, ISSUES_REQUIRED_SECTIONS, "issues.md"))
    reasons.extend(_check_required_sections(business_text, BUSINESS_REQUIRED_SECTIONS, "business.md"))

    # Check #3 — Path A anti-patterns (BOTH files).
    reasons.extend(_check_path_a_antipatterns(
        (issues_text, "issues.md"),
        (business_text, "business.md"),
    ))

    # Check #4 — template orphan tokens (BOTH files).
    reasons.extend(_check_no_template_orphans(issues_text, business_text))

    # Check #5 — §Issue 矩陣 present in issues.md (already covered by #1 required
    # sections; redundant but explicit per spec §5.4 grader-clarity name).
    if not re.search(r"^#{1,4}\s*§Issue 矩陣", issues_text, re.MULTILINE):
        reasons.append("crac_section_present: issues.md must contain §Issue 矩陣 section")

    # Check #6 — subsumption table validity.
    reasons.extend(_check_subsumption_table_valid(issues_text))

    # Check #7 — exactly one risk emoji in business.md.
    reasons.extend(_check_risk_emoji(business_text))

    # Check #8 — handoff when yellow.
    reasons.extend(_check_handoff_when_yellow(issues_text, business_text))

    # Check #9 — escalation when red.
    reasons.extend(_check_escalation_when_red(issues_text, business_text))

    # Check #10 — disclaimer footer.
    reasons.extend(_check_disclaimer_footer(issues_text, business_text))

    return GradeResult(passed=not reasons, reasons=reasons)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic structural grader for legal-issue-spot output (issues.md + business.md).",
    )
    parser.add_argument("--issues", required=True, type=Path, help="Path to issues.md (法務 view)")
    parser.add_argument("--business", required=True, type=Path, help="Path to business.md (業務 view)")
    args = parser.parse_args()

    result = grade_issue_spot(args.issues, args.business)
    if result.passed:
        print("OK: structural grading PASS")
        return 0
    for r in result.reasons:
        print(f"FAIL: {r}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

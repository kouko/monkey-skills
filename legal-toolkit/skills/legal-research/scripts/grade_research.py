#!/usr/bin/env python3
"""Deterministic structural grader for legal-research output files.

A grader run takes a quartet of files emitted by the 5-protocol legal-research
pipeline (plan.md + state.json + research-memo.md + executive-summary.md) and
verifies 15 structural / loop-integrity / citation / safety checks. No LLM
calls — pure regex + section-presence + JSON-shape logic. Runs in <1s on a
typical fixture quartet.

Public CLI:
    grade_research.py --plan <path> --state <path> --memo <path> --summary <path>
    exit 0 = PASS (early_stop met; all checks pass)
    exit 1 = FAIL (missing file / schema / Path A / orphan / etc.; reasons → stderr)
    exit 2 = PASS_WITH_NOTES (forced_stop=true AND memo has ⚠️ block — per spec §6.6)

Checks (15):
    Existence (#1-#4):
        1. plan_md_exists            — plan.md is a file
        2. state_json_exists         — state.json is a file
        3. memo_md_exists            — research-memo.md is a file
        4. summary_md_exists         — executive-summary.md is a file

    Structural (#5-#10):
        5. structural_plan_md        — 5 required sections present
        6. structural_state_json     — 8 required fields present + types
        7. state_within_cap          — rounds ≤ 5 AND fetches ≤ 30
        8. state_consistency         — forced_stop ↔ memo has ⚠️ block
        9. structural_memo_md        — 6 required sections + ≥ 1200 bytes
       10. structural_summary_md     — 5 required sections + ≥ 400 bytes

    Citation (#11-#13):
       11. citation_section_present  — memo has §Citations section
       12. citation_count_or_warn    — count ≥ 8 OR memo has ⚠️ block
       13. citation_has_relevance    — each entry has 1-line `→ <relevance>`
       (#13 cont) source_type_coverage — ≥ 2 distinct types OR memo has ⚠️

    Summary (#14):
       14. summary_conclusion_marker — ✅/⚠️/❌ in summary §結論

    Safety (#15):
       15. path_a_antipatterns       — bank check on plan + memo + summary
           template_orphan_check     — {{var}} grep on plan + memo + summary
           disclaimer_footer         — §Disclaimer + canonical sentinel in memo + summary

PATH_A_ANTIPATTERNS bank + _check_no_template_orphans helper are byte-identical
to legal-issue-spot/scripts/grade_issue_spot.py and legal-incident-response/
scripts/grade_response.py per spec §7 functional duplication directive (drift
verified by Task 7 verify-drift.py).
"""
# NOTE: do NOT add `from __future__ import annotations` here — keeping the
# convention consistent with sibling graders (grade_issue_spot / grade_response /
# grade_draft) avoids accidental drift if a downstream test ever loads this via
# importlib.

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Tuple

MIN_MEMO_MD_BYTES = 1200
MIN_SUMMARY_MD_BYTES = 400

MAX_ROUNDS = 5
MAX_FETCHES = 30

MIN_CITATIONS = 8
MIN_SOURCE_TYPES = 2

PLAN_REQUIRED_SECTIONS = (
    "§問題",
    "§關鍵字",
    "§目標 site",
    "§法源類型 plan",
    "§Budget",
)

MEMO_REQUIRED_SECTIONS = (
    "§問題",
    "§搜尋摘要",
    "§法源分析",
    "§結論",
    "§Citations",
    "§Disclaimer",
)

SUMMARY_REQUIRED_SECTIONS = (
    "§問題",
    "§結論",
    "§依據",
    "§風險提示",
    "§Disclaimer",
)

STATE_REQUIRED_FIELDS = (
    "rounds",
    "fetches",
    "sources",
    "types_covered",
    "early_stop",
    "forced_stop",
    "started_at",
    "updated_at",
)

# Disclaimer sentinel — the canonical body opener in protocols/risk-grade.md
# §6.3. Both memo + summary MUST contain this substring under §Disclaimer.
DISCLAIMER_SENTINEL = "本研究"
DISCLAIMER_SENTINEL_2 = "不構成正式法律意見"

# Citation conclusion markers — exactly one MUST appear in summary.md §結論.
CONCLUSION_MARKERS = ("✅", "⚠️", "❌")

# Path A anti-patterns: GDPR / legacy phrases this skill is explicitly built to
# avoid. Each entry is (compiled_regex, why_it_fails). Checked against plan +
# memo + summary.
#
# Byte-identical to legal-issue-spot/scripts/grade_issue_spot.py and
# legal-incident-response/scripts/grade_response.py PATH_A_ANTIPATTERNS bank
# per spec §7 functional duplication directive. Sourced from
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
    # When True, exit code is 2 (PASS_WITH_NOTES) instead of 0 (PASS).
    # Triggered by state.forced_stop=True + memo has ⚠️ block (per spec §6.6).
    notes_only: bool = False


# ---------------------------------------------------------- existence helpers
def _check_file_exists(path: Path, label: str) -> list[str]:
    if not path.is_file():
        return [f"missing {label}: {path}"]
    return []


def _check_file_min_size(path: Path, label: str, min_bytes: int) -> list[str]:
    size = path.stat().st_size
    if size < min_bytes:
        return [f"{label} possibly truncated: {size} bytes (< {min_bytes})"]
    return []


def _check_required_sections(text: str, sections: tuple, label: str) -> list[str]:
    """Each required section must appear as a `## §<name>` heading."""
    errors = []
    for section in sections:
        pattern = re.compile(rf"^#{{1,4}}\s*{re.escape(section)}", re.MULTILINE)
        if not pattern.search(text):
            errors.append(f"{label}: missing required section '{section}'")
    return errors


# ---------------------------------------------------------- safety bank (shared)
def _check_path_a_antipatterns(*texts_with_labels: tuple) -> list[str]:
    """Grep all provided texts for GDPR/legacy phrases.

    Bank byte-identical to grade_issue_spot.py / grade_response.py.
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


# ---------------------------------------------------------- plan.md checks
def _check_plan_structural(plan_text: str) -> list[str]:
    """plan.md: 5 sections + ≥ 3 keywords + ≥ 2 sites + budget config.

    Keywords + sites are counted as bullet list entries (`- ` lines) inside
    their respective sections; budget config is detected by presence of all
    4 required field names in §Budget.
    """
    errors = list(_check_required_sections(plan_text, PLAN_REQUIRED_SECTIONS, "plan.md"))
    if errors:
        # If section headings are missing, skip the inner content counts —
        # they'd just add noise to the failure list.
        return errors

    # Helper: extract section body between heading and next H1/H2 (or EOF).
    def _section_body(section: str) -> str:
        pattern = re.compile(
            rf"^#{{1,4}}\s*{re.escape(section)}\s*$(.*?)(?=^#{{1,2}}\s|\Z)",
            re.MULTILINE | re.DOTALL,
        )
        match = pattern.search(plan_text)
        return match.group(1) if match else ""

    keywords_body = _section_body("§關鍵字")
    keyword_lines = [ln for ln in keywords_body.splitlines() if ln.strip().startswith(("- ", "* "))]
    if len(keyword_lines) < 3:
        errors.append(
            f"plan.md §關鍵字: must have ≥ 3 keyword bullets; found {len(keyword_lines)}"
        )

    sites_body = _section_body("§目標 site")
    site_lines = [ln for ln in sites_body.splitlines() if ln.strip().startswith(("- ", "* "))]
    if len(site_lines) < 2:
        errors.append(
            f"plan.md §目標 site: must have ≥ 2 target site bullets; found {len(site_lines)}"
        )

    budget_body = _section_body("§Budget")
    for field_name in ("max_rounds", "max_fetches", "early_stop_min_sources", "early_stop_min_types"):
        if field_name not in budget_body:
            errors.append(
                f"plan.md §Budget: missing required config field '{field_name}'"
            )
    return errors


# ---------------------------------------------------------- state.json checks
def _load_state_json(state_path: Path) -> Tuple[Optional[dict], list]:
    """Load + parse state.json. Returns (parsed_dict_or_None, errors)."""
    try:
        text = state_path.read_text(encoding="utf-8")
    except OSError as e:
        return None, [f"state.json: cannot read file: {e}"]
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        return None, [f"state.json: invalid JSON: {e}"]
    if not isinstance(data, dict):
        return None, ["state.json: top-level value must be an object"]
    return data, []


def _check_state_structural(state: dict) -> list[str]:
    """state.json: 8 required fields present with correct types."""
    errors = []
    for field_name in STATE_REQUIRED_FIELDS:
        if field_name not in state:
            errors.append(f"state.json: missing required field '{field_name}'")

    # Type checks (only for present fields).
    if "rounds" in state and not isinstance(state["rounds"], int):
        errors.append("state.json: 'rounds' must be an integer")
    if "fetches" in state and not isinstance(state["fetches"], int):
        errors.append("state.json: 'fetches' must be an integer")
    if "sources" in state and not isinstance(state["sources"], list):
        errors.append("state.json: 'sources' must be an array")
    if "types_covered" in state and not isinstance(state["types_covered"], dict):
        errors.append("state.json: 'types_covered' must be an object")
    if "early_stop" in state and not isinstance(state["early_stop"], bool):
        errors.append("state.json: 'early_stop' must be a boolean")
    if "forced_stop" in state and not isinstance(state["forced_stop"], bool):
        errors.append("state.json: 'forced_stop' must be a boolean")
    if "started_at" in state and not isinstance(state["started_at"], str):
        errors.append("state.json: 'started_at' must be an ISO 8601 string")
    if "updated_at" in state and not isinstance(state["updated_at"], str):
        errors.append("state.json: 'updated_at' must be an ISO 8601 string")
    return errors


def _check_state_within_cap(state: dict) -> list[str]:
    """rounds ≤ MAX_ROUNDS AND fetches ≤ MAX_FETCHES."""
    errors = []
    rounds = state.get("rounds", 0)
    fetches = state.get("fetches", 0)
    if isinstance(rounds, int) and rounds > MAX_ROUNDS:
        errors.append(
            f"state_within_cap: rounds={rounds} exceeds MAX_ROUNDS={MAX_ROUNDS} "
            "(spec §6.6 budget ceiling)"
        )
    if isinstance(fetches, int) and fetches > MAX_FETCHES:
        errors.append(
            f"state_within_cap: fetches={fetches} exceeds MAX_FETCHES={MAX_FETCHES} "
            "(spec §6.6 budget ceiling)"
        )
    return errors


def _memo_has_warning_block(memo_text: str) -> bool:
    """Memo MUST contain ⚠️ inside its content when forced_stop=true.

    The warning block is prepended above §問題 per output-schema-memo.json
    `conditional_sections`. We check for ⚠️ anywhere outside the §Disclaimer
    section (so a generic Disclaimer mention of ⚠️ doesn't satisfy the
    consistency check).
    """
    # Strip out the §Disclaimer section before grepping for ⚠️.
    disclaimer_pattern = re.compile(
        r"^#{1,4}\s*§Disclaimer\s*$.*",
        re.MULTILINE | re.DOTALL,
    )
    body_before_disclaimer = disclaimer_pattern.sub("", memo_text)
    return "⚠️" in body_before_disclaimer


def _check_state_consistency(state: dict, memo_text: str) -> Tuple[list, bool]:
    """forced_stop=true MUST imply memo has ⚠️ block (and vice-versa, since
    a ⚠️ block without forced_stop suggests the state ledger is stale).

    Returns (errors, notes_only_flag) — notes_only_flag is True iff
    forced_stop=True AND memo has the ⚠️ block (PASS_WITH_NOTES per spec §6.6).
    """
    forced_stop = state.get("forced_stop")
    has_warning = _memo_has_warning_block(memo_text)
    errors = []
    notes_only = False
    if forced_stop is True and not has_warning:
        errors.append(
            "state_consistency: state.forced_stop=true but memo has no ⚠️ warning "
            "block — spec §6.6 requires the memo to surface the forced-stop "
            "coverage gap with a ⚠️ block prepended above §問題"
        )
    elif forced_stop is False and has_warning:
        errors.append(
            "state_consistency: memo contains ⚠️ warning block but state.forced_stop=false — "
            "stale state ledger suspected; either drop the ⚠️ block or set forced_stop=true"
        )
    elif forced_stop is True and has_warning:
        # Acceptable degraded path; downgrade exit code to 2 (PASS_WITH_NOTES).
        notes_only = True
    return errors, notes_only


# ---------------------------------------------------------- citation checks
def _extract_citation_entries(memo_text: str) -> list[str]:
    """Pull out the §Citations block as a list of entry strings.

    Each entry is delimited by a leading `N. **<type>**:` line. We return
    the full block of lines belonging to each entry (including the
    `→ <relevance>` continuation), so callers can grep for the relevance
    arrow on a per-entry basis.
    """
    sec_pattern = re.compile(
        r"^#{1,4}\s*§Citations\s*$(.*?)(?=^#{1,2}\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = sec_pattern.search(memo_text)
    if not match:
        return []
    body = match.group(1)

    entries: list[str] = []
    current: list[str] = []
    entry_head = re.compile(r"^\s*\d+\.\s+\*\*(條文|判決|函釋|學說)\*\*")
    for line in body.splitlines():
        if entry_head.match(line):
            if current:
                entries.append("\n".join(current))
            current = [line]
        elif current:
            current.append(line)
    if current:
        entries.append("\n".join(current))
    return entries


def _check_citation_section_present(memo_text: str) -> list[str]:
    if not re.search(r"^#{1,4}\s*§Citations", memo_text, re.MULTILINE):
        return ["citation_section_present: memo missing §Citations section"]
    return []


def _check_citation_count_or_warn(memo_text: str) -> list[str]:
    entries = _extract_citation_entries(memo_text)
    if len(entries) >= MIN_CITATIONS:
        return []
    if _memo_has_warning_block(memo_text):
        return []
    return [
        f"citation_count_or_warn: memo has {len(entries)} citations (< {MIN_CITATIONS}) "
        "and no ⚠️ warning block — either add more sources or surface the gap "
        "with a ⚠️ block (spec §6.6)"
    ]


def _check_citation_has_relevance(memo_text: str) -> list[str]:
    """Every entry in §Citations MUST have a `→ <relevance>` continuation line.

    Vague 1-token relevance (e.g. `→ 相關`) is NOT caught here per the
    citation-format.md anti-pattern §4.3 — that lives in a separate Path A
    grade step (not in the v0.5.2 grader). Here we only enforce presence.
    """
    entries = _extract_citation_entries(memo_text)
    errors = []
    for idx, entry in enumerate(entries, start=1):
        # Require a `→` line in the entry body (any line that starts with → after
        # optional indent).
        if not re.search(r"^\s*→\s*\S", entry, re.MULTILINE):
            # Pull the first 60 chars of the entry head for the error message.
            head = entry.splitlines()[0].strip()[:60]
            errors.append(
                f"citation_has_relevance: entry #{idx} ({head!r}) missing "
                "`→ <relevance>` continuation line (citation-format.md §1)"
            )
    return errors


def _check_source_type_coverage(memo_text: str) -> list[str]:
    """≥ 2 distinct types in §Citations OR memo has ⚠️ block.

    Types are extracted from the `**<type>**:` token of each entry.
    """
    entries = _extract_citation_entries(memo_text)
    types_seen: set[str] = set()
    entry_head = re.compile(r"^\s*\d+\.\s+\*\*(條文|判決|函釋|學說)\*\*")
    for entry in entries:
        m = entry_head.match(entry.splitlines()[0]) if entry.splitlines() else None
        if m:
            types_seen.add(m.group(1))
    if len(types_seen) >= MIN_SOURCE_TYPES:
        return []
    if _memo_has_warning_block(memo_text):
        return []
    return [
        f"source_type_coverage: memo has {len(types_seen)} distinct 法源類型 "
        f"({sorted(types_seen)}; < {MIN_SOURCE_TYPES}) and no ⚠️ block — "
        "either broaden source types or surface the gap with a ⚠️ block (spec §6.6)"
    ]


# ---------------------------------------------------------- summary checks
def _check_summary_conclusion_marker(summary_text: str) -> list[str]:
    """summary.md §結論 MUST contain at least one of ✅/⚠️/❌."""
    sec_pattern = re.compile(
        r"^#{1,4}\s*§結論\s*$(.*?)(?=^#{1,2}\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = sec_pattern.search(summary_text)
    if not match:
        # If §結論 is missing entirely, that's caught by structural_summary_md;
        # don't double-flag here.
        return []
    body = match.group(1)
    if not any(marker in body for marker in CONCLUSION_MARKERS):
        return [
            "conclusion_marker_required: summary.md §結論 must contain at least "
            f"one of {CONCLUSION_MARKERS} (per output-schema-summary.json)"
        ]
    return []


# ---------------------------------------------------------- disclaimer footer
def _check_disclaimer_footer(memo_text: str, summary_text: str) -> list[str]:
    """Both memo + summary MUST have §Disclaimer heading + canonical sentinels
    (`本研究` AND `不構成正式法律意見`).
    """
    errors = []
    disclaimer_heading = re.compile(r"^#{1,4}\s*§Disclaimer", re.MULTILINE)
    for label, text in (("research-memo.md", memo_text), ("executive-summary.md", summary_text)):
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
def grade_research(
    plan_path: Path,
    state_path: Path,
    memo_path: Path,
    summary_path: Path,
) -> GradeResult:
    reasons: list[str] = []
    notes_only = False

    # Existence (#1-#4).
    plan_missing = _check_file_exists(plan_path, "plan.md")
    state_missing = _check_file_exists(state_path, "state.json")
    memo_missing = _check_file_exists(memo_path, "research-memo.md")
    summary_missing = _check_file_exists(summary_path, "executive-summary.md")
    reasons.extend(plan_missing)
    reasons.extend(state_missing)
    reasons.extend(memo_missing)
    reasons.extend(summary_missing)
    if plan_missing or state_missing or memo_missing or summary_missing:
        return GradeResult(passed=False, reasons=reasons)

    # Size floors.
    reasons.extend(_check_file_min_size(memo_path, "research-memo.md", MIN_MEMO_MD_BYTES))
    reasons.extend(_check_file_min_size(summary_path, "executive-summary.md", MIN_SUMMARY_MD_BYTES))

    plan_text = plan_path.read_text(encoding="utf-8")
    memo_text = memo_path.read_text(encoding="utf-8")
    summary_text = summary_path.read_text(encoding="utf-8")

    # Structural (#5).
    reasons.extend(_check_plan_structural(plan_text))

    # Structural (#6-#8).
    state, state_load_errors = _load_state_json(state_path)
    reasons.extend(state_load_errors)
    if state is not None:
        reasons.extend(_check_state_structural(state))
        reasons.extend(_check_state_within_cap(state))
        consistency_errors, notes_only = _check_state_consistency(state, memo_text)
        reasons.extend(consistency_errors)

    # Structural (#9-#10).
    reasons.extend(_check_required_sections(memo_text, MEMO_REQUIRED_SECTIONS, "research-memo.md"))
    reasons.extend(_check_required_sections(summary_text, SUMMARY_REQUIRED_SECTIONS, "executive-summary.md"))

    # Citation (#11-#13).
    reasons.extend(_check_citation_section_present(memo_text))
    reasons.extend(_check_citation_count_or_warn(memo_text))
    reasons.extend(_check_citation_has_relevance(memo_text))
    reasons.extend(_check_source_type_coverage(memo_text))

    # Summary (#14).
    reasons.extend(_check_summary_conclusion_marker(summary_text))

    # Safety (#15).
    reasons.extend(_check_path_a_antipatterns(
        (plan_text, "plan.md"),
        (memo_text, "research-memo.md"),
        (summary_text, "executive-summary.md"),
    ))
    reasons.extend(_check_no_template_orphans(plan_text, memo_text, summary_text))
    reasons.extend(_check_disclaimer_footer(memo_text, summary_text))

    return GradeResult(passed=not reasons, reasons=reasons, notes_only=notes_only)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Deterministic structural grader for legal-research output "
            "(plan.md + state.json + research-memo.md + executive-summary.md)."
        ),
    )
    parser.add_argument("--plan", required=True, type=Path, help="Path to plan.md")
    parser.add_argument("--state", required=True, type=Path, help="Path to state.json")
    parser.add_argument("--memo", required=True, type=Path, help="Path to research-memo.md")
    parser.add_argument("--summary", required=True, type=Path, help="Path to executive-summary.md")
    args = parser.parse_args()

    result = grade_research(args.plan, args.state, args.memo, args.summary)
    if result.passed:
        if result.notes_only:
            print("OK_WITH_NOTES: structural grading PASS_WITH_NOTES (forced_stop + ⚠️)")
            return 2
        print("OK: structural grading PASS")
        return 0
    for r in result.reasons:
        print(f"FAIL: {r}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

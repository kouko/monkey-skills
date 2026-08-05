"""Pointer-pin pytest for the writing-plans SKILL.md extraction batch,
Partition A (docs/loom/specs/2026-08-05-loom-skill-extraction-batch.md
§Partition A — the FROZEN extraction SSOT).

Guards: A1 (Cross-skill contract) + A2 (What this skill does NOT do) fold
into references/cross-skill-map.md, headings absent from SKILL.md, a
residue/pointer line present in each's old location; A3 (Red Flags table)
moves to references/red-flags.md under pilot house shape — the heading +
a one-line refusal-posture distillation STAY inline, only the table rows
move; A4 (maintainer-facing fragments in §BLOCKED fallback, §Plan size
ceiling, §Consuming) move to references/design-evidence.md (author-facing
header) while the rules they qualify, and the 5-step process / anti-pattern
paragraph / detection-cascade rule sentences, stay inline verbatim. Word
ceiling drops to <=3900. §Amending a PASS plan (MUST NOT MOVE, including
its exactly-3-item closed list — pinned separately by
test_post_pass_amendment_gate.py) and the splitting framework are
untouched anti-vacuous survivors.
"""
import re
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1] / "skills" / "writing-plans"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFERENCES = SKILL_DIR / "references"


def _norm(text: str) -> str:
    """Whitespace-normalize for robust substring checks."""
    return re.sub(r"\s+", " ", text).strip()


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _skill_text() -> str:
    return _read(SKILL_MD)


# --- (a) pointer/residue lines present in SKILL.md -------------------------

def test_cross_skill_map_pointer_present():
    assert "references/cross-skill-map.md" in _skill_text()


def test_red_flags_pointer_present():
    assert "references/red-flags.md" in _skill_text()


def test_design_evidence_pointer_present():
    assert "references/design-evidence.md" in _skill_text()


# --- (b) moved section headings absent from SKILL.md, present in destinations (A1 + A2) ---

def test_cross_skill_contract_heading_absent_from_skill_present_in_reference():
    assert "## Cross-skill contract" not in _skill_text()
    dest = _read(REFERENCES / "cross-skill-map.md")
    assert "Cross-skill contract" in dest
    assert "**Upstream**" in dest and "`brainstorming`" in dest


def test_what_skill_does_not_do_heading_absent_from_skill_present_in_reference():
    assert "## What this skill does NOT do" not in _skill_text()
    dest = _read(REFERENCES / "cross-skill-map.md")
    assert "What this skill does NOT do" in dest
    assert "Does **not** write code" in dest


# --- (c) Red Flags: pilot house shape — heading + distillation STAY, table moves ---

def test_red_flags_table_absent_from_skill_present_in_reference():
    marker = '"Just skip planning, the brief is enough."'
    assert marker not in _skill_text()
    dest = _read(REFERENCES / "red-flags.md")
    assert marker in dest
    assert "「先跳過 plan 直接派 SDD 吧 / プランは飛ばして」" in dest
    # house shape (requesting-code-review pilot): the heading itself stays
    assert "## Red Flags — refuse these rationalizations" in _skill_text()


# --- (d) A4 maintainer fragments absent from SKILL.md, present in design-evidence.md ---

def test_beck_quote_absent_from_skill_present_in_design_evidence():
    fragment = "When you are working on a test and it gets too big"
    assert fragment not in _skill_text()
    dest = _read(REFERENCES / "design-evidence.md")
    assert fragment in dest


def test_why_depth_evidence_absent_from_skill_present_in_design_evidence():
    fragment = "a depth-5 chain at ~95% per-step reliability succeeds only ~77% of the time"
    assert fragment not in _skill_text()
    dest = _read(REFERENCES / "design-evidence.md")
    assert fragment in dest


def test_industry_precedent_parenthetical_absent_from_skill_present_in_design_evidence():
    fragment = "spec-kit, OpenSpec, Jira smart commits"
    assert fragment not in _skill_text()
    dest = _read(REFERENCES / "design-evidence.md")
    assert fragment in dest


def test_d8_mirror_sentence_absent_from_skill_present_in_design_evidence():
    fragment = 'mirrors `code-reviewer.md`\'s D8 "Activation is self-derived" anchor pattern'
    assert fragment not in _skill_text()
    dest = _read(REFERENCES / "design-evidence.md")
    assert fragment in dest


def test_design_evidence_header_states_author_facing_no_runtime_load():
    dest_norm = _norm(_read(REFERENCES / "design-evidence.md"))
    assert "author-facing" in dest_norm
    assert "do NOT load this file at runtime" in dest_norm


# --- (e) pinned survivors still inline in SKILL.md (anti-vacuous positives) ---

def test_amending_a_pass_plan_still_inline():
    text = _skill_text()
    assert "**Amending a PASS plan:**" in text
    # its exactly-3-item closed list must survive untouched
    assert "**Stamping the verdict**" in text
    assert "**Fixing a typo**" in text
    assert "**Filling a schema field**" in text


def test_splitting_framework_heading_still_inline():
    assert "## The splitting framework" in _skill_text()


def test_blocked_fallback_five_step_process_and_anti_pattern_stay_inline():
    text = _skill_text()
    assert "Applies the splitting framework to produce **child tasks**" in text
    assert "**Anti-pattern**" in text


def test_consuming_section_and_detection_rule_sentences_stay_inline():
    text = _skill_text()
    assert "## Consuming a loom-spec change-folder" in text
    assert "git rev-parse --show-toplevel" in text
    assert "resolve the target repo's root" in text


def test_plan_size_ceiling_core_rule_stays_inline():
    text = _skill_text()
    assert "critical-path **depth**" in text
    assert "Route back to brainstorming" in text


# --- (f) word cap ------------------------------------------------------------

def test_word_count_at_most_3900():
    word_count = len(_skill_text().split())
    assert word_count <= 3900, f"SKILL.md is {word_count} words, over the 3900 cap"

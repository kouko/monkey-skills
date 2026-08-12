"""Pointer-pin pytest for the requesting-code-review SKILL.md extraction pilot.

Guards the brief's FROZEN partition
(docs/loom/specs/2026-08-05-rcr-skill-extraction-pilot.md §The partition):
five pointer/residue lines land in SKILL.md, the four moved section
headings/tables leave SKILL.md and land in their destination reference
files, the audience-misplaced evidence fragments leave §Verdict structure
for references/design-evidence.md while the fragments other tests pin
stay inline, and the word count drops under the new ceiling.
"""
import re
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1] / "skills" / "requesting-code-review"
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

def test_scope_comparison_pointer_present():
    assert "references/scope-comparison.md" in _skill_text()


def test_cross_skill_map_pointer_present():
    assert "references/cross-skill-map.md" in _skill_text()


def test_push_trigger_rationalizations_pointer_present():
    assert "references/push-trigger-rationalizations.md" in _skill_text()


def test_red_flags_pointer_present():
    assert "references/red-flags.md" in _skill_text()


def test_design_evidence_pointer_present():
    assert "references/design-evidence.md" in _skill_text()


# --- (b) moved section headings/table absent from SKILL.md, present in destinations ---

def test_scope_comparison_heading_absent_from_skill_present_in_reference():
    heading = "When this is different from SDD's per-task reviewer"
    assert heading not in _skill_text()
    dest = _read(REFERENCES / "scope-comparison.md")
    assert heading in dest
    assert "Cumulative branch diff (all tasks combined)" in dest


def test_cross_skill_contract_heading_absent_from_skill_present_in_reference():
    assert "## Cross-skill contract" not in _skill_text()
    dest = _read(REFERENCES / "cross-skill-map.md")
    assert "Cross-skill contract" in dest
    assert "Calls this skill as Step 1 of the close-branch flow" in dest


def test_push_trigger_rationalizations_table_absent_from_skill_present_in_reference():
    marker = "User's message ends with"
    assert marker not in _skill_text()
    dest = _read(REFERENCES / "push-trigger-rationalizations.md")
    assert marker in dest
    assert "Auto-mode classifier passes the `git push` invocation" in dest


def test_red_flags_table_absent_from_skill_present_in_reference():
    marker = "\"It's fine, just merge.\""
    assert marker not in _skill_text()
    dest = _read(REFERENCES / "red-flags.md")
    assert marker in dest
    assert "「審查跳過 / レビューはスキップ」" in dest
    # house shape (finishing-a-development-branch): the heading itself stays
    assert "## Red Flags — refuse these rationalizations" in _skill_text()


# --- (c) audience-misplaced evidence fragments absent from SKILL.md, present in design-evidence.md ---

def test_exit_clause_absent_from_skill_present_in_design_evidence():
    fragment = "re-evaluate panel width against the G4 baseline"
    assert fragment not in _skill_text()
    dest = _read(REFERENCES / "design-evidence.md")
    assert fragment in dest


def test_g4_ab_evidence_absent_from_skill_present_in_design_evidence():
    fragment = "a single-Sonnet verdict missed the correct call 1-of-2 times"
    assert fragment not in _skill_text()
    dest = _read(REFERENCES / "design-evidence.md")
    assert fragment in dest
    assert "2026-07-06-g4-sonnet-vs-fable-ab.md" in dest


def test_design_evidence_header_states_author_facing_no_runtime_load():
    dest_norm = _norm(_read(REFERENCES / "design-evidence.md"))
    assert "author-facing" in dest_norm
    assert "do NOT load this file at runtime" in dest_norm


# --- (d) pinned survivors still inline in SKILL.md --------------------------

def test_g4_measured_why_fragment_stays_inline():
    assert "a single-arm verdict is degraded evidence — G4 measured why" in _skill_text()


def test_advisory_only_rule_sentence_stays_inline_evidence_tail_gone():
    text = _skill_text()
    assert "each arm's own `verdict:` is advisory only" in text
    assert "Evidence: G4 A/B" not in text


def test_inherit_by_design_rule_stays_inline_calibration_parenthetical_gone():
    text = _skill_text()
    assert "reviewers inherit the session model by design" in text
    assert "G4's evidence was measured on exactly the inherit configuration" not in text


def test_union_evidence_rule_stays_inline_parenthetical_gone():
    text = _skill_text()
    assert "no cross-arm adjudication" in text
    assert "PR #503/#504" not in text


def test_see_also_version_tag_deleted_not_moved():
    assert "v0.6.0+ / P15-12 Phase 2" not in _skill_text()
    assert "v0.6.0+ / P15-12 Phase 2" not in _read(REFERENCES / "design-evidence.md")


def test_pinned_refusal_and_pass_down_contracts_untouched():
    text = _skill_text()
    assert "§Pinned refusal contract" in text
    assert "§Pinned pass-down contract" in text


# --- (e) word cap ------------------------------------------------------------

# Raised deliberately 3920 -> 3935 by the 2026-08-10 ship-progress-tooling
# arc, Task 2: one plugin-fallback cascade sentence on the review-round
# stage-flip duty so external repos resolve the plugin-shipped
# plan_card.py instead of degrading to hand-edits. Raised again
# 3935 -> 4150 by the 2026-08-11 review-cost-reduction arc, Task 8: the
# contract/record classification SSOT section plus the record-only,
# docs-only, and mixed-branch routing-bullet rewrites (record-class `.md`
# exemption + the record-only continuity marker verb) net-added ~215
# words that could not be trimmed further without losing pinned
# hand-off-pattern substrings other tests in this repo assert on. Raised
# again 4150 -> 4300 by the same arc's Task 12: the M3 mechanical
# upgrade rule paragraph (three path-based triggers + the honesty note,
# ~70 words) plus the docs-only bullet's stale-cross-ref rewrite (the
# old "bounded convergence cap (2 rounds + one conditional auto-delta
# round)" replaced with a pointer to requesting-docs-review's own
# Directives, net near-zero) landed at 4220 words -- under the 4300
# fallback the task brief authorizes, so no further trim was needed;
# the chain is cumulative: 3920 -> 3935 -> 4150 -> 4300 -> 4315 (the
# last raise by the 2026-08-12 adjudication-view arc's T7 pointer
# sentence at Step 5 — the conversation-language findings-rendition
# duty, ~15 words, pointer-not-copy so untrimmable without losing the
# duty).
WORD_CEILING = 4315

def test_word_count_within_ceiling():
    word_count = len(_skill_text().split())
    assert word_count <= WORD_CEILING, (
        f"SKILL.md is {word_count} words, over the {WORD_CEILING} ceiling "
        "(raised deliberately 3900 -> 3920 by the 2026-08-08 "
        "progress-display-hardening arc, Task 3 fix round, to restore "
        "the plan's 'and commit the flip' wording that round-1 had "
        "trimmed to fit under the old cap, then 3920 -> 3935 by the "
        "2026-08-10 ship-progress-tooling arc's cascade sentence, then "
        "3935 -> 4150 by the 2026-08-11 review-cost-reduction arc's Task "
        "8 contract/record classification SSOT + record-only routing, "
        "then 4150 -> 4300 by the same arc's Task 12 M3 upgrade-rule "
        "paragraph + stale-cross-ref rewrite, then 4300 -> 4315 by the "
        "2026-08-12 adjudication-view arc's T7 Step-5 pointer sentence; "
        "the extraction-pilot brief reserves ~600 words of true headroom "
        "to CHK-SKL-010)"
    )

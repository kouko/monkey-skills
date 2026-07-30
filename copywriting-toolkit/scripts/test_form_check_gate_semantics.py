"""Pins for copywriting-form-check-stage's 8b verdict rule (contract-class
aggregation, pointer to CLAUDE.md — no local restatement) and the
form-appropriate-gate rubric's dimension-row class annotations
(contract = objective form-constraint; craft = qualitative, recorded).

Window discipline (docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md):
presence assertions are scoped to the specific passage/heading anchor —
never whole-file — so generic terms elsewhere cannot false-green a pin.
The whole-file assertions are the two ABSENCE pins (retired "2+ 🟡 →
NEEDS_REVISION" accumulation rule must not survive in either file) and
the loop-back+caps UNCHANGED pin (byte-identical anchored window).

No registered REQ-ids in this dispatch — @req tags intentionally omitted.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_MD = ROOT / "skills" / "copywriting-form-check-stage" / "SKILL.md"
RUBRIC_MD = (
    ROOT
    / "skills"
    / "copywriting-form-check-stage"
    / "rubrics"
    / "form-appropriate-gate.md"
)

VERDICT_ANCHOR = "Gate 8b runs in **flag mode**"
LOOPBACK_HEADING = "## Loop-Back on `NEEDS_REVISION`"
LOOPBACK_END = "## Returned Envelope"

# Byte-identical pin: this is the exact loop-back mechanics + caps window as
# it existed BEFORE this task's edit. Task 3 must not touch it.
LOOPBACK_PINNED_EXCERPT = """## Loop-Back on `NEEDS_REVISION`

Per plugin convention (see `../../CLAUDE.md`, and revise-loop cap
inherited from copywriting-team), **maximum 2 revise rounds** per
phase. Protocol:

1. Attach the evaluator's per-item findings to the envelope as
   `form_findings`.
2. Set `next_stage` back to the Phase 4 drafter skill implied by
   `envelope.form`:
   - `short-form` → `copywriting-short-form`
   - `mid-form` → `copywriting-mid-form`
   - `long-form-pasona` → `copywriting-long-form-pasona`
   - `long-form-extended` → `copywriting-long-form-extended`
   - `light-action` → `copywriting-light-action`
3. Track `revise_round_count` in the envelope. On entering a 3rd
   round, stop the loop and surface the situation to the user for a
   human decision (change `form`, change `message_thesis`, or
   accept-with-notes).

Do NOT re-run Phase 5 (positioning), Phase 6 (tone), or Phase 7
(ethics) on loop-back unless the drafter materially changes the
message thesis. Ethics re-gating is required if the drafter's rewrite
introduces new claims, testimonials, or urgency framing.

"""

# Dimension rows expected to be tagged `contract` — objective form-constraint
# rows (explicit length/char limits, mandatory declared-voice-target checks).
CONTRACT_ROWS = (
    "RUB-CTW-FA-L3",  # Word-Count Ratios
    "RUB-CTW-FA-S2",  # 7-15 字 Discipline
)

# Dimension rows expected to be tagged `craft` — qualitative execution rows
# (flow, drop-off hooks, persuasion depth/thickness, clarity/technique feel).
CRAFT_ROWS = (
    "RUB-CTW-FA-L1",  # Flow / Progression
    "RUB-CTW-FA-L2",  # Drop-off Prevention Design
    "RUB-CTW-FA-L4",  # PASBECONA B/E/C Persuasion Depth
    "RUB-CTW-FA-M1",  # Benefit-first Clarity
    "RUB-CTW-FA-M2",  # Evidence Concreteness
    "RUB-CTW-FA-M3",  # Advantage Comparison Clarity
    "RUB-CTW-FA-S1",  # 3-Second Land Ability
    "RUB-CTW-FA-S3",  # 掛詞 / Phonetic Technique Recognition
    "RUB-CTW-FA-S4",  # 5-Type 切入点 Clarity
)


def _skill() -> str:
    return SKILL_MD.read_text(encoding="utf-8")


def _rubric() -> str:
    return RUBRIC_MD.read_text(encoding="utf-8")


def _verdict_window() -> str:
    """The 8b verdict-rule passage: from its unique anchor to the next H2."""
    text = _skill()
    start = text.find(VERDICT_ANCHOR)
    assert start != -1, f"anchor {VERDICT_ANCHOR!r} absent from SKILL.md"
    nxt = text.find("\n## ", start)
    return text[start:nxt] if nxt != -1 else text[start:]


def _row_window(row_id: str) -> str:
    """One dimension row: from its `### RUB-CTW-FA-*` heading to the next
    `###` or `##` heading."""
    text = _rubric()
    heading_start = text.find(f"### {row_id}")
    assert heading_start != -1, f"dimension heading {row_id!r} absent from rubric"
    line_end = text.find("\n", heading_start)
    nxt_h3 = text.find("\n### ", line_end)
    nxt_h2 = text.find("\n## ", line_end)
    candidates = [i for i in (nxt_h3, nxt_h2) if i != -1]
    end = min(candidates) if candidates else len(text)
    return text[heading_start:end]


def test_skill_verdict_rule_is_contract_class_pointer_no_restatement():
    # WHY: the retired accumulation rule ("2+ 🟡 → NEEDS_REVISION") must be
    # replaced by a one-line pointer to CLAUDE.md's canonical vocabulary —
    # not a local re-derivation of the class definitions.
    window = _verdict_window()
    assert re.search(r"CLAUDE\.md.*Gate Convergence Vocabulary", window), (
        "8b verdict passage missing a pointer to CLAUDE.md's canonical "
        "vocabulary section"
    )
    assert "contract-class" in window, "8b verdict passage lacks contract-class aggregation wording"
    # no local restatement of the canonical definition prose
    # (case-insensitive — a capitalization-only rephrasing must not
    # false-pass; same fix class as commit 7f13682c)
    assert "objective checkable referent" not in window.lower()
    assert "qualitative observation" not in window.lower()


def test_old_yellow_accumulation_rule_absent_skill():
    # WHY: absence pin (whole-file on purpose) — the retired count-based
    # "2+ 🟡 → NEEDS_REVISION" rule must not survive anywhere in SKILL.md.
    text = _skill()
    assert not re.search(r"2\+\s*🟡", text), "retired 2+ 🟡 accumulation rule present"
    assert not re.search(r"two or more 🟡", text)


def test_old_yellow_accumulation_rule_absent_rubric():
    # WHY: same absence pin, applied to the rubric file — the Verdict Rules
    # section must not restate the retired accumulation rule either.
    # Markdown bold markers (`**`) may sit between the count and the emoji
    # (e.g. "**2 or more** 🟡"), so strip them before matching.
    text = _rubric().replace("**", "")
    assert not re.search(r"2\s*(or more|\+)\s*🟡", text), (
        "retired 2-or-more 🟡 accumulation rule present in rubric"
    )
    assert not re.search(r"two or more 🟡", text)


def test_rubric_verdict_rules_points_at_claude_md():
    # WHY: the rubric's own Verdict Rules section must not restate the
    # retired count rule — it points at the canonical vocabulary instead.
    text = _rubric()
    assert re.search(r"CLAUDE\.md.*Gate Convergence Vocabulary", text), (
        "rubric Verdict Rules section missing a pointer to CLAUDE.md's "
        "canonical vocabulary section"
    )


def test_contract_rows_annotated():
    # WHY: objective form-constraint rows (length/char-count checkable
    # against a stated band) must be tagged `contract` so they gate.
    for row_id in CONTRACT_ROWS:
        window = _row_window(row_id)
        assert re.search(r"Class:\s*`contract`", window), (
            f"{row_id} missing `Class: contract` annotation"
        )


def test_craft_rows_annotated():
    # WHY: qualitative execution rows (flow, hooks, persuasion depth,
    # clarity/technique feel) must be tagged `craft` — recorded, never gate.
    for row_id in CRAFT_ROWS:
        window = _row_window(row_id)
        assert re.search(r"Class:\s*`craft`", window), (
            f"{row_id} missing `Class: craft` annotation"
        )


def test_additional_dimensions_annotated():
    # WHY: the two plugin-native 8b dimensions also need a class — the
    # word-count band check is an explicit length limit (contract); the
    # schwartz_alignment carry-forward checks a declared voice target
    # (contract per the vocabulary's own referent list).
    text = _rubric()
    heading = "### Dimension — Word-count band adherence"
    start = text.find(heading)
    assert start != -1, "word-count band adherence dimension absent"
    nxt = text.find("\n### ", start + len(heading))
    window = text[start:nxt] if nxt != -1 else text[start:]
    assert re.search(r"Class:\s*`contract`", window)

    heading2 = "### Dimension — `schwartz_alignment: conflict_flagged`"
    start2 = text.find(heading2)
    assert start2 != -1, "schwartz_alignment carry-forward dimension absent"
    window2 = text[start2:]
    assert re.search(r"Class:\s*`contract`", window2)


def test_loopback_and_caps_window_unchanged():
    # WHY: Task 3 scope explicitly excludes the loop-back mechanics + caps —
    # this pin proves the anchored window is byte-identical to its
    # pre-task state.
    text = _skill()
    start = text.find(LOOPBACK_HEADING)
    assert start != -1, f"heading {LOOPBACK_HEADING!r} absent from SKILL.md"
    end = text.find(LOOPBACK_END, start)
    assert end != -1, f"heading {LOOPBACK_END!r} absent from SKILL.md"
    window = text[start:end]
    assert window == LOOPBACK_PINNED_EXCERPT, (
        "loop-back mechanics + caps window changed — this is out of scope "
        "for Task 3"
    )

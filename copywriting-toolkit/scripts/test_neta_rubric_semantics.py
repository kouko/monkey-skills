"""Pins for copywriting-neta-injection/rubrics/neta-safety-gate.md's
Verdict Rules section: contract-class-only aggregation (mirrors the
sibling fix already landed on voice-consistency-gate.md, commits
50caf36a + e32498db) and copywriting-neta-injection/SKILL.md's verdict
enum declaration.

Window discipline (docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md):
presence assertions for the verdict-rules pointer + contract-class wording
are scoped to the "## Verdict Rules" section by its unique heading anchor.
The retired count-based rule strings are pinned as whole-file ABSENCE
checks (the exact phrases that used to live at :322-326).

Path depth note: this rubric lives at
skills/copywriting-neta-injection/rubrics/neta-safety-gate.md — THREE
levels below the plugin-root CLAUDE.md (rubrics/ -> copywriting-neta-
injection/ -> skills/ -> copywriting-toolkit/), so the correct pointer is
`../../../CLAUDE.md`. A sibling rubric (voice-consistency-gate.md, same
depth) landed with the wrong two-level `../../CLAUDE.md` by mistake —
this test guards against repeating that.

No registered REQ-ids in this dispatch — @req tags intentionally omitted.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUBRIC = (
    ROOT
    / "skills"
    / "copywriting-neta-injection"
    / "rubrics"
    / "neta-safety-gate.md"
)
SKILL = ROOT / "skills" / "copywriting-neta-injection" / "SKILL.md"

VERDICT_HEADING = "## Verdict Rules"

# The exact retired count-based lines this task retires (originally :322-326).
RETIRED_ALL_GREEN = "All 3 soft dimensions 🟢 → `PASS`"
RETIRED_1_2_YELLOW = "1-2 soft dimensions 🟡, rest 🟢, no 🔴 → `PASS_WITH_NOTES`"
RETIRED_ANY_RED = "Any soft dimension 🔴 → `NEEDS_REVISION`"
RETIRED_3_YELLOW = "3 soft dimensions 🟡 → `NEEDS_REVISION`"

DIMENSION_HEADING_RE = re.compile(r"^### Dimension \d+:", re.MULTILINE)


def _text() -> str:
    return RUBRIC.read_text(encoding="utf-8")


def _verdict_window() -> str:
    """The Verdict Rules section: from its unique heading to the next H2."""
    text = _text()
    start = text.find(VERDICT_HEADING)
    assert start != -1, f"heading {VERDICT_HEADING!r} absent from neta-safety-gate.md"
    nxt = text.find("\n## ", start + len(VERDICT_HEADING))
    return text[start:nxt] if nxt != -1 else text[start:]


def test_verdict_rules_pointer_to_claude_md_vocabulary():
    # WHY: contract/craft semantics are canonical in CLAUDE.md §Gate
    # Convergence Vocabulary; this rubric must point at it — at the
    # correct THREE-level relative depth — rather than restate a second,
    # now-stale local definition.
    window = _verdict_window()
    refs = re.findall(r"(?:\.\./)+CLAUDE\.md", window)
    assert refs, "Verdict Rules must pointer-cite CLAUDE.md §Gate Convergence Vocabulary"
    assert "Gate Convergence Vocabulary" in window
    for ref in refs:
        assert ref == "../../../CLAUDE.md", (
            "CLAUDE.md pointer must be the three-level '../../../CLAUDE.md' "
            "(rubrics/ -> copywriting-neta-injection/ -> skills/ -> "
            f"copywriting-toolkit/), got {ref!r}"
        )


def test_verdict_rules_contract_class_only_aggregation():
    # WHY: verdicts aggregate over contract-class findings ONLY; craft-class
    # findings (Cringe Index, Audience Capital Match) are recorded but never
    # gate, alone or in accumulation.
    window = _verdict_window()
    assert "contract-class" in window, "contract-class aggregation wording missing"
    assert "craft" in window and re.search(r"never gate", window), (
        "craft-class never-gates carve-out missing from Verdict Rules"
    )


def test_retired_count_based_verdict_rules_absent_whole_file():
    # WHY: absence pin (whole-file on purpose) — the retired count-based
    # soft-dimension accumulation rules must not survive anywhere in this
    # file, including under a renamed heading or moved position.
    # case-insensitive — a capitalization-only revival must not
    # false-pass (same fix class as commit 7f13682c / 0e85e073)
    text = _text().lower()
    assert RETIRED_ALL_GREEN.lower() not in text, "retired 'All 3 soft dimensions 🟢' rule present"
    assert RETIRED_1_2_YELLOW.lower() not in text, "retired '1-2 soft dimensions 🟡' rule present"
    assert RETIRED_ANY_RED.lower() not in text, "retired 'Any soft dimension 🔴' rule present"
    assert RETIRED_3_YELLOW.lower() not in text, "retired '3 soft dimensions 🟡' rule present"


def test_each_dimension_carries_contract_craft_class_annotation():
    # WHY: task (c) — every one of the 5 dimensions (2 hard vetoes + 3 soft)
    # must be annotated per the SSOT definitions (objective checkable
    # referent -> contract; taste -> craft) so aggregation is unambiguous.
    text = _text()
    headings = list(DIMENSION_HEADING_RE.finditer(text))
    assert len(headings) == 5, f"expected 5 dimension headings, found {len(headings)}"
    verdict_start = text.find("\n## Verdict Rules")
    for i, m in enumerate(headings):
        start = m.end()
        end = headings[i + 1].start() if i + 1 < len(headings) else verdict_start
        block = text[start:end]
        assert re.search(r"\*\*Class\*\*:\s*(contract|craft)\b", block), (
            f"dimension block starting {m.group(0)!r} missing a **Class**: contract|craft annotation"
        )


def test_hard_veto_dimensions_classed_contract():
    # WHY: hard vetoes (copyright/trademark, 景表法 stealth marketing) are
    # contract by nature — no ambiguity should be tolerated here.
    text = _text()
    headings = list(DIMENSION_HEADING_RE.finditer(text))
    verdict_start = text.find("\n## Verdict Rules")
    for i, m in enumerate(headings[:2]):
        start = m.end()
        end = headings[i + 1].start() if i + 1 < len(headings) else verdict_start
        block = text[start:end]
        assert re.search(r"\*\*Class\*\*:\s*contract\b", block), (
            f"hard-veto dimension {m.group(0)!r} must be classed contract"
        )


def test_verdict_arrows_from_yellow_require_contract_class_qualifier():
    # WHY: no rule may aggregate a VERDICT from a bare 🟡 count; any line
    # that routes a 🟡 finding to a verdict must say so via the
    # contract-class qualifier.
    window = _verdict_window()
    yellow_verdict_lines = [
        line
        for line in window.splitlines()
        if "🟡" in line and re.search(r"→\s*`(NEEDS_REVISION|PASS_WITH_NOTES)`", line)
    ]
    assert yellow_verdict_lines, "expected at least one 🟡-to-verdict rule line in Verdict Rules"
    for line in yellow_verdict_lines:
        assert "contract-class" in line, (
            f"verdict-routing line uses bare 🟡 without contract-class qualifier: {line!r}"
        )


def test_diverged_header_present_and_cites_tier2_exception():
    # WHY: task (d) — Tier-2 divergence requires a header naming exactly
    # what is replaced and citing the sanctioned exception + plan. This
    # file opens with YAML frontmatter (unlike the voice rubric sibling),
    # so the DIVERGED header sits right after the frontmatter closes,
    # not at the absolute file start — placing it before the frontmatter
    # would break YAML parsing.
    text = _text()
    header_start = text.find("<!--")
    assert header_start != -1, "DIVERGED header comment missing"
    frontmatter_end = text.find("---", text.find("---") + 3) + 3
    assert header_start >= frontmatter_end, (
        "DIVERGED header must come after the YAML frontmatter closes, not before it"
    )
    header_end = text.find("-->", header_start)
    header = text[header_start : header_end + 3]
    assert "DIVERGED FROM domain-teams:copywriting-team" in header
    assert "Tier 2" in header and "Exception" in header, (
        "header must cite CLAUDE.md §Tier 2 Exception"
    )
    assert "2026-07-30-copywriting-convergence-modernization" in header, (
        "header must cite the modernization plan"
    )
    assert "v1.15.0" in header
    # Gotcha guard: the header must not restate the literal verdict-section
    # heading string, or find-first windowing on "## Verdict Rules" breaks.
    assert "## Verdict Rules" not in header


def test_skill_md_verdict_enum_is_three_valued():
    # WHY: task (e) — the enforcing schema (envelope.schema.json) declares
    # a 3-valued verdict enum; SKILL.md's prose enum line must match.
    text = SKILL.read_text(encoding="utf-8")
    assert "Verdict enum: `PASS` | `PASS_WITH_NOTES` | `NEEDS_REVISION`" in text, (
        "SKILL.md verdict enum line must be three-valued"
    )

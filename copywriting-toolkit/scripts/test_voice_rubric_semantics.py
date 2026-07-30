"""Pins for copywriting-voice-tone-stage/rubrics/voice-consistency-gate.md's
Verdict Rules section: contract-class-only aggregation (mirrors the sibling
fix already landed in the SKILL.md gate passage, commit 0ea45ea1).

Window discipline (docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md):
presence assertions for the verdict-rules pointer + contract-class wording
are scoped to the "## Verdict Rules" section by its unique heading anchor.
The retired count-based rule strings are pinned as whole-file ABSENCE checks
(the exact phrases that used to live at :241-242).

No registered REQ-ids in this dispatch — @req tags intentionally omitted.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUBRIC = (
    ROOT
    / "skills"
    / "copywriting-voice-tone-stage"
    / "rubrics"
    / "voice-consistency-gate.md"
)

VERDICT_HEADING = "## Verdict Rules"

# The exact retired count-based lines this task retires (originally :241-242).
RETIRED_2_OR_MORE = "**2 or more** 🟡 warnings → `NEEDS_REVISION`"
RETIRED_1_WARNING = "**1** 🟡 warning (no 🔴) → `PASS_WITH_NOTES` (auto-revise trigger)"

DIMENSION_HEADING_RE = re.compile(r"^### Dimension \d+:.*\(RUB-CTW-VC-\d+\)", re.MULTILINE)


def _text() -> str:
    return RUBRIC.read_text(encoding="utf-8")


def _verdict_window() -> str:
    """The Verdict Rules section: from its unique heading to the next H2."""
    text = _text()
    start = text.find(VERDICT_HEADING)
    assert start != -1, f"heading {VERDICT_HEADING!r} absent from voice-consistency-gate.md"
    nxt = text.find("\n## ", start + len(VERDICT_HEADING))
    return text[start:nxt] if nxt != -1 else text[start:]


def test_verdict_rules_pointer_to_claude_md_vocabulary():
    # WHY: contract/craft semantics are canonical in CLAUDE.md §Gate
    # Convergence Vocabulary; this rubric must point at it, not restate a
    # second (and now contradicting) local definition.
    window = _verdict_window()
    assert "../../../CLAUDE.md" in window and "Gate Convergence Vocabulary" in window, (
        "Verdict Rules must pointer-cite CLAUDE.md §Gate Convergence Vocabulary"
    )


def test_verdict_rules_contract_class_only_aggregation():
    # WHY: verdicts aggregate over contract-class findings ONLY; craft-class
    # findings are recorded but never gate, alone or in accumulation.
    window = _verdict_window()
    assert "contract-class" in window, "contract-class aggregation wording missing"
    assert "craft" in window and re.search(r"never gate", window), (
        "craft-class never-gates carve-out missing from Verdict Rules"
    )


def test_retired_count_based_verdict_rules_absent_whole_file():
    # WHY: absence pin (whole-file on purpose) — the retired count-based
    # accumulation rules must not survive anywhere in this file, including
    # under a renamed heading or moved position.
    text = _text()
    assert RETIRED_2_OR_MORE not in text, "retired '2 or more 🟡 warnings' rule present"
    assert RETIRED_1_WARNING not in text, "retired '1 🟡 warning' rule present"


def test_each_dimension_carries_contract_craft_class_annotation():
    # WHY: task (c) — every dimension row must be annotated per the SSOT
    # definitions (objective checkable referent -> contract; qualitative ->
    # craft) so the evaluator's per-dimension aggregation is unambiguous.
    text = _text()
    headings = list(DIMENSION_HEADING_RE.finditer(text))
    assert len(headings) == 7, f"expected 7 dimension headings, found {len(headings)}"
    for i, m in enumerate(headings):
        start = m.end()
        end = headings[i + 1].start() if i + 1 < len(headings) else text.find("\n## Verdict Rules")
        block = text[start:end]
        assert re.search(r"\*\*Class\*\*:\s*(contract|craft)\b", block), (
            f"dimension block starting {m.group(0)!r} missing a **Class**: contract|craft annotation"
        )


def test_verdict_arrows_from_yellow_require_contract_class_qualifier():
    # WHY: task (d) — 🔴/🟡 severity marks may remain as severity, but no
    # rule may aggregate a VERDICT from bare 🟡 counts; any line that routes
    # a 🟡 finding to a verdict must say so via the contract-class qualifier.
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

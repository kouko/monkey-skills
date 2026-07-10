"""Structural grep-test guarding the two NEW optional PRINCIPLES.md sections
(`## Anchors`, `## Deviation Ledger`) in the rules SSOT —
`skills/product-principles/references/principles-rules.md` (Task 3).

A later task (Task 4) extends `validate_principles_output.py` with
enforce-when-present checks for these sections; this rules file is the SSOT
the validator contract points at. This test pins the section formats +
validator-contract rows the rules file must define, tolerant of wording
variation, per the existing test style in test_question_sets.py.

No REQ-ids are registered for this dispatch — `@req` tags omitted per the
implementer contract.

Stdlib only (re + pathlib). Resolve the reference file relative to this
test file.
"""

import re
from pathlib import Path

RULES = (
    Path(__file__).parents[1]
    / "skills"
    / "product-principles"
    / "references"
    / "principles-rules.md"
)

EM = "—"  # em dash


def _text() -> str:
    assert RULES.is_file(), f"principles-rules.md is absent at {RULES}"
    return RULES.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    """Slice out the section body from `heading` up to the next horizontal-rule
    separator (`---` on its own line) — the file's own section delimiter.
    (A plain next-'## '-heading search would stop early: fenced-example
    blocks inside a section body legitimately embed a nested '## Heading'
    line as sample markdown.)
    """
    start = text.find(heading)
    assert start != -1, f"heading {heading!r} not found"
    rest = text[start + len(heading):]
    nxt = re.search(r"(?m)^---\s*$", rest)
    return rest[: nxt.start()] if nxt else rest


# --- existing content untouched (surgical-edit sanity check) ---------------

def test_existing_required_sections_still_present():
    text = _text()
    for heading in ("## North Star", "## Product Principles", "## Design Principles"):
        assert heading in text, f"existing heading {heading!r} must survive"


def test_existing_validator_contract_rules_1_through_5_still_present():
    text = _text()
    contract = _section(text, "## Validator contract (summary)")
    # rule 2's distinctive "3-7" language and rule 4's legacy-heading language
    # must both survive untouched.
    assert "3–7" in contract or "3-7" in contract, contract
    assert "legacy" in contract.lower(), contract


# --- ## Anchors --------------------------------------------------------------

def test_anchors_heading_exists():
    assert "## Anchors" in _text()


def test_anchors_is_optional():
    text = _text()
    section = _section(text, "## Anchors")
    assert "optional" in section.lower(), \
        "## Anchors must be documented as optional"


def test_anchors_is_a_table_of_canon_plus_version():
    text = _text()
    section = _section(text, "## Anchors")
    low = section.lower()
    assert "table" in low, "## Anchors must be documented as a table"
    assert "canon" in low, "## Anchors row must name the canon"
    assert "version" in low, \
        "## Anchors row must require a pinned version/edition"


def test_anchors_format_block_has_table_header_row():
    text = _text()
    section = _section(text, "## Anchors")
    # A markdown table header row naming both columns.
    assert re.search(r"\|\s*Canon\s*\|", section), \
        "## Anchors format block must show a 'Canon' table column"
    assert re.search(r"pinned version", section, re.IGNORECASE), \
        "## Anchors format block must show a 'pinned version/edition' column"


def test_anchors_present_but_empty_is_invalid():
    text = _text()
    section = _section(text, "## Anchors")
    assert "present-but-empty" in section.lower() or \
        ("present" in section.lower() and "empty" in section.lower()), \
        "## Anchors must forbid a present-but-empty table"


# --- ## Deviation Ledger ------------------------------------------------------

def test_deviation_ledger_heading_exists():
    assert "## Deviation Ledger" in _text()


def test_deviation_ledger_is_optional():
    text = _text()
    section = _section(text, "## Deviation Ledger")
    assert "optional" in section.lower(), \
        "## Deviation Ledger must be documented as optional"


def test_deviation_ledger_entries_bind_deviation_reason_and_principle():
    text = _text()
    section = _section(text, "## Deviation Ledger")
    assert f"{EM} reason:" in section, \
        "## Deviation Ledger entries must carry the literal '— reason:' marker"
    assert f"{EM} principle:" in section, \
        "## Deviation Ledger entries must carry the literal '— principle:' marker"


def test_deviation_ledger_format_block_is_ordered_list():
    text = _text()
    section = _section(text, "## Deviation Ledger")
    assert re.search(r"(?m)^1\.\s", section), \
        "## Deviation Ledger format block must show a numbered ('1.') entry"


def test_deviation_ledger_present_but_empty_is_invalid():
    text = _text()
    section = _section(text, "## Deviation Ledger")
    assert "present-but-empty" in section.lower() or \
        ("present" in section.lower() and "empty" in section.lower()), \
        "## Deviation Ledger must forbid a present-but-empty section"


# --- Validator contract summary rows for both new sections -------------------

def test_validator_contract_documents_anchors_rule():
    text = _text()
    contract = _section(text, "## Validator contract (summary)")
    assert "## Anchors" in contract, \
        "Validator contract must document a rule for '## Anchors'"
    low = contract.lower()
    assert "optional" in low, \
        "Validator contract's Anchors rule must state it is optional"


def test_validator_contract_documents_deviation_ledger_rule():
    text = _text()
    contract = _section(text, "## Validator contract (summary)")
    assert "## Deviation Ledger" in contract, \
        "Validator contract must document a rule for '## Deviation Ledger'"
    low = contract.lower()
    assert "optional" in low, \
        "Validator contract's Deviation Ledger rule must state it is optional"


# --- Round-2 fix pins (reviewer findings) -----------------------------------

def test_anchors_section_has_valid_invalid_example_pair():
    text = _text()
    section = _section(text, "## Anchors")
    assert "✅" in section and "❌" in section, \
        "## Anchors must show a valid/invalid (✅/❌) example pair, per the " \
        "file's own idiom (see the Design/Engineering ✅/❌ examples)"


def test_deviation_ledger_section_has_valid_invalid_example_pair():
    text = _text()
    section = _section(text, "## Deviation Ledger")
    assert "✅" in section and "❌" in section, \
        "## Deviation Ledger must show a valid/invalid (✅/❌) example pair"


def test_validator_contract_anchors_rule_pins_detection_regex():
    text = _text()
    contract = _section(text, "## Validator contract (summary)")
    assert "separator row" in contract.lower(), \
        "Anchors rule must name the GFM separator row as part of detection, " \
        "the same way sibling rules pin a detection method"
    assert r"^\|[\s:-]+\|" in contract, \
        "Anchors rule must pin the separator-row regex literally, in the " \
        "same exact-regex idiom rule 2 uses for `^\\d+\\.\\s`"


def test_deviation_ledger_states_single_physical_line_rule():
    text = _text()
    section = _section(text, "## Deviation Ledger")
    assert "single physical line" in section.lower(), \
        "## Deviation Ledger must state the single-physical-line rule " \
        "explicitly, mirroring the ## Product Principles wording"
    assert "by name" in section.lower(), \
        "## Deviation Ledger must require the principle be referenced by " \
        "name, not quoted in full"


def test_deviation_ledger_format_block_entry_is_not_soft_wrapped():
    text = _text()
    section = _section(text, "## Deviation Ledger")
    m = re.search(r"(?m)^1\.\s.*$", section)
    assert m, "Deviation Ledger Format block must have a '1.' entry line"
    assert f"{EM} reason:" in m.group(0) and f"{EM} principle:" in m.group(0), \
        "Format block entry must carry both markers on the same physical line"


def test_deviation_ledger_synthetic_example_is_not_soft_wrapped():
    text = _text()
    section = _section(text, "## Deviation Ledger")
    lines = [ln for ln in section.splitlines() if re.match(r"^1\.\s", ln)]
    assert len(lines) >= 2, \
        "expected both a Format-block and a Synthetic-example '1.' entry line"
    for line in lines:
        assert f"{EM} reason:" in line and f"{EM} principle:" in line, \
            f"entry line must carry both markers on one physical line: {line!r}"


def test_deviation_ledger_principle_referenced_by_name_not_quoted_in_full():
    text = _text()
    section = _section(text, "## Deviation Ledger")
    assert "check: count steps" not in section, \
        "Deviation Ledger synthetic example must not quote a principle's " \
        "full '— check:' clause — reference it by short name instead"


def test_deviation_ledger_precedent_claim_is_accurate():
    text = _text()
    section = _section(text, "## Deviation Ledger")
    assert 'record shape used elsewhere for' not in section.lower(), \
        "must not overstate the architecture-doc precedent as an identical " \
        "record shape (that log's format is prose, not this marker shape)"
    # prose paragraphs (unlike ledger entries) may still soft-wrap, so allow
    # whitespace (incl. a newline) between the two words.
    assert re.search(r"extends\s+this\s+file", section.lower()), \
        "must claim only that this extends the file's own '— check:' idiom"

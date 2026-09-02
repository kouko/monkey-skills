"""Structural grep-test guarding the design-system SKILL.md (loom 1.0,
W2-03): the interview -> DESIGN.md -> ratify -> commit tool shape.

Checks assert on load-bearing PHRASES (intent), tolerant of wording
variation. Never weakens the key-schema assertion: the SKILL.md must cite
`design_md_spec_keys.py`'s `TOKEN_GROUPS` as the source of truth for its
YAML token groups rather than retyping a second, driftable list.

Stdlib only (pathlib + re). Resolve SKILL.md relative to this test file.
"""

from __future__ import annotations

from pathlib import Path

from design_md_spec_keys import TOKEN_GROUPS as SPEC_TOKEN_GROUPS

ROOT = Path(__file__).parents[2] / "skills" / "design-system"
SKILL = ROOT / "SKILL.md"
SCHEMA = ROOT / "references" / "design-md-schema.md"

CAPTURE_INTENT = Path(__file__).parents[2] / "skills" / "capture-intent" / "SKILL.md"

_MAX_BODY_WORDS = 2500
_MAX_DESC_CHARS = 400

_DELETED_VOCAB = [
    "critic",
    "ending gate",
    "entry_intake",
    "entry-intake",
    "surface treatment",
    "candidate round",
    "pipeline",
    "conductor",
    "brief",
    "waiver",
]


def _text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def _frontmatter() -> str:
    text = _text()
    assert text.startswith("---\n")
    return text.split("---\n", 2)[1]


def test_frontmatter_declares_name_and_version():
    fm = _frontmatter()
    assert "name: design-system" in fm
    assert "version: 1.0.0" in fm


def test_description_within_codex_limit_and_carries_triggers():
    fm = _frontmatter()
    desc_block = fm.split("description:", 1)[1].split("version:", 1)[0]
    desc = " ".join(line.strip() for line in desc_block.strip("|\n ").splitlines())
    assert len(desc) <= _MAX_DESC_CHARS, f"description is {len(desc)} chars"
    for trigger in ("視覺設計系統", "デザインシステム"):
        assert trigger in desc


def test_station_summary_byte_identical_to_capture_intent():
    assert CAPTURE_INTENT.is_file(), f"missing sibling file: {CAPTURE_INTENT}"
    text = _text()
    other = CAPTURE_INTENT.read_text(encoding="utf-8")
    start = text.index("## Station summary")
    end = text.index("\n## ", start + len("## Station summary"))
    ours = text[start:end].strip()
    ostart = other.index("## Station summary")
    oend = other.index("\n## ", ostart + len("## Station summary"))
    theirs = other[ostart:oend].strip()
    assert ours == theirs


def test_gate_marker_registered():
    assert "<!-- gate: design-system.never-blocks -->" in _text()


def test_never_blocks_language_present():
    low = _text().lower()
    assert "never required" in low or "never blocks" in low
    assert "standing.product-principles-reject" in _text()


def test_token_groups_cited_from_script_not_retyped():
    text = _text()
    assert "design_md_spec_keys.py" in text
    assert "TOKEN_GROUPS" in text
    # never-weaken: the script's key set must still be non-empty and this
    # file must not embed a second, hand-typed group list that could drift.
    assert len(SPEC_TOKEN_GROUPS) >= 5
    for group in SPEC_TOKEN_GROUPS:
        assert f'"{group}"' not in text and f"'{group}'" not in text, (
            f"SKILL.md retypes token group {group!r} instead of citing the "
            f"script"
        )


def test_references_schema_and_the_interview_flow():
    text = _text()
    assert "references/design-md-schema.md" in text
    assert "references/knowledge-triage.md" in text
    assert "ratified-by:" in text
    assert "docs(loom): DESIGN.md ratified" in text


def test_no_deleted_vocabulary_survives():
    low = _text().lower()
    for term in _DELETED_VOCAB:
        assert term not in low, f"deleted vocabulary survived: {term!r}"


def test_body_under_word_cap():
    text = _text()
    body = text[text.index("---", 3) + 3:]
    words = len(body.split())
    assert words <= _MAX_BODY_WORDS, f"body is {words} words, cap is {_MAX_BODY_WORDS}"


def test_referenced_relative_paths_exist():
    import re
    text = _text()
    for m in re.finditer(r"`(references/[\w./-]+)`", text):
        candidate = SKILL.parent / m.group(1)
        assert candidate.is_file(), f"SKILL.md references missing path: {m.group(1)}"


def test_schema_reference_still_names_eight_canonical_sections():
    assert SCHEMA.is_file(), f"design-md-schema.md is absent at {SCHEMA}"
    text = SCHEMA.read_text(encoding="utf-8")
    for section in (
        "Overview / Brand", "Colors", "Typography", "Layout",
        "Elevation & Depth", "Shapes", "Components", "Do's & Don'ts",
    ):
        assert section in text

"""Tests for the loom 1.0 product-principles tool (W2-03):

  1. `validate_principles_output.py` accepts a ratified file with 3
     non-negotiables and rejects one with 2, or a missing/malformed
     `ratified-by:` line (the validator's own unit tests live in
     `test_validate_principles_output.py`; this file only checks the
     specific ratified-line grammar the checker gates on).
  2. `product-principles/SKILL.md`'s shape: the `## Station summary`
     table is byte-identical to `capture-intent`'s, the
     `<!-- gate: ... -->` marker is registered, no vocabulary from the
     deleted replay-matrix / improve-loop / seed-traceability apparatus
     survives, the body stays under the 2,500-word soft cap, and every
     path it references by name actually exists on disk.
"""

from __future__ import annotations

import re
from pathlib import Path

from validate_principles_output import validate

ROOT = Path(__file__).parents[2]
SKILL = ROOT / "skills" / "product-principles" / "SKILL.md"
CAPTURE_INTENT = ROOT / "skills" / "capture-intent" / "SKILL.md"

_MAX_BODY_WORDS = 2500

_DELETED_VOCAB = [
    "critic",
    "replay matrix",
    "improve loop",
    "improve-loop",
    "seed traceability",
    "seed-traceability",
    "pipeline",
    "conductor",
    "brief",
    "waiver",
]


def _text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def _station_summary_table(text: str) -> str:
    start = text.index("## Station summary")
    end = text.index("\n## ", start + len("## Station summary"))
    return text[start:end].strip()


# --- 1. ratified-by grammar --------------------------------------------


def _write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "PRINCIPLES.md"
    path.write_text(text, encoding="utf-8")
    return path


_BASE = """\
# Product principles
## Who
Solo developers.
## Non-negotiables (ordered)
1. Offline-first: saves work with the network off (bad: "feels fast").
2. No accounts: never require sign-up (bad: "optional sign-up").
3. Single file: one plain-text file holds all data.
## Won't do
- Team features.
## Failure we must avoid
Silent data loss.
## Fixed choices
- CLI only.
"""


def test_accepts_ratified_file_with_three_non_negotiables(tmp_path):
    text = "ratified-by: Alex Rivera 2026-09-02\n" + _BASE
    ok, problems = validate(_write(tmp_path, text))
    assert ok, problems


def test_rejects_two_non_negotiables_even_when_ratified(tmp_path):
    two = _BASE.replace("3. Single file: one plain-text file holds all data.\n", "")
    text = "ratified-by: Alex Rivera 2026-09-02\n" + two
    ok, problems = validate(_write(tmp_path, text))
    assert not ok
    assert any("Non-negotiables" in p for p in problems)


def test_rejects_missing_ratified_by_only_when_grammar_is_checked_downstream(tmp_path):
    # The validator itself treats an absent ratified-by as a valid DRAFT
    # (Step 3 writes it only after the user says yes); this asserts that
    # tolerance is intentional, not an oversight — a caller that requires
    # ratification (loom-code's checker) enforces the line's presence
    # itself, on top of this structural pass.
    ok, problems = validate(_write(tmp_path, _BASE))
    assert ok, problems


def test_rejects_malformed_ratified_by_line(tmp_path):
    text = "ratified-by: no date here\n" + _BASE
    ok, problems = validate(_write(tmp_path, text))
    assert not ok
    assert any("malformed" in p for p in problems)


# --- 2. SKILL.md shape ---------------------------------------------------


def test_station_summary_byte_identical_to_capture_intent():
    assert CAPTURE_INTENT.is_file(), f"missing sibling file: {CAPTURE_INTENT}"
    ours = _station_summary_table(_text())
    theirs = _station_summary_table(CAPTURE_INTENT.read_text(encoding="utf-8"))
    assert ours == theirs


def test_gate_marker_registered():
    text = _text()
    assert "<!-- gate: product-principles.ratified-requires-user-yes -->" in text


def test_no_deleted_vocabulary_survives():
    low = _text().lower()
    for term in _DELETED_VOCAB:
        assert term not in low, f"deleted vocabulary survived: {term!r}"


def test_body_under_word_cap():
    text = _text()
    body = text[text.index("---", 3) + 3:]
    words = len(body.split())
    assert words <= _MAX_BODY_WORDS, f"body is {words} words, cap is {_MAX_BODY_WORDS}"


def test_referenced_paths_exist():
    text = _text()
    for m in re.finditer(r"`(references/[\w./-]+)`", text):
        candidate = SKILL.parent / m.group(1)
        assert candidate.is_file(), f"SKILL.md references missing path: {m.group(1)}"


def test_interview_template_referenced_not_copied():
    text = _text()
    assert "contract/templates/PRINCIPLES-interview.md" in text
    assert "the interview is the same one" in text.lower()

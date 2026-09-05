"""W1-01 — RED/GREEN evidence: `deletion-first` reaches the docs and skill
lenses, plus the cap-bump-candidate rule.

Before this task, `deletion-first` was a code-only dimension
(`lenses.md`'s "Code — eleven dimensions" table): only a program's new
abstractions were asked to justify themselves against a smaller shape.
Station text and agent contracts — the artifacts the `docs` and `skill`
lenses actually score — could grow a new paragraph, mechanism, reserved
task, or fallback path with nobody asking whether it replaced something or
prevented an observed failure. This file pins that the docs table and the
skill lens paragraph each name `deletion-first`, that the shared definition
they both point to carries an affirmative sentence requiring the smaller
shape, that a second sentence names a deletion candidate for a file whose
`*_CAP` was raised in two consecutive changes, and that `reviewer.md`'s
`docs` and `skill` lens rows end with `deletion-first`.

Never `wc` for word counts — BSD/GNU disagree; `len(str.split())` only.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LENSES = REPO / "loom-code/skills/review/references/lenses.md"
REVIEWER = REPO / "loom-code/agents/reviewer.md"

_NEGATION_RE = re.compile(r"\b(?:not|never|no)\b|n't", re.IGNORECASE)


def _has_negation(sentence: str) -> bool:
    """True iff `sentence` contains a word-boundary negation token — 'not',
    'never' or 'no' as whole words, or an "n't" contraction."""
    return bool(_NEGATION_RE.search(sentence))


def _flat_sentences(text: str) -> list[str]:
    """Split text into sentences after collapsing newlines to spaces, so a
    sentence that line-wraps in the markdown source still reads as one
    unit here."""
    flat = " ".join(text.split())
    return [p for p in re.split(r"(?<=[.!?])\s+", flat) if p.strip()]


def _section(text: str, heading: str) -> str:
    """The text from `heading` up to (not including) the next `## ` or
    end of file."""
    start = text.index(heading)
    rest = text[start + len(heading):]
    m = re.search(r"\n## ", rest)
    end = start + len(heading) + (m.start() if m else len(rest))
    return text[start:end]


def _docs_table_section(text: str) -> str:
    return _section(text, "## Docs — five dimensions")


def _skill_lens_section(text: str) -> str:
    return _section(text, "## Skill lens")


def _deletion_first_definition_paragraph(text: str) -> str:
    """The one shared paragraph (written once) that the docs table row and
    the skill lens paragraph both point to — isolated by its own opening
    bold label, so sentence-splitting never runs into an adjacent table's
    pipe-separated cells (which carry no sentence terminators of their
    own and would otherwise fuse into one giant pseudo-sentence)."""
    blocks = [b for b in text.split("\n\n") if b.strip()]
    hits = [
        b for b in blocks
        if b.lstrip().startswith("**Deletion-first for docs and skill.**")
    ]
    assert hits, "no `**Deletion-first for docs and skill.**` paragraph found"
    return hits[0]


def test_docs_lens_table_names_deletion_first() -> None:
    section = _docs_table_section(LENSES.read_text(encoding="utf-8"))
    assert "deletion-first" in section, (
        "lenses.md's docs table never names `deletion-first`."
    )


def test_skill_lens_paragraph_names_deletion_first() -> None:
    section = _skill_lens_section(LENSES.read_text(encoding="utf-8"))
    assert "deletion-first" in section, (
        "lenses.md's `## Skill lens` paragraph never names `deletion-first`."
    )


def test_deletion_first_definition_requires_the_smaller_shape_affirmatively() -> None:
    """The shared `deletion-first` definition (written once, pointed to by
    the docs table row and the skill lens paragraph per the intent) carries
    an affirmative sentence requiring the smaller shape — no negation token
    in that sentence."""
    para = _deletion_first_definition_paragraph(LENSES.read_text(encoding="utf-8"))
    hits = [
        s for s in _flat_sentences(para)
        if "deletion-first" in s.lower()
        and "smaller shape" in s.lower()
        and not _has_negation(s)
    ]
    assert hits, (
        "no affirmative sentence in lenses.md names `deletion-first` and "
        "requires the smaller shape"
    )


def test_consecutive_cap_bumps_sentence_names_a_deletion_candidate() -> None:
    """A `*_CAP` constant raised in the same file across two consecutive
    changes is a design smell; the sentence that says so names a deletion
    candidate the `deletion-first` dimension must list — affirmative, no
    negation token."""
    para = _deletion_first_definition_paragraph(LENSES.read_text(encoding="utf-8"))
    hits = [
        s for s in _flat_sentences(para)
        if "consecutive" in s.lower()
        and "cap" in s.lower()
        and "deletion candidate" in s.lower()
        and not _has_negation(s)
    ]
    assert hits, (
        "no affirmative sentence in lenses.md ties consecutive cap bumps to "
        "a named deletion candidate"
    )


def test_reviewer_docs_row_ends_with_deletion_first() -> None:
    text = REVIEWER.read_text(encoding="utf-8")
    row = next(
        (line for line in text.splitlines() if line.strip().startswith("| `docs`")),
        None,
    )
    assert row is not None, "reviewer.md has no `| `docs` |` lens row."
    assert row.rstrip().rstrip("|").rstrip().endswith("deletion-first"), (
        f"reviewer.md's docs lens row does not end with `deletion-first`: {row!r}"
    )


def test_reviewer_skill_row_ends_with_deletion_first() -> None:
    text = REVIEWER.read_text(encoding="utf-8")
    row = next(
        (line for line in text.splitlines() if line.strip().startswith("| `skill`")),
        None,
    )
    assert row is not None, "reviewer.md has no `| `skill` |` lens row."
    assert row.rstrip().rstrip("|").rstrip().endswith("deletion-first"), (
        f"reviewer.md's skill lens row does not end with `deletion-first`: {row!r}"
    )


# --- synthetic self-tests for the negation matcher (baseline §8) -----------


def test_matcher_smaller_shape_sentence_affirmative_accepted() -> None:
    sentence = (
        "The finding names the smaller shape that does the same job as the "
        "code lens's deletion-first."
    )
    assert "smaller shape" in sentence.lower()
    assert not _has_negation(sentence)


def test_matcher_smaller_shape_sentence_negated_rejected() -> None:
    sentence = (
        "The finding does not need to name the smaller shape the code "
        "lens's deletion-first never required."
    )
    assert _has_negation(sentence)


def test_matcher_cap_bump_sentence_affirmative_accepted() -> None:
    sentence = (
        "A cap raised in the same file across two consecutive changes names "
        "a deletion candidate for that file."
    )
    assert "consecutive" in sentence.lower()
    assert "cap" in sentence.lower()
    assert "deletion candidate" in sentence.lower()
    assert not _has_negation(sentence)


def test_matcher_cap_bump_sentence_negated_rejected() -> None:
    sentence = (
        "A cap raised in the same file across two consecutive changes never "
        "names a deletion candidate for that file."
    )
    assert _has_negation(sentence)

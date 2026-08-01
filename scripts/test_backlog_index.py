"""Tests for the loom family backlog store (docs/loom/backlog/).

Task 1 adds only the charter test. Later tasks (2-5, 8, 9) extend this
file with parser/validator/generator/migration tests.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHARTER_PATH = REPO_ROOT / "docs" / "loom" / "backlog" / "README.md"

# Transcribed VERBATIM from the plan's §Pinned frontmatter contract
# (docs/loom/plans/2026-08-01-backlog-one-entry-per-file.md, ## Notes).
CLOSED_STATUS_VOCABULARY = [
    "COMMITTED-NEXT",
    "OPEN",
    "PARKED",
    "UPSTREAM",
    "SHIPPED",
    "CLOSED — SUPERSEDED",
    "archived",
]


def _charter_vocabulary_section() -> str:
    """The charter's §Closed status vocabulary body, nothing else.

    Scoped deliberately: the bare word "archived" also appears ~8 times in
    the charter's ordinary archive-rule prose, so a whole-file substring
    search cannot tell "the enum documents this value" from "the English
    word happens to occur". Section-scoped + backtick-fenced is what makes
    the assertion fail when an enum entry is actually removed.
    """
    text = CHARTER_PATH.read_text(encoding="utf-8")
    _, _, after = text.partition("## Closed status vocabulary")
    assert after, "charter has no '## Closed status vocabulary' section"
    body, _, _ = after.partition("\n## ")
    return body


def test_charter_documents_the_closed_status_vocabulary():
    assert CHARTER_PATH.is_file(), f"charter missing at {CHARTER_PATH}"
    section = _charter_vocabulary_section()
    for status in CLOSED_STATUS_VOCABULARY:
        assert f"- `{status}`" in section, (
            f"charter's vocabulary section does not LIST status {status!r} "
            f"as an enum bullet (prose mentioning it does not count)"
        )

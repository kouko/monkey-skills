"""Structural grep-test guarding the `where:` schema examples in three
files are anchor-primary (not line-number-first).

Files guarded:
- loom-code/skills/requesting-code-review/references/gate-markers-spec.md
- loom-code/skills/requesting-code-review/SKILL.md
- loom-code/skills/requesting-docs-review/SKILL.md

The `where:` citation form must be anchor-primary: a path plus an
anchor (a verbatim string or stable heading), with an optional line
number for precision — `where: <path + anchor; line optional>`.  The
old line-number-first placeholder (`where: <file:line>`) contradicts
the inverted rule and must not survive as the required/illustrative
form.

Stdlib only (pathlib + re).  Resolve references relative to this test
file.
"""

import re
from pathlib import Path

FILES = [
    (
        Path(__file__).parent
        / ".."
        / "skills"
        / "requesting-code-review"
        / "references"
        / "gate-markers-spec.md"
    ).resolve(),
    (
        Path(__file__).parent
        / ".."
        / "skills"
        / "requesting-code-review"
        / "SKILL.md"
    ).resolve(),
    (
        Path(__file__).parent
        / ".."
        / "skills"
        / "requesting-docs-review"
        / "SKILL.md"
    ).resolve(),
]

NEW_FORM = "where: <path + anchor; line optional>"
OLD_PATTERN = re.compile(r"where:\s*<[^>]*file:line")


def _flatten(text: str) -> str:
    """Collapse whitespace runs to single spaces for whitespace-insensitive
    substring matching."""
    return re.sub(r"\s+", " ", text)


def test_schema_examples_are_anchor_primary():
    for path in FILES:
        assert path.is_file(), f"file is absent at {path}"
        text = path.read_text(encoding="utf-8")
        flat = _flatten(text)

        # The new anchor-primary form must be present.
        assert NEW_FORM in flat, (
            f"{path.name} must carry the anchor-primary `where:` form "
            f"`{NEW_FORM}`"
        )

        # The old line-number-first placeholder must not survive in any
        # `where:` schema example line.
        assert OLD_PATTERN.search(text) is None, (
            f"{path.name} still has a line-number-first `where:` placeholder "
            f"using `file:line` — must be replaced with anchor-primary form"
        )
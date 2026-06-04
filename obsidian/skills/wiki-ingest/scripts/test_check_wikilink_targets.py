#!/usr/bin/env python3
# test_check_wikilink_targets.py — tests for check-wikilink-targets.py.
#
# Run from the skill ROOT (sys.path[0] = scripts dir):
#   PYTHONDONTWRITEBYTECODE=1 python -m pytest \
#     obsidian/skills/wiki-ingest/scripts/test_check_wikilink_targets.py
#
# Python >= 3.10, stdlib only.

from __future__ import annotations

import importlib.util
from pathlib import Path

# check-wikilink-targets.py has a hyphenated name (not a valid module
# identifier), so load it by file path rather than `import`.
_MODULE_PATH = Path(__file__).with_name("check-wikilink-targets.py")
_spec = importlib.util.spec_from_file_location("check_wikilink_targets", _MODULE_PATH)
assert _spec and _spec.loader
cwt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cwt)


def test_core_resolution(tmp_path: Path) -> None:
    """Existing / alias / display-stripped links resolve; only Missing is flagged."""
    vault = tmp_path

    # Existing.md with an alias "Alt".
    (vault / "Existing.md").write_text(
        '---\naliases: ["Alt"]\n---\n\nbody\n',
        encoding="utf-8",
    )

    page = vault / "page.md"
    page.write_text(
        "Links: [[Existing]], [[Missing]], [[Existing|disp]], [[Alt]].\n",
        encoding="utf-8",
    )

    unresolved = cwt.find_unresolved_targets(page, vault, exclude_dirs=[])

    assert unresolved == ["Missing"]

    # CORE branch coverage: case-insensitivity + '#heading' suffix strip.
    page2 = vault / "page2.md"
    page2.write_text(
        "Case: [[EXISTING]]. Heading: [[Existing#Sec]].\n",
        encoding="utf-8",
    )
    assert cwt.find_unresolved_targets(page2, vault, exclude_dirs=[]) == []


def test_exemptions(tmp_path: Path) -> None:
    """Same-note headings, `## Source` links, code spans, and path-prefix
    forms are NOT flagged."""
    vault = tmp_path

    (vault / "Existing.md").write_text("body\n", encoding="utf-8")

    page = vault / "page.md"
    page.write_text(
        "\n".join(
            [
                # Same-note heading link (empty base after '#' strip).
                "See [[#八、結論]] above.",
                "",
                # Path-prefixed form resolves on trailing basename.
                "Link: [[sub/Existing]].",
                "",
                # Fenced code block — its wikilink is not a live link.
                "```",
                "[[NotALink]]",
                "```",
                "",
                # Inline code span — also not a live link.
                "Inline `[[AlsoNotALink]]` example.",
                "",
                # `## Source` body link points outside wiki/ — exempt.
                "## Source",
                "[[some-source-basename]]",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    unresolved = cwt.find_unresolved_targets(page, vault, exclude_dirs=[])

    assert unresolved == []

"""Shared line-leading heading-anchor helper for loom-design's structural
pin tests -- this module is the single in-package source, so a fix to the
anchor logic lands once instead of at every site that used to hand-roll
it. Scope note: `scripts/` here is split into per-subdirectory import
roots, so this module serves `pipeline/` only -- `interface/` keeps its
two sites inline rather than take a third copy of four lines. Sibling-module import (no `__init__.py`,
no conftest), following the existing sibling-import pattern already used
in this scripts/pipeline/ directory.
"""
from __future__ import annotations

# Not shared with loom-code/scripts/heading_window.py: the two plugin
# trees are hashed independently as cold-install packages and must not
# import across each other.


def line_leading(text: str, heading: str, start: int = 0) -> int:
    """Index of `heading` where it begins a LINE, or -1.

    A bare substring search binds `"### Foo"` to a prose mention of the same
    words, and `"## Foo"` to an earlier `"### Foo"` — either silently
    retargets the window to the wrong region and the assertions inside it
    keep passing. Only a line start is a heading.
    """
    if start == 0 and text.startswith(heading):
        return 0
    idx = text.find("\n" + heading, max(0, start - 1))
    return -1 if idx == -1 else idx + 1

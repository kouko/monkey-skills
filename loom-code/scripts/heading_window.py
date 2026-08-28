"""Shared line-leading heading-anchor helper for loom-code's structural
pin tests -- three byte-identical copies of `_line_leading` existed across
test files in this package (and a sibling copy in loom-design); this
module is the single in-package source so a fix to the anchor logic
lands once instead of N times. Sibling-module import (no `__init__.py`,
no conftest), following the existing `import distribute` precedent in
this same scripts/ directory.
"""
from __future__ import annotations

# Not shared with loom-design/scripts/pipeline/heading_window.py: the two
# plugin trees are hashed independently as cold-install packages and must
# not import across each other.


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

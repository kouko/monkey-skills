"""Collect living-spec ``@req`` bindings across a source tree.

`collect_bindings(root, patterns)` globs test files under ``root``,
runs `living_spec_tags.locate_bindings` on each, and tags every
returned binding with its file path RELATIVE to ``root`` under the
``"file"`` key — so the downstream git adapter can pass it to
``git -C root log -L <range>:<file>``.

Files are processed in sorted order, so the flat result list is
deterministic. Only files matching ``patterns`` are read; everything
else (including non-test files carrying ``@req``-looking comments) is
ignored. Pure file I/O plus the locator — no git here.

Stdlib only (pathlib).
"""
from __future__ import annotations

from pathlib import Path

from living_spec_tags import locate_bindings


def collect_bindings(
    root: Path,
    patterns: tuple[str, ...] = ("test_*.py", "*_test.py"),
) -> list[dict]:
    """Return all ``@req`` bindings under ``root``, tagged with ``file``.

    Recursively globs every test file matching any of ``patterns``,
    runs `locate_bindings` on its text, and stamps each binding with
    its path relative to ``root`` under ``"file"``. Files are sorted
    (and de-duplicated across overlapping patterns) before processing,
    so the flat list is deterministic. Non-matching files are ignored.
    """
    root = Path(root)
    matched = {
        path
        for pattern in patterns
        for path in root.rglob(pattern)
        if path.is_file()
    }

    bindings: list[dict] = []
    for path in sorted(matched):
        relative = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        for binding in locate_bindings(text):
            binding["file"] = relative
            bindings.append(binding)
    return bindings

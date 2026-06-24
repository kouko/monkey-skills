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

# Directory names that hold vendored / generated code we must not walk
# into — a `git log -L` per test file there is wasted work.
_VENDOR_DIRS = frozenset(
    {"node_modules", "site-packages", "__pycache__", "venv", ".eggs"}
)


def _is_vendored(relative_parts: tuple[str, ...]) -> bool:
    """True if any directory component is a dot-dir or a vendor dir."""
    # The last part is the file name; only directory components count.
    for part in relative_parts[:-1]:
        if part.startswith(".") or part in _VENDOR_DIRS:
            return True
    return False


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
        and not _is_vendored(path.relative_to(root).parts)
    }

    bindings: list[dict] = []
    for path in sorted(matched):
        relative = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        for binding in locate_bindings(text):
            binding["file"] = relative
            bindings.append(binding)
    return bindings


def collect_structural_records(
    root: Path,
    patterns: tuple[str, ...] = ("test_*.py", "*_test.py"),
) -> list[dict]:
    """Return one ``extract_tags``-shaped record per tagged test.

    Regroups `collect_bindings` output — one record per ``@req``
    binding — by ``(file, test)`` into the structural shape that
    `find_structural_violations` and `generate_index` consume::

        [{"test": <name>, "reqs": [...], "invariant_refs": []}]

    Reusing `collect_bindings` means the ANCHORED `locate_bindings`
    path does the parsing, so a ``@req:`` buried in a string literal
    (a test fixture) is NOT a binding and never reaches the index —
    unlike a naive `extract_tags` over the tree, whose non-anchored
    ``.search`` would mistake the fixture string for a real binding.

    ``invariant_refs`` is always ``[]``: the drift lane's locator
    tracks only ``@req``, and the structural-violation + index
    consumers read only ``reqs`` + ``test``. Records preserve
    `collect_bindings`' sorted-by-file order, so the result is
    deterministic.
    """
    records: list[dict] = []
    by_key: dict[tuple[str, str], dict] = {}
    for binding in collect_bindings(root, patterns):
        key = (binding["file"], binding["test"])
        record = by_key.get(key)
        if record is None:
            record = {
                "test": binding["test"],
                "reqs": [],
                "invariant_refs": [],
            }
            by_key[key] = record
            records.append(record)
        record["reqs"].append(binding["req"])
    return records

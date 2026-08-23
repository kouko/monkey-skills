#!/usr/bin/env python3
"""Reject Markdown references that couple one plugin to another's files.

The checker scans Markdown below a single plugin root.  It reports relative
Markdown links whose lexically resolved path leaves that root, and operational
path references to another ``loom-*`` plugin's private ``hooks/``, ``skills/``,
or ``scripts/`` tree.  Plugin-qualified skill names such as
``loom-code:using-loom-code`` are public names and are therefore allowed.

Pure stdlib.  ``find_boundary_violations`` is the hermetic test surface; the
CLI exits non-zero and prints each violation when passed a plugin root.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


_LINK_RE = re.compile(r"\]\((?P<target>[^)]+)\)")
_REFERENCE_LINK_RE = re.compile(
    r"^\s{0,3}\[[^]]+\]:\s*(?P<target><[^>]+>|\S+)"
)
_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
_SIBLING_INTERNAL_RE = re.compile(
    r"(?<![A-Za-z0-9_./:-])"
    r"(?P<target>(?:(?:/|(?:\.{1,2}|[A-Za-z0-9_.-]+)/))*"
    r"(?P<plugin>loom-[a-z0-9-]+)"
    r"/(?:hooks|skills|scripts)/[A-Za-z0-9_./-]+)"
)


def _is_archival_markdown(root: Path, markdown: Path) -> bool:
    """Return whether a Markdown file records history, not install behavior."""
    relative = markdown.relative_to(root)
    return (
        (len(relative.parts) == 1 and markdown.name.startswith("CHANGELOG"))
        or (len(relative.parts) == 1 and markdown.name == "TECH-SPEC.md")
        or relative.parts[0] == "research"
    )


def _link_path(raw_target: str) -> str | None:
    """Return the filesystem portion of a relative Markdown link."""
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    else:
        # This checker follows the repository's title-less-link convention,
        # while tolerating a conventional quoted title if one appears.
        target = re.split(r'\s+["\']', target, maxsplit=1)[0]
    if not target or target.startswith(("#", "/", "//")):
        return None
    if _SCHEME_RE.match(target):
        return None
    return target.split("#", 1)[0].split("?", 1)[0]


def _escapes(root: Path, source: Path, target: str) -> bool:
    resolved = (source.parent / target).resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError:
        return True
    return False


def _plugin_name(root: Path) -> str:
    """Read installed identity from the Claude manifest, else use dirname."""
    manifest = root / ".claude-plugin" / "plugin.json"
    if manifest.is_file():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        name = data.get("name")
        if isinstance(name, str) and name:
            return name
    return root.name


def find_boundary_violations(plugin_root: str | Path) -> list[str]:
    """Return stable ``file:line: reason: target`` boundary violations."""
    root = Path(plugin_root).resolve(strict=True)
    plugin_name = _plugin_name(root)
    violations: list[str] = []

    for markdown in sorted(root.rglob("*.md")):
        if _is_archival_markdown(root, markdown):
            continue
        for line_number, line in enumerate(
            markdown.read_text(encoding="utf-8").splitlines(), start=1
        ):
            reported_link_spans: list[tuple[int, int]] = []
            link_matches = list(_LINK_RE.finditer(line))
            reference_match = _REFERENCE_LINK_RE.match(line)
            if reference_match:
                link_matches.append(reference_match)
            for match in sorted(link_matches, key=lambda item: item.start("target")):
                target = _link_path(match.group("target"))
                if target and _escapes(root, markdown, target):
                    reported_link_spans.append(match.span("target"))
                    violations.append(
                        f"{markdown}:{line_number}: escaping relative link: {target}"
                    )

            for match in _SIBLING_INTERNAL_RE.finditer(line):
                if match.group("plugin") == plugin_name:
                    continue
                start, end = match.span("target")
                if any(
                    start >= link_start and end <= link_end
                    for link_start, link_end in reported_link_spans
                ):
                    continue
                violations.append(
                    f"{markdown}:{line_number}: sibling internal path: "
                    f"{match.group('target')}"
                )

    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plugin_root", type=Path)
    args = parser.parse_args(argv)
    violations = find_boundary_violations(args.plugin_root)
    if violations:
        for violation in violations:
            print(violation, file=sys.stderr)
        print(f"FAIL: {len(violations)} plugin-boundary violation(s).", file=sys.stderr)
        return 1
    print(f"OK: {args.plugin_root} is filesystem-boundary clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

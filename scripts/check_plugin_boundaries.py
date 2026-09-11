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


def _is_internal_path(root: Path, plugin: str, target: str) -> bool:
    """Whether a ``loom-*``-shaped match names this plugin's OWN skill folder
    rather than a sibling plugin's private tree.

    A plugin may ship a skill whose directory name happens to look like a
    sibling plugin — ``loom-workflow/skills/loom-memory/`` is the case this
    exists for. Only that shape is exempt: the target must resolve to a real
    path under this plugin's ``skills/<plugin>/``.

    An earlier version exempted anything that merely resolved to an existing
    path under the plugin root, which let a decoy defeat the gate: a file
    planted at ``<root>/loom-code/scripts/loom_checker.py`` made a genuine
    reference to the real sibling's private script read as internal. Requiring
    the ``skills/<plugin>/`` prefix, and refusing the exemption outright when a
    real sibling plugin of that name exists, closes that.
    """
    if _sibling_plugin_exists(root, plugin):
        return False
    candidate = target[1:] if target.startswith("/") else target
    resolved = (root / candidate).resolve(strict=False)
    own_skill = (root / "skills" / plugin).resolve(strict=False)
    try:
        resolved.relative_to(own_skill)
    except ValueError:
        return False
    return resolved.exists()


def _sibling_plugin_exists(root: Path, plugin: str) -> bool:
    """True when ``plugin`` is a real installable plugin beside this one.

    Checks both the flat install shape (``<plugin>/.claude-plugin/
    plugin.json``) and the versioned-install shape this repo's own suite
    proves is real (``<plugin>/<version>/.claude-plugin/plugin.json``), and
    checks both from ``root``'s own parent (when ``root`` itself is flat)
    and from ``root``'s grandparent (when ``root`` itself is a version
    directory, e.g. ``.../loom-design/0.4.0``, so the sibling's install
    root sits beside ``loom-design``, not beside ``0.4.0``).

    An earlier version checked only the flat shape from ``root``'s parent,
    so a sibling installed under a version directory went undetected — the
    bare ``root/skills/<plugin>/`` existence check in ``_is_internal_path``
    then let a same-named decoy through exactly as before the flat-layout
    fix.
    """
    resolved_root = root.resolve(strict=False)
    bases = {resolved_root.parent, resolved_root.parent.parent}
    for base in bases:
        sibling_base = base / plugin
        if (sibling_base / ".claude-plugin" / "plugin.json").is_file():
            return True
        if sibling_base.is_dir():
            for child in sibling_base.iterdir():
                if child.is_dir() and (child / ".claude-plugin" / "plugin.json").is_file():
                    return True
    return False


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
                if _is_internal_path(root, match.group("plugin"), match.group("target")):
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

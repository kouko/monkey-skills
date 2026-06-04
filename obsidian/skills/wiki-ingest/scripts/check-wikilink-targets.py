#!/usr/bin/env python3
# check-wikilink-targets.py — Flag [[wikilinks]] whose target does NOT
# resolve against the vault note inventory (part of wiki-ingest).
#
# Purpose:
#   Authoring-time gate. Given a just-written markdown page, return the
#   [[Target]] links whose Target is NOT an existing note (by bare
#   basename, case-insensitive) and NOT a frontmatter alias of any note.
#   Shares L07's inventory concept (lint-checks.md:58-66) but diverges
#   intentionally (not a bug): it rglob's the whole passed <vault-root>
#   rather than L07's fixed wiki/{...}/ subdir list, and it RESOLVES
#   path-prefixed [[dir/Name]] on the trailing basename, whereas L07
#   routes those to L04 as violations.
#
# Usage (CLI):
#   python check-wikilink-targets.py <page.md> <vault-root> [exclude-dir ...]
#     → prints one unresolved Target per line; exit 1 if any, 0 if none.
#
# Usage (importable):
#   find_unresolved_targets(page_path, vault_root, exclude_dirs) -> list[str]
#
# Resolution rules (CORE — Task 1):
#   - Inventory = every *.md basename minus '.md' (case-insensitive)
#     PLUS each note's frontmatter `aliases` entries.
#   - For each [[Target]]: strip a trailing '|display' and a
#     '#heading' / '#^block' suffix to get the base, then match the
#     base (case-insensitive) against the inventory.
#   - [[Existing]] / [[Existing|disp]] / [[Alt]] (alias) → resolved.
#   - [[Missing]] → flagged (returned).
#
# Exemptions (Task 2): same-note `[[#…]]`-only links (empty base),
#   wikilinks inside the `## Source` section, wikilinks inside fenced
#   ``` ``` ``` / inline `` ` `` code spans (not live links — same
#   backtick-gate reasoning as wiki-ingest), and `dir/Name` path-prefix
#   forms (resolve on the trailing basename). _strip_exempt_regions
#   blanks the non-live regions before _extract_wikilinks scans;
#   _link_base normalizes display / heading / path-prefix to the base.
#
# Python >= 3.10, stdlib only.

from __future__ import annotations

import sys
from pathlib import Path

import re

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# A wikilink: [[...]] capturing the inner text (no nested brackets).
_WIKILINK_RE = re.compile(r"\[\[([^\[\]]+?)\]\]")

# Frontmatter block at the very top of a file: --- ... ---
_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---", re.DOTALL)

# Fenced code block: a ``` (or ~~~) line through its closing fence, or EOF.
_FENCE_RE = re.compile(r"^([ \t]*)(`{3,}|~{3,}).*?(?:\n\1\2[ \t]*$|\Z)", re.DOTALL | re.MULTILINE)

# Inline code span: one or more backticks, shortest balanced run.
_INLINE_CODE_RE = re.compile(r"(`+)(?:(?!\1).)*?\1", re.DOTALL)

# A markdown heading line (level 2+) marking a section boundary.
_HEADING_RE = re.compile(r"^#{1,6}[ \t]", re.MULTILINE)

# The `## Source` heading specifically (exact level-2, case-insensitive).
_SOURCE_HEADING_RE = re.compile(r"^##[ \t]+Source[ \t]*$", re.IGNORECASE | re.MULTILINE)


# ---------------------------------------------------------------------------
# Frontmatter alias parsing (minimal — no third-party YAML)
# ---------------------------------------------------------------------------

def _frontmatter_block(text: str) -> str | None:
    """Return the raw frontmatter block (between the leading --- fences)."""
    m = _FRONTMATTER_RE.match(text)
    return m.group(1) if m else None


def _parse_aliases(block: str) -> list[str]:
    """Return alias values from a frontmatter block.

    Handles both inline and block list forms:
        aliases: [a, b, c]
        aliases:
          - a
          - b

    Minimal lossy-by-design parser (no third-party YAML): inline form
    cannot contain a literal ']' in a value, and block form stops at the
    first non '- ' line. This is intentional — vault aliases are short
    basenames, not arbitrary YAML — not a bug to "fix" by adding cases.
    """
    aliases: list[str] = []

    # Inline form: aliases: [val1, val2, ...]
    inline_re = re.compile(r"^aliases\s*:\s*\[([^\]]*)\]", re.MULTILINE)
    m = inline_re.search(block)
    if m:
        for v in m.group(1).split(","):
            v = v.strip().strip('"').strip("'")
            if v:
                aliases.append(v)
        return aliases

    # Block form: aliases:\n  - val
    block_re = re.compile(
        r"^aliases\s*:\s*\n((?:[ \t]*-[ \t]*\S[^\n]*\n?)+)",
        re.MULTILINE,
    )
    m = block_re.search(block)
    if m:
        for line in m.group(1).splitlines():
            v = line.strip().lstrip("-").strip().strip('"').strip("'")
            if v:
                aliases.append(v)
    return aliases


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------

def build_inventory(
    vault_root: Path,
    exclude_dirs: list[str] | None = None,
) -> set[str]:
    """Return the case-folded set of resolvable wikilink targets in the vault.

    Each *.md file contributes its basename (minus '.md') plus every
    frontmatter `aliases` entry. Directories named in `exclude_dirs`
    (matched by path component) are skipped.
    """
    exclude = set(exclude_dirs or [])
    inventory: set[str] = set()

    for md in vault_root.rglob("*.md"):
        if exclude and any(part in exclude for part in md.relative_to(vault_root).parts):
            continue

        inventory.add(md.stem.casefold())

        try:
            text = md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        block = _frontmatter_block(text)
        if block:
            for alias in _parse_aliases(block):
                inventory.add(alias.casefold())

    return inventory


# ---------------------------------------------------------------------------
# Link extraction + base normalization
# ---------------------------------------------------------------------------

def _blank_match(m: re.Match[str]) -> str:
    """Replace a matched region with newline-preserving blanks.

    Keeps the text length and line structure stable so later regex
    anchors (`## Source`, headings) still see the right line geometry,
    while removing any `[[...]]` inside the region from the scan.
    """
    return re.sub(r"[^\n]", " ", m.group(0))


def _strip_exempt_regions(text: str) -> str:
    """Blank out regions whose wikilinks are NOT live links (Task 2).

    Exempt regions:
      - fenced code blocks (``` / ~~~) — render as code, not links;
      - inline code spans (`` `...` ``) — same backtick-gate reasoning
        as wiki-ingest's grep-gate (backtick-wrapped == inline code);
      - the `## Source` body section of a reference page — its wikilink
        points outside wiki/ and resolves via L14, not this inventory
        (lint-checks.md L07 exemption).

    Returns text with those regions replaced by spaces (length-preserved),
    so the surviving `[[...]]` are exactly the live links to resolve.
    """
    # Fences first (an inline-code regex must not see inside a fence).
    text = _FENCE_RE.sub(_blank_match, text)
    text = _INLINE_CODE_RE.sub(_blank_match, text)

    # `## Source` body: from the heading line to the next heading or EOF.
    m = _SOURCE_HEADING_RE.search(text)
    if m:
        nxt = _HEADING_RE.search(text, m.end())
        end = nxt.start() if nxt else len(text)
        section = text[m.start():end]
        text = text[:m.start()] + _blank_match_str(section) + text[end:]

    return text


def _blank_match_str(s: str) -> str:
    """Newline-preserving blanking of a raw substring."""
    return re.sub(r"[^\n]", " ", s)


def _extract_wikilinks(text: str) -> list[str]:
    """Return the raw inner text of every live [[...]] in document order.

    Exempt regions (code spans / fences / `## Source`) are blanked out
    first so their wikilinks never enter the scan.
    """
    return _WIKILINK_RE.findall(_strip_exempt_regions(text))


def _link_base(inner: str) -> str:
    """Reduce a wikilink's inner text to its match base.

    Strips a trailing '|display' alias, a '#heading' / '#^block' suffix,
    and a leading 'dir/' path prefix (Obsidian resolves path-prefixed
    forms on the trailing basename). e.g. 'Existing|disp' -> 'Existing',
    'Note#Sec' -> 'Note', 'sub/Existing' -> 'Existing'.
    A same-note '#'-only link ('#Heading') reduces to '' (empty base),
    which find_unresolved_targets treats as an exemption.
    """
    base = inner.split("|", 1)[0]
    base = base.split("#", 1)[0]
    base = base.rsplit("/", 1)[-1]
    return base.strip()


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------

def find_unresolved_targets(
    page_path: Path,
    vault_root: Path,
    exclude_dirs: list[str] | None = None,
) -> list[str]:
    """Return the [[Target]] bases in `page_path` that don't resolve.

    A target resolves if its case-folded base is in the vault inventory
    (note basenames + frontmatter aliases). Returns unresolved bases in
    document order, de-duplicated (first occurrence wins).
    """
    inventory = build_inventory(vault_root, exclude_dirs)

    text = page_path.read_text(encoding="utf-8", errors="replace")

    unresolved: list[str] = []
    seen: set[str] = set()
    for inner in _extract_wikilinks(text):
        base = _link_base(inner)
        if not base:
            # '#'-only same-note link — no target to resolve.
            continue
        folded = base.casefold()
        if folded in inventory:
            continue
        # De-dup case-consistently with resolution: a page linking both
        # [[Missing]] and [[missing]] reports the target only once.
        if folded in seen:
            continue
        seen.add(folded)
        unresolved.append(base)

    return unresolved


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(
            "usage: check-wikilink-targets.py <page.md> <vault-root> "
            "[exclude-dir ...]",
            file=sys.stderr,
        )
        return 2

    page_path = Path(argv[1])
    vault_root = Path(argv[2])
    exclude_dirs = list(argv[3:])

    # Bad-input guard: a non-existent page is a usage error (exit 2), kept
    # distinct from the gate-trip exit 1 so a typo'd path can't masquerade
    # as "unresolved links found".
    if not page_path.is_file():
        print(
            f"error: page not found: {page_path}",
            file=sys.stderr,
        )
        return 2

    unresolved = find_unresolved_targets(page_path, vault_root, exclude_dirs)
    for target in unresolved:
        print(target)

    return 1 if unresolved else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

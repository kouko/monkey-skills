#!/usr/bin/env python3
"""Build the ja-JP <-> zh-TW pair glossary from manual seed + EN-pivot derivation.

Sources:
  scripts/canonical/manual-entries-ja-JP--zh-TW.md  — hand-curated false-friend
                                                       seed grouped by domain.
  scripts/canonical/glossary-en-US--ja-JP.md         — EN→ja pivot table.
  scripts/canonical/glossary-en-US--zh-TW.md         — EN→zh-TW pivot table.

Algorithm:
  1. Parse the manual seed into domain → list[entry].
  2. Parse both EN-pivot files into (en_term, domain) → target_term maps.
  3. For every (en_term, domain) present in BOTH EN-pivot maps, derive an entry
     {ja-JP, zh-TW, source: "derived", notes: "en-pivot: <term>"}.
     (en-term citation lives in `notes` — not `source` — so the frontmatter
     `sources:` YAML stays a small label set rather than blowing up to one
     entry per pivot term.)
  4. Merge per-domain: manual entries first, then derived. Deduplicate on
     (ja-JP, zh-TW) tuple — manual entries win on conflict.
  5. Emit via build-pairs-from-en.py::emit_pair_file.

Output: scripts/canonical/glossary-ja-JP--zh-TW.md (BCP-47 alphabetical:
ja-JP < zh-TW), 4-column table per domain (ja-JP | zh-TW | source | notes).

Note: build-pairs-from-en.py has hyphens in its filename, so it is loaded
via importlib.util.spec_from_file_location rather than `import`.
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANUAL_MD = ROOT / "scripts" / "canonical" / "manual-entries-ja-JP--zh-TW.md"
DEFAULT_EN_JA_MD = ROOT / "scripts" / "canonical" / "glossary-en-US--ja-JP.md"
DEFAULT_EN_ZH_MD = ROOT / "scripts" / "canonical" / "glossary-en-US--zh-TW.md"
DEFAULT_OUT = ROOT / "scripts" / "canonical"

PAIR = ("ja-JP", "zh-TW")  # BCP-47 alphabetical order
OUT_FILENAME = f"glossary-{PAIR[0]}--{PAIR[1]}.md"

# Domain section header: "## domain: <name>"
_DOMAIN_HDR = re.compile(r"^##\s+domain:\s+(\S+)\s*$")
# Table separator row: "|---|---|---|---|" (any pipe-only-with-dashes line)
_SEP_ROW = re.compile(r"^\|\s*[-:|\s]+\|\s*$")


def _load_build_pairs_module():
    """Load build-pairs-from-en.py as a module despite hyphens in filename."""
    src_path = Path(__file__).resolve().parent / "build-pairs-from-en.py"
    spec = importlib.util.spec_from_file_location("build_pairs_from_en", src_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load module from {src_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _split_table_row(line: str) -> list[str] | None:
    """Split a markdown table row into trimmed cells; return None if not a row.

    A row looks like: ``| a | b | c | d |`` (leading + trailing pipe).
    Returns the inner cells (no leading/trailing empty from outer pipes).
    """
    line = line.rstrip("\n")
    if not line.startswith("|") or not line.endswith("|"):
        return None
    if _SEP_ROW.match(line):
        return None
    # Strip the outer pipes once, then split on internal pipes.
    inner = line[1:-1]
    return [c.strip() for c in inner.split("|")]


def parse_pair_md(md_path: Path,
                  lang_a: str,
                  lang_b: str) -> dict[str, list[dict]]:
    """Parse a glossary-{lang_a}--{lang_b}.md file into domain → list[entry].

    Each entry is a dict with keys {lang_a, lang_b, source, notes}. The header
    row that names the columns is detected and used to drive cell extraction;
    we tolerate extra columns by indexing on header names. The separator row
    is skipped. Anything outside ``## domain:`` blocks is ignored (frontmatter
    + meta section).
    """
    entries_by_domain: dict[str, list[dict]] = defaultdict(list)
    if not md_path.exists():
        return entries_by_domain

    current_domain: str | None = None
    header_cells: list[str] | None = None

    for raw in md_path.read_text(encoding="utf-8").splitlines():
        m = _DOMAIN_HDR.match(raw)
        if m:
            current_domain = m.group(1)
            header_cells = None
            continue
        if current_domain is None:
            continue
        # The `|---|---|...|` separator row is part of the table; skip it
        # without resetting state. Other non-table lines DO end the table.
        if _SEP_ROW.match(raw):
            continue
        cells = _split_table_row(raw)
        if cells is None:
            # Tables MUST be separated from prose / subsection headings by
            # treating ANY non-table line as table-end inside a domain block.
            # Otherwise an intervening `### subsection` or `> note` (without
            # a blank-line separator) would let `header_cells` carry over,
            # and the NEXT table's header row would be parsed as a data row
            # and silently dropped by the empty-cell guard below.
            if current_domain is not None:
                header_cells = None
            continue
        if header_cells is None:
            # First row inside the domain block is the header naming columns.
            header_cells = cells
            continue
        # Map cells to header positions; tolerate row length drift defensively.
        row = dict(zip(header_cells, cells))
        a = row.get(lang_a, "").strip()
        b = row.get(lang_b, "").strip()
        if not a or not b:
            continue
        entries_by_domain[current_domain].append({
            lang_a: a,
            lang_b: b,
            "source": row.get("source", "").strip() or "—",
            "notes": row.get("notes", "").strip() or "—",
        })

    return entries_by_domain


def derive_from_en_pivot(en_ja: dict[str, list[dict]],
                         en_zh: dict[str, list[dict]]
                         ) -> dict[str, list[dict]]:
    """Intersect EN→ja and EN→zh-TW maps to derive ja-JP ↔ zh-TW entries.

    For each (en_term, domain) present in BOTH maps, emit
    {ja-JP, zh-TW, source: "derived", notes: "en-pivot: <en_term>"}.

    The en-term citation lives in ``notes`` (not ``source``) so the frontmatter
    ``sources:`` list stays a small set of literal labels rather than blowing
    up to one entry per pivot term.

    If a domain has duplicate (en_term) rows on either side, the first
    occurrence is used (keeps emit-side dedup deterministic and keeps the
    citation note short).
    """
    # Reshape each side into {(domain, en_term): target_term} for direct lookup.
    ja_by_key: dict[tuple[str, str], str] = {}
    for domain, rows in en_ja.items():
        for e in rows:
            en = e.get("en-US", "").strip()
            ja = e.get("ja-JP", "").strip()
            if not en or not ja:
                continue
            ja_by_key.setdefault((domain, en), ja)

    derived: dict[str, list[dict]] = defaultdict(list)
    for domain, rows in en_zh.items():
        for e in rows:
            en = e.get("en-US", "").strip()
            zh = e.get("zh-TW", "").strip()
            if not en or not zh:
                continue
            ja = ja_by_key.get((domain, en))
            if not ja:
                continue
            derived[domain].append({
                "ja-JP": ja,
                "zh-TW": zh,
                "source": "derived",
                "notes": f"en-pivot: {en}",
            })
    return derived


def merge_manual_and_derived(manual: dict[str, list[dict]],
                             derived: dict[str, list[dict]]
                             ) -> dict[str, list[dict]]:
    """Merge per-domain. Manual first (priority); derived second; dedupe on (ja, zh).

    Dedup is GLOBAL across domains: if a (ja-JP, zh-TW) pair appears in any
    manual domain, it suppresses the same pair from any derived domain. This
    keeps a glossary lookup from returning two rows for the same term just
    because the domain inference disagreed (e.g. manual placed ログイン in
    tech.software while EN-pivot placed Login in ui).
    """
    merged: dict[str, list[dict]] = defaultdict(list)
    seen: set[tuple[str, str]] = set()
    # Manual first across all its domains (priority).
    for domain, rows in manual.items():
        for e in rows:
            key = (e.get("ja-JP", ""), e.get("zh-TW", ""))
            if key in seen:
                continue
            seen.add(key)
            merged[domain].append(e)
    # Then derived; suppressed by any (ja, zh) already taken by manual.
    for domain, rows in derived.items():
        for e in rows:
            key = (e.get("ja-JP", ""), e.get("zh-TW", ""))
            if key in seen:
                continue
            seen.add(key)
            merged[domain].append(e)
    return merged


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build glossary-ja-JP--zh-TW.md from manual seed + EN-pivot intersection.",
    )
    parser.add_argument("--manual-md", default=None,
                        help=f"Override manual seed markdown path "
                             f"(default: {DEFAULT_MANUAL_MD}).")
    parser.add_argument("--en-ja-md", default=None,
                        help=f"Override EN→ja pivot path "
                             f"(default: {DEFAULT_EN_JA_MD}).")
    parser.add_argument("--en-zh-md", default=None,
                        help=f"Override EN→zh-TW pivot path "
                             f"(default: {DEFAULT_EN_ZH_MD}).")
    parser.add_argument("--out-dir", default=None,
                        help=f"Override output directory "
                             f"(default: {DEFAULT_OUT}).")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    bp = _load_build_pairs_module()

    manual_md = Path(args.manual_md) if args.manual_md else DEFAULT_MANUAL_MD
    en_ja_md = Path(args.en_ja_md) if args.en_ja_md else DEFAULT_EN_JA_MD
    en_zh_md = Path(args.en_zh_md) if args.en_zh_md else DEFAULT_EN_ZH_MD
    out_dir = Path(args.out_dir) if args.out_dir else DEFAULT_OUT
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / OUT_FILENAME

    if not manual_md.exists():
        print(f"WARN: manual seed not found at {manual_md}; "
              f"proceeding with derived-only entries.", file=sys.stderr)
    manual = parse_pair_md(manual_md, "ja-JP", "zh-TW")
    en_ja = parse_pair_md(en_ja_md, "en-US", "ja-JP")
    en_zh = parse_pair_md(en_zh_md, "en-US", "zh-TW")

    if not en_ja:
        print(f"WARN: EN→ja pivot empty / missing at {en_ja_md}", file=sys.stderr)
    if not en_zh:
        print(f"WARN: EN→zh-TW pivot empty / missing at {en_zh_md}", file=sys.stderr)

    derived = derive_from_en_pivot(en_ja, en_zh)
    merged = merge_manual_and_derived(manual, derived)

    if not merged:
        print(f"WARN: no entries collected; emitting empty glossary file.",
              file=sys.stderr)

    bp.emit_pair_file(
        pair=PAIR,
        entries_by_domain=dict(merged),
        out_path=out_path,
        generator_note="Generated by scripts/build-pair-ja-JP--zh-TW.py — do not hand-edit.",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

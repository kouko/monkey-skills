#!/usr/bin/env python3
"""Build typography summaries (jlreq + clreq) from W3C source extracts.

Sources:
  vendor/w3c/jlreq-source.md  — manually extracted W3C jlreq subset
  vendor/w3c/clreq-source.md  — manually extracted W3C clreq subset

Output (canonical SSOT):
  scripts/canonical/jlreq-summary.md
  scripts/canonical/clreq-summary.md

Each summary has frontmatter (source / version / last_synced) and a
compact prose body covering the rules the LLM needs at translation time:

  jlreq: 句末「。」、列舉「、」、半角英数字 spacing、kinsoku 禁則、
         parenthesis pairs、ruby placement basics
  clreq: 標點符號 zh-CN vs zh-TW differences (curly Western vs corner
         brackets), 行首行末 rules, 書名號 differences, dates / numerals.

Build pipeline:
  1. Read the corresponding vendor/w3c/<spec>-source.md.
  2. Slice down to the LLM-relevant prose (drop reference appendices that
     are useful in vendor/ for traceability but bloat the prompt).
  3. Prepend frontmatter and the canonical preamble.
  4. Write to scripts/canonical/<spec>-summary.md.

The slicing is intentionally light — the source files are already
pre-curated. This script's job is to (a) attach machine-readable
frontmatter, (b) attach a standardized preamble pointing to the W3C
canonical URL, and (c) trim the trailing "References" section the
vendor source carries.

Usage:
  python3 scripts/build-typography-summaries.py
  python3 scripts/build-typography-summaries.py --spec jlreq
  python3 scripts/build-typography-summaries.py --spec clreq
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
VENDOR = ROOT / "vendor" / "w3c"
CANONICAL = ROOT / "scripts" / "canonical"

VERSION = "0.1.0"
LAST_SYNCED = "2026-05-06"

SPECS = {
    "jlreq": {
        "source": VENDOR / "jlreq-source.md",
        "out": CANONICAL / "jlreq-summary.md",
        "frontmatter_source": "w3c/jlreq",
        "title": "jlreq summary — Japanese typography rules for translation",
        "scope_pair": "ja-JP",
        "url": "https://www.w3.org/TR/jlreq/",
        "preamble": (
            "This summary distills the W3C jlreq rules a translator / "
            "LLM must respect when producing Japanese (ja-JP) output. "
            "It covers punctuation choice (`。`、`、`、quotation), "
            "half-width/full-width spacing (和欧文間隔), kinsoku "
            "(禁則 line-break exclusion), parenthesis pairs, and ruby "
            "(振り仮名) basics. Refer to the canonical W3C spec for "
            "implementation-level layout details."
        ),
    },
    "clreq": {
        "source": VENDOR / "clreq-source.md",
        "out": CANONICAL / "clreq-summary.md",
        "frontmatter_source": "w3c/clreq",
        "title": "clreq summary — Chinese typography rules for translation",
        "scope_pair": "zh-CN, zh-TW (zh-HK noted)",
        "url": "https://www.w3.org/TR/clreq/",
        "preamble": (
            "This summary distills the W3C clreq rules a translator / "
            "LLM must respect when producing Chinese (zh-CN / zh-TW / "
            "zh-HK) output. The single largest variant difference is "
            "QUOTATION MARKS — zh-CN uses curly Western quotes "
            "(`“ ” / ‘ ’`), zh-TW / zh-HK use corner brackets "
            "(`「 」 / 『 』`). Other differences: 書名號 conventions, "
            "民國 era dates in zh-TW. Line-break exclusion rules "
            "(避頭尾) are essentially identical to jlreq's kinsoku."
        ),
    },
}


def _slice_body(source_md: str, src_path: Path | None = None) -> str:
    """Return the body of the vendor source with the trailing 'References'
    section trimmed (the canonical-URL preamble in the summary already
    carries the reference; the long appendix bloats the prompt).

    Also strips the source-extract preamble (the first '## 1.' is the
    real content start)."""
    lines = source_md.splitlines()

    # Find first H2 ("## ") — body starts there.
    body_start = 0
    found_h2 = False
    for i, line in enumerate(lines):
        if line.startswith("## "):
            body_start = i
            found_h2 = True
            break
    if not found_h2:
        # Silent fallback emitted the entire file (incl. H1 preamble) into
        # the canonical summary. Surface this so the operator can verify.
        label = src_path if src_path is not None else "<source>"
        print(
            f"WARN: no H2 heading found in {label}; emitting full file "
            f"body — verify output",
            file=sys.stderr,
        )

    # Find a trailing "## N. References" / "## References" — body ends there.
    body_end = len(lines)
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()
        # Match "## 7. References" or "## References"
        if line.startswith("## ") and line.lower().endswith("references"):
            body_end = i
            break

    return "\n".join(lines[body_start:body_end]).rstrip() + "\n"


def _emit_summary(spec_key: str, spec: dict) -> Path:
    """Build a single summary file from its vendor source."""
    src_path: Path = spec["source"]
    if not src_path.exists():
        raise FileNotFoundError(
            f"vendor source missing: {src_path} — "
            f"create it before running this script."
        )

    source_md = src_path.read_text(encoding="utf-8")
    body = _slice_body(source_md, src_path)

    frontmatter = (
        "---\n"
        f"source: {spec['frontmatter_source']}\n"
        f"version: {VERSION}\n"
        f"last_synced: {LAST_SYNCED}\n"
        f"applies_to: {spec['scope_pair']}\n"
        "---\n\n"
    )

    header = (
        f"# {spec['title']}\n\n"
        f"> Source: {spec['url']} (W3C Document License). "
        f"Distilled for prompt context — see vendor/w3c/{spec_key}-source.md "
        f"for the longer extract this summary is built from, and the W3C URL "
        f"for the full normative text.\n\n"
        f"{spec['preamble']}\n\n"
    )

    out: Path = spec["out"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(frontmatter + header + body, encoding="utf-8")
    return out


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--spec",
        choices=sorted(SPECS.keys()),
        help="Build only one spec (default: build both).",
    )
    args = parser.parse_args(argv)

    targets = [args.spec] if args.spec else sorted(SPECS.keys())

    for key in targets:
        spec = SPECS[key]
        try:
            out = _emit_summary(key, spec)
        except FileNotFoundError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 2
        n_lines = out.read_text(encoding="utf-8").count("\n")
        print(f"OK    {out.relative_to(ROOT)}  ({n_lines} lines)")

    return 0


if __name__ == "__main__":
    sys.exit(main())

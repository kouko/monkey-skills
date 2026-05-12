#!/usr/bin/env python3
"""Build the NICT 日英中基本文 corpus markdown from the vendor fixture.

Source:
  vendor/nict/JEC_basic_sentence_v1-2.csv  (v0.1 fixture, ~30 triples)
  -- or vendor/nict/JEC_basic_sentence_v1-2.xls if shipping the full
     5,304-triple corpus in a future version (requires xlrd / openpyxl;
     extend _read_corpus accordingly).

Output:
  scripts/canonical/nict-en-ja-zh.md

Format (markdown):
  ---
  source: nict-jec-basic-sentence
  version: 1.2
  license: CC-BY 3.0
  count: <N>
  ---

  # NICT 日英中基本文 — v1.2 (sample)

  > Parallel sentence triples for LLM translation context. NOT term
  > pairs — sentence-level exemplars the model can use to anchor style
  > across en / ja / zh.

  ## Topic: <topic-name>
  | en | ja | zh |
  |---|---|---|
  | ... |

Triples are grouped by their `topic` column; topic order = first-occurrence
order in the source CSV (preserves a curator-chosen flow).

Usage:
  python3 scripts/build-nict-corpus.py
  python3 scripts/build-nict-corpus.py --in vendor/nict/JEC_basic_sentence_v1-2.csv
  python3 scripts/build-nict-corpus.py --out scripts/canonical/nict-en-ja-zh.md
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_IN = ROOT / "vendor" / "nict" / "JEC_basic_sentence_v1-2.csv"
DEFAULT_OUT = ROOT / "scripts" / "canonical" / "nict-en-ja-zh.md"


def _read_corpus(csv_path: Path) -> "OrderedDict[str, list[dict]]":
    """Read the NICT CSV fixture and group triples by topic.

    Expected columns: topic, en, ja, zh (UTF-8). Tolerates UTF-8 BOM.
    """
    if not csv_path.exists():
        raise FileNotFoundError(
            f"NICT corpus source not found: {csv_path}\n"
            f"v0.1 ships a small CSV fixture; see vendor/nict/README.md."
        )

    grouped: "OrderedDict[str, list[dict]]" = OrderedDict()
    with csv_path.open(encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required = {"topic", "en", "ja", "zh"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(
                f"NICT CSV missing required columns: {sorted(missing)}; "
                f"got {reader.fieldnames}"
            )
        for row in reader:
            topic = (row.get("topic") or "").strip() or "uncategorized"
            triple = {
                "en": (row.get("en") or "").strip(),
                "ja": (row.get("ja") or "").strip(),
                "zh": (row.get("zh") or "").strip(),
            }
            if not (triple["en"] and triple["ja"] and triple["zh"]):
                # Skip rows missing any of the three languages.
                continue
            grouped.setdefault(topic, []).append(triple)
    return grouped


def _escape_pipe(s: str) -> str:
    """Escape `|` for markdown table cells."""
    return s.replace("|", "\\|")


def _emit_corpus_md(grouped: "OrderedDict[str, list[dict]]") -> str:
    total = sum(len(v) for v in grouped.values())

    parts: list[str] = []
    parts.append("---")
    parts.append("source: nict-jec-basic-sentence")
    parts.append("version: 1.2")
    parts.append("license: CC-BY 3.0")
    parts.append(f"count: {total}")
    parts.append("---")
    parts.append("")
    parts.append("# NICT 日英中基本文 — v1.2 (sample)")
    parts.append("")
    parts.append(
        "> Parallel sentence triples for LLM translation context. NOT term"
    )
    parts.append(
        "> pairs — sentence-level exemplars the model can use to anchor style"
    )
    parts.append(
        "> across en / ja / zh. Source: NICT (情報通信研究機構),"
        " https://alaginrc.nict.go.jp/jecbs/ — CC-BY 3.0."
    )
    parts.append("")

    for topic, triples in grouped.items():
        parts.append(f"## Topic: {topic}")
        parts.append("")
        parts.append("| en | ja | zh |")
        parts.append("|---|---|---|")
        for t in triples:
            parts.append(
                f"| {_escape_pipe(t['en'])} "
                f"| {_escape_pipe(t['ja'])} "
                f"| {_escape_pipe(t['zh'])} |"
            )
        parts.append("")

    return "\n".join(parts).rstrip() + "\n"


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--in",
        dest="src",
        type=Path,
        default=DEFAULT_IN,
        help=f"Input CSV (default: {DEFAULT_IN.relative_to(ROOT)})",
    )
    parser.add_argument(
        "--out",
        dest="dst",
        type=Path,
        default=DEFAULT_OUT,
        help=f"Output markdown (default: {DEFAULT_OUT.relative_to(ROOT)})",
    )
    args = parser.parse_args(argv)

    try:
        grouped = _read_corpus(args.src)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    md = _emit_corpus_md(grouped)
    args.dst.parent.mkdir(parents=True, exist_ok=True)
    args.dst.write_text(md, encoding="utf-8")

    total = sum(len(v) for v in grouped.values())
    print(
        f"OK    {args.dst.relative_to(ROOT)}  "
        f"({total} triples across {len(grouped)} topics)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

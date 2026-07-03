#!/usr/bin/env python3
"""arc_check.py — consolidated arc-book postcondition gate for daily-news-digest.

One command, one verdict, exit code decides:

    python3 arc_check.py <vault_root> <YYYY-MM-DD> --expect-milestones N [--titles zh-tw|off]

Checks (all must pass → exit 0, "ALL PASS"):
  1. starters   — all 16 canonical starter concepts exist in news/arcs/.
  1b. titles    — starter title + filename match the spec table verbatim
                  (default zh-tw; --titles off for non-zh-TW vaults).
  2. anchors    — every [[<date> …#anchor|…]] in arc books resolves to a real
                  heading in that date's digest.
  3. milestones — today's milestone-line total across books ≥ --expect-milestones
                  (REQUIRED: the number of sweep-table rows marked as matched).
  3b. links     — every milestone line carries the mandatory digest link.
  3.5 keywords  — no book may have an empty keyword list.
  4. dedup      — every kind:event book must share ZERO keywords with any other
                  book, AND its title/milestone text must not contain another
                  book's keyword (catches keyword-dodging; ASCII keywords match
                  on word boundaries, CJK keywords by substring).

Any FAIL prints the offending items and exits 1 — fix and re-run until exit 0.
"""
from __future__ import annotations

import argparse
import glob
import re
import sys
from pathlib import Path

CANONICAL_TITLES = {  # concept -> zh-TW Title-column text, verbatim from the spec table
    "us-equities": "美股大盤", "taiwan-equities": "台股", "japan-equities": "日股",
    "ust-us-rates": "美債與美國利率", "us-inflation-data": "美國通膨與經濟數據",
    "boj-jpy": "日銀與日圓", "usd-majors": "美元與主要貨幣",
    "oil-energy": "油價與能源", "precious-metals": "貴金屬",
    "industrial-metals-commodities": "工業金屬與大宗",
    "fed-policy-speak": "Fed 政策與官員發言", "other-central-banks": "其他央行",
    "geopolitics-middle-east": "地緣政治：中東",
    "geopolitics-us-china-taiwan": "地緣政治：美中與台海",
    "china-macro": "中國經濟", "ai-semiconductors": "AI 與半導體",
}
CANONICAL_CONCEPTS = set(CANONICAL_TITLES)


def _contained(keyword: str, hay: str) -> bool:
    """Containment with word boundaries for pure-ASCII keywords.

    CJK text has no word delimiters, so non-ASCII keywords use plain
    substring matching; ASCII keywords require alphanumeric boundaries
    ("gold" must not match inside "Goldman").
    """
    if keyword.isascii():
        return re.search(rf"(?<![A-Za-z0-9]){re.escape(keyword)}(?![A-Za-z0-9])",
                         hay) is not None
    return keyword in hay


def parse_book(path: str) -> dict:
    text = Path(path).read_text(encoding="utf-8")
    concept = re.search(r"^concept:\s*(\S+)", text, re.M)
    kind = re.search(r"^kind:\s*(\S+)", text, re.M)
    title = re.search(r"^title:\s*(.+)$", text, re.M)
    kw_block = re.search(r"^keywords:\s*\n((?:[ \t]+-[ \t]+.+\n?)+)", text, re.M)
    keywords = ({k.strip().lower() for k in re.findall(r"-\s+(.+)", kw_block.group(1))}
                if kw_block else set())
    return {"path": path, "name": Path(path).name, "text": text,
            "concept": concept.group(1) if concept else "",
            "kind": kind.group(1) if kind else "topic",
            "title": title.group(1).strip() if title else "",
            "keywords": keywords}


def check_starters(books: list[dict]) -> list[str]:
    concepts = {b["concept"] for b in books}
    missing = sorted(CANONICAL_CONCEPTS - concepts)
    print(f"[1 starters] books={len(books)} missing={missing or 'none'}")
    return [f"starters: missing {missing}"] if missing else []


def check_titles(books: list[dict]) -> list[str]:
    bad = []
    for b in books:
        want = CANONICAL_TITLES.get(b["concept"])
        if want is None:
            continue  # event books: free naming (dedup check governs them)
        if b["title"] != want or b["name"] != f"Arc - {want}.md":
            bad.append((b["name"], b["title"], f"expected 'Arc - {want}.md' / title '{want}'"))
    print(f"[1b titles] bad={bad or 'none'}")
    return [f"titles: starter title/filename not verbatim from the spec table {bad}"] if bad else []


def check_anchors(books: list[dict], root: Path, date: str) -> list[str]:
    digests = glob.glob(str(root / "news" / f"{date} *.md"))
    heads: set[str] = set()
    if digests:
        dtext = Path(digests[0]).read_text(encoding="utf-8")
        heads = {h.strip() for h in re.findall(r"^#{1,6}\s+(.*)$", dtext, re.M)}
    bad = []
    for b in books:
        for target in re.findall(r"\[\[([^\]|]+)\|", b["text"]):
            if "#" in target and target.split("#", 1)[0].strip().startswith(date):
                anchor = target.split("#", 1)[1]
                if anchor not in heads:
                    bad.append((b["name"], anchor))
    print(f"[2 anchors] bad={bad or 'none'}")
    return [f"anchors: invented/broken {bad}"] if bad else []


def check_milestones(books: list[dict], date: str, expect: int) -> list[str]:
    total = sum(len(re.findall(rf"^- \*\*{re.escape(date)}\*\*", b["text"], re.M))
                for b in books)
    print(f"[3 milestones] on-disk={total} expected>={expect}")
    if total < expect:
        return [f"milestones: {total} on disk < {expect} sweep-matched "
                "(books created without appending milestones?)"]
    return []


def check_milestone_links(books: list[dict], date: str) -> list[str]:
    linkless = []
    for b in books:
        for line in re.findall(rf"^- \*\*{re.escape(date)}\*\*.*$", b["text"], re.M):
            if "[[" not in line:
                linkless.append((b["name"], line[:60]))
    print(f"[3b milestone-links] missing={linkless or 'none'}")
    return [f"milestone-format: lines missing the mandatory digest link {linkless}"] if linkless else []


def check_keywords(books: list[dict]) -> list[str]:
    empty = [b["name"] for b in books if not b["keywords"]]
    print(f"[3.5 keywords] empty={empty or 'none'}")
    if empty:
        return [f"keywords: empty keyword list in {empty} — starters must seed the "
                "spec table's keywords verbatim; event books coin their own"]
    return []


def check_event_dedup(books: list[dict]) -> list[str]:
    hits = []
    for b in books:
        if b["kind"] != "event":
            continue
        ms_text = "\n".join(
            re.findall(r"^- \*\*\d{4}-\d{2}-\d{2}\*\*.*$", b["text"], re.M)).lower()
        hay = (b["title"] + "\n" + b["name"] + "\n" + ms_text).lower()
        for other in books:
            if other["path"] == b["path"]:
                continue
            overlap = b["keywords"] & other["keywords"]
            if overlap:
                hits.append((b["name"], other["name"], f"shared keywords {sorted(overlap)}"))
                continue
            embedded = [k for k in other["keywords"] if k and _contained(k, hay)]
            if embedded:
                hits.append((b["name"], other["name"], f"title/milestone contains {embedded}"))
    print(f"[4 dedup] hits={hits or 'none'}")
    return [f"dedup: event book overlaps existing book — merge instead: {hits}"] if hits else []


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("vault_root")
    ap.add_argument("date")
    ap.add_argument("--expect-milestones", type=int, required=True,
                    help="number of sweep-table rows marked as matched — REQUIRED")
    ap.add_argument("--titles", choices=["zh-tw", "off"], default="zh-tw",
                    help="verify starter titles/filenames against the canonical "
                         "zh-TW table (default); 'off' for non-zh-TW vaults")
    args = ap.parse_args()

    root = Path(args.vault_root)
    books = [parse_book(p) for p in sorted(glob.glob(str(root / "news" / "arcs" / "*.md")))]

    failures = check_starters(books)
    if args.titles == "zh-tw":
        failures += check_titles(books)
    failures += check_anchors(books, root, args.date)
    failures += check_milestones(books, args.date, args.expect_milestones)
    failures += check_milestone_links(books, args.date)
    failures += check_keywords(books)
    failures += check_event_dedup(books)

    if failures:
        print("\nRESULT: FAIL — fix these in THIS run, then re-run arc_check until ALL PASS:")
        for f in failures:
            print(f"  ✗ {f}")
        return 1
    print("\nRESULT: ALL PASS ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())

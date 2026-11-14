"""Per-note structure statistics, so flag counts can share one denominator.

Usage: python3 notestats.py <notes-dir>
Counts sentences (split at 。！？) separately for paragraphs, list items and
callouts; skips frontmatter, headings, tables, code blocks and the numbered
source list (the section whose heading contains 來源 or Sources).
"""
import re
import sys
from pathlib import Path

SENT = re.compile(r"[。！？!?]")


def stats(text):
    out = {"para": 0, "list": 0, "callout": 0, "para_chars": 0, "total_chars": 0, "table_rows": 0}
    lines = text.splitlines()
    i = 0
    if lines and lines[0].strip() == "---":
        i = 1
        while i < len(lines) and lines[i].strip() != "---":
            i += 1
        i += 1
    in_code = False
    in_sources = False
    for line in lines[i:]:
        s = line.strip()
        out["total_chars"] += len(re.sub(r"\s", "", s))
        if s.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not s:
            continue
        if s.startswith("#"):
            in_sources = bool(re.search(r"來源|Sources|參考", s)) and "方法" not in s
            continue
        if in_sources:
            continue
        if s.startswith("|"):
            out["table_rows"] += 1
            continue
        n = len([p for p in SENT.split(s) if p.strip()]) if SENT.search(s) else 0
        if s.startswith(">"):
            out["callout"] += n
        elif re.match(r"^([-*+]|\d+\.)\s", s):
            out["list"] += n
        else:
            out["para"] += n
            out["para_chars"] += len(re.sub(r"\s", "", s))
    return out


print(f"{'note':<8}{'chars':>7}{'tblrows':>8}{'para_s':>8}{'list_s':>8}{'call_s':>8}{'all_s':>7}{'c/para_s':>10}")
for f in sorted(Path(sys.argv[1]).glob("*.md")):
    st = stats(f.read_text(encoding="utf-8"))
    alls = st["para"] + st["list"] + st["callout"]
    cps = st["para_chars"] / st["para"] if st["para"] else 0
    print(f"{f.stem:<8}{st['total_chars']:>7}{st['table_rows']:>8}{st['para']:>8}{st['list']:>8}{st['callout']:>8}{alls:>7}{cps:>10.1f}")

#!/usr/bin/env python3
"""Query a kobodl `--export-library` JSON dump with rich filters.

Reads a JSON file produced by `kobodl book list --export-library FILE` and
applies filters across BookEntitlement / BookMetadata / ReadingState fields.

Outputs a table (default) or full JSON, suitable for piping into shell loops or
LLM consumption.

Usage:
  kobo_query.py --library FILE [filters] [--format FMT] [--fields F1,F2,...]

Filters (all optional, AND-combined):
  --title PATTERN          substring match on Title (case-insensitive)
  --author PATTERN         substring match on any Contributor name
  --series PATTERN         substring match on Series.Name
  --description PATTERN    substring match on plain-text Description
                           (HTML stripped). Multi-keyword OR via comma:
                           --description "AI,人工智慧,機器學習"
  --description-all PATTERN comma list, ALL keywords must match (AND)
  --status STATUS          ReadingState.StatusInfo.Status (Finished / Reading / ReadyToRead)
  --language CODE          BookMetadata.Language (zh / ja / en ...)
  --country CODE           Locale.CountryCode (tw / jp / us ...)
  --publisher PATTERN      substring match on Publisher.Name
  --isbn ISBN              exact match on ISBN
  --pub-after YYYY[-MM-DD] only books with PublicationDate >= this
  --pub-before YYYY[-MM-DD] only books with PublicationDate <= this
  --purchased-after YYYY[-MM-DD] BookEntitlement.Created >= this (acquisition date)
  --purchased-before YYYY[-MM-DD] BookEntitlement.Created <= this
  --finished-after YYYY[-MM-DD] StatusInfo.LastTimeFinished >= this
  --finished-before YYYY[-MM-DD] StatusInfo.LastTimeFinished <= this
  --origin CAT             BookEntitlement.OriginCategory exact match (Purchased / Trial / KoboPlus)
  --genre UUID             exact match on BookMetadata.Genre
  --category UUID          UUID present in BookMetadata.Categories list
  --include-removed        include books with IsRemoved=True (excluded by default)
  --include-hidden         include books with IsHiddenFromArchive=True
  --revision-id ID         exact match on RevisionId
  --min-progress N         min ProgressPercent (0-100)
  --max-progress N         max ProgressPercent (0-100)

Output:
  --format table           tabular human output (default)
  --format json            full BookMetadata + ReadingState as JSON array
  --format ids             one RevisionId per line (for shell loops)
  --format markdown        Obsidian-style book card per match
  --fields F1,F2,...       (table only) subset of columns to show
  --limit N                cap result count

Exit code: 0 if matches found, 1 if zero matches (so shell can detect).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from typing import Any, Iterable


HTML_BR = re.compile(r"<br\s*/?>", re.IGNORECASE)
HTML_TAG = re.compile(r"<[^>]+>")


def clean_html(text: str) -> str:
    """Strip HTML from Description, keeping linebreaks readable."""
    if not text:
        return ""
    text = HTML_BR.sub("\n", text)
    text = HTML_TAG.sub("", text)
    return text.strip()


@dataclass
class Book:
    """Flattened view over the three NewEntitlement subobjects."""

    revision_id: str
    cross_revision_id: str
    title: str
    subtitle: str
    authors: list[str]
    publisher: str
    series_name: str
    series_number: str
    language: str
    country: str
    isbn: str
    pub_date: str
    genre: str
    categories: list[str]
    cover_url: str
    description_html: str
    description_text: str
    is_removed: bool
    is_hidden: bool
    accessibility: str
    origin: str
    purchase_date: str
    status: str
    progress_pct: float
    spent_minutes: int
    times_started: int
    last_started: str
    last_finished: str

    @classmethod
    def from_entitlement(cls, e: dict[str, Any]) -> "Book | None":
        if "BookMetadata" not in e:
            return None
        m = e["BookMetadata"]
        be = e.get("BookEntitlement", {})
        rs = e.get("ReadingState", {})
        si = rs.get("StatusInfo", {}) or {}
        st = rs.get("Statistics", {}) or {}
        bm = rs.get("CurrentBookmark", {}) or {}
        loc = m.get("Locale", {}) or {}
        series = m.get("Series", {}) or {}
        cover = m.get("CoverImageUrl", "") or ""
        if cover.startswith("//"):
            cover = "https:" + cover
        desc = m.get("Description", "") or ""
        return cls(
            revision_id=m.get("RevisionId", ""),
            cross_revision_id=m.get("CrossRevisionId", ""),
            title=m.get("Title", "") or "",
            subtitle=m.get("Subtitle", "") or "",
            authors=list(m.get("Contributors", []) or []),
            publisher=(m.get("Publisher", {}) or {}).get("Name", "") or "",
            series_name=series.get("Name", "") or "",
            series_number=str(series.get("Number", "") or ""),
            language=m.get("Language", "") or "",
            country=loc.get("CountryCode", "") or "",
            isbn=m.get("Isbn", "") or "",
            pub_date=(m.get("PublicationDate", "") or "")[:10],
            genre=m.get("Genre", "") or "",
            categories=list(m.get("Categories", []) or []),
            cover_url=cover,
            description_html=desc,
            description_text=clean_html(desc),
            is_removed=bool(be.get("IsRemoved", False)),
            is_hidden=bool(be.get("IsHiddenFromArchive", False)),
            accessibility=be.get("Accessibility", "") or "",
            origin=be.get("OriginCategory", "") or "",
            purchase_date=(be.get("Created", "") or "")[:10],
            status=si.get("Status", "") or "",
            progress_pct=float(bm.get("ProgressPercent", 0) or 0),
            spent_minutes=int(st.get("SpentReadingMinutes", 0) or 0),
            times_started=int(si.get("TimesStartedReading", 0) or 0),
            last_started=(si.get("LastTimeStartedReading", "") or "")[:10],
            last_finished=(si.get("LastTimeFinished", "") or "")[:10],
        )


def load_books(path: str) -> list[Book]:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    out: list[Book] = []
    for item in raw:
        e = item.get("NewEntitlement", {})
        b = Book.from_entitlement(e)
        if b is not None:
            out.append(b)
    return out


def matches(b: Book, args: argparse.Namespace) -> bool:
    if not args.include_removed and b.is_removed:
        return False
    if not args.include_hidden and b.is_hidden:
        return False
    if args.revision_id and b.revision_id != args.revision_id:
        return False
    if args.title and args.title.lower() not in b.title.lower():
        return False
    if args.author:
        needle = args.author.lower()
        if not any(needle in a.lower() for a in b.authors):
            return False
    if args.series and args.series.lower() not in b.series_name.lower():
        return False
    if args.status and b.status != args.status:
        return False
    if args.language and b.language != args.language:
        return False
    if args.country and b.country != args.country:
        return False
    if args.publisher and args.publisher.lower() not in b.publisher.lower():
        return False
    if args.isbn and b.isbn != args.isbn:
        return False
    if args.min_progress is not None and b.progress_pct < args.min_progress:
        return False
    if args.max_progress is not None and b.progress_pct > args.max_progress:
        return False
    if args.pub_after and b.pub_date < normalize_date(args.pub_after):
        return False
    if args.pub_before and b.pub_date > normalize_date(args.pub_before, end=True):
        return False
    if args.purchased_after and (not b.purchase_date or b.purchase_date < normalize_date(args.purchased_after)):
        return False
    if args.purchased_before and (not b.purchase_date or b.purchase_date > normalize_date(args.purchased_before, end=True)):
        return False
    if args.finished_after and (not b.last_finished or b.last_finished < normalize_date(args.finished_after)):
        return False
    if args.finished_before and (not b.last_finished or b.last_finished > normalize_date(args.finished_before, end=True)):
        return False
    if args.origin and b.origin != args.origin:
        return False
    if args.genre and b.genre != args.genre:
        return False
    if args.category and args.category not in b.categories:
        return False
    if args.description:
        keywords = [k.strip().lower() for k in args.description.split(",") if k.strip()]
        haystack = (b.title + " " + b.subtitle + " " + b.description_text).lower()
        if not any(k in haystack for k in keywords):
            return False
    if args.description_all:
        keywords = [k.strip().lower() for k in args.description_all.split(",") if k.strip()]
        haystack = (b.title + " " + b.subtitle + " " + b.description_text).lower()
        if not all(k in haystack for k in keywords):
            return False
    return True


def normalize_date(s: str, end: bool = False) -> str:
    """Pad partial dates so YYYY < YYYY-MM-DD comparisons behave intuitively.

    --pub-after 2020      → 2020-01-01
    --pub-before 2020     → 2020-12-31
    --pub-after 2020-06   → 2020-06-01
    --pub-before 2020-06  → 2020-06-31  (loose; we use string compare)
    --pub-after 2020-06-15 → 2020-06-15  (unchanged)
    """
    s = s.strip()
    parts = s.split("-")
    if len(parts) == 1:
        return f"{parts[0]}-12-31" if end else f"{parts[0]}-01-01"
    if len(parts) == 2:
        return f"{parts[0]}-{parts[1]}-31" if end else f"{parts[0]}-{parts[1]}-01"
    return s


# ---------- output renderers ----------

DEFAULT_TABLE_FIELDS = [
    "revision_id_short",
    "title",
    "authors_str",
    "series_str",
    "status",
    "progress_pct",
    "language",
]

FIELD_HEADERS = {
    "revision_id": "RevisionId",
    "revision_id_short": "ID",
    "title": "Title",
    "subtitle": "Subtitle",
    "authors_str": "Author(s)",
    "publisher": "Publisher",
    "series_str": "Series",
    "series_name": "Series",
    "series_number": "#",
    "language": "Lang",
    "country": "CC",
    "isbn": "ISBN",
    "pub_date": "Published",
    "purchase_date": "Purchased",
    "status": "Status",
    "progress_pct": "Prog%",
    "spent_minutes": "Min",
    "times_started": "Reads",
    "last_started": "LastStarted",
    "last_finished": "LastFinished",
    "origin": "Origin",
    "is_removed": "Rm",
    "is_hidden": "Hide",
}


def field_value(b: Book, name: str) -> str:
    if name == "revision_id_short":
        return b.revision_id[:8]
    if name == "authors_str":
        return ", ".join(b.authors)
    if name == "series_str":
        if not b.series_name:
            return ""
        return f"{b.series_name} #{b.series_number}" if b.series_number else b.series_name
    val = getattr(b, name, "")
    if isinstance(val, float):
        return f"{val:.0f}"
    return str(val)


def visual_width(s: str) -> int:
    """Approximate display width — CJK chars count as 2 cells."""
    w = 0
    for ch in s:
        cp = ord(ch)
        if (
            0x1100 <= cp <= 0x115F
            or 0x2E80 <= cp <= 0xA4CF
            or 0xAC00 <= cp <= 0xD7A3
            or 0xF900 <= cp <= 0xFAFF
            or 0xFE30 <= cp <= 0xFE4F
            or 0xFF00 <= cp <= 0xFF60
            or 0xFFE0 <= cp <= 0xFFE6
        ):
            w += 2
        else:
            w += 1
    return w


def pad(s: str, width: int) -> str:
    return s + " " * max(0, width - visual_width(s))


def render_table(books: list[Book], fields: list[str]) -> str:
    rows = [[field_value(b, f) for f in fields] for b in books]
    headers = [FIELD_HEADERS.get(f, f) for f in fields]
    cols = list(zip(headers, *rows)) if rows else [[h] for h in headers]
    widths = [max(visual_width(c) for c in col) for col in cols]
    lines = [
        "  ".join(pad(h, w) for h, w in zip(headers, widths)),
        "  ".join("-" * w for w in widths),
    ]
    for r in rows:
        lines.append("  ".join(pad(c, w) for c, w in zip(r, widths)))
    return "\n".join(lines)


def render_json(books: list[Book]) -> str:
    out = []
    for b in books:
        out.append(
            {
                "revision_id": b.revision_id,
                "cross_revision_id": b.cross_revision_id,
                "title": b.title,
                "subtitle": b.subtitle,
                "authors": b.authors,
                "publisher": b.publisher,
                "series": {"name": b.series_name, "number": b.series_number},
                "language": b.language,
                "country": b.country,
                "isbn": b.isbn,
                "publication_date": b.pub_date,
                "cover_url": b.cover_url,
                "description": b.description_text,
                "is_removed": b.is_removed,
                "is_hidden": b.is_hidden,
                "accessibility": b.accessibility,
                "origin": b.origin,
                "purchase_date": b.purchase_date,
                "reading": {
                    "status": b.status,
                    "progress_pct": b.progress_pct,
                    "spent_minutes": b.spent_minutes,
                    "times_started": b.times_started,
                    "last_started": b.last_started,
                    "last_finished": b.last_finished,
                },
            }
        )
    return json.dumps(out, ensure_ascii=False, indent=2)


def render_ids(books: list[Book]) -> str:
    return "\n".join(b.revision_id for b in books)


def render_markdown(books: list[Book]) -> str:
    parts = []
    for b in books:
        title = b.title + (f" — {b.subtitle}" if b.subtitle else "")
        parts.append(f"## {title}")
        meta_bits = []
        if b.authors:
            meta_bits.append(f"**作者**: {', '.join(b.authors)}")
        if b.publisher:
            meta_bits.append(f"**出版**: {b.publisher}")
        if b.pub_date:
            meta_bits.append(f"**日期**: {b.pub_date}")
        if b.isbn:
            meta_bits.append(f"**ISBN**: {b.isbn}")
        if meta_bits:
            parts.append(" | ".join(meta_bits))
        if b.series_name:
            parts.append(f"**系列**: {b.series_name} #{b.series_number}")
        if b.purchase_date:
            origin = f" ({b.origin})" if b.origin and b.origin != "Purchased" else ""
            parts.append(f"**購入**: {b.purchase_date}{origin}")
        if b.status:
            prog = f"{b.progress_pct:.0f}%" if b.progress_pct else ""
            timeline = ""
            if b.last_finished:
                timeline = f" — 完成 {b.last_finished}"
            elif b.last_started:
                timeline = f" — 開讀 {b.last_started}"
            parts.append(f"**閱讀**: {b.status} {prog} ({b.spent_minutes} 分鐘){timeline}")
        parts.append(f"**RevisionId**: `{b.revision_id}`")
        if b.cover_url:
            parts.append(f"![cover]({b.cover_url})")
        if b.description_text:
            for line in b.description_text.splitlines():
                line = line.strip()
                if line:
                    parts.append(f"> {line}")
        parts.append("")
    return "\n".join(parts)


# ---------- summary ----------

def render_summary(books: list[Book]) -> str:
    from collections import Counter

    if not books:
        return "(no matches)"
    status = Counter(b.status for b in books)
    lang = Counter(b.language for b in books)
    series = Counter(b.series_name for b in books if b.series_name)
    total_min = sum(b.spent_minutes for b in books)
    purchase_year = Counter(b.purchase_date[:4] for b in books if b.purchase_date)
    lines = [
        f"matches: {len(books)}",
        f"status: {dict(status)}",
        f"language: {dict(lang)}",
        f"top series: {dict(series.most_common(5))}",
        f"total reading: {total_min} min ({total_min/60:.1f} h)",
    ]
    if purchase_year:
        sorted_years = dict(sorted(purchase_year.items()))
        lines.append(f"purchase year: {sorted_years}")
    return "\n".join(lines)


# ---------- main ----------

def main() -> int:
    p = argparse.ArgumentParser(
        description="Query kobodl --export-library JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--library", required=True, help="path to JSON from kobodl --export-library")
    p.add_argument("--title")
    p.add_argument("--author")
    p.add_argument("--series")
    p.add_argument("--description", help="comma-separated keywords; ANY match")
    p.add_argument("--description-all", help="comma-separated keywords; ALL must match")
    p.add_argument("--status", choices=["Finished", "Reading", "ReadyToRead"])
    p.add_argument("--language")
    p.add_argument("--country")
    p.add_argument("--publisher")
    p.add_argument("--isbn")
    p.add_argument("--pub-after", help="YYYY or YYYY-MM or YYYY-MM-DD")
    p.add_argument("--pub-before", help="YYYY or YYYY-MM or YYYY-MM-DD")
    p.add_argument("--purchased-after", help="acquisition date >= YYYY[-MM[-DD]]")
    p.add_argument("--purchased-before", help="acquisition date <= YYYY[-MM[-DD]]")
    p.add_argument("--finished-after", help="LastTimeFinished >= YYYY[-MM[-DD]]")
    p.add_argument("--finished-before", help="LastTimeFinished <= YYYY[-MM[-DD]]")
    p.add_argument("--origin", help="OriginCategory exact match (Purchased / Trial / KoboPlus / ...)")
    p.add_argument("--genre", help="exact UUID match on BookMetadata.Genre")
    p.add_argument("--category", help="UUID present in BookMetadata.Categories list")
    p.add_argument("--revision-id")
    p.add_argument("--include-removed", action="store_true")
    p.add_argument("--include-hidden", action="store_true")
    p.add_argument("--min-progress", type=float)
    p.add_argument("--max-progress", type=float)
    p.add_argument("--format", choices=["table", "json", "ids", "markdown", "summary"], default="table")
    p.add_argument("--fields", help="comma-separated field list for --format=table")
    p.add_argument("--limit", type=int)
    p.add_argument(
        "--sort",
        choices=[
            "title", "author", "series", "progress", "spent", "pub_date",
            "purchase_date", "last_started", "last_finished",
        ],
        help="sort key. Date sorts (purchase_date / last_started / last_finished) "
             "are descending (newest first); progress / spent are descending "
             "(highest first); the rest are ascending. Books with empty values "
             "for date sorts sort to the end.",
    )
    args = p.parse_args()

    try:
        books = load_books(args.library)
    except FileNotFoundError:
        print(f"error: library file not found: {args.library}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON in library file: {e}", file=sys.stderr)
        return 2

    filtered = [b for b in books if matches(b, args)]

    sort_keys = {
        "title": lambda b: b.title,
        "author": lambda b: (b.authors[0] if b.authors else ""),
        "series": lambda b: (b.series_name, b.series_number),
        "progress": lambda b: -b.progress_pct,
        "spent": lambda b: -b.spent_minutes,
        "pub_date": lambda b: b.pub_date,
    }
    DATE_DESC_SORTS = ("purchase_date", "last_started", "last_finished")
    if args.sort in sort_keys:
        filtered.sort(key=sort_keys[args.sort])
    elif args.sort in DATE_DESC_SORTS:
        # Newest first; empty values sort to the end so they don't block useful results.
        filled = [b for b in filtered if getattr(b, args.sort)]
        empty = [b for b in filtered if not getattr(b, args.sort)]
        filled.sort(key=lambda b: getattr(b, args.sort), reverse=True)
        filtered = filled + empty

    if args.limit:
        filtered = filtered[: args.limit]

    if args.format == "table":
        fields = args.fields.split(",") if args.fields else DEFAULT_TABLE_FIELDS
        print(render_table(filtered, fields))
    elif args.format == "json":
        print(render_json(filtered))
    elif args.format == "ids":
        print(render_ids(filtered))
    elif args.format == "markdown":
        print(render_markdown(filtered))
    elif args.format == "summary":
        print(render_summary(filtered))

    return 0 if filtered else 1


if __name__ == "__main__":
    sys.exit(main())

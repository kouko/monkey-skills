#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""build_citation_url — Phase 1.7 (v0.3.3+) citation-URL constructors.

Pure URL construction (no network). The LLM calls this to derive a
WebFetch target before fetching law.moj.gov.tw / judgment.judicial.gov.tw /
主管機關 sites. Output is the target URL only; the WebFetch + parse +
cache write happens at protocol level in L7 Step 9.3.x.

URL templates + agency hosts come from
assets/legal-sources.json. This script bundles a copy at module-load
time to avoid filesystem coupling in tests.

Usage:
  uv run build_citation_url.py statute --statute 民法 --article 247-1
  uv run build_citation_url.py case --court 最高法院 --year 105 --type 台上 --number 1501
  uv run build_citation_url.py function-letter --agency 個人資料保護委員會

Output (stdout JSON):
  {"url": "<url>", "source_host": "<host>",
   "source_metadata": {<type-specific>}, "verified": "templated"|"search-only"}

Exit codes:
  0 = url constructed
  1 = source not in registry (statute name unknown, court code unknown, etc.)
  2 = bad usage
"""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from pathlib import Path


_DEFAULT_LEGAL_SOURCES = (
    Path(__file__).resolve().parent.parent / "assets" / "legal-sources.json"
)


def load_legal_sources(path: Path | None = None) -> dict:
    """Load legal-sources.json (cached single-read)."""
    path = path or _DEFAULT_LEGAL_SOURCES
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_statute_name(name: str, sources: dict) -> str | None:
    """Resolve common short / long name aliases to the canonical statute key."""
    nfc = unicodedata.normalize("NFC", name.strip())
    statutes = sources.get("statute_sources", {})
    if nfc in statutes:
        return nfc
    # Check alias_short_name
    for canonical, entry in statutes.items():
        if entry.get("alias_short_name") == nfc:
            return canonical
    return None


def build_statute_url(
    statute: str, article: str, *, sources: dict | None = None
) -> dict:
    """Build single-article URL for a TW statute.

    Returns dict with url + source_host + metadata. Raises ValueError if
    statute is not in the registry.
    """
    sources = sources or load_legal_sources()
    canonical = _normalize_statute_name(statute, sources)
    if canonical is None:
        raise ValueError(
            f"statute {statute!r} not in legal-sources.json registry; "
            f"add it under statute_sources or use a recognised alias"
        )
    entry = sources["statute_sources"][canonical]
    url = entry["single_article_url_template"].format(
        pcode=entry["pcode"], article=article
    )
    return {
        "url": url,
        "source_host": entry["host"],
        "source_metadata": {
            "statute": canonical,
            "article": article,
            "pcode": entry["pcode"],
            "alias_short_name": entry.get("alias_short_name"),
        },
        "verified": "templated",
    }


def build_case_url(
    court: str,
    year: int,
    case_type: str,
    number: int,
    *,
    sources: dict | None = None,
) -> dict:
    """Build direct-data URL for a judicial case.

    Uses judgment.judicial.gov.tw direct-data pattern when court_code is
    in the registry. Falls back to search-page URL otherwise.
    """
    sources = sources or load_legal_sources()
    case_src = sources.get("case_sources", {}).get("default", {})
    court_codes = case_src.get("court_codes", {})
    court_nfc = unicodedata.normalize("NFC", court.strip())

    if court_nfc not in court_codes:
        # Fall back to search-page URL — LLM will need to do a keyword search
        search_url = case_src.get("search_url")
        if not search_url:
            raise ValueError(
                f"court {court!r} not in court_codes registry AND no search_url; "
                f"cannot build any URL"
            )
        return {
            "url": search_url,
            "source_host": case_src.get("host", "judgment.judicial.gov.tw"),
            "source_metadata": {
                "court": court_nfc,
                "year": year,
                "case_type": case_type,
                "number": number,
                "court_code": None,
                "fallback_reason": f"court {court_nfc!r} not in court_codes registry",
            },
            "verified": "search-only",
        }

    court_code = court_codes[court_nfc]
    url = case_src["direct_data_url_template"].format(
        court_code=court_code, year=year, type=case_type, number=number
    )
    return {
        "url": url,
        "source_host": case_src["host"],
        "source_metadata": {
            "court": court_nfc,
            "year": year,
            "case_type": case_type,
            "number": number,
            "court_code": court_code,
        },
        "verified": "templated",
    }


def build_function_letter_url(agency: str, *, sources: dict | None = None) -> dict:
    """Build search-page URL for a function letter (LLM follows up to find the specific letter).

    Function letters don't have direct-data permalinks like cases do.
    Best the constructor can do is return the agency's search-page URL.
    """
    sources = sources or load_legal_sources()
    agencies = sources.get("function_letter_sources", {})
    agency_nfc = unicodedata.normalize("NFC", agency.strip())

    if agency_nfc not in agencies:
        raise ValueError(
            f"agency {agency!r} not in function_letter_sources registry; "
            f"add it or use a recognised name"
        )
    entry = agencies[agency_nfc]
    return {
        "url": entry["search_url_hint"],
        "source_host": entry["host"],
        "source_metadata": {
            "agency": agency_nfc,
            "fetch_note": entry.get("fetch_note", ""),
        },
        "verified": "search-only",
    }


# --------------------------------------------------------- CLI


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--legal-sources",
        type=Path,
        default=None,
        help="override path to legal-sources.json (default: assets/legal-sources.json)",
    )

    subparsers = parser.add_subparsers(dest="entry_type", required=True)

    s = subparsers.add_parser("statute", help="build statute single-article URL")
    s.add_argument("--statute", required=True)
    s.add_argument("--article", required=True)

    c = subparsers.add_parser("case", help="build judicial case URL")
    c.add_argument("--court", required=True)
    c.add_argument("--year", required=True, type=int)
    c.add_argument("--type", required=True, dest="case_type")
    c.add_argument("--number", required=True, type=int)

    f = subparsers.add_parser("function-letter", help="build function-letter agency search URL")
    f.add_argument("--agency", required=True)

    args = parser.parse_args(argv)
    sources = load_legal_sources(args.legal_sources)

    try:
        if args.entry_type == "statute":
            result = build_statute_url(args.statute, args.article, sources=sources)
        elif args.entry_type == "case":
            result = build_case_url(
                args.court, args.year, args.case_type, args.number, sources=sources
            )
        elif args.entry_type == "function-letter":
            result = build_function_letter_url(args.agency, sources=sources)
        else:
            parser.error(f"unsupported entry type: {args.entry_type!r}")
    except ValueError as e:
        sys.stderr.write(f"build_citation_url: {e}\n")
        return 1

    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""cache_check — Phase 1.7 (v0.3.3+) runtime-fetch cache layer.

Checks whether a citation cache entry exists, is well-formed, and is still
within its TTL window. The LLM consults this BEFORE deciding whether to
WebFetch from law.moj.gov.tw / judgment.judicial.gov.tw / 主管機關.

Cache layout (relative to --cache-dir, defaults to <cwd>/.legal-toolkit/cache/):
  statutes/<statute-slug>-<article>.json
  cases/<court-slug>-<year>-<type-slug>-<number>.json
  function_letters/<agency-slug>-<letter-id-slug>.json

Cache entry format defined in
assets/output-schema-citation-cache.json. cache_check validates the
shape lightly (required keys + expiry).

Usage:
  uv run cache_check.py statute --statute 民法 --article 247-1
  uv run cache_check.py case --court 最高法院 --year 105 --type 台上 --number 1501
  uv run cache_check.py function-letter --agency 個人資料保護委員會 --letter-id 113-0001

Output (stdout JSON):
  {"status": "hit"|"miss"|"expired"|"invalid", "path": "<abs path or null>",
   "entry": <cache content or null>, "reason": "<one line>"}

Exit codes:
  0 = hit (entry exists, schema valid, not expired)
  1 = miss (no file at expected path)
  2 = expired (file exists but past expires_at)
  3 = invalid (file exists but fails minimum schema check)
  4 = bad usage (missing required CLI args)
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
import unicodedata
from pathlib import Path


REQUIRED_KEYS_TOP = {"type", "key", "fetched_at", "ttl_days", "expires_at", "source_url", "content", "verification"}
VALID_TYPES = {"statute", "case", "function_letter"}


# --------------------------------------------------------- key normalization


def _slugify(text: str) -> str:
    """NFC-normalize + remove path-unsafe chars + collapse whitespace.

    Preserves Han characters (so '民法' stays '民法') because cache files are
    user-visible and Chinese cache keys are easier to scan than slugified ones.
    Only removes filesystem-illegal characters."""
    nfc = unicodedata.normalize("NFC", text)
    # Strip whitespace, replace path separators / shell-special chars with hyphen
    cleaned = re.sub(r"[\s/\\:*?\"<>|]+", "-", nfc.strip())
    # Collapse runs of hyphens
    cleaned = re.sub(r"-{2,}", "-", cleaned)
    return cleaned.strip("-")


def statute_cache_key(statute: str, article: str) -> str:
    return f"{_slugify(statute)}-{_slugify(article)}"


def case_cache_key(court: str, year: int, case_type: str, number: int) -> str:
    return f"{_slugify(court)}-{year}-{_slugify(case_type)}-{number}"


def function_letter_cache_key(agency: str, letter_id: str) -> str:
    return f"{_slugify(agency)}-{_slugify(letter_id)}"


# --------------------------------------------------------- cache directory


def default_cache_dir() -> Path:
    """Default cache root: <cwd>/.legal-toolkit/cache/."""
    return Path.cwd() / ".legal-toolkit" / "cache"


def cache_path_for(cache_dir: Path, entry_type: str, key: str) -> Path:
    """Map (type, key) → filesystem path."""
    if entry_type == "statute":
        sub = "statutes"
    elif entry_type == "case":
        sub = "cases"
    elif entry_type == "function_letter":
        sub = "function_letters"
    else:
        raise ValueError(f"unsupported entry type: {entry_type!r}")
    return cache_dir / sub / f"{key}.json"


# --------------------------------------------------------- cache check


def _now_iso() -> str:
    return _dt.datetime.now().replace(microsecond=0).isoformat()


def _parse_iso(value: str) -> _dt.datetime:
    return _dt.datetime.fromisoformat(value.replace("Z", "+00:00").rstrip("Z"))


def _minimum_schema_ok(entry: dict) -> tuple[bool, str]:
    """Lightweight schema check — strict-JSONSchema deferred to LLM/test."""
    missing = REQUIRED_KEYS_TOP - entry.keys()
    if missing:
        return False, f"missing required keys: {sorted(missing)}"
    if entry.get("type") not in VALID_TYPES:
        return False, f"invalid type: {entry.get('type')!r}"
    if not isinstance(entry.get("ttl_days"), int) or entry["ttl_days"] < 1:
        return False, "ttl_days must be positive int"
    for ts_field in ("fetched_at", "expires_at"):
        try:
            _parse_iso(entry[ts_field])
        except (ValueError, KeyError, AttributeError):
            return False, f"{ts_field} not ISO 8601"
    return True, "ok"


def check_cache(
    entry_type: str,
    *,
    key: str,
    cache_dir: Path | None = None,
    now: _dt.datetime | None = None,
) -> dict:
    """Core check. Returns dict with status + path + entry + reason."""
    cache_dir = cache_dir or default_cache_dir()
    path = cache_path_for(cache_dir, entry_type, key)
    now = now or _dt.datetime.now()

    if not path.exists():
        return {
            "status": "miss",
            "path": None,
            "entry": None,
            "reason": f"no cache file at {path}",
        }

    try:
        entry = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return {
            "status": "invalid",
            "path": str(path),
            "entry": None,
            "reason": f"JSON decode error: {e}",
        }

    ok, reason = _minimum_schema_ok(entry)
    if not ok:
        return {
            "status": "invalid",
            "path": str(path),
            "entry": entry,
            "reason": reason,
        }

    try:
        expires_at = _parse_iso(entry["expires_at"])
    except ValueError as e:
        return {
            "status": "invalid",
            "path": str(path),
            "entry": entry,
            "reason": f"unparseable expires_at: {e}",
        }

    if now > expires_at:
        return {
            "status": "expired",
            "path": str(path),
            "entry": entry,
            "reason": f"expired at {entry['expires_at']} (now: {now.isoformat(timespec='seconds')})",
        }

    return {
        "status": "hit",
        "path": str(path),
        "entry": entry,
        "reason": "cache hit within TTL",
    }


# --------------------------------------------------------- CLI


_STATUS_EXIT_CODES = {"hit": 0, "miss": 1, "expired": 2, "invalid": 3}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=None,
        help="cache root directory (default: <cwd>/.legal-toolkit/cache/)",
    )

    subparsers = parser.add_subparsers(dest="entry_type", required=True)

    s = subparsers.add_parser("statute", help="check statute article cache")
    s.add_argument("--statute", required=True, help="e.g. 民法 / 個人資料保護法")
    s.add_argument("--article", required=True, help="e.g. 247-1 / 20-1")

    c = subparsers.add_parser("case", help="check judicial case cache")
    c.add_argument("--court", required=True, help="e.g. 最高法院 / 智慧財產法院")
    c.add_argument("--year", required=True, type=int, help="民國 year, e.g. 105")
    c.add_argument("--type", required=True, dest="case_type", help="e.g. 台上 / 民營訴 / 判")
    c.add_argument("--number", required=True, type=int, help="case number")

    f = subparsers.add_parser("function-letter", help="check function letter cache")
    f.add_argument("--agency", required=True, help="e.g. 個人資料保護委員會")
    f.add_argument("--letter-id", required=True, help="e.g. 113-0001")

    args = parser.parse_args(argv)

    if args.entry_type == "statute":
        key = statute_cache_key(args.statute, args.article)
        result = check_cache("statute", key=key, cache_dir=args.cache_dir)
    elif args.entry_type == "case":
        key = case_cache_key(args.court, args.year, args.case_type, args.number)
        result = check_cache("case", key=key, cache_dir=args.cache_dir)
    elif args.entry_type == "function-letter":
        key = function_letter_cache_key(args.agency, args.letter_id)
        result = check_cache("function_letter", key=key, cache_dir=args.cache_dir)
    else:
        parser.error(f"unsupported entry type: {args.entry_type!r}")

    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return _STATUS_EXIT_CODES.get(result["status"], 4)


if __name__ == "__main__":
    sys.exit(main())

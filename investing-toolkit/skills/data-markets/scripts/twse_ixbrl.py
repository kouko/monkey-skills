#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests==2.33.1"]
# ///
"""twse_ixbrl.py — investing-toolkit TW MOPS iXBRL client CLI (Task 5)

Composes the four TW iXBRL modules into one client: fetches the raw
tagged filing (`twse_ixbrl_fetch`, Task 2), parses it into flat fact
records (`twse_ixbrl_parser`, Task 1), then maps those facts into the
canonical three-statement shape (`twse_ixbrl_canonical`, Task 3) and the
curated note fields (`twse_ixbrl_notes`, Task 4). Emits ONE JSON object
to stdout: `{"canonical": {...}, "notes": {...}, "_meta": {...}}`.

On any failure (period not filed, parse/mapping error) emits a JSON
`_error` envelope instead — mirrors sec_edgar_client.py's fail-loud
convention, but keyed `_error` (not `error`) to match `pack_tw.run_client`'s
top-level error-envelope contract, since this is the `run_client`-invokable
entry point (`pack_tw.run_client` shells `uv run twse_ixbrl.py ...`).
Never a raw traceback to stdout.

Usage:
  uv run twse_ixbrl.py --co-id 2330 --year 2024 --season 3 --report-id C

  # report-id defaults to "C" (consolidated); "A" (parent-only) is not
  # served by the t164sb01 endpoint and always resolves to not-found.
  uv run twse_ixbrl.py --co-id 2330 --year 2024 --season 3
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

import twse_ixbrl_canonical
import twse_ixbrl_fetch
import twse_ixbrl_notes
import twse_ixbrl_parser

_LOG_TAG = "twse-ixbrl"
_QUIET = False


def _log(stage: str, msg: str = "") -> None:
    if _QUIET:
        return
    suffix = f": {msg}" if msg else ""
    sys.stderr.write(f"[{_LOG_TAG}] {stage}{suffix}\n")
    sys.stderr.flush()


def _propagate_quiet() -> None:
    """Propagate --quiet to the 4 composed sibling modules' stderr
    logging. `twse_ixbrl_fetch` gates its own `_log` on a `_QUIET`
    global, so setting that is enough for it; `twse_ixbrl_parser`,
    `twse_ixbrl_canonical` and `twse_ixbrl_notes` have no such gate
    (their `_log` always writes) -- for those, neutralize `_log`
    itself at the module-attribute level. Runtime attribute-setting
    on the imported module objects only -- the sibling source files
    are never edited.
    """
    for mod in (twse_ixbrl_fetch, twse_ixbrl_parser, twse_ixbrl_canonical, twse_ixbrl_notes):
        if hasattr(mod, "_QUIET"):
            setattr(mod, "_QUIET", True)
        if hasattr(mod, "_log"):
            setattr(mod, "_log", lambda *_args, **_kwargs: None)


def run_pipeline(co_id: str, year: int, season: int, report_id: str = "C") -> dict[str, Any]:
    """Fetch -> parse -> canonical + curated notes for one
    (co_id, year, season, report_id). Never raises -- any failure is
    returned as a JSON-serializable `{"_error": ...}` envelope.
    """
    meta: dict[str, Any] = {
        "co_id": co_id, "year": year, "season": season, "report_id": report_id,
    }

    try:
        body = twse_ixbrl_fetch.fetch_ixbrl_body(
            co_id=co_id, year=year, season=season, report_id=report_id,
        )
    except Exception as exc:  # noqa: BLE001 — fail loud, don't guess the shape
        _log("fetch failed", str(exc))
        return {"_error": f"fetch_failed: {exc}", **meta}

    if body is None:
        _log("not found", f"co_id={co_id} year={year} season={season} report_id={report_id}")
        return {
            "_error": "not_found: TWSE MOPS filing not filed for this period (檔案不存在)",
            **meta,
        }

    try:
        facts = twse_ixbrl_parser.parse_ixbrl_facts(body)
        canonical = twse_ixbrl_canonical.build_canonical(facts)
        notes = twse_ixbrl_notes.extract_curated_notes(facts)
    except Exception as exc:  # noqa: BLE001 — fail loud, don't guess the shape
        _log("parse/build failed", str(exc))
        return {"_error": f"parse_failed: {exc}", **meta}

    meta["fact_count"] = len(facts)
    return {"canonical": canonical, "notes": notes, "_meta": meta}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="TW MOPS iXBRL client for investing-toolkit"
    )
    parser.add_argument("--co-id", required=True, help="TW company code (e.g. 2330)")
    parser.add_argument("--year", required=True, type=int, help="Filing year (e.g. 2024)")
    parser.add_argument(
        "--season", required=True, type=int, choices=[1, 2, 3, 4],
        help="Filing season/quarter (1-4)",
    )
    parser.add_argument(
        "--report-id", default="C",
        help="C=consolidated 合併 (default), A=parent-only (not served by this endpoint)",
    )
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress progress logging on stderr (default: verbose)")

    args = parser.parse_args()
    global _QUIET
    _QUIET = args.quiet
    if _QUIET:
        _propagate_quiet()

    result = run_pipeline(args.co_id, args.year, args.season, args.report_id)
    print(json.dumps(result, default=str, ensure_ascii=False, indent=2))
    sys.exit(1 if "_error" in result else 0)


if __name__ == "__main__":
    main()

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
taxonomy-routed note fields (`twse_ixbrl_notes`, Task 4/9/10 — curated
notes for -ci, NPL/coverage notes for -fh/-basi, none for -bd/-ins).
Emits ONE JSON object to stdout:
`{"canonical": {...}, "notes": {...}, "_meta": {...}}`.

On any failure (period not filed, parse/mapping error) emits a JSON
`_error` envelope instead — mirrors sec_edgar_client.py's fail-loud
convention, but keyed `_error` (not `error`) to match `pack_tw.run_client`'s
top-level error-envelope contract, since this is the `run_client`-invokable
entry point (`pack_tw.run_client` shells `uv run twse_ixbrl.py ...`).
Never a raw traceback to stdout.

Usage:
  # --report-id omitted (default): tries C (consolidated) then A
  # (individual) automatically -- covers both consolidated (-ci/-fh/-basi/
  # -bd) filers (served at C) and individual-only filers (standalone
  # insurers, bills-finance, e.g. 華票 2820) served ONLY at A.
  uv run twse_ixbrl.py --co-id 2330 --year 2024 --season 3

  # --report-id is an explicit override -- skips the C/A fallback and
  # fetches only the given scope.
  uv run twse_ixbrl.py --co-id 2330 --year 2024 --season 3 --report-id C
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


def _extract_notes(facts: list[Any], canonical: dict[str, Any]) -> dict[str, Any]:
    """Route note extraction by canonical's taxonomy family (Task 11).

    -ci (taxonomy absent from canonical -- see
    twse_ixbrl_canonical._build_ci_canonical) keeps the curated-notes set
    unchanged. -fh and -basi each carry their own NPL/coverage note shape
    routed to their own extractor. -bd/-ins have no NPL/coverage note at
    all (brokers/insurers) -- deliberately no extractor call, not even
    extract_curated_notes, which is -ci-shaped.
    """
    taxonomy = canonical.get("taxonomy")
    if taxonomy == "fh":
        return twse_ixbrl_notes.extract_fh_npl_coverage_notes(facts)
    if taxonomy == "basi":
        return twse_ixbrl_notes.extract_basi_npl_coverage_notes(facts)
    if taxonomy in ("bd", "ins"):
        return {}
    return twse_ixbrl_notes.extract_curated_notes(facts)


def run_pipeline(co_id: str, year: int, season: int, report_id: str | None = None) -> dict[str, Any]:
    """Fetch -> parse -> canonical + notes for one (co_id, year, season).
    Never raises -- any failure is returned as a JSON-serializable
    `{"_error": ...}` envelope.

    `report_id`: an explicit override ("C" or "A") fetches at that
    report_id only (no fallback) -- callers that already know a filer's
    consolidation scope should pass it. When omitted (None, the default),
    the pipeline tries report_id="C" (consolidated) then "A" (individual)
    via `twse_ixbrl_fetch.fetch_with_report_fallback` -- consolidated
    (-ci) filers are served only at C, but individual-only filers
    (standalone insurers, bills-finance) are served ONLY at A.
    """
    meta: dict[str, Any] = {"co_id": co_id, "year": year, "season": season}

    try:
        if report_id is not None:
            body = twse_ixbrl_fetch.fetch_ixbrl_body(
                co_id=co_id, year=year, season=season, report_id=report_id,
            )
            report_id_used = report_id
        else:
            body, report_id_used = twse_ixbrl_fetch.fetch_with_report_fallback(
                co_id, year, season, fetch_fn=twse_ixbrl_fetch.fetch_ixbrl_body,
            )
    except Exception as exc:  # noqa: BLE001 — fail loud, don't guess the shape
        _log("fetch failed", str(exc))
        return {"_error": f"fetch_failed: {exc}", **meta, "report_id": report_id}

    meta["report_id"] = report_id_used
    if body is None:
        _log("not found", f"co_id={co_id} year={year} season={season} report_id={report_id_used}")
        return {
            "_error": "not_found: TWSE MOPS filing not filed for this period (檔案不存在)",
            **meta,
        }

    try:
        facts = twse_ixbrl_parser.parse_ixbrl_facts(body)
        canonical = twse_ixbrl_canonical.build_canonical(facts)
        notes = _extract_notes(facts, canonical)
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
        "--report-id", default=None,
        help=(
            "Explicit consolidation-scope override: C=consolidated 合併, "
            "A=individual/parent-only 個別. Default (omitted): try C then A "
            "automatically -- individual-only filers (standalone insurers, "
            "bills-finance) are served ONLY at A."
        ),
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

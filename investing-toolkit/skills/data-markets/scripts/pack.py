#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""
pack.py — investing-toolkit unified data-markets facade

Single CLI entry point across all 5 markets (us/jp/tw/kr/cn). Detects the
market from ticker suffix, dispatches to the matching
`pack_{market}.build_pack(pack_name, tickers)`, and enforces a fail-loud
exit-code contract. Pure stdlib — the market modules (pack_us.py etc.,
same directory) own their own subprocess/client dependencies.

Usage:
  uv run pack.py --ticker AAPL --pack snapshot
  uv run pack.py --ticker 2330.TW --pack snapshot
  uv run pack.py --tickers AAPL,MSFT --pack screener-batch
  uv run pack.py --pack regime-pack --market us
  uv run pack.py --ticker 005930.KS --pack snapshot --quiet

Market auto-detection (suffix-based; --market overrides detection
entirely):
  .TW / .TWO             -> tw
  .KS / .KQ              -> kr
  .SS / .SZ / .HK        -> cn
  .T  or bare 4-digit     -> jp
  else                    -> us (historical default; noted in
                                 _status.warnings — the ticker matched no
                                 explicit suffix rule)

- `--pack regime-pack` has no ticker dimension: `--market` is REQUIRED.
- A `--tickers` list whose members resolve to MORE THAN ONE market is
  rejected (exit 64) — one market per invocation, matching the historical
  per-market skill behavior. Do not silently pick one.

Exit contract:
  0   all sections ok                _status.status = "ok"
  2   some sections failed           _status.status = "partial"
  1   all sections failed, or an
      unexpected exception           _status.status = "failed"
  64  usage error (bad args, bad
      pack name, mixed-market
      tickers, missing --market
      for regime-pack)               _status.status = "usage_error"

`_status` is injected at the top level of the emitted JSON:
  status, market, pack, failed_sections (list), warnings (list),
  plus `message` (usage_error) or `traceback` (failed via crash).

The 5 markets speak different error dialects (see `_classify_result`
below): us/cn/jp fail per-section (`{"error": ...}` / `{"_error": ...}`
nested directly under a top-level section key, or one level below it —
inside a ticker-keyed sub-dict, or inside a per-ticker list item); kr/tw
also usually fail one level below a section (wrap()-nested `_error`, or a
ticker-keyed dict whose entries carry the raw client error) — visible to
the same one-level walk. Only a failure nested TWO OR MORE levels below a
section still relies on the whole-pack top-level `_partial: true` flag
with no per-section attribution (see the LOOM-SIMPLIFY note below).

Dropped flags: the old per-market CLIs' `--indicators` (data-kr
regime-pack indicator-group subset) and `--kosdaq` (data-kr force-.KQ
ticker override) are intentionally NOT carried forward — grep of every
downstream skill/doc found zero references to either flag. The underlying
functions (`pack_kr.pack_regime_pack(indicators)`,
`pack_kr.normalize_ticker(ticker, force_kosdaq)`) remain directly
importable/callable if a future need arises; this facade always invokes
them with their defaults ("all" / False).

Environment:
  INVESTING_TOOLKIT_CACHE   passed through unchanged to underlying clients
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import traceback
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import pack_cn  # noqa: E402
import pack_jp  # noqa: E402
import pack_kr  # noqa: E402
import pack_tw  # noqa: E402
import pack_us  # noqa: E402

MARKET_MODULES = {
    "us": pack_us,
    "jp": pack_jp,
    "tw": pack_tw,
    "kr": pack_kr,
    "cn": pack_cn,
}
MARKETS: tuple[str, ...] = tuple(MARKET_MODULES)

EXIT_OK = 0
EXIT_PARTIAL = 2
EXIT_FAILED = 1
EXIT_USAGE_ERROR = 64

# Suffix -> market. Order matters only in that each pattern is disjoint.
_SUFFIX_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\.(TW|TWO)$", re.IGNORECASE), "tw"),
    (re.compile(r"\.(KS|KQ)$", re.IGNORECASE), "kr"),
    (re.compile(r"\.(SS|SZ|HK)$", re.IGNORECASE), "cn"),
    (re.compile(r"\.T$", re.IGNORECASE), "jp"),
)
_BARE_4DIGIT = re.compile(r"^\d{4}$")


class _UsageError(Exception):
    """Raised for any argument/detection problem the facade must reject
    before calling into a market module. Always maps to exit 64."""


class _ArgumentParser(argparse.ArgumentParser):
    """argparse calls sys.exit(2) with a stderr message by default; the
    fail-loud contract requires exit 64 + a JSON _status block on stdout
    instead, so route parse errors through _UsageError."""

    def error(self, message: str) -> None:  # type: ignore[override]
        raise _UsageError(message)


def detect_market(ticker: str) -> tuple[str, bool]:
    """Detect (market, matched_explicit_rule) from a ticker's suffix.

    matched_explicit_rule is False when the ticker fell through to the
    'us' historical default with no suffix match — callers surface that
    as a _status.warnings entry rather than silently guessing.
    """
    for pattern, market in _SUFFIX_RULES:
        if pattern.search(ticker):
            return market, True
    if _BARE_4DIGIT.match(ticker):
        return "jp", True
    return "us", False


def _parse_tickers(args: argparse.Namespace) -> list[str]:
    if args.tickers:
        return [t.strip() for t in args.tickers.split(",") if t.strip()]
    if args.ticker:
        return [args.ticker.strip()]
    return []


def _resolve_market(
    pack: str, tickers: list[str], explicit_market: str | None
) -> tuple[str, list[str]]:
    """Resolve the single market this invocation targets.

    Returns (market, warnings). Raises _UsageError when regime-pack is
    requested without --market, or when the ticker list spans more than
    one detected market.
    """
    if explicit_market:
        return explicit_market, []

    if pack == "regime-pack":
        raise _UsageError(
            "--pack regime-pack has no ticker dimension; --market is required"
        )

    if not tickers:
        raise _UsageError(f"--pack {pack} requires --ticker or --tickers")

    warnings: list[str] = []
    detected: list[str] = []
    for t in tickers:
        market, matched = detect_market(t)
        if not matched:
            warnings.append(
                f"ticker {t!r}: unrecognized suffix, defaulted to market 'us'"
            )
        detected.append(market)

    distinct = sorted(set(detected))
    if len(distinct) > 1:
        raise _UsageError(
            f"tickers resolve to multiple markets {distinct}; a single "
            f"invocation must target one market (pass --market to override "
            f"detection)"
        )
    return distinct[0], warnings


def _has_error_marker(value: object) -> bool:
    """A dict directly carries a failure marker at its own top level."""
    return isinstance(value, dict) and ("error" in value or "_error" in value)


def _dict_section_status(value: dict) -> str:
    """Classify a dict-valued section (or list item) as ok/partial/failed,
    walking exactly ONE level: a direct "error"/"_error" key is immediate
    failure; otherwise inspect this dict's own NON-EMPTY dict-valued
    sub-fields (an empty sub-dict carries no signal either way — it is
    absent data, not a checked-and-ok result, so it is skipped rather than
    counted as non-failed) — if every non-empty sub-dict carries a direct
    error, the whole thing is "failed"; if only some do, "partial";
    otherwise "ok"."""
    if _has_error_marker(value):
        return "failed"
    subdicts = [v for v in value.values() if isinstance(v, dict) and v]
    if not subdicts:
        return "ok"
    flags = [_has_error_marker(v) for v in subdicts]
    if all(flags):
        return "failed"
    if any(flags):
        return "partial"
    return "ok"


def _list_section_status(value: list) -> str | None:
    """Classify a list-valued section as ok/partial/failed, or None if it
    is not classifiable (its items are not dicts — e.g. a bare
    ticker-string list, which stays outside the ok/failed vocabulary
    entirely). An empty list from a known ticker-fan-out pack is itself a
    failure signal: zero entries for a requested batch means nothing came
    back, not "nothing to report"."""
    if not value:
        return "failed"
    dict_items = [item for item in value if isinstance(item, dict)]
    if not dict_items:
        return None
    statuses = [_dict_section_status(item) for item in dict_items]
    if all(s == "failed" for s in statuses):
        return "failed"
    if any(s != "ok" for s in statuses):
        return "partial"
    return "ok"


def _section_status(value: object) -> str | None:
    """Classify one top-level result key as ok/partial/failed, or None if
    it is not a classifiable section at all — a plain scalar, a list of
    non-dict items, or a dict that is completely empty (zero keys carries
    no directly-checkable signal on its own; see LOOM-SIMPLIFY below)."""
    if isinstance(value, dict):
        if not value:
            return None
        return _dict_section_status(value)
    if isinstance(value, list):
        return _list_section_status(value)
    return None


def _classify_result(result: dict) -> tuple[str, list[str]]:
    """Classify a build_pack() result into (status, failed_sections).

    Walks exactly ONE level into each top-level section: a direct
    "error"/"_error" key is immediate failure (as before); a dict section
    whose own dict-valued sub-fields ALL carry that marker is also failed
    (SOME-but-not-all contributes "partial"); a list section (e.g. jp/cn's
    "tickers", which is a list of per-ticker dicts) gets the identical
    one-level treatment per item. failed_sections lists every section that
    is not fully "ok" (failed OR partial).

    LOOM-SIMPLIFY: one-level-deep dict/list section walk | ceiling: (a) a
    failure nested TWO OR MORE levels below a section (source -> field ->
    subfield carrying "_error", e.g. mops.balance_sheet.rows.assets._error)
    stays invisible to this classifier — the whole-pack `_partial: true`
    flag remains the only signal for that case; (b) a section that
    degrades to a completely empty dict (zero keys, e.g. a per-ticker
    "info" alias with nothing promoted into it) is excluded from
    classification entirely rather than read as a failure signal on its
    own — correctness for the 5 current market packs relies on a sibling
    section (their "tickers" list/dict view of the same fetch)
    independently carrying the signal | upgrade: general recursive
    per-source provenance walk once cross-market provenance normalization
    (T5+) gives every market the same section shape | ref:
    docs/loom/plans/2026-07-11-investing-toolkit-data-consolidation.md
    Task 4 round 2
    """
    # Only dict/list-valued top-level keys are even candidates for
    # classification — plain metadata fields (pack/country/ticker strings)
    # are neither ok nor failed, so they must not dilute the count.
    candidate_keys = [
        k for k in result
        if not k.startswith("_") and isinstance(result[k], (dict, list))
    ]
    statuses: dict[str, str] = {}
    for k in candidate_keys:
        status = _section_status(result[k])
        if status is not None:
            statuses[k] = status

    degraded = [k for k, s in statuses.items() if s != "ok"]

    if not degraded and ("error" in result or "_error" in result):
        # The whole result is itself one error envelope (no real sections
        # beneath it, or none of them independently signal failure) — e.g.
        # a market module's own unreachable/guard path.
        return "failed", list(statuses) or ["_root"]

    if statuses and all(s == "failed" for s in statuses.values()):
        return "failed", degraded

    if degraded:
        return "partial", degraded

    if result.get("_partial"):
        return "partial", ["_partial"]

    return "ok", []


def _status_block(
    status: str,
    market: str | None,
    pack: str | None,
    *,
    message: str | None = None,
    tb: str | None = None,
    failed_sections: list[str] | None = None,
    warnings: list[str] | None = None,
) -> dict:
    block: dict = {
        "status": status,
        "market": market,
        "pack": pack,
        "failed_sections": failed_sections or [],
        "warnings": warnings or [],
    }
    if message is not None:
        block["message"] = message
    if tb is not None:
        block["traceback"] = tb
    return block


def _emit(obj: dict) -> None:
    print(json.dumps(obj, indent=2, default=str))


def build_arg_parser() -> argparse.ArgumentParser:
    parser = _ArgumentParser(
        description="investing-toolkit unified data-markets pack facade",
    )
    parser.add_argument("--ticker", help="single ticker")
    parser.add_argument("--tickers", help="comma-separated ticker list")
    parser.add_argument("--pack", required=True, help="pack type to build")
    parser.add_argument(
        "--market",
        choices=sorted(MARKETS),
        help="override market auto-detection",
    )
    parser.add_argument(
        "--quiet", action="store_true", help="suppress progress stderr logging"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args: argparse.Namespace | None = None
    try:
        args = parser.parse_args(argv)
        tickers = _parse_tickers(args)
        market, warnings = _resolve_market(args.pack, tickers, args.market)
    except _UsageError as exc:
        pack_name = args.pack if args is not None else None
        _emit(
            {
                "_status": _status_block(
                    "usage_error", None, pack_name, message=str(exc)
                )
            }
        )
        return EXIT_USAGE_ERROR

    module = MARKET_MODULES[market]
    if args.quiet:
        module._QUIET = True  # noqa: SLF001 — shared CLI passthrough convention

    try:
        result = module.build_pack(args.pack, tickers)
    except ValueError as exc:
        _emit(
            {
                "_status": _status_block(
                    "usage_error", market, args.pack, message=str(exc), warnings=warnings
                )
            }
        )
        return EXIT_USAGE_ERROR
    except Exception:  # noqa: BLE001 — fail-loud: surface the full traceback, never swallow
        tb = traceback.format_exc()
        _emit(
            {
                "_status": _status_block(
                    "failed", market, args.pack, tb=tb, warnings=warnings
                )
            }
        )
        return EXIT_FAILED

    status, failed_sections = _classify_result(result)
    exit_code = {"ok": EXIT_OK, "partial": EXIT_PARTIAL, "failed": EXIT_FAILED}[status]

    output = dict(result)
    output["_status"] = _status_block(
        status,
        market,
        args.pack,
        failed_sections=failed_sections,
        warnings=warnings,
    )
    _emit(output)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

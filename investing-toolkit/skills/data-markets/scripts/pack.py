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
nested directly under a top-level section key); kr/tw fail via a
whole-pack top-level `_partial: true` flag with no per-section attribution
at the top level.

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


def _section_failed(value: object) -> bool:
    return isinstance(value, dict) and ("error" in value or "_error" in value)


def _classify_result(result: dict) -> tuple[str, list[str]]:
    """Classify a build_pack() result into (status, failed_sections).

    us/cn/jp dialect: each top-level section is itself a dict; a failed
    section carries "error" or "_error" directly. Section names in
    failed_sections come straight from these keys.

    kr/tw dialect: failures nest two levels deep (out[source][field] carries
    "_error"), invisible to a top-level-only scan; these markets instead
    set a whole-pack top-level `_partial: true` flag.

    LOOM-SIMPLIFY: shallow top-level-only detection | ceiling: a kr/tw pack
    where `_partial` is true and no top-level section independently trips
    the error check is reported as one synthetic "_partial" failed section
    rather than the true nested source name(s) | upgrade: walk one level
    into each section's sub-dict for the kr/tw dialect once cross-market
    provenance normalization (T5+) gives every market the same section
    shape | ref: docs/loom/plans/2026-07-11-investing-toolkit-data-consolidation.md Task 4
    """
    # Only dict-valued top-level keys are classifiable "sections" — plain
    # metadata fields (pack/country/ticker strings) are neither ok nor
    # failed, so they must not dilute the all-failed vs some-failed count.
    sections = [
        k for k in result if not k.startswith("_") and isinstance(result[k], dict)
    ]
    failed = [k for k in sections if _section_failed(result[k])]

    if not failed and ("error" in result or "_error" in result):
        # The whole result is itself one error envelope (no real sections
        # beneath it) — e.g. a market module's own unreachable/guard path.
        return "failed", sections or ["_root"]

    if failed:
        if sections and len(failed) == len(sections):
            return "failed", failed
        return "partial", failed

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

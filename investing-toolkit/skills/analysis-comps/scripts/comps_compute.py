#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Pure-compute peer multiples comparison (Comps Analysis).

Layer 2 (Analysis) under the v2.0.0 three-layer design:
- NO I/O: it does NOT fetch data from any network/file source other than
  the JSON paths supplied via --anchor and --peers.
- Caller (data-{country}/pack.py --pack comps-multiples) is responsible
  for pre-fetching multiples for both anchor and each peer ticker, and
  for shaping them into the input contract documented below.
- Peer-discovery (which tickers count as peers) is the report layer's
  job; this script trusts the supplied peer list verbatim.

Output: comps table JSON with median / mean / quartile statistics across
peers, anchor delta vs median + percentile, per-multiple and composite
rankings, and a no-I/O provenance stamp.

Input JSON contract (per --anchor and per --peers entry)
--------------------------------------------------------
{
  "pack": "comps-multiples",
  "ticker": "AAPL",                          # optional; falls back to single key under info{}
  "fetched_at": "2026-05-01T00:00:00Z",
  "info": {
    "AAPL": {
      "trailingPE":         28.5,
      "forwardPE":          25.1,
      "priceToSales":        7.2,
      "priceToBook":        35.4,
      "enterpriseToEbitda": 21.3              # OR "evEbitda" — both accepted
    }
  },
  "_provenance": { "skill": "data-us", ... }
}

Multiples set (Spec §5.3, classic 5)
------------------------------------
- trailingPE
- forwardPE
- evEbitda      (input alias enterpriseToEbitda accepted)
- priceToSales
- priceToBook
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

# Canonical output multiple names (Spec §5.3)
MULTIPLES = ["trailingPE", "forwardPE", "evEbitda", "priceToSales", "priceToBook"]

# Accept yfinance's "enterpriseToEbitda" as an alias for "evEbitda"
ALIASES = {
    "evEbitda": ["evEbitda", "enterpriseToEbitda"],
    "trailingPE": ["trailingPE"],
    "forwardPE": ["forwardPE"],
    "priceToSales": ["priceToSales"],
    "priceToBook": ["priceToBook"],
}

DIVERGENCE_BAND_LOW  = 0.05   # 5%   — boundary inclusive (≤ low)
DIVERGENCE_BAND_HIGH = 0.15   # 15%  — boundary inclusive for medium (high band is strict >)

# Multiples currently deferred to v2.2.0-l (memo-fetch lacks the raw fields):
#   priceToBook  → needs total_stockholders_equity
#   evEbitda     → needs depreciation_amortization
DEFERRED_MULTIPLES = ("priceToBook", "evEbitda")


def _load_pack(path: Path) -> dict:
    """Load a comps-multiples pack JSON. No network access."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _load_memo_fetch_pack(path: Path, expected_ticker: str) -> dict:
    """Load and validate a memo-fetch pack. Layer-1 input contract — no I/O beyond this read."""
    with path.open("r", encoding="utf-8") as f:
        pack = json.load(f)
    if pack.get("pack") != "memo-fetch":
        raise ValueError(
            f"--anchor-base must be a memo-fetch pack; got pack={pack.get('pack')!r}"
        )
    if pack.get("ticker") != expected_ticker:
        raise ValueError(
            f"--anchor-base ticker {pack.get('ticker')!r} does not match "
            f"--anchor ticker {expected_ticker!r}"
        )
    return pack


def _resolve_ticker(pack: dict, fallback: str) -> str:
    """Find the ticker symbol used as the info{} key."""
    if isinstance(pack.get("ticker"), str) and pack["ticker"]:
        return pack["ticker"]
    info = pack.get("info") or {}
    if len(info) == 1:
        return next(iter(info.keys()))
    # Last resort: derive from filename
    return fallback


def _extract_multiples(pack: dict, ticker: str) -> dict:
    """Pull the 5 canonical multiples out of pack.info[ticker], normalising aliases.
    Missing values become None.
    """
    info = (pack.get("info") or {}).get(ticker) or {}
    out: dict[str, float | None] = {}
    for canonical, aliases in ALIASES.items():
        value = None
        for alias in aliases:
            if alias in info and info[alias] is not None:
                try:
                    value = float(info[alias])
                except (TypeError, ValueError):
                    value = None
                break
        out[canonical] = value
    return out


def _safe_first(arr, default=None):
    """First element of a list, or default if empty/non-list."""
    return arr[0] if isinstance(arr, list) and arr else default


def _compute_multiples_from_memo_fetch(memo_fetch: dict, direct_multiples: dict) -> tuple[dict, dict, list[str]]:
    """Recompute the 5 canonical multiples from a memo-fetch pack.

    Returns (multiples_compute, compute_provenance, warnings).
    Layer 2 derived metrics: trailingPE / priceToSales / forwardPE pass-through;
    priceToBook + evEbitda deferred to v2.2.0-l with explicit null + note.
    """
    warnings: list[str] = [
        "trailingPE compute uses latest FY (not TTM); systematic divergence vs yfinance TTM expected during fiscal year"
    ]
    out_compute: dict[str, float | None] = {}
    out_prov: dict[str, dict] = {}

    # Inputs
    inc = memo_fetch.get("income_statement") or {}
    ci = memo_fetch.get("company_info") or {}
    price = memo_fetch.get("current_price")
    if price is None:
        price = ci.get("regularMarketPrice")
    shares = memo_fetch.get("shares_outstanding")
    if shares is None:
        shares = ci.get("sharesOutstanding")
    market_cap = ci.get("marketCap")

    revenue_fy = _safe_first(inc.get("revenue"))
    net_income_fy = _safe_first(inc.get("net_income"))

    fy_end = _safe_first(((inc.get("_meta") or {}).get("fiscal_year_ends") or []))
    filings = ((inc.get("_meta") or {}).get("filings_used") or [])

    # trailingPE (FY)
    if price is None or net_income_fy is None or not shares:
        out_compute["trailingPE"] = None
        out_prov["trailingPE"] = {
            "computed": False,
            "note": "compute skipped — current_price / net_income[0] / shares_outstanding required",
        }
        if price is None:
            warnings.append("price-based compute skipped: current_price missing")
        elif net_income_fy is None:
            warnings.append("trailingPE compute skipped: net_income FY array empty")
        elif not shares:
            warnings.append("trailingPE compute skipped: shares_outstanding missing")
    else:
        eps_fy = net_income_fy / shares
        out_compute["trailingPE"] = price / eps_fy if eps_fy != 0 else None
        out_prov["trailingPE"] = {
            "numerator_source":   "memo-fetch.current_price",
            "denominator_source": "memo-fetch.income_statement.net_income[0] / memo-fetch.shares_outstanding",
            "accession_basis":    [filings[0]] if filings else [],
            "fiscal_year_end":    fy_end,
            "computed":           True,
            "note":               "FY-trailing, not TTM — see ROADMAP §v2.2.0-b §7.3",
        }

    # priceToSales (FY)
    if market_cap is None or revenue_fy is None:
        out_compute["priceToSales"] = None
        out_prov["priceToSales"] = {
            "computed": False,
            "note": "compute skipped — marketCap / revenue[0] required",
        }
        if market_cap is None:
            warnings.append("priceToSales compute skipped: marketCap missing")
        elif revenue_fy is None:
            warnings.append("priceToSales compute skipped: revenue FY array empty")
    else:
        out_compute["priceToSales"] = market_cap / revenue_fy
        out_prov["priceToSales"] = {
            "numerator_source":   "memo-fetch.company_info.marketCap",
            "denominator_source": "memo-fetch.income_statement.revenue[0]",
            "accession_basis":    [filings[0]] if filings else [],
            "fiscal_year_end":    fy_end,
            "computed":           True,
        }

    # forwardPE pass-through
    out_compute["forwardPE"] = direct_multiples.get("forwardPE")
    out_prov["forwardPE"] = {
        "computed": False,
        "note": "pass-through from comps-multiples pack (consensus EPS has no primary source)",
    }

    # Deferred multiples (v2.2.0-l)
    for m in DEFERRED_MULTIPLES:
        out_compute[m] = None
        out_prov[m] = {
            "computed": False,
            "note": (
                "deferred to v2.2.0-l (memo-fetch missing total_stockholders_equity)"
                if m == "priceToBook" else
                "deferred to v2.2.0-l (memo-fetch missing depreciation_amortization)"
            ),
        }

    return out_compute, out_prov, warnings


def _classify_divergence_alert(pct_diff: float) -> str:
    """Map |pct_diff| (in %) onto low/medium/high band per divergence-thresholds.md."""
    abs_pct = abs(pct_diff)
    if abs_pct <= DIVERGENCE_BAND_LOW * 100:
        return "low"
    if abs_pct <= DIVERGENCE_BAND_HIGH * 100:
        return "medium"
    return "high"


def _compute_divergence(direct: dict, compute: dict, prov: dict) -> dict[str, dict]:
    """For each multiple, compute abs/pct diff between direct and compute, classify alert.
    Null in either side → alert n/a with note from compute_provenance.
    """
    out: dict[str, dict] = {}
    for m in MULTIPLES:
        d_val = direct.get(m)
        c_val = compute.get(m)
        if d_val is None or c_val is None:
            note = (prov.get(m) or {}).get("note") or "compute null; cannot diff"
            out[m] = {"abs_diff": None, "pct_diff": None, "alert": "n/a", "note": note}
            continue
        abs_diff = c_val - d_val
        if d_val == 0:
            out[m] = {"abs_diff": abs_diff, "pct_diff": None, "alert": "n/a", "note": "direct value zero — pct_diff undefined"}
            continue
        pct_diff = (abs_diff / d_val) * 100.0
        # forwardPE is pass-through → c_val == d_val → pct_diff == 0; surface as n/a
        if m == "forwardPE":
            out[m] = {"abs_diff": 0.0, "pct_diff": 0.0, "alert": "n/a", "note": "pass-through"}
            continue
        out[m] = {
            "abs_diff": abs_diff,
            "pct_diff": pct_diff,
            "alert":    _classify_divergence_alert(pct_diff),
        }
    return out


def _provenance_label(pack: dict, fallback_path: Path) -> str:
    prov = pack.get("_provenance") or {}
    skill = prov.get("skill")
    source = prov.get("source")
    if skill and source:
        return f"{skill}/{source}"
    if skill:
        # Match the spec's documented label for data-{country} packs
        return f"{skill}/pack.py --pack comps-multiples"
    return str(fallback_path)


def _percentiles(values: list[float]) -> tuple[float, float]:
    """Return (q1, q3) = (25th pct, 75th pct), empirical / linear interpolation.
    statistics.quantiles requires n>=2; for n<2 fall back to the value itself.
    """
    if len(values) < 2:
        v = values[0] if values else 0.0
        return (v, v)
    qs = statistics.quantiles(values, n=4, method="inclusive")
    # qs == [q1, q2, q3]
    return (qs[0], qs[2])


def _empirical_percentile(value: float, all_values: list[float]) -> float:
    """Empirical percentile of `value` within `all_values` (inclusive of value).
    Returns a fraction in [0, 1]: (#values <= value) / n.
    Ties give the upper rank (standard 'weak' percentile).
    """
    if not all_values:
        return 0.5
    leq = sum(1 for v in all_values if v <= value)
    return leq / len(all_values)


def _stat_block(peer_values: list[float], anchor_value: float | None) -> dict:
    """Statistics across peers (anchor excluded). Peer values are filtered of None
    upstream. anchor_value is for the empty-peers fallback only.
    """
    n = len(peer_values)
    if n == 0:
        # Empty-peers fallback per skill spec edge case.
        v = anchor_value if anchor_value is not None else 0.0
        return {
            "median": v, "mean": v, "q1": v, "q3": v, "min": v, "max": v, "n": 0,
        }
    q1, q3 = _percentiles(peer_values)
    return {
        "median": statistics.median(peer_values),
        "mean":   statistics.fmean(peer_values),
        "q1":     q1,
        "q3":     q3,
        "min":    min(peer_values),
        "max":    max(peer_values),
        "n":      n,
    }


def _anchor_delta(anchor_value: float | None, peer_values: list[float]) -> dict | None:
    if anchor_value is None:
        return None
    if not peer_values:
        # Empty-peers fallback per skill spec.
        return {"value": anchor_value, "vs_median_pct": 0.0, "percentile": 0.5}
    median = statistics.median(peer_values)
    if median == 0:
        vs_median_pct = 0.0
    else:
        vs_median_pct = ((anchor_value - median) / median) * 100.0
    pct = _empirical_percentile(anchor_value, peer_values + [anchor_value])
    return {
        "value":         anchor_value,
        "vs_median_pct": vs_median_pct,
        "percentile":    pct,
    }


def _rank_ascending(pairs: list[tuple[str, float]]) -> dict[str, int]:
    """Rank tickers ascending by value (lowest = rank 1).
    Ties receive the same rank (competition / min ranking: e.g. values
    [10, 20, 20, 30] → ranks [1, 2, 2, 4] — not dense [1, 2, 2, 3]).
    """
    sorted_pairs = sorted(pairs, key=lambda kv: kv[1])
    ranks: dict[str, int] = {}
    last_value = None
    last_rank = 0
    for idx, (ticker, value) in enumerate(sorted_pairs, start=1):
        if last_value is not None and value == last_value:
            ranks[ticker] = last_rank
        else:
            ranks[ticker] = idx
            last_rank = idx
            last_value = value
    return ranks


def _build_ranking(
    anchor_ticker: str,
    anchor_multiples: dict,
    peers: list[dict],
) -> list[dict]:
    """Per-multiple ranks + composite rank for anchor + peers.
    peers: list of {"ticker": str, "multiples": dict, "rationale": str|None}
    """
    all_entries: list[tuple[str, dict]] = [(anchor_ticker, anchor_multiples)]
    all_entries.extend((p["ticker"], p["multiples"]) for p in peers)

    per_multiple_ranks: dict[str, dict[str, int | None]] = {m: {} for m in MULTIPLES}
    for m in MULTIPLES:
        valid = [(t, mults[m]) for t, mults in all_entries if mults.get(m) is not None]
        ranks = _rank_ascending(valid)
        for t, _mults in all_entries:
            per_multiple_ranks[m][t] = ranks.get(t)  # None if missing

    ranking: list[dict] = []
    for ticker, _mults in all_entries:
        rank_values = [
            per_multiple_ranks[m][ticker]
            for m in MULTIPLES
            if per_multiple_ranks[m][ticker] is not None
        ]
        if rank_values:
            composite = sum(rank_values) / len(rank_values)
        else:
            composite = float("inf")  # sorts last; no usable multiples
        entry: dict = {"ticker": ticker, "composite_rank_avg": composite}
        for m in MULTIPLES:
            entry[f"{m}_rank"] = per_multiple_ranks[m][ticker]
        ranking.append(entry)

    # Sort ascending by composite_rank_avg, then assign final composite_rank (1..N).
    ranking.sort(key=lambda r: r["composite_rank_avg"])
    for idx, entry in enumerate(ranking, start=1):
        entry["composite_rank"] = idx
    # Reorder fields so composite_rank comes second after ticker (cleaner JSON).
    cleaned: list[dict] = []
    for entry in ranking:
        ordered = {
            "ticker": entry["ticker"],
            "composite_rank": entry["composite_rank"],
            "composite_rank_avg": round(entry["composite_rank_avg"], 4)
                if entry["composite_rank_avg"] != float("inf") else None,
        }
        for m in MULTIPLES:
            ordered[f"{m}_rank"] = entry[f"{m}_rank"]
        cleaned.append(ordered)
    return cleaned


def _parse_peer_paths(arg: str) -> list[Path]:
    paths = [Path(p.strip()) for p in arg.split(",") if p.strip()]
    if not paths:
        raise ValueError("--peers must contain at least one path")
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Pure-compute peer multiples comparison (Layer 2)."
    )
    parser.add_argument(
        "--anchor", required=True, type=Path,
        help="Path to anchor ticker's comps-multiples pack JSON",
    )
    parser.add_argument(
        "--peers", required=True, type=str,
        help="Comma-separated peer comps-multiples pack JSON paths",
    )
    parser.add_argument(
        "--mode", choices=["direct", "compute"], default="direct",
        help="direct = use multiples in JSON (v2.0.0 only mode); compute = recompute from base financials (v2.1+ placeholder)",
    )
    parser.add_argument(
        "--rationale-map", type=Path, default=None,
        help="Optional JSON file mapping ticker -> rationale string",
    )
    parser.add_argument(
        "--anchor-base", type=Path, default=None,
        help="Path to anchor's memo-fetch pack JSON (REQUIRED for --mode compute)",
    )
    args = parser.parse_args()

    # Validate compute-mode arg shape early.
    if args.mode == "compute" and args.anchor_base is None:
        parser.error("--mode compute requires --anchor-base")
    if args.mode == "direct" and args.anchor_base is not None:
        sys.stderr.write(
            "[analysis-comps WARN] --anchor-base ignored in --mode direct\n"
        )

    warnings: list[str] = []

    requested_mode = args.mode
    effective_mode = args.mode

    # Load anchor
    anchor_pack = _load_pack(args.anchor)
    anchor_ticker = _resolve_ticker(anchor_pack, fallback=args.anchor.stem.upper())
    anchor_multiples = _extract_multiples(anchor_pack, anchor_ticker)
    anchor_source = _provenance_label(anchor_pack, args.anchor)

    # Compute mode: load + validate memo-fetch pack
    anchor_base = None
    if effective_mode == "compute":
        try:
            anchor_base = _load_memo_fetch_pack(args.anchor_base, anchor_ticker)
        except (json.JSONDecodeError, ValueError) as exc:
            sys.stderr.write(f"[analysis-comps ERROR] {exc}\n")
            return 1

    # Load peers
    peer_paths = _parse_peer_paths(args.peers)
    peer_packs: list[tuple[str, dict, str]] = []  # (ticker, multiples, source_label)
    for p in peer_paths:
        pack = _load_pack(p)
        ticker = _resolve_ticker(pack, fallback=p.stem.upper())
        if ticker == anchor_ticker:
            warnings.append(f"Peer file {p} resolves to anchor ticker {ticker}; skipped")
            continue
        mults = _extract_multiples(pack, ticker)
        peer_packs.append((ticker, mults, _provenance_label(pack, p)))

    if not peer_packs:
        warnings.append("No peers supplied or all peers de-duplicated against anchor; statistics use anchor-only fallback")

    # Optional rationale map
    rationale_map: dict[str, str | None] = {}
    if args.rationale_map is not None:
        try:
            with args.rationale_map.open("r", encoding="utf-8") as f:
                rationale_map = json.load(f)
            if not isinstance(rationale_map, dict):
                warnings.append(f"--rationale-map {args.rationale_map} is not a JSON object; ignored")
                rationale_map = {}
        except (OSError, json.JSONDecodeError) as exc:
            warnings.append(f"--rationale-map {args.rationale_map} unreadable ({exc}); ignored")
            rationale_map = {}

    # Build peers payload
    peers_out: list[dict] = []
    for ticker, mults, _src in peer_packs:
        peers_out.append({
            "ticker": ticker,
            "multiples": mults,
            "rationale": rationale_map.get(ticker),
        })

    # Statistics + anchor delta per multiple (peers only for stats, anchor excluded)
    stats: dict[str, dict] = {}
    anchor_delta: dict[str, dict | None] = {}
    for m in MULTIPLES:
        peer_values = [
            mults[m] for _t, mults, _s in peer_packs if mults.get(m) is not None
        ]
        stats[m] = _stat_block(peer_values, anchor_multiples.get(m))
        anchor_delta[m] = _anchor_delta(anchor_multiples.get(m), peer_values)

    # Ranking across anchor + peers
    ranking = _build_ranking(anchor_ticker, anchor_multiples, peers_out)

    anchor_block: dict = {
        "ticker": anchor_ticker,
        "multiples_direct": anchor_multiples,
    }
    if effective_mode == "compute":
        multiples_compute, compute_provenance, compute_warnings = (
            _compute_multiples_from_memo_fetch(anchor_base, anchor_multiples)
        )
        warnings.extend(compute_warnings)
        divergence = _compute_divergence(anchor_multiples, multiples_compute, compute_provenance)
        anchor_block["multiples_compute"] = multiples_compute
        anchor_block["divergence"] = divergence
        anchor_block["compute_provenance"] = compute_provenance

    payload = {
        "anchor": anchor_block,
        "peers": peers_out,
        "statistics": stats,
        "anchor_delta": anchor_delta,
        "ranking": ranking,
        "_provenance": {
            "skill":              "analysis-comps",
            "anchor_data_source": anchor_source,
            **(
                {"anchor_base_source": _provenance_label(anchor_base, args.anchor_base)}
                if effective_mode == "compute" else {}
            ),
            "peer_data_sources":  [src for _t, _m, src in peer_packs],
            "computed_at":        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "io":                 "none",
            "mode":               effective_mode,
            "requested_mode":     requested_mode,
            "warnings":           warnings,
        },
    }

    json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

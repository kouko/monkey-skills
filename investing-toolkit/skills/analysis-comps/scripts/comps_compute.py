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


def _load_pack(path: Path) -> dict:
    """Load a comps-multiples pack JSON. No network access."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


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
    args = parser.parse_args()

    warnings: list[str] = []

    # v2.0.0: only --mode direct is wired; --mode compute is a placeholder.
    # If a caller explicitly requests compute, warn loudly on stderr, fall
    # back to direct, and stamp both the actual mode and the requested mode
    # in _provenance so the audit trail survives the fallback.
    requested_mode = args.mode
    effective_mode = args.mode
    if requested_mode == "compute":
        sys.stderr.write(
            "[analysis-comps WARN] --mode compute not yet implemented in "
            "v2.0.0; falling back to direct mode\n"
        )
        effective_mode = "direct"

    # Load anchor
    anchor_pack = _load_pack(args.anchor)
    anchor_ticker = _resolve_ticker(anchor_pack, fallback=args.anchor.stem.upper())
    anchor_multiples = _extract_multiples(anchor_pack, anchor_ticker)
    anchor_source = _provenance_label(anchor_pack, args.anchor)

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

    payload = {
        "anchor": {
            "ticker": anchor_ticker,
            "multiples_direct": anchor_multiples,
        },
        "peers": peers_out,
        "statistics": stats,
        "anchor_delta": anchor_delta,
        "ranking": ranking,
        "_provenance": {
            "skill":              "analysis-comps",
            "anchor_data_source": anchor_source,
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

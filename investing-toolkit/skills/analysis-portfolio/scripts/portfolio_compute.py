#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
analysis-portfolio — pure compute.

Input:
    --holdings <path>  CSV or JSON: {ticker, quantity, cost_basis [, purchase_date]}
    --prices   <path>  JSON: list of {ticker, price} OR object {ticker: price}
                       OR screener-batch records with regularMarketPrice/last_price

Output: JSON {positions, totals, _provenance} on stdout.

All ratio fields (pnl_ratio, total_pnl_ratio, weight, contribution, max_weight)
are fractional (0.0–1.0). e.g. pnl_ratio=0.4033 means +40.33%.

NO network I/O. NO macro overlay. NO rebalance logic.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# --------------------------------------------------------------------------- #
# Loaders                                                                     #
# --------------------------------------------------------------------------- #


def load_holdings(path: Path) -> list[dict[str, Any]]:
    """Load holdings from CSV or JSON. Returns list of dicts with normalized keys."""
    suffix = path.suffix.lower()
    rows: list[dict[str, Any]] = []

    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "holdings" in data:
            data = data["holdings"]
        if not isinstance(data, list):
            raise ValueError(
                f"holdings JSON must be a list (or object with 'holdings' key); got {type(data).__name__}"
            )
        for r in data:
            rows.append(_normalize_holding_row(r))
    elif suffix in (".csv", ".tsv", ".txt"):
        delimiter = "\t" if suffix == ".tsv" else ","
        with path.open(encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh, delimiter=delimiter)
            for r in reader:
                rows.append(_normalize_holding_row(r))
    else:
        # Best-effort sniff: try JSON first, fall back to CSV
        text = path.read_text(encoding="utf-8").lstrip()
        if text.startswith("[") or text.startswith("{"):
            data = json.loads(text)
            if isinstance(data, dict) and "holdings" in data:
                data = data["holdings"]
            for r in data:
                rows.append(_normalize_holding_row(r))
        else:
            with path.open(encoding="utf-8", newline="") as fh:
                reader = csv.DictReader(fh)
                for r in reader:
                    rows.append(_normalize_holding_row(r))

    if not rows:
        raise ValueError(f"No holdings rows parsed from {path}")
    return rows


def _normalize_holding_row(raw: dict[str, Any]) -> dict[str, Any]:
    """Lowercase keys, coerce numeric fields, accept aliases."""
    r = {k.strip().lower(): v for k, v in raw.items()}
    ticker = r.get("ticker") or r.get("symbol")
    if not ticker:
        raise ValueError(f"holdings row missing 'ticker': {raw}")
    quantity = r.get("quantity") if r.get("quantity") is not None else r.get("shares")
    cost_basis = (
        r.get("cost_basis")
        if r.get("cost_basis") is not None
        else r.get("avg_cost") if r.get("avg_cost") is not None else r.get("cost")
    )
    if quantity is None or cost_basis is None:
        raise ValueError(f"holdings row missing quantity/cost_basis: {raw}")
    out = {
        "ticker": str(ticker).strip(),
        "quantity": float(quantity),
        "cost_basis": float(cost_basis),
    }
    purchase_date = r.get("purchase_date") or r.get("acquired_at")
    if purchase_date:
        out["purchase_date"] = str(purchase_date).strip()
    return out


def load_prices(path: Path) -> dict[str, float]:
    """Load prices into {ticker: price}."""
    data = json.loads(path.read_text(encoding="utf-8"))
    prices: dict[str, float] = {}

    if isinstance(data, dict):
        # Could be {ticker: price} OR a wrapper like {"prices": [...]} OR a single record
        if "prices" in data and isinstance(data["prices"], list):
            data = data["prices"]
        elif "data" in data and isinstance(data["data"], list):
            data = data["data"]
        elif "ticker" in data:
            data = [data]
        else:
            # Treat as flat ticker->price map
            for k, v in data.items():
                price = _extract_price(v) if isinstance(v, dict) else v
                if price is not None:
                    prices[str(k).strip()] = float(price)
            return prices

    if isinstance(data, list):
        for r in data:
            if not isinstance(r, dict):
                continue
            ticker = r.get("ticker") or r.get("symbol")
            if not ticker:
                continue
            price = _extract_price(r)
            if price is not None:
                prices[str(ticker).strip()] = float(price)

    return prices


def _extract_price(record: dict[str, Any]) -> float | None:
    """Pull the most-likely price field out of a record."""
    for key in (
        "price",
        "current_price",
        "regularMarketPrice",
        "last_price",
        "close",
        "Close",
    ):
        if key in record and record[key] is not None:
            try:
                return float(record[key])
            except (TypeError, ValueError):
                continue
    return None


# --------------------------------------------------------------------------- #
# Compute                                                                     #
# --------------------------------------------------------------------------- #


def compute_portfolio(
    holdings: list[dict[str, Any]], prices: dict[str, float]
) -> dict[str, Any]:
    positions: list[dict[str, Any]] = []
    missing: list[str] = []

    # First pass — resolve prices, drop missing
    resolved: list[dict[str, Any]] = []
    for h in holdings:
        ticker = h["ticker"]
        price = prices.get(ticker)
        if price is None:
            missing.append(ticker)
            continue
        market_value = h["quantity"] * price
        cost = h["quantity"] * h["cost_basis"]
        pnl_abs = market_value - cost
        pnl_ratio = (pnl_abs / cost) if cost else 0.0
        resolved.append(
            {
                **h,
                "current_price": price,
                "_market_value": market_value,
                "_cost": cost,
                "_pnl_abs": pnl_abs,
                "_pnl_ratio": pnl_ratio,
            }
        )

    total_cost = sum(p["_cost"] for p in resolved)
    total_mv = sum(p["_market_value"] for p in resolved)
    total_pnl_abs = total_mv - total_cost
    total_pnl_ratio = (total_pnl_abs / total_cost) if total_cost else 0.0

    for p in resolved:
        weight = (p["_market_value"] / total_mv) if total_mv else 0.0
        contribution = (p["_pnl_abs"] / total_cost) if total_cost else 0.0
        position = {
            "ticker": p["ticker"],
            "quantity": p["quantity"],
            "cost_basis": p["cost_basis"],
            "current_price": p["current_price"],
            "market_value": round(p["_market_value"], 4),
            "pnl_abs": round(p["_pnl_abs"], 4),
            "pnl_ratio": round(p["_pnl_ratio"], 6),  # fractional (0.0–1.0); 0.4033 = +40.33%
            "weight": round(weight, 6),
            "contribution": round(contribution, 6),
        }
        if "purchase_date" in p:
            position["purchase_date"] = p["purchase_date"]
        positions.append(position)

    # Sort positions by descending weight for stable, useful output ordering
    positions.sort(key=lambda x: x["weight"], reverse=True)

    max_weight_pos = positions[0] if positions else None
    totals = {
        "total_cost": round(total_cost, 4),
        "total_market_value": round(total_mv, 4),
        "total_pnl_abs": round(total_pnl_abs, 4),
        "total_pnl_ratio": round(total_pnl_ratio, 6),
        "position_count": len(positions),
        "max_weight": round(max_weight_pos["weight"], 6) if max_weight_pos else 0.0,
        "max_weight_ticker": max_weight_pos["ticker"] if max_weight_pos else None,
    }

    return {"positions": positions, "totals": totals, "missing_prices": missing}


# --------------------------------------------------------------------------- #
# CLI                                                                         #
# --------------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="analysis-portfolio — pure compute portfolio P&L + holdings stats"
    )
    parser.add_argument(
        "--holdings", required=True, help="Path to holdings file (CSV or JSON)"
    )
    parser.add_argument(
        "--prices", required=True, help="Path to prices JSON (list or object)"
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indent for output (default: 2; use 0 for compact)",
    )
    args = parser.parse_args(argv)

    holdings_path = Path(args.holdings)
    prices_path = Path(args.prices)

    if not holdings_path.exists():
        print(f"error: holdings file not found: {holdings_path}", file=sys.stderr)
        return 2
    if not prices_path.exists():
        print(f"error: prices file not found: {prices_path}", file=sys.stderr)
        return 2

    try:
        holdings = load_holdings(holdings_path)
        prices = load_prices(prices_path)
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result = compute_portfolio(holdings, prices)

    output = {
        "positions": result["positions"],
        "totals": result["totals"],
        "_provenance": {
            "skill": "analysis-portfolio",
            "computed_at": datetime.now(timezone.utc).isoformat(),
            "holdings_path": str(holdings_path),
            "prices_path": str(prices_path),
            "missing_prices": result["missing_prices"],
        },
    }

    indent = args.indent if args.indent > 0 else None
    print(json.dumps(output, indent=indent, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

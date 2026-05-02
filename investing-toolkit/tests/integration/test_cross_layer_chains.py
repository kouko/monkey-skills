"""Cross-layer integration tests — Layer 1 → Layer 2 chain wiring.

These tests verify that data-{country}/pack.py output (Layer 1) can be
consumed directly by analysis-*/scripts/*.py (Layer 2) WITHOUT
caller-side shape adaptation.

Goal of this file:
- Surface chains where Layer 1 emission shape does NOT match Layer 2 input
  expectation. Such chains either crash, produce silently-degenerate output
  (all-None / all-zero), or quietly drop data — all of which are bugs the
  v2.0.1 schema work did NOT catch (schemas validate Layer 1 self-shape,
  not cross-layer contract).
- Use the bundled fixtures at `tests/data/fixtures/data-us-*.json` so these
  tests are offline + deterministic.

Pattern per test:
1. Read a Layer 1 fixture (no network).
2. Subprocess-invoke the Layer 2 script with the fixture as --input.
3. Parse stdout JSON.
4. Assert the Layer 2 output has non-degenerate values (real numbers,
   not all None, not all 0).

## xfail markers — current status of cross-layer chains

Per ADR-0002 (Layer 1 staging-tier normalization), 4 of 5 chains are
known-broken on main as of 2026-05-02. They carry pytest xfail markers
referencing the planned fix PR. Each fix PR's success criterion is
removing the corresponding xfail marker AND the test passing.

| Chain | Status     | Fix PR                              |
|-------|------------|-------------------------------------|
|   1   | xfail      | PR #178 — Tier 1 (OHLCV alias)      |
|   2   | xfail      | PR #180 — Tier 3 (XBRL → flat)      |
|   3   | xfail      | PR #178 — Tier 1 (Multiples rename) |
|   4   | passing    | n/a — Layer 1 emit already matches  |
|   5   | xfail      | PR #179 — Tier 2 (groups flatten)   |

If an xfail test unexpectedly passes (XPASS), pytest fails the run with
strict=True — that signals an undocumented chain fix and the marker
should be removed in the same PR that fixed it.

See `docs/normalization-contract.md` and `docs/adr/0002-layer-1-staging-
tier-normalization.md` for the contract these tests enforce.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "skills"
FIXTURES = ROOT / "tests" / "data" / "fixtures"


def _run_layer2(script: Path, args: list[str]) -> tuple[int, dict, str]:
    """Run a Layer 2 script and return (exit_code, parsed_stdout, stderr)."""
    proc = subprocess.run(
        ["uv", "run", str(script), *args],
        capture_output=True,
        text=True,
        timeout=60,
    )
    try:
        payload = json.loads(proc.stdout) if proc.stdout.strip() else {}
    except json.JSONDecodeError:
        payload = {"_unparseable_stdout": proc.stdout[:500]}
    return proc.returncode, payload, proc.stderr


# ---------------------------------------------------------------------------
# Chain 1: data-us snapshot → analysis-technical
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    strict=True,
    reason="Chain 1 broken: snapshot emits price_history.data (nested), "
           "ta_compute reads top-level history/data. Fix in PR #178 (Tier 1 "
           "OHLCV canonical alias per docs/normalization-contract.md).",
)
def test_chain_snapshot_to_technical():
    """data-us snapshot pack feeds analysis-technical without adapter.

    Expected current state: BROKEN — ta_compute reads top-level `history`
    or `data`, but data-us snapshot emits `price_history.data` (nested).
    """
    fixture = FIXTURES / "data-us-snapshot-sample.json"
    script = SKILLS / "analysis-technical" / "scripts" / "ta_compute.py"
    if not fixture.exists() or not script.exists():
        pytest.skip("missing fixture or script")

    rc, out, stderr = _run_layer2(script, ["--input", str(fixture)])

    assert rc == 0, f"exit {rc}\nstderr: {stderr}\nstdout: {out}"
    assert "error" not in out, (
        f"ta_compute reported error: {out.get('error')!r} — "
        f"shape mismatch likely (snapshot emits price_history.data nested, "
        f"ta_compute expects top-level history/data)"
    )
    indicators = out.get("indicators") or {}
    assert indicators.get("rsi_14") is not None, (
        f"RSI not computed; indicators: {indicators}"
    )
    sma = indicators.get("sma") or {}
    assert sma.get("200") is not None, f"SMA-200 not computed; sma: {sma}"


# ---------------------------------------------------------------------------
# Chain 2: data-us memo-fetch → analysis-dcf
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    strict=True,
    reason="Chain 2 broken: memo-fetch emits sec_facts (raw XBRL), dcf_compute "
           "reads top-level income_statement/cash_flow/balance_sheet (flat). "
           "Fix in PR #180 (Tier 3 financial statement normalization with "
           "country-specific XBRL/EDINET/MOPS concept mapping; requires its "
           "own ADR per docs/normalization-contract.md).",
)
def test_chain_memofetch_to_dcf():
    """data-us memo-fetch pack feeds analysis-dcf without adapter.

    Expected current state: BROKEN — analysis-dcf reads top-level
    `income_statement / cash_flow / balance_sheet / shares_outstanding /
    current_price` (per its SKILL.md Input Contract), but memo-fetch
    emits `sec_facts` (raw XBRL companyfacts, deeply nested) with NO
    top-level normalised flat statements. SKILL.md claims memo-fetch
    'normalises into this contract' but pack.py:177 does no such normalize.
    """
    fixture = FIXTURES / "data-us-memo-fetch-sample.json"
    script = SKILLS / "analysis-dcf" / "scripts" / "dcf_compute.py"
    if not fixture.exists() or not script.exists():
        pytest.skip("missing fixture or script")

    rc, out, stderr = _run_layer2(script, ["--input", str(fixture)])

    # DCF may not crash — it may silently produce zero/None values.
    # The real test: did it derive anything sensible from the input?
    valuation = out.get("valuation") or {}
    intrinsic = valuation.get("intrinsic_value_per_share")
    revenue_cagr = (out.get("assumptions") or {}).get("revenue_cagr")

    assert rc == 0, f"exit {rc}\nstderr: {stderr}"
    assert intrinsic is not None and intrinsic > 0, (
        f"DCF produced degenerate intrinsic value {intrinsic!r} — likely "
        f"because dcf_compute could not find income_statement/cash_flow/"
        f"balance_sheet at top level (memo-fetch puts them under sec_facts)."
    )
    assert revenue_cagr is not None and revenue_cagr != 0, (
        f"DCF produced degenerate revenue CAGR {revenue_cagr!r}"
    )


# ---------------------------------------------------------------------------
# Chain 3: data-us comps-multiples → analysis-comps
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    strict=True,
    reason="Chain 3 broken (silent corruption): comps-multiples emits "
           "pack.tickers[ticker], comps_compute reads pack.info[ticker]. "
           "Layer 2 returns all-None multiples without crashing. Fix in PR #178 "
           "(Tier 1 multiples canonical rename per docs/normalization-contract.md).",
)
def test_chain_comps_to_comps_compute(tmp_path):
    """data-us comps-multiples pack feeds analysis-comps without adapter.

    Expected current state: BROKEN — analysis-comps reads `pack.info[ticker]`
    but data-us comps-multiples emits `pack.tickers[ticker]`. This is the
    most dangerous failure mode: it does NOT crash. analysis-comps silently
    extracts None for every multiple → composite scores are all-None →
    verdict produced by investing-team is garbage.
    """
    fixture = FIXTURES / "data-us-comps-multiples-sample.json"
    script = SKILLS / "analysis-comps" / "scripts" / "comps_compute.py"
    if not fixture.exists() or not script.exists():
        pytest.skip("missing fixture or script")

    pack = json.loads(fixture.read_text())
    tickers = list((pack.get("tickers") or {}).keys())
    if len(tickers) < 2:
        pytest.skip(f"fixture needs >=2 tickers, has {len(tickers)}")

    # Slice the multi-ticker fixture into anchor + peer files
    # (comps_compute expects per-ticker pack files).
    anchor_ticker, peer_ticker = tickers[0], tickers[1]
    anchor_file = tmp_path / f"{anchor_ticker}-anchor.json"
    peer_file = tmp_path / f"{peer_ticker}-peer.json"
    anchor_file.write_text(json.dumps({
        "pack": "comps-multiples",
        "ticker": anchor_ticker,
        "tickers": {anchor_ticker: pack["tickers"][anchor_ticker]},
    }))
    peer_file.write_text(json.dumps({
        "pack": "comps-multiples",
        "ticker": peer_ticker,
        "tickers": {peer_ticker: pack["tickers"][peer_ticker]},
    }))

    rc, out, stderr = _run_layer2(script, [
        "--anchor", str(anchor_file),
        "--peers", str(peer_file),
    ])

    assert rc == 0, f"exit {rc}\nstderr: {stderr}"

    # Critical check: anchor multiples must be NON-None for at least PE/PB
    # (the fixture has trailingPE=35.46, priceToBook=46.71 for AAPL).
    anchor_block = out.get("anchor") or {}
    anchor_multiples = anchor_block.get("multiples") or {}
    pe = anchor_multiples.get("trailingPE")
    pb = anchor_multiples.get("priceToBook")

    assert pe is not None or pb is not None, (
        f"analysis-comps extracted ALL-None multiples for anchor "
        f"{anchor_ticker} — this is the silent-corruption failure mode. "
        f"Likely cause: comps_compute reads pack.info[ticker] but "
        f"data-us comps-multiples emits pack.tickers[ticker]. "
        f"anchor_multiples={anchor_multiples!r}"
    )


# ---------------------------------------------------------------------------
# Chain 4: data-us screener-batch → analysis-screener
# ---------------------------------------------------------------------------

def test_chain_screenerbatch_to_screener():
    """data-us screener-batch pack feeds analysis-screener without adapter.

    Expected current state: PARTIALLY GREEN — analysis-screener accepts
    `pack.tickers` in dict-shape OR list-shape (multi-shape adapter at
    lines 100-105), matching what screener-batch emits AT THE TOP LEVEL.

    The chain wiring is correct (universe_size > 0 means screener read the
    tickers). Whether `ranked` returns rows depends on preset thresholds vs
    the fixture's tickers — the 3 fixture tickers (AAPL/MSFT/GOOGL) all
    have P/E > 25 so the 'value' preset filters them all out, but that is
    a preset-vs-data issue, not a shape mismatch.
    """
    fixture = FIXTURES / "data-us-screener-batch-sample.json"
    script = SKILLS / "analysis-screener" / "scripts" / "screener_compute.py"
    if not fixture.exists() or not script.exists():
        pytest.skip("missing fixture or script")

    rc, out, stderr = _run_layer2(script, [
        "--input", str(fixture),
        "--preset", "value",
        "--top-n", "5",
    ])

    assert rc == 0, f"exit {rc}\nstderr: {stderr}\nstdout: {out}"
    universe_size = out.get("universe_size", 0)
    pack_tickers = json.loads(fixture.read_text()).get("tickers") or {}
    expected_size = len(pack_tickers) if isinstance(pack_tickers, dict) else len(pack_tickers)
    assert universe_size == expected_size, (
        f"screener saw {universe_size} tickers but fixture has {expected_size}; "
        f"shape mismatch likely — output keys: {list(out.keys())}"
    )


# ---------------------------------------------------------------------------
# Chain 5: data-us regime-pack → analysis-macro-regime
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    strict=True,
    reason="Chain 5 broken (silent corruption): regime-pack emits "
           "pack.groups.{*}.series (nested), regime_compose reads pack.series "
           "(flat top-level). Layer 2 returns all-flat defaults + real_rates: "
           "null without crashing. Fix in PR #179 (Tier 2 macro time-series "
           "flatten per docs/normalization-contract.md).",
)
def test_chain_regimepack_to_macroregime():
    """data-us regime-pack pack feeds analysis-macro-regime without adapter.

    Expected current state: BROKEN (silent degradation) — regime_compose
    reads `pack.series` (flat top-level dict at line 251), but data-us
    regime-pack emits `pack.groups.{rates,inflation,...}.series` (two-level
    nested). Result: regime_compose finds no series, defaults every
    indicator to 'flat', confidence=low, real_rates=None — but does NOT
    crash. classify_country returns a quadrant based on all-flat defaults,
    which is meaningless garbage but looks superficially correct.
    """
    fixture = FIXTURES / "data-us-regime-pack-sample.json"
    script = SKILLS / "analysis-macro-regime" / "scripts" / "regime_compose.py"
    if not fixture.exists() or not script.exists():
        pytest.skip("missing fixture or script")

    rc, out, stderr = _run_layer2(script, [
        "--input", f"us={fixture}",
    ])

    assert rc == 0, f"exit {rc}\nstderr: {stderr}\nstdout: {out}"
    countries = out.get("countries") or out.get("by_country") or {}
    us = countries.get("us") if isinstance(countries, dict) else None
    assert us is not None, (
        f"regime_compose did not produce a US classification; "
        f"output keys: {list(out.keys())}"
    )

    # Critical check: real-rate block must be derivable. The fixture
    # contains DGS10 (under groups.rates.series) and T10YIE (under
    # groups.real_rates.series). If chain wiring works, real_rates
    # block should be a dict with nominal_10y/breakeven_10y/real_10y.
    # If chain is broken (current state), real_rates is None and notes
    # explicitly say "missing DGS10 or T10YIE in regime-pack".
    real_rates = us.get("real_rates")
    notes = us.get("notes") or []
    assert real_rates is not None and isinstance(real_rates, dict), (
        f"real-rate block is None — regime_compose could not find "
        f"DGS10/T10YIE in the regime-pack. Likely cause: regime_compose "
        f"reads pack.series (flat) but data-us regime-pack emits "
        f"pack.groups.{{rates,real_rates}}.series (two-level nested). "
        f"notes: {notes}"
    )

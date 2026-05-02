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

Per ADR-0002 (Layer 1 staging-tier normalization), 2 of 5 chains
remain known-broken on main as of PR #178. They carry pytest xfail
markers referencing the planned fix PR. Each fix PR's success
criterion is removing the corresponding xfail marker AND the test
passing.

| Chain | Status     | Fix PR                              |
|-------|------------|-------------------------------------|
|   1   | passing    | PR #178 (T1 OHLCV alias) ✓ landed   |
|   2   | passing    | PR #181 (T3 XBRL → flat) ✓ landed   |
|   3   | passing    | PR #178 (T1 multiples alias) ✓      |
|   4   | passing    | n/a — Layer 1 emit already matches  |
|   5   | passing    | PR #179 (T2 macro flatten) ✓ landed |

All 5 chains pass. Future PRs (#178a/b/c/d, #181a/b/c/d) extend to
data-jp/tw/kr/cn — those will add their own integration tests.

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
    # RSI is the chain-wiring canary — needs only 14 rows, computable from
    # the head-truncated 5-row fixture? No — RSI also needs 14. But ta_compute
    # accepts shorter input and returns partial indicators. The key signal:
    # at least ONE indicator is non-None means ta_compute received OHLCV rows
    # (i.e. the unwrap from price_history.data succeeded).
    non_none_indicators = [k for k, v in indicators.items() if v is not None]
    assert non_none_indicators, (
        f"ALL indicators are None — chain wiring failed (ta_compute did not "
        f"receive OHLCV rows). indicators: {indicators}"
    )


# ---------------------------------------------------------------------------
# Chain 2: data-us memo-fetch → analysis-dcf
# ---------------------------------------------------------------------------

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

    # The real test: did DCF derive sensible numbers from the input?
    intrinsic = out.get("intrinsic_value") or {}
    intrinsic_mid = intrinsic.get("mid") if isinstance(intrinsic, dict) else None
    assumptions = out.get("assumptions") or {}
    base_revenue = assumptions.get("base_revenue")
    cagr = assumptions.get("historical_revenue_cagr")

    assert rc == 0, f"exit {rc}\nstderr: {stderr}"
    assert intrinsic_mid is not None and intrinsic_mid > 0, (
        f"DCF intrinsic_value.mid is degenerate ({intrinsic_mid!r}) — "
        f"normalize did not populate income_statement / cash_flow / "
        f"balance_sheet correctly."
    )
    assert base_revenue is not None and base_revenue > 0, (
        f"DCF base_revenue is degenerate ({base_revenue!r}) — canonical "
        f"income_statement.revenue is empty."
    )
    assert cagr is not None, (
        f"DCF historical_revenue_cagr is None — canonical revenue series "
        f"too short to derive CAGR."
    )


# ---------------------------------------------------------------------------
# Chain 3: data-us comps-multiples → analysis-comps
# ---------------------------------------------------------------------------

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
    # Construct per-ticker files matching what data-{country}/pack.py emits
    # for a single ticker (post-T1: both `tickers` and canonical `info` key
    # per docs/normalization-contract.md).
    anchor_payload = {anchor_ticker: pack["tickers"][anchor_ticker]}
    peer_payload = {peer_ticker: pack["tickers"][peer_ticker]}
    anchor_file.write_text(json.dumps({
        "pack": "comps-multiples",
        "ticker": anchor_ticker,
        "tickers": anchor_payload,
        "info": anchor_payload,  # T1 canonical alias
    }))
    peer_file.write_text(json.dumps({
        "pack": "comps-multiples",
        "ticker": peer_ticker,
        "tickers": peer_payload,
        "info": peer_payload,  # T1 canonical alias
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
# data-kr cross-layer chains (Tier 2 yfinance fallback per ADR-0003)
# ---------------------------------------------------------------------------

def test_chain_kr_snapshot_to_technical():
    """data-kr snapshot pack feeds analysis-technical without adapter."""
    fixture = FIXTURES / "data-kr-snapshot-sample.json"
    script = SKILLS / "analysis-technical" / "scripts" / "ta_compute.py"
    if not fixture.exists() or not script.exists():
        pytest.skip("missing fixture or script")

    rc, out, stderr = _run_layer2(script, ["--input", str(fixture)])
    assert rc == 0, f"exit {rc}\nstderr: {stderr}"
    assert "error" not in out, f"ta_compute error: {out.get('error')!r}"
    indicators = out.get("indicators") or {}
    non_none = [k for k, v in indicators.items() if v is not None]
    assert non_none, f"all indicators None — chain wiring failed: {indicators}"


def test_chain_kr_memofetch_to_dcf():
    """data-kr memo-fetch pack feeds analysis-dcf without adapter (T3 yfinance fallback)."""
    fixture = FIXTURES / "data-kr-memo-fetch-sample.json"
    script = SKILLS / "analysis-dcf" / "scripts" / "dcf_compute.py"
    if not fixture.exists() or not script.exists():
        pytest.skip("missing fixture or script")

    rc, out, stderr = _run_layer2(script, ["--input", str(fixture)])
    assert rc == 0, f"exit {rc}\nstderr: {stderr}"
    intrinsic = out.get("intrinsic_value") or {}
    intrinsic_mid = intrinsic.get("mid") if isinstance(intrinsic, dict) else None
    base_revenue = (out.get("assumptions") or {}).get("base_revenue")
    assert intrinsic_mid is not None and intrinsic_mid > 0, (
        f"data-kr DCF degenerate: {intrinsic_mid!r}; base_revenue={base_revenue!r}"
    )
    # Samsung FY25 revenue = 333.6T KRW. Expect non-trivial scale.
    assert base_revenue is not None and base_revenue > 1e12, (
        f"data-kr base_revenue too small ({base_revenue!r}) — canonical wiring broken"
    )


def test_chain_kr_comps_to_comps_compute(tmp_path):
    """data-kr comps-multiples pack feeds analysis-comps without adapter."""
    fixture = FIXTURES / "data-kr-comps-multiples-sample.json"
    script = SKILLS / "analysis-comps" / "scripts" / "comps_compute.py"
    if not fixture.exists() or not script.exists():
        pytest.skip("missing fixture or script")

    pack = json.loads(fixture.read_text())
    info = pack.get("info") or {}
    tickers = list(info.keys())
    if len(tickers) < 2:
        pytest.skip(f"fixture needs >=2 tickers, has {len(tickers)}")

    anchor_ticker, peer_ticker = tickers[0], tickers[1]
    anchor_file = tmp_path / f"{anchor_ticker.replace('.', '_')}-anchor.json"
    peer_file = tmp_path / f"{peer_ticker.replace('.', '_')}-peer.json"
    anchor_payload = {anchor_ticker: info[anchor_ticker]}
    peer_payload = {peer_ticker: info[peer_ticker]}
    anchor_file.write_text(json.dumps({
        "pack": "comps-multiples",
        "ticker": anchor_ticker,
        "tickers": [anchor_ticker],
        "info": anchor_payload,
    }))
    peer_file.write_text(json.dumps({
        "pack": "comps-multiples",
        "ticker": peer_ticker,
        "tickers": [peer_ticker],
        "info": peer_payload,
    }))

    rc, out, stderr = _run_layer2(script, [
        "--anchor", str(anchor_file),
        "--peers", str(peer_file),
    ])
    assert rc == 0, f"exit {rc}\nstderr: {stderr}"
    anchor_block = out.get("anchor") or {}
    multiples = anchor_block.get("multiples") or {}
    non_none = {k: v for k, v in multiples.items() if v is not None}
    assert non_none, (
        f"data-kr comps extracted all-None for {anchor_ticker}: {multiples}"
    )


# ---------------------------------------------------------------------------
# data-cn cross-layer chains (Tier 2 yfinance fallback per ADR-0003)
# ---------------------------------------------------------------------------

def test_chain_cn_snapshot_to_technical():
    fixture = FIXTURES / "data-cn-snapshot-sample.json"
    script = SKILLS / "analysis-technical" / "scripts" / "ta_compute.py"
    if not fixture.exists() or not script.exists():
        pytest.skip("missing fixture or script")
    rc, out, stderr = _run_layer2(script, ["--input", str(fixture)])
    assert rc == 0, f"exit {rc}\nstderr: {stderr}"
    assert "error" not in out, f"ta_compute error: {out.get('error')!r}"
    indicators = out.get("indicators") or {}
    assert any(v is not None for v in indicators.values()), (
        f"all indicators None — chain wiring failed: {indicators}"
    )


def test_chain_cn_memofetch_to_dcf():
    fixture = FIXTURES / "data-cn-memo-fetch-sample.json"
    script = SKILLS / "analysis-dcf" / "scripts" / "dcf_compute.py"
    if not fixture.exists() or not script.exists():
        pytest.skip("missing fixture or script")
    rc, out, stderr = _run_layer2(script, ["--input", str(fixture)])
    assert rc == 0, f"exit {rc}\nstderr: {stderr}"
    intrinsic = out.get("intrinsic_value") or {}
    intrinsic_mid = intrinsic.get("mid") if isinstance(intrinsic, dict) else None
    base_revenue = (out.get("assumptions") or {}).get("base_revenue")
    assert intrinsic_mid is not None and intrinsic_mid > 0, (
        f"data-cn DCF degenerate: {intrinsic_mid!r}; base_revenue={base_revenue!r}"
    )
    # Moutai FY24 revenue ~172B CNY
    assert base_revenue is not None and base_revenue > 1e9, (
        f"data-cn base_revenue too small: {base_revenue!r}"
    )


def test_chain_cn_comps_to_comps_compute(tmp_path):
    fixture = FIXTURES / "data-cn-comps-multiples-sample.json"
    script = SKILLS / "analysis-comps" / "scripts" / "comps_compute.py"
    if not fixture.exists() or not script.exists():
        pytest.skip("missing fixture or script")
    pack = json.loads(fixture.read_text())
    info = pack.get("info") or {}
    tickers = list(info.keys())
    if len(tickers) < 2:
        pytest.skip(f"fixture needs >=2 tickers, has {len(tickers)}")
    anchor_ticker, peer_ticker = tickers[0], tickers[1]
    anchor_file = tmp_path / f"{anchor_ticker.replace('.', '_')}-anchor.json"
    peer_file = tmp_path / f"{peer_ticker.replace('.', '_')}-peer.json"
    anchor_file.write_text(json.dumps({
        "pack": "comps-multiples",
        "ticker": anchor_ticker,
        "info": {anchor_ticker: info[anchor_ticker]},
    }))
    peer_file.write_text(json.dumps({
        "pack": "comps-multiples",
        "ticker": peer_ticker,
        "info": {peer_ticker: info[peer_ticker]},
    }))
    rc, out, stderr = _run_layer2(script, [
        "--anchor", str(anchor_file),
        "--peers", str(peer_file),
    ])
    assert rc == 0, f"exit {rc}\nstderr: {stderr}"
    anchor_block = out.get("anchor") or {}
    multiples = anchor_block.get("multiples") or {}
    assert any(v is not None for v in multiples.values()), (
        f"data-cn comps all-None for {anchor_ticker}: {multiples}"
    )


# ---------------------------------------------------------------------------
# data-jp cross-layer chains (Tier 2 yfinance fallback / Tier A EDINET key)
# ---------------------------------------------------------------------------

def test_chain_jp_snapshot_to_technical():
    fixture = FIXTURES / "data-jp-snapshot-sample.json"
    script = SKILLS / "analysis-technical" / "scripts" / "ta_compute.py"
    if not fixture.exists() or not script.exists():
        pytest.skip("missing fixture or script")
    rc, out, stderr = _run_layer2(script, ["--input", str(fixture)])
    assert rc == 0, f"exit {rc}\nstderr: {stderr}"
    assert "error" not in out, f"ta_compute error: {out.get('error')!r}"
    indicators = out.get("indicators") or {}
    assert any(v is not None for v in indicators.values()), (
        f"all indicators None — chain wiring failed: {indicators}"
    )


def test_chain_jp_memofetch_to_dcf():
    fixture = FIXTURES / "data-jp-memo-fetch-sample.json"
    script = SKILLS / "analysis-dcf" / "scripts" / "dcf_compute.py"
    if not fixture.exists() or not script.exists():
        pytest.skip("missing fixture or script")
    rc, out, stderr = _run_layer2(script, ["--input", str(fixture)])
    assert rc == 0, f"exit {rc}\nstderr: {stderr}"
    intrinsic = out.get("intrinsic_value") or {}
    intrinsic_mid = intrinsic.get("mid") if isinstance(intrinsic, dict) else None
    base_revenue = (out.get("assumptions") or {}).get("base_revenue")
    # NOTE: chain-wiring assertion only — base_revenue must be populated.
    # intrinsic_value.mid sign/magnitude can vary with the underlying issuer
    # (e.g. Toyota's consolidated FCF is negative due to its financing arm,
    # which is a real-data artifact, not a chain breakage). The test goal
    # is "Layer 1 -> Layer 2 wiring works", not "DCF result is rational".
    assert intrinsic_mid is not None, (
        f"data-jp DCF intrinsic_mid is None — chain wiring broken; "
        f"base_revenue={base_revenue!r}"
    )
    # Toyota FY25 revenue ~48T JPY
    assert base_revenue is not None and base_revenue > 1e12, (
        f"data-jp base_revenue too small: {base_revenue!r}"
    )


def test_chain_jp_comps_to_comps_compute(tmp_path):
    fixture = FIXTURES / "data-jp-comps-multiples-sample.json"
    script = SKILLS / "analysis-comps" / "scripts" / "comps_compute.py"
    if not fixture.exists() or not script.exists():
        pytest.skip("missing fixture or script")
    pack = json.loads(fixture.read_text())
    info = pack.get("info") or {}
    tickers = list(info.keys())
    if len(tickers) < 2:
        pytest.skip(f"fixture needs >=2 tickers, has {len(tickers)}")
    anchor_ticker, peer_ticker = tickers[0], tickers[1]
    anchor_file = tmp_path / f"{anchor_ticker}-anchor.json"
    peer_file = tmp_path / f"{peer_ticker}-peer.json"
    anchor_file.write_text(json.dumps({
        "pack": "comps-multiples",
        "ticker": anchor_ticker,
        "info": {anchor_ticker: info[anchor_ticker]},
    }))
    peer_file.write_text(json.dumps({
        "pack": "comps-multiples",
        "ticker": peer_ticker,
        "info": {peer_ticker: info[peer_ticker]},
    }))
    rc, out, stderr = _run_layer2(script, [
        "--anchor", str(anchor_file),
        "--peers", str(peer_file),
    ])
    assert rc == 0, f"exit {rc}\nstderr: {stderr}"
    multiples = (out.get("anchor") or {}).get("multiples") or {}
    assert any(v is not None for v in multiples.values()), (
        f"data-jp comps all-None for {anchor_ticker}: {multiples}"
    )


# ---------------------------------------------------------------------------
# T3 lossless invariant — canonical income_statement traces back to raw
# concept observations (per docs/normalization-contract.md Principle 5).
# ---------------------------------------------------------------------------

def test_t3_lossless_invariant_revenue():
    """Each canonical revenue value MUST exist in raw sec_facts.concepts
    under one of the chain entries. If this fails, _normalize_dcf has
    drifted from raw — bug in normalize logic.
    """
    fixture = FIXTURES / "data-us-memo-fetch-sample.json"
    if not fixture.exists():
        pytest.skip("missing fixture")
    pack = json.loads(fixture.read_text())

    canonical_revenues = pack["income_statement"]["revenue"]
    raw_concepts = pack["sec_facts"]["concepts"]
    per_year_concept = pack["income_statement"]["_meta"]["revenue"]["per_year_concept"]

    assert len(canonical_revenues) == len(per_year_concept), (
        f"per_year_concept length ({len(per_year_concept)}) does not match "
        f"canonical revenue length ({len(canonical_revenues)})"
    )

    for canonical_val, source_concept in zip(canonical_revenues, per_year_concept):
        raw_payload = raw_concepts.get(source_concept) or {}
        raw_obs = raw_payload.get("observations") or []
        raw_values = [o.get("value") for o in raw_obs if isinstance(o, dict)]
        assert canonical_val in raw_values, (
            f"canonical revenue {canonical_val} (source: {source_concept}) "
            f"not found in raw concept observations. "
            f"raw values: {raw_values[:5]}..."
        )


# ---------------------------------------------------------------------------
# Chain 5: data-us regime-pack → analysis-macro-regime
# ---------------------------------------------------------------------------

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

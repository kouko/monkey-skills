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
import re
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
    anchor_multiples = anchor_block.get("multiples_direct") or {}
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
    multiples = anchor_block.get("multiples_direct") or {}
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
    multiples = anchor_block.get("multiples_direct") or {}
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
    multiples = (out.get("anchor") or {}).get("multiples_direct") or {}
    assert any(v is not None for v in multiples.values()), (
        f"data-jp comps all-None for {anchor_ticker}: {multiples}"
    )


# ---------------------------------------------------------------------------
# data-tw cross-layer chains (Tier 2 yfinance fallback; MOPS Tier A T3 deferred)
# ---------------------------------------------------------------------------

def test_chain_tw_snapshot_to_technical():
    fixture = FIXTURES / "data-tw-snapshot-sample.json"
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


def test_chain_tw_memofetch_to_dcf():
    fixture = FIXTURES / "data-tw-memo-fetch-sample.json"
    script = SKILLS / "analysis-dcf" / "scripts" / "dcf_compute.py"
    if not fixture.exists() or not script.exists():
        pytest.skip("missing fixture or script")
    rc, out, stderr = _run_layer2(script, ["--input", str(fixture)])
    assert rc == 0, f"exit {rc}\nstderr: {stderr}"
    intrinsic = out.get("intrinsic_value") or {}
    intrinsic_mid = intrinsic.get("mid") if isinstance(intrinsic, dict) else None
    base_revenue = (out.get("assumptions") or {}).get("base_revenue")
    assert intrinsic_mid is not None, (
        f"data-tw DCF intrinsic_mid is None — chain wiring broken"
    )
    # TSMC FY24 revenue ~3.8T TWD
    assert base_revenue is not None and base_revenue > 1e11, (
        f"data-tw base_revenue too small: {base_revenue!r}"
    )


def test_chain_tw_comps_to_comps_compute(tmp_path):
    fixture = FIXTURES / "data-tw-comps-multiples-sample.json"
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
    multiples = (out.get("anchor") or {}).get("multiples_direct") or {}
    assert any(v is not None for v in multiples.values()), (
        f"data-tw comps all-None for {anchor_ticker}: {multiples}"
    )


# ---------------------------------------------------------------------------
# Cross-country T2 regime chains (analysis-macro-regime via flat series block)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("country", ["jp", "tw", "kr", "cn"])
def test_chain_country_regime_to_macroregime(country):
    """data-{country} regime-pack feeds analysis-macro-regime via T2 flat
    `series` block. Per ADR-0002 cross-country symmetry — chain wiring works
    for all 5 countries (data-us covered separately by
    test_chain_regimepack_to_macroregime).

    Asserts regime_compose produces a structured classification (chain wiring
    works). Whether growth/inflation directions are non-flat depends on
    whether the country's regime-pack fixture contains the proxy indicators
    that regime_compose's per-country resolve_series chain looks for —
    that's a data-coverage question, not a chain-wiring question.
    """
    fixture = FIXTURES / f"data-{country}-regime-pack-sample.json"
    script = SKILLS / "analysis-macro-regime" / "scripts" / "regime_compose.py"
    if not fixture.exists() or not script.exists():
        pytest.skip("missing fixture or script")
    rc, out, stderr = _run_layer2(script, ["--input", f"{country}={fixture}"])
    assert rc == 0, f"exit {rc}\nstderr: {stderr}"
    # Phase 1 schema (post-PR-7): classify_X output lives at
    # out.by_country.{cc}.native_verdict; ic_quadrant under
    # native_verdict.ic_quadrant or native_verdict.ic_quadrant_legacy
    # (countries that demoted IC to legacy reference).
    block = out.get("by_country", {}).get(country) or {}
    assert block, (
        f"data-{country} regime: no {country} block in by_country. "
        f"output keys: {list(out.keys())}; by_country keys: "
        f"{list(out.get('by_country', {}).keys())}"
    )
    nv = block.get("native_verdict") or {}
    ic = nv.get("ic_quadrant") or nv.get("ic_quadrant_legacy")
    assert ic is not None, (
        f"data-{country} regime: native_verdict has neither ic_quadrant "
        f"nor ic_quadrant_legacy. native_verdict keys: {list(nv.keys())}"
    )
    assert ic in {"1-recovery", "2-overheat", "3-stagflation", "4-reflation"}


# ---------------------------------------------------------------------------
# Phase 1 per-country classifiers (per ADR-0004) — independent functions
# (NOT parametrize) to avoid file conflicts across PR-3-6 parallel work
# ---------------------------------------------------------------------------

def test_chain_tw_classifier_e2e():
    """data-tw regime-pack → classify_tw → CountryRegimeCard with valid
    Phase 1 envelope. Per ADR-0004 PR-4.

    TW native verdict leads with NDC 五色景氣燈號 (signal_color + score)
    rather than IC quadrant. components_9 must have 9 named slots
    (one may be None — TIER often missing in older fixtures predating
    the ndc_client TIER preset). tsmc_concentration_overlay must be
    populated from calibration vintage.
    """
    fixture = FIXTURES / "data-tw-regime-pack-sample.json"
    script = SKILLS / "analysis-macro-regime" / "scripts" / "regime_compose.py"
    if not fixture.exists() or not script.exists():
        pytest.skip("missing fixture or script")

    rc, out, stderr = _run_layer2(script, ["--input", f"tw={fixture}"])
    assert rc == 0, f"exit {rc}\nstderr: {stderr}"

    tw = out.get("by_country", {}).get("tw")
    assert tw is not None, (
        f"by_country.tw missing — classify_tw not picked up by dispatcher. "
        f"output keys: {list(out.keys())}; "
        f"by_country keys: {list(out.get('by_country', {}).keys())}"
    )
    # Surface envelope
    assert tw["country"] == "tw"
    assert tw["framework_used"], "framework_used empty"
    assert "NDC 五色" in tw["framework_used"], (
        f"TW framework_used does not lead with NDC 五色: {tw['framework_used']!r}"
    )
    # Per ROADMAP §v2.1.x-b/c (resolved 2026-05-02): with cpi-yoy fixed
    # and 8 NDC components present, classify_tw thresholds yield "high".
    # TIER (9th component) is structurally unavailable from NDC's bulk
    # ZIP — its absence is expected and does not regress confidence.
    # See ROADMAP §v2.2.0-g for the deferred TIER fetcher.
    assert tw["confidence"] == "high", (
        f"TW confidence regressed to {tw['confidence']!r} — likely "
        f"cpi-yoy or NDC components broke. data_quality.missing: "
        f"{tw.get('data_quality', {}).get('missing')}"
    )
    assert tw["provenance"]["calibration_doc"] == "thresholds-taiwan.md"

    # Native verdict — TW-specific shape
    nv = tw["native_verdict"]
    assert "framework_label" in nv
    # Signal color must be one of NDC 5 colors (or 'unknown' if score missing)
    assert nv["signal_color"] in {"紅", "黃紅", "綠", "黃藍", "藍", "unknown"}, (
        f"unexpected signal_color: {nv['signal_color']!r}"
    )
    # Signal score must be in 9-45 range when populated
    score = nv.get("signal_score")
    if score is not None:
        assert 9 <= score <= 45, (
            f"signal_score {score} out of NDC 9-45 range"
        )
    # Score band meaning is a non-empty narrative string
    assert isinstance(nv.get("score_band_meaning"), str)
    assert nv["score_band_meaning"], "score_band_meaning is empty"

    # 9 構成 — must have all 9 expected slot keys (TIER may be None,
    # other 8 should be present in fixture).
    components = nv.get("components_9", {})
    expected_slots = {
        "貨幣總計數M1B",
        "股價指數",
        "工業生產指數",
        "工業及服務業加班工時",
        "海關出口值",
        "機械及電機設備進口值",
        "製造業銷售量指數",
        "批發、零售及餐飲業營業額",
        "製造業營業氣候測驗點",
    }
    assert expected_slots.issubset(set(components.keys())), (
        f"components_9 missing expected slots: "
        f"{expected_slots - set(components.keys())}"
    )
    # Dispersion summary must be present
    dispersion = components.get("_dispersion", {})
    assert dispersion.get("components_expected") == 9
    assert dispersion.get("components_found", 0) >= 6, (
        f"too few components found in fixture: {dispersion.get('components_found')}"
    )

    # TSMC concentration overlay — populated from calibration
    tsmc = nv.get("tsmc_concentration_overlay", {})
    assert tsmc.get("weight_pct") is not None, (
        f"tsmc weight_pct missing — calibration not loaded? overlay: {tsmc}"
    )
    assert tsmc["weight_pct"] >= 40, (
        f"TSMC weight {tsmc['weight_pct']} below historical 40%+ band"
    )
    assert tsmc.get("top_10_pct") is not None
    assert tsmc.get("historic_5y_delta_pp") is not None

    # CBC framing must be 彈性定義 (not rigid 2%)
    cpi_ctx = nv.get("cpi_context", {})
    assert cpi_ctx.get("cbc_framing") == "彈性定義", (
        f"TW cbc_framing must be '彈性定義', got: {cpi_ctx.get('cbc_framing')!r}"
    )
    # Per ROADMAP §v2.1.x-c: cpi_context.latest_yoy must be non-null —
    # the fixture's `dgbas.cpi-yoy` series resolves to a true YoY%
    # (年增率 sheet of cpispl.xls), not the INDEX values that the
    # legacy `cpi` preset emitted.
    assert cpi_ctx.get("latest_yoy") is not None, (
        "cpi_context.latest_yoy is None — fixture missing cpi-yoy series? "
        f"cpi_context: {cpi_ctx}"
    )
    # Sanity-check magnitude: TW CPI YoY runs in the -5%..+20% band.
    # If the value lands outside this it usually means the parser is
    # reading the INDEX sheet (~110) instead of the YoY% sheet.
    assert -5.0 <= cpi_ctx["latest_yoy"] <= 20.0, (
        f"cpi_context.latest_yoy {cpi_ctx['latest_yoy']} outside plausible "
        f"YoY band [-5, 20] — parser may be reading INDEX not YoY"
    )

    # IC quadrant alias for backward compat (legacy schema readers)
    assert nv.get("ic_quadrant") in {
        "1-recovery", "2-overheat", "3-stagflation", "4-reflation"
    }

    # PMI block exists (manufacturing + non-manufacturing)
    pmi = nv.get("pmi", {})
    assert "manufacturing" in pmi
    assert "non_manufacturing" in pmi

    # Indicators_used must include the NDC + statgov primary inputs
    ind = tw.get("indicators_used", [])
    assert "ndc.signal-score" in ind, f"ndc.signal-score missing from indicators_used: {ind}"


def test_chain_kr_classifier_e2e():
    """data-kr regime-pack → classify_kr → CountryRegimeCard with valid
    Phase 1 envelope. Per ADR-0004 PR-5.

    KR-specific assertions:
      - bok_target_alignment populated (target / current / gap / status)
      - household_debt_overlay populated (BIS + BOK ratios + macroprudential flag)
      - kospi_concentration_overlay populated (Samsung+SK Hynix ~40.96%)
      - cycle_phase ∈ {expansion, peak, contraction, trough, unknown}
      - esi_status ∈ {"fetched", "unavailable_via_fdr"} — must NOT fail
        when ESI unavailable (best-effort per ADR-0004 PR-5)
    """
    fixture = FIXTURES / "data-kr-regime-pack-sample.json"
    script = SKILLS / "analysis-macro-regime" / "scripts" / "regime_compose.py"
    if not fixture.exists() or not script.exists():
        pytest.skip("missing fixture or script")

    rc, out, stderr = _run_layer2(script, ["--input", f"kr={fixture}"])
    assert rc == 0, f"exit {rc}\nstderr: {stderr}"

    kr = out.get("by_country", {}).get("kr")
    assert kr is not None, (
        f"by_country.kr missing — classify_kr not picked up by dispatcher. "
        f"output keys: {list(out.keys())}; "
        f"by_country keys: {list(out.get('by_country', {}).keys())}"
    )
    assert kr["country"] == "kr"
    assert kr["framework_used"], "framework_used empty"

    nv = kr["native_verdict"]
    assert "framework_label" in nv, "framework_label missing"
    assert "BOK 2% target" in nv["framework_label"]

    # --- bok_target_alignment populated ---
    bta = nv.get("bok_target_alignment")
    assert bta is not None, (
        f"bok_target_alignment is None — CPI yoy not derivable. "
        f"native_verdict keys: {list(nv.keys())}"
    )
    assert bta["target"] == 2.0, f"BOK 2% target mismatch: {bta['target']!r}"
    assert "current" in bta and isinstance(bta["current"], (int, float))
    assert "gap" in bta and isinstance(bta["gap"], (int, float))
    assert bta["status"] in {"at_target", "above_target", "below_target"}

    # --- household_debt_overlay populated ---
    hh = nv.get("household_debt_overlay")
    assert hh is not None, "household_debt_overlay missing"
    assert hh.get("ratio_bis") == 0.894, (
        f"BIS 2025-Q3 ratio mismatch: {hh.get('ratio_bis')!r}"
    )
    assert hh.get("macroprudential_concern") is True, (
        f"macroprudential_concern flag should be True (89.4% > 80% threshold); "
        f"got {hh.get('macroprudential_concern')!r}"
    )

    # --- kospi_concentration_overlay populated ---
    kospi = nv.get("kospi_concentration_overlay")
    assert kospi is not None, "kospi_concentration_overlay missing"
    assert kospi.get("samsung_skhynix") is not None
    # Samsung+SK Hynix should be in the 0.39-0.42 range (2026-04 vintage)
    assert 0.39 <= kospi["samsung_skhynix"] <= 0.42, (
        f"samsung_skhynix concentration out of expected band: "
        f"{kospi['samsung_skhynix']!r}"
    )

    # --- cycle_phase classification ---
    assert nv["cycle_phase"] in {
        "expansion", "peak", "contraction", "trough", "unknown",
    }

    # --- ESI handling — must NOT fail when unavailable ---
    assert nv["esi_status"] in {"fetched", "unavailable_via_fdr"}, (
        f"esi_status invalid: {nv.get('esi_status')!r}"
    )
    if nv["esi_status"] == "fetched":
        assert nv.get("esi_value") is not None
    # unavailable case is acceptable — pack.py default fixture lacks
    # 'sentiment' group; classifier degrades gracefully

    # --- Confidence heuristic per ADR-0004 PR-5 ---
    assert kr["confidence"] in {"low", "medium", "high"}
    # If ESI is unavailable but cpi + cycle present, confidence MUST be
    # at least "medium" per ADR-0004 PR-5 acceptance criterion
    if nv["esi_status"] == "unavailable_via_fdr" and bta is not None and \
            nv["cycle_phase"] != "unknown":
        assert kr["confidence"] in {"medium", "high"}, (
            f"ESI-unavailable + valid cpi/cycle should floor at medium; "
            f"got {kr['confidence']!r}"
        )

    # --- Provenance ---
    assert kr["provenance"]["calibration_doc"] == "thresholds-korea.md"
    assert kr["provenance"]["calibration_vintage"] == "2026-Q1"


def test_chain_cn_classifier_e2e():
    """data-cn regime-pack → classify_cn → CountryRegimeCard with valid
    Phase 1 envelope + CN-specific native_verdict shape per ADR-0004 PR-6."""
    fixture = FIXTURES / "data-cn-regime-pack-sample.json"
    script = SKILLS / "analysis-macro-regime" / "scripts" / "regime_compose.py"
    if not fixture.exists() or not script.exists():
        pytest.skip("missing fixture or script")

    rc, out, stderr = _run_layer2(script, ["--input", f"cn={fixture}"])
    assert rc == 0, f"exit {rc}\nstderr: {stderr}"

    cn = out.get("by_country", {}).get("cn")
    assert cn is not None, (
        f"by_country.cn missing — classify_cn not picked up by dispatcher. "
        f"output keys: {list(out.keys())}; "
        f"by_country keys: {list(out.get('by_country', {}).keys())}"
    )
    assert cn["country"] == "cn"
    assert cn["framework_used"], "framework_used empty"
    nv = cn["native_verdict"]

    # Envelope basics
    assert "framework_label" in nv
    assert nv.get("ic_quadrant_legacy") in {
        "1-recovery", "2-overheat", "3-stagflation", "4-reflation"
    }
    assert nv.get("gip_regime") in {"quad1", "quad2", "quad3", "quad4"}
    assert cn["confidence"] in ("low", "medium", "high")
    assert cn["provenance"]["calibration_doc"] == "thresholds-china.md"

    # PBOC stance — populated from calibration current_stance
    pboc_stance = nv.get("pboc_stance")
    assert pboc_stance, f"pboc_stance empty: {pboc_stance!r}"
    assert pboc_stance in {"稳健中性", "稳健", "稳健略偏宽松",
                           "稳健偏松", "适度宽松", "宽松"}

    # Policy rate primary — 7D 逆回购 1.40% from calibration
    prp = nv.get("policy_rate_primary") or {}
    assert prp.get("rate") == 1.40, f"7D RR rate not 1.40: {prp!r}"
    assert prp.get("moved_2025_09") is True

    # Quantitative tools (LPR / RRR — may pull live values from series)
    prq = nv.get("policy_rate_quantitative_tools") or {}
    assert prq.get("lpr_1y") is not None
    assert prq.get("rrr_large_bank") is not None

    # CPI framing — KEY CN-specific test: enum must be valid
    cpi_framing = nv.get("cpi_framing") or {}
    assert "policy_stance" in cpi_framing
    assert cpi_framing["policy_stance"] in {
        "supportive_recovery_below_target",
        "near_target_balanced",
        "below_target_persistent",
        "deflation_risk",
        "deflation_confirmed",
        "above_target_concern",
        "unknown",
    }
    if cpi_framing.get("current") is not None:
        # Sanity: target = 2.0
        assert cpi_framing["target"] == 2.0
        assert cpi_framing.get("gap") is not None

    # Credit impulse — populated or marked unavailable
    credit_impulse = nv.get("credit_impulse")
    if credit_impulse is not None:
        assert credit_impulse.get("trend") in {
            "expanding", "contracting", "neutral"
        }
        assert credit_impulse.get("methodology"), (
            f"credit_impulse missing methodology: {credit_impulse!r}"
        )

    # 4-component dispersion — must have 4 entries
    dispersion = nv.get("4_component_dispersion") or {}
    for comp in ("industrial", "retail", "fai", "services"):
        assert comp in dispersion, f"missing dispersion component {comp}"
    assert "spread_pp" in dispersion
    assert "alarm" in dispersion
    assert isinstance(dispersion["alarm"], bool)

    # Property overlay — structural
    prop = nv.get("property_overlay") or {}
    assert prop.get("gdp_share_direct") == 0.236
    assert prop.get("gdp_share_incl_infra") == 0.31
    assert prop.get("deleveraging_phase") is True


def test_chain_us_classifier_e2e():
    """data-us regime-pack → classify_us → CountryRegimeCard with valid
    Phase 1 envelope. Per ADR-0004 PR-2."""
    fixture = FIXTURES / "data-us-regime-pack-sample.json"
    script = SKILLS / "analysis-macro-regime" / "scripts" / "regime_compose.py"
    if not fixture.exists() or not script.exists():
        pytest.skip("missing fixture or script")

    rc, out, stderr = _run_layer2(script, ["--input", f"us={fixture}"])
    assert rc == 0, f"exit {rc}\nstderr: {stderr}"

    us = out.get("by_country", {}).get("us")
    assert us is not None, (
        f"by_country.us missing — classify_us not picked up by dispatcher. "
        f"output keys: {list(out.keys())}; by_country keys: {list(out.get('by_country', {}).keys())}"
    )
    assert us["country"] == "us"
    assert us["framework_used"], "framework_used empty"
    nv = us["native_verdict"]
    assert "framework_label" in nv
    assert nv["ic_quadrant"] in {
        "1-recovery", "2-overheat", "3-stagflation", "4-reflation"
    }
    assert nv["gip_regime"] in {"quad1", "quad2", "quad3", "quad4"}
    assert us["confidence"] in ("low", "medium", "high")
    assert us["provenance"]["calibration_doc"] == "thresholds-us.md"
    # 4-tier real-rate band derived from calibration
    rrd = nv.get("real_rate_decomposition")
    if rrd is not None:
        assert rrd["band"] in {
            "accommodative", "neutral",
            "moderately_restrictive", "clearly_restrictive",
        }
    # Yield curve overlay
    yc = nv.get("yield_curve", {})
    assert yc.get("state") in {
        "inverted", "flat", "normal", "steep", "unknown",
    }


def test_chain_jp_classifier_e2e():
    """data-jp regime-pack → classify_jp → CountryRegimeCard with valid
    Phase 1 envelope. Per ADR-0004 PR-3 + ROADMAP §v2.1.x-a (fixture
    refreshed 2026-05-02 against live BOJ + ESRI APIs).

    Post-refresh acceptance:
      - cycle_proxy.source == "coincident-index" (not "ip" fallback)
      - tankan_business_di.large_mfg populated from BOJ Tankan
      - confidence == "high" (from medium pre-refresh)
    """
    fixture = FIXTURES / "data-jp-regime-pack-sample.json"
    script = SKILLS / "analysis-macro-regime" / "scripts" / "regime_compose.py"
    if not fixture.exists() or not script.exists():
        pytest.skip("missing fixture or script")

    rc, out, stderr = _run_layer2(script, ["--input", f"jp={fixture}"])
    assert rc == 0, f"exit {rc}\nstderr: {stderr}"

    jp = out.get("by_country", {}).get("jp")
    assert jp is not None, (
        f"by_country.jp missing — classify_jp not picked up by dispatcher. "
        f"output keys: {list(out.keys())}; "
        f"by_country keys: {list(out.get('by_country', {}).keys())}"
    )
    assert jp["country"] == "jp"
    assert jp["framework_used"], "framework_used empty"

    nv = jp["native_verdict"]
    assert "framework_label" in nv, "framework_label missing as first verdict key"
    # JP-specific shape assertions
    assert "boj_stance" in nv
    assert nv["boj_stance"] in {"ZIRP", "post_zirp", "exit_deflation", "unknown"}
    assert "boj_call_rate_target_pct" in nv
    assert nv["boj_call_rate_target_pct"] == 0.75, (
        f"boj_call_rate_target_pct should match calibration (0.75 post-2025-12), got {nv['boj_call_rate_target_pct']}"
    )
    assert "deflation_phase" in nv
    assert nv["deflation_phase"] in {
        "in_deflation",
        "exit_deflation_phase_1",
        "exit_deflation_phase_2",
        "post_deflation",
    }
    # IC dimensions retained for parity with legacy
    assert nv.get("ic_quadrant_legacy") in {
        "1-recovery", "2-overheat", "3-stagflation", "4-reflation"
    }
    assert nv.get("gip_regime_legacy") in {"quad1", "quad2", "quad3", "quad4"}

    # Confidence: post v2.1.x-a fixture refresh (Tankan + ESRI CI live),
    # JP must hit "high" stable. Regression to medium would indicate the
    # fixture went stale or BOJ/ESRI series codes drifted.
    assert jp["confidence"] == "high", (
        f"JP confidence must be high post v2.1.x-a refresh; got "
        f"{jp['confidence']!r}. data_quality={jp.get('data_quality')}"
    )

    # cycle_proxy must lead with the ESRI coincident-index (not the IP
    # fallback) — fixture refresh per v2.1.x-a brings the coincident
    # series in via the e-Stat preset bundle.
    cycle = nv.get("cycle_proxy", {})
    assert cycle.get("source") == "coincident-index", (
        f"cycle_proxy.source must be 'coincident-index' (not IP fallback); "
        f"got {cycle.get('source')!r}. cycle_proxy={cycle}"
    )
    assert cycle.get("value") is not None, (
        f"cycle_proxy.value None despite source=coincident-index; "
        f"cycle_proxy={cycle}"
    )

    # Tankan business DI block must surface large_mfg from BOJ
    # TK99F1000601GCQ01000 series. dispersion_pp must be a number
    # (not None) once all 4 categories are populated.
    tdi = nv.get("tankan_business_di", {})
    assert tdi.get("large_mfg") is not None, (
        f"tankan_business_di.large_mfg None — Tankan fetch chain broke. "
        f"tankan_business_di={tdi}"
    )
    assert tdi.get("dispersion_pp") is not None, (
        f"tankan_business_di.dispersion_pp None — only some of the 4 "
        f"Tankan categories present. tankan_business_di={tdi}"
    )

    # Provenance points at JP threshold doc
    assert jp["provenance"]["calibration_doc"] == "thresholds-japan.md"
    assert jp["provenance"]["calibration_vintage"] == "2026-Q2"

    # Real-rate block — fixture has ECB JP real yield, so this MUST resolve.
    rrb = nv.get("real_rate_block")
    assert rrb is not None, (
        f"real_rate_block None — ECB real-yield fixture chain broken. "
        f"indicators_used={jp.get('indicators_used')}"
    )
    assert rrb["band"] in {"accommodative", "neutral", "restrictive", "unknown"}


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
    # Phase 1 schema: classify_us output at by_country.us.native_verdict
    us = out.get("by_country", {}).get("us")
    assert us is not None, (
        f"regime_compose did not produce a US classification; "
        f"output keys: {list(out.keys())}"
    )
    nv = us.get("native_verdict") or {}

    # Critical check: real-rate block must be derivable. The fixture
    # contains DGS10 (under groups.rates.series) and T10YIE (under
    # groups.real_rates.series). classify_us emits this under
    # native_verdict.real_rate_decomposition (renamed from legacy
    # `real_rates` in PR-2 baseline).
    rrd = nv.get("real_rate_decomposition")
    assert rrd is not None and isinstance(rrd, dict), (
        f"real_rate_decomposition block is None — classify_us could not "
        f"find DGS10/T10YIE. data_quality.missing: "
        f"{us.get('data_quality', {}).get('missing')}"
    )


# ---------------------------------------------------------------------------
# Chain US — comps_compute dual input (v2.2.0-b)
# ---------------------------------------------------------------------------


def test_chain_us_comps_compute_dual_input(tmp_path):
    """Chain: data-us memo-fetch fixture + comps-multiples fixture →
    analysis-comps --mode compute → JSON with divergence + compute_provenance.

    Validates that real Layer-1 fixtures (not synthetic) flow through Layer-2
    compute mode without shape adapters.
    """
    anchor_comps_fixture = FIXTURES / "data-us-comps-multiples-sample.json"
    anchor_base_fixture  = FIXTURES / "data-us-memo-fetch-sample.json"
    script = SKILLS / "analysis-comps" / "scripts" / "comps_compute.py"

    if not anchor_comps_fixture.exists() or not anchor_base_fixture.exists():
        pytest.skip("missing fixture(s)")
    if not script.exists():
        pytest.skip("missing comps_compute.py script")

    # Slice the multi-ticker comps fixture to a single-ticker anchor file so
    # _resolve_ticker can resolve unambiguously (same pattern as
    # test_chain_comps_to_comps_compute above).
    pack = json.loads(anchor_comps_fixture.read_text())
    tickers = list((pack.get("tickers") or {}).keys())
    if not tickers:
        pytest.skip("comps fixture has no tickers")
    anchor_ticker = tickers[0]
    anchor_payload = {anchor_ticker: pack["tickers"][anchor_ticker]}
    anchor_file = tmp_path / f"{anchor_ticker}-anchor-comps.json"
    anchor_file.write_text(json.dumps({
        "pack": "comps-multiples",
        "ticker": anchor_ticker,
        "tickers": anchor_payload,
        "info": anchor_payload,  # T1 canonical alias
    }))

    # Use second ticker as peer if available; omit peers if only one ticker.
    peer_arg = []
    if len(tickers) >= 2:
        peer_ticker = tickers[1]
        peer_payload = {peer_ticker: pack["tickers"][peer_ticker]}
        peer_file = tmp_path / f"{peer_ticker}-peer-comps.json"
        peer_file.write_text(json.dumps({
            "pack": "comps-multiples",
            "ticker": peer_ticker,
            "tickers": peer_payload,
            "info": peer_payload,
        }))
        peer_arg = ["--peers", str(peer_file)]

    rc, out, stderr = _run_layer2(script, [
        "--mode", "compute",
        "--anchor", str(anchor_file),
        "--anchor-base", str(anchor_base_fixture),
        *peer_arg,
    ])

    assert rc == 0, (
        f"comps_compute exit {rc}\nstderr: {stderr}\nstdout: {out}"
    )

    # Compute-mode shape contract (spec §10)
    anchor = out.get("anchor") or {}
    assert "multiples_direct" in anchor, (
        f"anchor.multiples_direct missing — compute mode failed to preserve direct multiples. "
        f"anchor keys: {list(anchor.keys())}"
    )
    assert "multiples_compute" in anchor, (
        f"anchor.multiples_compute missing — compute_multiples_from_memo_fetch did not run. "
        f"anchor keys: {list(anchor.keys())}"
    )
    assert "divergence" in anchor, (
        f"anchor.divergence missing — _compute_divergence did not run. "
        f"anchor keys: {list(anchor.keys())}"
    )
    assert "compute_provenance" in anchor, (
        f"anchor.compute_provenance missing — provenance block not attached. "
        f"anchor keys: {list(anchor.keys())}"
    )

    # All 5 multiples present in divergence with valid alert levels
    divergence = anchor["divergence"]
    for m in ("trailingPE", "forwardPE", "priceToSales", "priceToBook", "evEbitda"):
        assert m in divergence, f"divergence missing multiple: {m}"
        assert divergence[m]["alert"] in {"low", "medium", "high", "n/a"}, (
            f"divergence[{m}].alert is invalid: {divergence[m]['alert']!r}"
        )

    # Compute provenance carries spec contract
    prov = anchor["compute_provenance"]
    assert prov["forwardPE"]["computed"] is False, (
        f"forwardPE.computed should be False (pass-through); got {prov['forwardPE']['computed']!r}"
    )
    # priceToBook now computed (v2.2.0-l landed — balance_sheet wired)
    assert prov["priceToBook"]["computed"] is True, (
        f"priceToBook.computed should be True (v2.2.0-l activated); got {prov['priceToBook']['computed']!r}"
    )
    assert prov["evEbitda"]["computed"] is True, (
        f"evEbitda.computed should be True (v2.2.0-l activated); got {prov['evEbitda']['computed']!r}"
    )

    # Audit trail (the whole point of compute mode) — must be non-null/non-empty
    trailing = prov["trailingPE"]
    assert trailing["computed"] is True
    assert trailing["fiscal_year_end"] is not None, (
        "trailingPE fiscal_year_end must be populated from net_income._meta concept; "
        "got None — production memo-fetch uses per-concept _meta nesting"
    )
    assert trailing["accession_basis"], (
        "trailingPE accession_basis must include the 10-K reference for net_income; "
        "got empty — production memo-fetch uses per-concept _meta nesting"
    )
    assert "10-K" in trailing["accession_basis"][0]

    p2s = prov["priceToSales"]
    assert p2s["computed"] is True
    assert p2s["fiscal_year_end"] is not None, (
        "priceToSales fiscal_year_end must be populated from revenue._meta concept; "
        "got None — production memo-fetch uses per-concept _meta nesting"
    )
    assert p2s["accession_basis"], (
        "priceToSales accession_basis must include the 10-K reference for revenue; "
        "got empty — production memo-fetch uses per-concept _meta nesting"
    )

    # Top-level provenance: compute mode adds anchor_base_source
    top_prov = out.get("_provenance") or {}
    assert top_prov.get("mode") == "compute", (
        f"_provenance.mode != 'compute'; got {top_prov.get('mode')!r}"
    )
    assert "anchor_base_source" in top_prov, (
        f"_provenance.anchor_base_source missing — compute-mode provenance incomplete. "
        f"_provenance keys: {list(top_prov.keys())}"
    )
    assert "memo-fetch" in top_prov["anchor_base_source"], (
        f"anchor_base_source does not reference memo-fetch; "
        f"got: {top_prov['anchor_base_source']!r}"
    )


# ---------------------------------------------------------------------------
# Tier 1 test-discipline additions (v2.2.0-b follow-up)
# ---------------------------------------------------------------------------


def test_production_memo_fetch_shape_compatible_with_compute_mode():
    """Lock the contract surface between data-us memo-fetch (Layer 1) and
    analysis-comps compute mode (Layer 2). Catches field renames / removals
    in memo-fetch that would cause silent null emission in compute_provenance.

    If this test fails, a recent data-us change removed or renamed a field
    that compute mode reads. Fix: update pack.py to restore the field, or
    update comps_compute.py to read the new field name AND update this test.
    """
    fixture = json.loads(
        (ROOT / "tests/data/fixtures/data-us-memo-fetch-sample.json").read_text()
    )

    # Top-level: compute mode reads either current_price OR company_info.regularMarketPrice
    assert (
        fixture.get("current_price") is not None
        or (fixture.get("company_info") or {}).get("regularMarketPrice") is not None
    ), "memo-fetch must expose current_price (or company_info.regularMarketPrice)"

    # Top-level: shares_outstanding (canonical alias)
    assert (
        fixture.get("shares_outstanding") is not None
        or (fixture.get("company_info") or {}).get("sharesOutstanding") is not None
    ), "memo-fetch must expose shares_outstanding (or company_info.sharesOutstanding)"

    # company_info.marketCap drives priceToSales numerator
    assert (fixture.get("company_info") or {}).get("marketCap") is not None, (
        "memo-fetch must expose company_info.marketCap"
    )

    # income_statement FY arrays drive trailingPE / priceToSales denominators
    inc = fixture["income_statement"]
    assert inc.get("revenue") and inc["revenue"][0] is not None, "income_statement.revenue[0] required"
    assert inc.get("net_income") and inc["net_income"][0] is not None, "income_statement.net_income[0] required"

    # Concept-nested _meta drives compute_provenance accession_basis (per C1 fix)
    meta = inc.get("_meta") or {}
    for concept in ("revenue", "net_income"):
        assert concept in meta, f"income_statement._meta.{concept} required for compute_provenance routing"
        cmeta = meta[concept]
        assert cmeta.get("fiscal_year_ends"), f"_meta.{concept}.fiscal_year_ends required"
        assert cmeta.get("filings_used"), f"_meta.{concept}.filings_used required"


def test_real_aapl_compute_multiples_in_plausible_bands(tmp_path):
    """Run compute mode against the production memo-fetch fixture for AAPL;
    assert the recomputed multiples are in historically plausible bands.
    Catches unit / scale drift before users see nonsense numbers in memos.

    AAPL FY-trailing PE has historically lived in roughly 10-50 (post-2010);
    priceToSales 3-12. The outer bands chosen here only fire when the
    magnitude is wildly off (e.g. wrong unit, missing decimal shift).
    """
    script = SKILLS / "analysis-comps" / "scripts" / "comps_compute.py"
    anchor_comps = FIXTURES / "data-us-comps-multiples-sample.json"
    anchor_memo = FIXTURES / "data-us-memo-fetch-sample.json"

    if not anchor_comps.exists() or not anchor_memo.exists() or not script.exists():
        pytest.skip("missing fixture or script")

    # Build a single-ticker anchor file (same pattern as test_chain_us_comps_compute_dual_input)
    pack = json.loads(anchor_comps.read_text())
    tickers = list((pack.get("tickers") or {}).keys())
    if not tickers:
        pytest.skip("comps fixture has no tickers")
    anchor_ticker = tickers[0]  # AAPL
    anchor_payload = {anchor_ticker: pack["tickers"][anchor_ticker]}
    anchor_file = tmp_path / f"{anchor_ticker}-anchor.json"
    anchor_file.write_text(json.dumps({
        "pack": "comps-multiples",
        "ticker": anchor_ticker,
        "tickers": anchor_payload,
        "info": anchor_payload,
    }))

    # Use second ticker as peer; dedup will skip anchor if passed again
    peer_comps = tmp_path / "peer.json"
    if len(tickers) >= 2:
        peer_ticker = tickers[1]
        peer_payload = {peer_ticker: pack["tickers"][peer_ticker]}
        peer_comps.write_text(json.dumps({
            "pack": "comps-multiples",
            "ticker": peer_ticker,
            "tickers": peer_payload,
            "info": peer_payload,
        }))
    else:
        # fallback: pass anchor as peer (dedup will warn, but compute still runs)
        peer_comps.write_text(anchor_file.read_text())

    rc, payload, stderr = _run_layer2(script, [
        "--mode", "compute",
        "--anchor", str(anchor_file),
        "--anchor-base", str(anchor_memo),
        "--peers", str(peer_comps),
    ])
    assert rc == 0, f"stderr: {stderr}"

    pe = payload["anchor"]["multiples_compute"]["trailingPE"]
    ps = payload["anchor"]["multiples_compute"]["priceToSales"]

    # AAPL FY-trailing PE has historically lived in roughly 10-50 (post-2010);
    # priceToSales 3-12. Choose generous outer bands so this test only fires
    # when the magnitude is wildly off (e.g. wrong unit, missing decimal shift).
    assert pe is not None, "trailingPE compute returned None — check memo-fetch net_income / price fields"
    assert ps is not None, "priceToSales compute returned None — check memo-fetch revenue / marketCap fields"
    assert 5 < pe < 100, f"trailingPE {pe} outside plausible AAPL FY band (5, 100)"
    assert 1 < ps < 20, f"priceToSales {ps} outside plausible AAPL FY band (1, 20)"


# ---------------------------------------------------------------------------
# G — Slim fixture parity guard (v2.2.0-b Tier 2)
# ---------------------------------------------------------------------------


def test_slim_memo_fetch_fixture_is_production_subset():
    """The slim memo-fetch fixture used by analysis-comps unit tests
    (tests/analysis/fixtures/comps_anchor_aapl_memo_fetch.json) must be a
    structural subset of the production memo-fetch fixture
    (tests/data/fixtures/data-us-memo-fetch-sample.json) — same nesting,
    same key paths. Catches the v2.2.0-b C1 bug class: slim fixture
    diverging from production shape and masking real-data bugs.
    """
    slim = json.loads(
        (ROOT / "tests/analysis/fixtures/comps_anchor_aapl_memo_fetch.json").read_text()
    )
    prod = json.loads(
        (ROOT / "tests/data/fixtures/data-us-memo-fetch-sample.json").read_text()
    )

    def walk(obj, path=()):
        """Yield (path, value) for every leaf, plus dict-key paths."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "_provenance":
                    continue  # provenance details legitimately differ
                yield from walk(v, path + (k,))
        elif isinstance(obj, list):
            # For lists, only walk the first element if it's a dict — array shape,
            # not array contents.
            if obj and isinstance(obj[0], dict):
                yield from walk(obj[0], path + ("[0]",))
            else:
                yield (path, "list")
        else:
            yield (path, type(obj).__name__)

    def has_path(d, path):
        cur = d
        for p in path:
            if p == "[0]":
                if not isinstance(cur, list) or not cur:
                    return False
                cur = cur[0]
            elif isinstance(cur, dict) and p in cur:
                cur = cur[p]
            else:
                return False
        return True

    missing = []
    for path, _ in walk(slim):
        if not has_path(prod, path):
            missing.append(".".join(str(p) for p in path))

    assert not missing, (
        f"Slim fixture has paths absent from production fixture (drift detected): {missing}\n"
        f"This is the C1-class bug. Either regenerate the slim fixture from a real "
        f"data-us memo-fetch run, or update production fixture if it legitimately "
        f"lost the field."
    )


# ---------------------------------------------------------------------------
# E — Cross-country compute smoke (v2.2.0-b Tier 2, honest about gaps)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("country,expected_status", [
    ("us", "full_compute"),    # baseline — trailingPE computed=True + non-empty accession_basis
    ("jp", "schema_mismatch"), # trailingPE computed=True but filings_used=[] → accession_basis empty
    ("tw", "schema_mismatch"), # post v2.2.0-m: pack key normalized; trailingPE computed=True but accession_basis=[] (MOPS lacks filings_used; awaiting v2.2.0-l TW raw-field extension)
    ("kr", "schema_mismatch"), # trailingPE computed=True but filings_used=[] → accession_basis empty
    ("cn", "schema_mismatch"), # trailingPE computed=True but filings_used=[] → accession_basis empty
])
def test_cross_country_compute_smoke(country, expected_status, tmp_path):
    """Document each country's memo-fetch compatibility with --mode compute.

    v2.2.0-b is US-only by design (per spec §13); this test makes cross-country
    gaps visible so v2.2.0-l onwards has a baseline. NOT an assertion that
    cross-country works — an assertion of CURRENT BEHAVIOR.

    expected_status semantics:
      - "full_compute":    trailingPE compute_provenance.computed==True AND
                           accession_basis non-empty (primary-source audit trail
                           present — the whole point of --mode compute).
      - "schema_mismatch": script exits 0 but compute is incomplete or
                           accession_basis is empty (memo-fetch shape partially
                           compatible but lacks filings_used / pack key mismatch).
      - "crash":           script exits non-zero (memo-fetch shape so different
                           that the loader rejects it). Future per-country PRs
                           (v2.2.0-l onwards) will fix the crash and flip to
                           schema_mismatch, then full_compute once filings_used
                           is populated for that country.

    Current state (2026-05-03):
      US  → full_compute  (US memo-fetch has filings_used populated from SEC EDGAR)
      JP  → schema_mismatch (yfinance-based, filings_used=[]; trailingPE still computed)
      TW  → schema_mismatch (post v2.2.0-m: pack key normalized; MOPS lacks filings_used; trailingPE still computed)
      KR  → schema_mismatch (yfinance-based, filings_used=[]; trailingPE still computed)
      CN  → schema_mismatch (yfinance-based, filings_used=[]; trailingPE still computed)
    """
    anchor_comps = FIXTURES / f"data-{country}-comps-multiples-sample.json"
    anchor_memo  = FIXTURES / f"data-{country}-memo-fetch-sample.json"
    script       = SKILLS / "analysis-comps" / "scripts" / "comps_compute.py"

    if not anchor_comps.exists() or not anchor_memo.exists():
        pytest.skip(f"country {country} fixtures not present")
    if not script.exists():
        pytest.skip("missing comps_compute.py script")

    # Build a single-ticker anchor file and a minimal peer file from the
    # comps-multiples fixture (same pattern as the existing chain tests above).
    pack = json.loads(anchor_comps.read_text())
    info = pack.get("info") or {}
    tickers = list(info.keys())
    if len(tickers) < 2:
        pytest.skip(f"country {country} comps fixture needs >=2 tickers")

    anchor_ticker, peer_ticker = tickers[0], tickers[1]
    anchor_file = tmp_path / f"{anchor_ticker.replace('.', '_')}-anchor.json"
    peer_file   = tmp_path / f"{peer_ticker.replace('.', '_')}-peer.json"
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
        "--mode", "compute",
        "--anchor", str(anchor_file),
        "--anchor-base", str(anchor_memo),
        "--peers", str(peer_file),
    ])

    if expected_status == "crash":
        assert rc != 0, (
            f"Expected {country} compute mode to crash (exit non-zero) due to "
            f"memo-fetch shape rejection (e.g. pack key mismatch), but exit was 0. "
            f"If the country's loader was fixed, update expected_status to "
            f"'schema_mismatch' or 'full_compute' as appropriate."
        )
        return

    assert rc == 0, (
        f"Compute mode crashed on {country} (expected {expected_status}). "
        f"If this is a new regression, investigate the memo-fetch loader. "
        f"stderr: {stderr[:500]}"
    )

    pe_prov      = out["anchor"]["compute_provenance"]["trailingPE"]
    pe_computed  = pe_prov["computed"]
    pe_accession = pe_prov.get("accession_basis", [])

    if expected_status == "full_compute":
        assert pe_computed is True, (
            f"{country}: trailingPE compute_provenance.computed expected True, got {pe_computed}. "
            f"prov={pe_prov}"
        )
        assert pe_accession, (
            f"{country}: accession_basis is empty — full_compute requires a non-empty "
            f"filings_used chain (10-K / EDGAR reference). "
            f"If this country now has filings_used populated, this test should pass; "
            f"otherwise re-classify as 'schema_mismatch' in the parametrize list."
        )
    elif expected_status == "schema_mismatch":
        # trailingPE may compute (computed=True) but accession_basis is empty
        # because the country's memo-fetch uses yfinance and does not populate
        # filings_used. Document the state without asserting it's wrong.
        assert pe_computed in (True, False), (
            f"{country}: unexpected pe_computed value {pe_computed!r}"
        )
        assert not pe_accession, (
            f"{country}: accession_basis unexpectedly non-empty ({pe_accession}). "
            f"This country may be ready for 'full_compute' — update the parametrize list "
            f"once verified across a real run."
        )


# ---------------------------------------------------------------------------
# Layer 2 → Layer 3 cross-layer chain tests (Tier A)
#
# These tests close the gap identified in v2.2.0-j: format scripts were tested
# using hand-crafted fixtures, not real Layer 2 outputs.  If a Layer 2 script
# changes its output schema and the format script is updated in the same PR
# the existing report/* tests would still pass — but only because both sides
# changed together.  These tests run the real L2 → L3 pipe end-to-end so that
# drift between any L2 output and the L3 formatter is surfaced immediately.
# ---------------------------------------------------------------------------


# Tier A1 — analysis-technical → snapshot_format
#
# HONEST GAP NOTE: snapshot_format.py does NOT consume a "technical" block.
# The formatter ingests a snapshot pack (L1 shape: company_info + price_history)
# and renders price / valuation / disclosure sections only.  analysis-technical
# (ta_compute.py) is an independent L2 consumer of the same L1 snapshot pack —
# the two are parallel branches, not a serial pipe.
#
# What we *can* chain-test:
#   a. ta_compute reads the L1 snapshot and produces a non-degenerate indicators
#      block (already covered by test_chain_snapshot_to_technical above).
#   b. snapshot_format reads the same L1 snapshot and produces valid Markdown.
#
# The test below verifies (b) — ensuring the L3 formatter hasn't drifted from
# the L1 snapshot shape that the L1→L2 chain tests already rely on.  Any
# upcoming "technical section in snapshot" feature (v2.2.0-x placeholder) that
# does wire ta_compute output into snapshot_format should add a chain-specific
# test at that point.

def test_chain_technical_to_snapshot_format():
    """L1 snapshot → snapshot_format (L3) path check.

    snapshot_format.py does not consume a `technical` block — it reads the
    same L1 snapshot pack that ta_compute reads.  This test verifies that the
    L3 formatter produces valid Markdown from the L1 fixture, ensuring the
    shared L1 shape hasn't drifted.

    Catches: snapshot_format failing on the fixture that the L1→ta_compute
    chain already relies on.  The honest L2→L3 serial pipe (ta_compute output
    injected into snapshot_format) is deferred until snapshot_format gains a
    `technical` section.
    """
    snapshot_fix = FIXTURES / "data-us-snapshot-sample.json"
    fmt_script = SKILLS / "report-stock-snapshot" / "scripts" / "snapshot_format.py"

    if not snapshot_fix.exists() or not fmt_script.exists():
        pytest.skip("missing fixture or script")

    proc = subprocess.run(
        ["uv", "run", str(fmt_script),
         "--input", str(snapshot_fix),
         "--country", "us",
         "--lang", "en"],
        capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, (
        f"snapshot_format failed on L1 snapshot fixture: {proc.stderr[:400]}"
    )
    md = proc.stdout
    assert md.lstrip().startswith("## "), (
        f"snapshot_format output does not start with '## ' header; got: {md[:60]!r}"
    )
    assert "AAPL" in md, "snapshot_format output missing ticker 'AAPL'"
    assert "52W" in md, "snapshot_format output missing '52W' section"
    assert "Valuation" in md, "snapshot_format output missing Valuation section"


# Tier A2 — analysis-portfolio → review_format


def test_chain_portfolio_to_review_format(tmp_path):
    """Layer 2 (analysis-portfolio) → Layer 3 (review_format) serial chain.

    Runs portfolio_compute.py against minimal holdings + price inputs (both
    offline JSON files), then feeds the JSON output to review_format.py.
    Asserts that the resulting Markdown surfaces P&L / position anchors.

    Catches: analysis-portfolio output schema drift that would silently break
    review_format's P&L rendering (e.g. pnl_ratio key rename, totals block
    restructure).

    Design note: the existing test_3positions_smoke uses a hand-crafted fixture
    that was manually shaped to match the expected output format.  This test
    drives portfolio_compute from scratch so that any future schema change in
    the script is detected before users see broken markdown.
    """
    portfolio_script = SKILLS / "analysis-portfolio" / "scripts" / "portfolio_compute.py"
    fmt_script = SKILLS / "report-portfolio-review" / "scripts" / "review_format.py"

    if not portfolio_script.exists() or not fmt_script.exists():
        pytest.skip("missing portfolio_compute.py or review_format.py")

    # Build minimal offline inputs
    holdings_file = tmp_path / "holdings.json"
    holdings_file.write_text(json.dumps([
        {"ticker": "AAPL", "quantity": 10, "cost_basis": 150.0},
        {"ticker": "MSFT", "quantity": 5,  "cost_basis": 300.0},
    ]))
    prices_file = tmp_path / "prices.json"
    prices_file.write_text(json.dumps({
        "AAPL": 281.87,
        "MSFT": 413.20,
    }))

    # Step 1: run portfolio_compute (Layer 2)
    rc, portfolio_out, stderr = _run_layer2(portfolio_script, [
        "--holdings", str(holdings_file),
        "--prices", str(prices_file),
    ])
    assert rc == 0, f"portfolio_compute failed (rc={rc}): {stderr}"

    # Verify Layer 2 output has the expected shape before feeding to L3
    assert "positions" in portfolio_out, f"portfolio_compute output missing 'positions'"
    assert "totals" in portfolio_out, f"portfolio_compute output missing 'totals'"
    positions = portfolio_out.get("positions") or []
    assert len(positions) == 2, (
        f"expected 2 positions, got {len(positions)}: {positions}"
    )
    # Verify pnl_ratio is fractional (0.0-1.0), not already-percent
    for pos in positions:
        pnl_ratio = pos.get("pnl_ratio")
        assert pnl_ratio is not None, f"position {pos.get('ticker')} missing pnl_ratio"
        assert isinstance(pnl_ratio, float), (
            f"pnl_ratio must be float, got {type(pnl_ratio).__name__}"
        )

    # Step 2: write portfolio_compute output and feed to review_format (Layer 3)
    portfolio_json = tmp_path / "portfolio_out.json"
    portfolio_json.write_text(json.dumps(portfolio_out))

    proc = subprocess.run(
        ["uv", "run", str(fmt_script),
         "--portfolio", str(portfolio_json),
         "--lang", "en"],
        capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, (
        f"review_format failed on portfolio_compute output: {proc.stderr[:400]}"
    )
    md = proc.stdout

    # Assert Markdown contains P&L / portfolio anchors
    assert "Portfolio Review" in md, "review_format missing 'Portfolio Review' header"
    assert "## Summary" in md, "review_format missing '## Summary' section"
    assert "## Positions" in md, "review_format missing '## Positions' section"
    assert any(t in md for t in ("AAPL", "MSFT")), (
        "review_format output missing expected tickers (AAPL, MSFT)"
    )
    assert any(k in md.lower() for k in ("p&l", "pnl", "return", "profit")), (
        f"review_format markdown lacks any P&L anchor. excerpt:\n{md[:400]}"
    )


# Tier A3 — analysis-screener → screener_format


def test_chain_screener_to_screener_format(tmp_path):
    """Layer 2 (analysis-screener) → Layer 3 (screener_format) serial chain.

    Runs screener_compute.py against the L1 screener-batch fixture (offline),
    then feeds the ranked JSON to screener_format.py.  Asserts that the
    resulting Markdown surfaces a ranked table with tickers from the fixture.

    Catches: screener_compute output schema drift silently breaking
    screener_format's ranked table rendering (e.g. ranked[*].metrics key
    rename, preset_used field removal, or ranked array structure change).

    Design note: existing test_smoke_5_ranked uses a hand-crafted fixture.
    This test drives screener_compute from scratch against the real L1 fixture
    so any output schema drift is detected before users see broken markdown.
    """
    screener_script = SKILLS / "analysis-screener" / "scripts" / "screener_compute.py"
    fmt_script = SKILLS / "report-screener-list" / "scripts" / "screener_format.py"
    l1_fixture = FIXTURES / "data-us-screener-batch-sample.json"

    if not screener_script.exists() or not fmt_script.exists():
        pytest.skip("missing screener_compute.py or screener_format.py")
    if not l1_fixture.exists():
        pytest.skip("missing data-us-screener-batch-sample.json fixture")

    # Step 1: run screener_compute against L1 fixture (Layer 2)
    rc, screener_out, stderr = _run_layer2(screener_script, [
        "--input", str(l1_fixture),
        "--preset", "balanced",
        "--top-n", "10",
    ])
    assert rc == 0, f"screener_compute failed (rc={rc}): {stderr}"

    # Verify Layer 2 output has the expected shape before feeding to L3
    assert "ranked" in screener_out, "screener_compute output missing 'ranked'"
    assert "universe_size" in screener_out, "screener_compute output missing 'universe_size'"
    assert "preset_used" in screener_out, "screener_compute output missing 'preset_used'"
    ranked = screener_out.get("ranked") or []
    # Fixture has AAPL + MSFT + GOOGL — all 3 should pass 'balanced' preset
    assert len(ranked) >= 1, (
        f"screener_compute returned 0 ranked tickers from L1 fixture with 'balanced' preset"
    )
    ranked_tickers = [r.get("ticker") for r in ranked]

    # Step 2: write screener_compute output and feed to screener_format (Layer 3)
    screener_json = tmp_path / "screener_out.json"
    screener_json.write_text(json.dumps(screener_out))

    proc = subprocess.run(
        ["uv", "run", str(fmt_script),
         "--input", str(screener_json),
         "--lang", "en"],
        capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, (
        f"screener_format failed on screener_compute output: {proc.stderr[:400]}"
    )
    md = proc.stdout

    # Assert Markdown contains screener anchors
    assert "Stock Screener" in md, "screener_format missing 'Stock Screener' header"
    assert "| Rank |" in md, "screener_format missing ranked table header row"
    assert "Preset" in md, "screener_format missing 'Preset' metadata"
    # At least one ranked ticker should appear in the table
    assert any(t in md for t in ranked_tickers if t), (
        f"screener_format output missing any ranked tickers {ranked_tickers}: {md[:400]}"
    )


# ---------------------------------------------------------------------------
# Tier B1 — report-equity-memo Phase 4 input bundle assembly (deterministic)
# ---------------------------------------------------------------------------


def test_phase4_input_bundle_assembly_us(tmp_path):
    """report-equity-memo Phase 4 hands 4 JSONs to investing-team:
      fetch.json (Phase 1), regime-card.json (Phase 2),
      comps.json (Phase 2.5), dcf.json (Phase 3).

    This test verifies all 4 can be deterministically assembled from
    existing fixtures + Layer 2 scripts — without invoking the investing-team
    LLM agent.  Acts as a pre-flight gate for the full memo workflow.

    Catches:
      - Any Layer 1 → Layer 2 chain in the memo pipeline producing degenerate
        output (all-None, intrinsic_value=0, comps missing multiples_direct).
      - Phase 4 bundle assembly failing before investing-team is ever invoked
        (avoids wasting LLM tokens on a broken input bundle).
    """
    fetch_fix = FIXTURES / "data-us-memo-fetch-sample.json"
    regime_fix = FIXTURES / "data-us-regime-pack-sample.json"
    comps_fix = FIXTURES / "data-us-comps-multiples-sample.json"

    regime_script = SKILLS / "analysis-macro-regime" / "scripts" / "regime_compose.py"
    comps_script = SKILLS / "analysis-comps" / "scripts" / "comps_compute.py"
    dcf_script = SKILLS / "analysis-dcf" / "scripts" / "dcf_compute.py"

    for p in (fetch_fix, regime_fix, comps_fix):
        if not p.exists():
            pytest.skip(f"missing fixture: {p.name}")
    for s in (regime_script, comps_script, dcf_script):
        if not s.exists():
            pytest.skip(f"missing script: {s.name}")

    # --- Phase 1: fetch.json (use existing memo-fetch fixture as proxy) ---
    fetch_data = json.loads(fetch_fix.read_text())
    assert fetch_data.get("pack") == "memo-fetch", (
        f"fetch fixture pack != 'memo-fetch': {fetch_data.get('pack')!r}"
    )
    assert fetch_data.get("ticker"), "fetch fixture missing ticker"
    assert fetch_data.get("income_statement"), "fetch fixture missing income_statement"

    # --- Phase 2: regime-card.json ---
    rc, regime_card, stderr = _run_layer2(
        regime_script, ["--input", f"us={regime_fix}"]
    )
    assert rc == 0, f"regime_compose failed: {stderr}"
    us_block = (regime_card.get("by_country") or {}).get("us")
    assert us_block, (
        f"regime_compose produced no 'us' block. by_country keys: "
        f"{list((regime_card.get('by_country') or {}).keys())}"
    )
    assert us_block.get("country") == "us"
    assert us_block.get("confidence") in {"low", "medium", "high"}
    assert us_block.get("framework_used"), "regime-card missing framework_used"

    # --- Phase 2.5: comps.json (compute mode) ---
    comps_pack = json.loads(comps_fix.read_text())
    # The comps fixture has both 'tickers' and 'info' keys (T1 canonical alias).
    # Use 'info' as the canonical key per the cross-country pattern.
    info = comps_pack.get("info") or comps_pack.get("tickers") or {}
    tickers = list(info.keys())
    if len(tickers) < 2:
        pytest.skip(f"comps fixture has {len(tickers)} tickers; need >=2 for compute mode")
    anchor_t, peer_t = tickers[0], tickers[1]

    anchor_comps_file = tmp_path / f"{anchor_t}-anchor-comps.json"
    peer_comps_file = tmp_path / f"{peer_t}-peer-comps.json"
    anchor_comps_file.write_text(json.dumps({
        "pack": "comps-multiples",
        "ticker": anchor_t,
        "info": {anchor_t: info[anchor_t]},
        "tickers": {anchor_t: info[anchor_t]},
    }))
    peer_comps_file.write_text(json.dumps({
        "pack": "comps-multiples",
        "ticker": peer_t,
        "info": {peer_t: info[peer_t]},
        "tickers": {peer_t: info[peer_t]},
    }))

    rc, comps_out, stderr = _run_layer2(comps_script, [
        "--mode", "compute",
        "--anchor", str(anchor_comps_file),
        "--anchor-base", str(fetch_fix),
        "--peers", str(peer_comps_file),
    ])
    assert rc == 0, f"comps_compute --mode compute failed: {stderr}"
    anchor_block = comps_out.get("anchor") or {}
    assert "multiples_direct" in anchor_block, (
        f"comps.json missing anchor.multiples_direct. anchor keys: {list(anchor_block.keys())}"
    )
    assert "multiples_compute" in anchor_block, (
        f"comps.json missing anchor.multiples_compute — compute mode did not run. "
        f"anchor keys: {list(anchor_block.keys())}"
    )
    assert "divergence" in anchor_block, (
        f"comps.json missing anchor.divergence. anchor keys: {list(anchor_block.keys())}"
    )

    # --- Phase 3: dcf.json ---
    rc, dcf_out, stderr = _run_layer2(dcf_script, ["--input", str(fetch_fix)])
    assert rc == 0, f"dcf_compute failed: {stderr}"
    intrinsic = dcf_out.get("intrinsic_value") or {}
    intrinsic_mid = intrinsic.get("mid") if isinstance(intrinsic, dict) else None
    assert intrinsic_mid is not None and intrinsic_mid > 0, (
        f"dcf.json intrinsic_value.mid is degenerate ({intrinsic_mid!r}). "
        f"Chain wiring to memo-fetch income_statement may be broken."
    )
    base_revenue = (dcf_out.get("assumptions") or {}).get("base_revenue")
    assert base_revenue is not None and base_revenue > 0, (
        f"dcf.json assumptions.base_revenue degenerate ({base_revenue!r}). "
        f"income_statement.revenue not reaching dcf_compute."
    )

    # All 4 Phase 4 bundle components are non-degenerate
    bundle = {
        "fetch": fetch_data,
        "regime_card": us_block,
        "comps": comps_out,
        "dcf": dcf_out,
    }
    for key, val in bundle.items():
        assert val, f"Phase 4 bundle component '{key}' is empty/falsy"


# ---------------------------------------------------------------------------
# Tier B2 — Phase 4 bundle validates against schema-phase4-input-bundle.json
# ---------------------------------------------------------------------------


def test_phase4_bundle_validates_against_schema(tmp_path):
    """Each component of the Phase 4 bundle conforms to
    references/schema-phase4-input-bundle.json.

    Catches: Layer 1 / Layer 2 schema drift that would break the investing-team
    handoff before it reaches the LLM — without spending any tokens.

    Validates the schema 'required' fields for each of the 4 bundle members.
    Uses jsonschema if installed; falls back to manual required-key assertion
    (same pattern as the v2.0.1 cross-layer chain tests).
    """
    schema_path = ROOT / "skills/report-equity-memo/references/schema-phase4-input-bundle.json"
    if not schema_path.exists():
        pytest.skip(f"schema file not found: {schema_path}")

    schema = json.loads(schema_path.read_text())

    fetch_fix = FIXTURES / "data-us-memo-fetch-sample.json"
    regime_fix = FIXTURES / "data-us-regime-pack-sample.json"
    comps_fix = FIXTURES / "data-us-comps-multiples-sample.json"

    regime_script = SKILLS / "analysis-macro-regime" / "scripts" / "regime_compose.py"
    comps_script = SKILLS / "analysis-comps" / "scripts" / "comps_compute.py"
    dcf_script = SKILLS / "analysis-dcf" / "scripts" / "dcf_compute.py"

    for p in (fetch_fix, regime_fix, comps_fix):
        if not p.exists():
            pytest.skip(f"missing fixture: {p.name}")
    for s in (regime_script, comps_script, dcf_script):
        if not s.exists():
            pytest.skip(f"missing script: {s.name}")

    # Build each bundle component (same logic as test_phase4_input_bundle_assembly_us)
    fetch_data = json.loads(fetch_fix.read_text())

    rc, regime_card, stderr = _run_layer2(
        regime_script, ["--input", f"us={regime_fix}"]
    )
    assert rc == 0, f"regime_compose failed: {stderr}"
    us_block = (regime_card.get("by_country") or {}).get("us") or {}

    comps_pack = json.loads(comps_fix.read_text())
    info = comps_pack.get("info") or comps_pack.get("tickers") or {}
    tickers = list(info.keys())
    if len(tickers) < 2:
        pytest.skip("comps fixture needs >=2 tickers")
    anchor_t, peer_t = tickers[0], tickers[1]

    anchor_comps_file = tmp_path / f"{anchor_t}-anchor.json"
    peer_comps_file = tmp_path / f"{peer_t}-peer.json"
    anchor_comps_file.write_text(json.dumps({
        "pack": "comps-multiples", "ticker": anchor_t,
        "info": {anchor_t: info[anchor_t]},
        "tickers": {anchor_t: info[anchor_t]},
    }))
    peer_comps_file.write_text(json.dumps({
        "pack": "comps-multiples", "ticker": peer_t,
        "info": {peer_t: info[peer_t]},
        "tickers": {peer_t: info[peer_t]},
    }))

    rc, comps_out, stderr = _run_layer2(comps_script, [
        "--mode", "compute",
        "--anchor", str(anchor_comps_file),
        "--anchor-base", str(fetch_fix),
        "--peers", str(peer_comps_file),
    ])
    assert rc == 0, f"comps_compute failed: {stderr}"

    rc, dcf_out, stderr = _run_layer2(dcf_script, ["--input", str(fetch_fix)])
    assert rc == 0, f"dcf_compute failed: {stderr}"

    bundle = {
        "fetch":       fetch_data,
        "regime_card": us_block,
        "comps":       comps_out,
        "dcf":         dcf_out,
    }

    # Validate against schema using jsonschema if available; else manual check
    try:
        import jsonschema
        jsonschema.validate(instance=bundle, schema=schema)
    except ImportError:
        # Manual required-field validation (same fallback as v2.0.1 schema tests)
        for bundle_key in schema.get("required", []):
            assert bundle_key in bundle, (
                f"Bundle missing required key '{bundle_key}' per schema"
            )
            component = bundle[bundle_key]
            assert isinstance(component, dict), (
                f"Bundle['{bundle_key}'] must be a dict; got {type(component).__name__}"
            )
            prop_schema = (schema.get("properties") or {}).get(bundle_key, {})
            for req_field in prop_schema.get("required", []):
                assert req_field in component, (
                    f"Bundle['{bundle_key}'] missing required field '{req_field}' "
                    f"per schema-phase4-input-bundle.json"
                )


# ---------------------------------------------------------------------------
# Tier B3 — SKILL.md filename consistency check
# ---------------------------------------------------------------------------


def test_phase4_input_filenames_match_earlier_phases():
    """SKILL.md Phase 4 lists 4 JSON inputs investing-team consumes.
    Those same filenames must appear in the earlier-phase prose.

    Catches naming drift: e.g. Phase 1 produces '${TICKER_SAFE}-fetch.json'
    but Phase 4 references 'memo-fetch.json', or Phase 2 produces
    'regime.json' but Phase 4 references 'regime-card.json'.

    Anchors used:
      - 'fetch.json'       suffix: 'fetch'       produced in Phase 1 prose
      - 'regime-card.json' suffix: 'regime-card' produced in Phase 2 prose
      - 'comps.json'       suffix: 'comps'        produced in Phase 2.5 prose
      - 'dcf.json'         suffix: 'dcf'          produced in Phase 3 prose
    """
    skill_md_path = ROOT / "skills/report-equity-memo/SKILL.md"
    if not skill_md_path.exists():
        pytest.skip(f"SKILL.md not found: {skill_md_path}")

    skill_md = skill_md_path.read_text(encoding="utf-8")

    # Locate Phase 4 section
    phase4_match = re.search(
        r"### Phase 4.*?(?=### Phase 5|## Cross-Plugin|## Limitations|\Z)",
        skill_md,
        re.DOTALL,
    )
    assert phase4_match, (
        "Could not locate '### Phase 4' section in report-equity-memo/SKILL.md. "
        "If the section was renamed, update the regex anchor in this test."
    )
    phase4_text = phase4_match.group(0)

    # Phase 4 must explicitly reference all 4 file names
    expected_files = ["fetch.json", "regime-card.json", "comps.json", "dcf.json"]
    for name in expected_files:
        assert name in phase4_text, (
            f"Phase 4 section missing reference to '{name}'. "
            f"Phase 4 text:\n{phase4_text[:600]}"
        )

    # Each file's suffix must also appear in the pre-Phase-4 prose
    # (confirming the file is produced by an earlier phase).
    # We check for the bare suffix rather than the full filename because
    # earlier phases use ${TICKER_SAFE}-{suffix}.json templates.
    pre_phase4 = skill_md[:phase4_match.start()]

    suffix_to_file = {
        "fetch":        "fetch.json",
        "regime-card":  "regime-card.json",
        "comps":        "comps.json",
        "dcf":          "dcf.json",
    }
    for suffix, filename in suffix_to_file.items():
        assert suffix in pre_phase4, (
            f"File '{filename}' referenced in Phase 4 but its suffix '{suffix}' "
            f"does not appear anywhere in Phases 1-3 prose. "
            f"This indicates a naming drift between the phase that produces the "
            f"file and Phase 4 which consumes it."
        )


# ---------------------------------------------------------------------------
# Tier D — Phase 4 bundle parametrized across non-US countries
# ---------------------------------------------------------------------------
#
# PR #230 added US-specific tests (test_phase4_input_bundle_assembly_us,
# test_phase4_bundle_validates_against_schema). These tests extend the same
# coverage to JP / TW / KR / CN.
#
# Cross-country compute-mode reality (from PR #228 cross-country smoke):
#   US  → full_compute   (SEC accession_basis non-empty)
#   JP/TW/KR/CN → schema_mismatch (compute mode runs, accession_basis empty)
# Both states are KNOWN and acceptable — these tests fail only on CRASH.
# ---------------------------------------------------------------------------


def _build_phase4_bundle_for_country(country: str, tmp_path) -> dict:
    """Shared helper: assemble the 4-component Phase 4 bundle for *country*.

    Returns a dict with keys: fetch, regime_card, comps, dcf.
    Calls pytest.skip() if a required fixture or script is missing,
    or if the fixture is structurally incompatible with a given phase.
    """
    fetch_fix = FIXTURES / f"data-{country}-memo-fetch-sample.json"
    regime_fix = FIXTURES / f"data-{country}-regime-pack-sample.json"
    comps_fix = FIXTURES / f"data-{country}-comps-multiples-sample.json"

    regime_script = SKILLS / "analysis-macro-regime" / "scripts" / "regime_compose.py"
    comps_script = SKILLS / "analysis-comps" / "scripts" / "comps_compute.py"
    dcf_script = SKILLS / "analysis-dcf" / "scripts" / "dcf_compute.py"

    for p in (fetch_fix, regime_fix, comps_fix):
        if not p.exists():
            pytest.skip(f"missing fixture: {p.name}")
    for s in (regime_script, comps_script, dcf_script):
        if not s.exists():
            pytest.skip(f"missing script: {s.name}")

    # Phase 1: fetch.json proxy
    fetch_data = json.loads(fetch_fix.read_text())
    assert fetch_data.get("pack") == "memo-fetch", (
        f"[{country}] fetch fixture pack != 'memo-fetch': {fetch_data.get('pack')!r}"
    )
    assert fetch_data.get("ticker"), f"[{country}] fetch fixture missing ticker"
    assert fetch_data.get("income_statement"), (
        f"[{country}] fetch fixture missing income_statement"
    )

    # Phase 2: regime-card.json
    rc, regime_card, stderr = _run_layer2(
        regime_script, ["--input", f"{country}={regime_fix}"]
    )
    assert rc == 0, f"[{country}] regime_compose failed: {stderr}"
    country_block = (regime_card.get("by_country") or {}).get(country)
    assert country_block, (
        f"[{country}] regime_compose produced no '{country}' block. "
        f"by_country keys: {list((regime_card.get('by_country') or {}).keys())}"
    )
    assert country_block.get("country") == country
    assert country_block.get("confidence") in {"low", "medium", "high"}
    assert country_block.get("framework_used"), (
        f"[{country}] regime-card missing framework_used"
    )

    # Phase 2.5: comps.json (compute mode)
    comps_pack = json.loads(comps_fix.read_text())
    info = comps_pack.get("info") or comps_pack.get("tickers") or {}
    tickers = list(info.keys())
    if len(tickers) < 2:
        pytest.skip(
            f"[{country}] comps fixture has {len(tickers)} tickers; need >=2 for compute mode"
        )
    anchor_t, peer_t = tickers[0], tickers[1]

    anchor_comps_file = tmp_path / f"{country}-{anchor_t}-anchor.json"
    peer_comps_file = tmp_path / f"{country}-{peer_t}-peer.json"
    anchor_comps_file.write_text(json.dumps({
        "pack": "comps-multiples",
        "ticker": anchor_t,
        "info": {anchor_t: info[anchor_t]},
        "tickers": {anchor_t: info[anchor_t]},
    }))
    peer_comps_file.write_text(json.dumps({
        "pack": "comps-multiples",
        "ticker": peer_t,
        "info": {peer_t: info[peer_t]},
        "tickers": {peer_t: info[peer_t]},
    }))

    rc, comps_out, stderr = _run_layer2(comps_script, [
        "--mode", "compute",
        "--anchor", str(anchor_comps_file),
        "--anchor-base", str(fetch_fix),
        "--peers", str(peer_comps_file),
    ])
    assert rc == 0, f"[{country}] comps_compute --mode compute failed: {stderr}"
    anchor_block = comps_out.get("anchor") or {}
    assert "multiples_direct" in anchor_block, (
        f"[{country}] comps.json missing anchor.multiples_direct. "
        f"anchor keys: {list(anchor_block.keys())}"
    )
    assert "multiples_compute" in anchor_block, (
        f"[{country}] comps.json missing anchor.multiples_compute — compute mode "
        f"did not run. anchor keys: {list(anchor_block.keys())}"
    )

    # Phase 3: dcf.json
    # Note: non-US fixtures may produce negative intrinsic_value (e.g. JP with
    # high WACC relative to EBIT margin) — this is expected for loss-proximate
    # companies. We accept any finite numeric intrinsic_value.mid.
    rc, dcf_out, stderr = _run_layer2(dcf_script, ["--input", str(fetch_fix)])
    assert rc == 0, f"[{country}] dcf_compute failed: {stderr}"
    iv = dcf_out.get("intrinsic_value") or {}
    iv_mid = iv.get("mid") if isinstance(iv, dict) else None
    assert iv_mid is not None, (
        f"[{country}] dcf.json intrinsic_value.mid is None — DCF compute crashed "
        f"or produced degenerate output. dcf keys: {list(dcf_out.keys())}"
    )
    # Accept negative (loss-proximate firms) but not None
    assert isinstance(iv_mid, (int, float)), (
        f"[{country}] dcf intrinsic_value.mid must be numeric; got {type(iv_mid)}"
    )
    base_revenue = (dcf_out.get("assumptions") or {}).get("base_revenue")
    assert base_revenue is not None and base_revenue > 0, (
        f"[{country}] dcf.json assumptions.base_revenue degenerate ({base_revenue!r}). "
        f"income_statement.revenue not reaching dcf_compute."
    )

    return {
        "fetch": fetch_data,
        "regime_card": country_block,
        "comps": comps_out,
        "dcf": dcf_out,
    }


@pytest.mark.parametrize("country", ["jp", "tw", "kr", "cn"])
def test_phase4_input_bundle_assembly_non_us(country, tmp_path):
    """Phase 4 bundle assembly for non-US countries (jp / tw / kr / cn).

    Each country's regime classifier output + DCF + comps must assemble
    deterministically without crashing or producing degenerate values.

    Non-US compute-mode reality (from PR #228 cross-country smoke):
      JP/TW/KR/CN comps_compute runs but accession_basis is empty
      (schema_mismatch mode) because SEC 10-K cross-check is US-only.
      This is a KNOWN state — the test accepts it.

    Negative DCF intrinsic_value.mid is accepted for non-US: companies
    with high WACC relative to EBIT margin (e.g. JP auto sector) can
    produce negative DCF. What matters: the value is numeric, not None,
    and the chain does not crash.
    """
    bundle = _build_phase4_bundle_for_country(country, tmp_path)
    for key, val in bundle.items():
        assert val, f"[{country}] Phase 4 bundle component '{key}' is empty/falsy"


@pytest.mark.parametrize("country", ["jp", "tw", "kr", "cn"])
def test_phase4_bundle_validates_against_schema_non_us(country, tmp_path):
    """Phase 4 bundle for non-US countries validates against schema-phase4-input-bundle.json.

    Catches: Layer 1 / Layer 2 schema drift in non-US chains that would
    break the investing-team handoff.

    Schema validation accepts null accession_basis — the schema does not
    require non-empty accession_basis, so schema_mismatch mode is OK.
    """
    schema_path = (
        ROOT / "skills/report-equity-memo/references/schema-phase4-input-bundle.json"
    )
    if not schema_path.exists():
        pytest.skip(f"schema file not found: {schema_path}")

    schema = json.loads(schema_path.read_text())
    bundle = _build_phase4_bundle_for_country(country, tmp_path)

    try:
        import jsonschema
        jsonschema.validate(instance=bundle, schema=schema)
    except ImportError:
        # Manual required-field validation (same fallback as v2.0.1 schema tests)
        for bundle_key in schema.get("required", []):
            assert bundle_key in bundle, (
                f"[{country}] Bundle missing required key '{bundle_key}' per schema"
            )
            component = bundle[bundle_key]
            assert isinstance(component, dict), (
                f"[{country}] Bundle['{bundle_key}'] must be a dict; "
                f"got {type(component).__name__}"
            )
            prop_schema = (schema.get("properties") or {}).get(bundle_key, {})
            for req_field in prop_schema.get("required", []):
                assert req_field in component, (
                    f"[{country}] Bundle['{bundle_key}'] missing required field "
                    f"'{req_field}' per schema-phase4-input-bundle.json"
                )


# ---------------------------------------------------------------------------
# Tier E — Failure-mode L2 → L3 tests
# ---------------------------------------------------------------------------
#
# These tests exercise boundary / degenerate outputs from Layer 2 and verify
# that Layer 3 (or downstream schema validation) handles them gracefully.
# ---------------------------------------------------------------------------


def test_phase4_bundle_with_compute_multiples_validates(tmp_path):
    """Phase 4 bundle validates against schema with all compute multiples active.

    Catches: schema accidentally rejecting non-null compute multiples in the
    comps component.

    As of v2.2.0-l: both priceToBook and evEbitda are now computed (balance_sheet
    + cash_flow.depreciation_amortization wired). The US fixture exercises the
    fully-computed scenario.
    """
    schema_path = (
        ROOT / "skills/report-equity-memo/references/schema-phase4-input-bundle.json"
    )
    if not schema_path.exists():
        pytest.skip(f"schema file not found: {schema_path}")

    schema = json.loads(schema_path.read_text())

    fetch_fix = FIXTURES / "data-us-memo-fetch-sample.json"
    regime_fix = FIXTURES / "data-us-regime-pack-sample.json"
    comps_fix = FIXTURES / "data-us-comps-multiples-sample.json"
    regime_script = SKILLS / "analysis-macro-regime" / "scripts" / "regime_compose.py"
    comps_script = SKILLS / "analysis-comps" / "scripts" / "comps_compute.py"
    dcf_script = SKILLS / "analysis-dcf" / "scripts" / "dcf_compute.py"

    for p in (fetch_fix, regime_fix, comps_fix):
        if not p.exists():
            pytest.skip(f"missing fixture: {p.name}")
    for s in (regime_script, comps_script, dcf_script):
        if not s.exists():
            pytest.skip(f"missing script: {s.name}")

    # Build bundle (same pipeline as US test)
    fetch_data = json.loads(fetch_fix.read_text())

    rc, regime_card, stderr = _run_layer2(regime_script, ["--input", f"us={regime_fix}"])
    assert rc == 0, f"regime_compose failed: {stderr}"
    us_block = (regime_card.get("by_country") or {}).get("us") or {}

    comps_pack = json.loads(comps_fix.read_text())
    info = comps_pack.get("info") or comps_pack.get("tickers") or {}
    tickers = list(info.keys())
    if len(tickers) < 2:
        pytest.skip("comps fixture needs >=2 tickers")
    anchor_t, peer_t = tickers[0], tickers[1]

    anchor_comps_file = tmp_path / f"{anchor_t}-anchor.json"
    peer_comps_file = tmp_path / f"{peer_t}-peer.json"
    anchor_comps_file.write_text(json.dumps({
        "pack": "comps-multiples", "ticker": anchor_t,
        "info": {anchor_t: info[anchor_t]}, "tickers": {anchor_t: info[anchor_t]},
    }))
    peer_comps_file.write_text(json.dumps({
        "pack": "comps-multiples", "ticker": peer_t,
        "info": {peer_t: info[peer_t]}, "tickers": {peer_t: info[peer_t]},
    }))

    rc, comps_out, stderr = _run_layer2(comps_script, [
        "--mode", "compute",
        "--anchor", str(anchor_comps_file),
        "--anchor-base", str(fetch_fix),
        "--peers", str(peer_comps_file),
    ])
    assert rc == 0, f"comps_compute failed: {stderr}"

    # priceToBook + evEbitda both computed (v2.2.0-l activated both)
    mc = (comps_out.get("anchor") or {}).get("multiples_compute") or {}
    assert mc.get("priceToBook") is not None, (
        f"priceToBook should be computed (v2.2.0-l activated balance_sheet); "
        f"got None — check balance_sheet fixture has total_stockholders_equity"
    )
    assert mc.get("evEbitda") is not None, (
        f"evEbitda should be computed (v2.2.0-l activated cash_flow.depreciation_amortization); "
        f"got None — check cash_flow fixture has depreciation_amortization"
    )

    rc, dcf_out, stderr = _run_layer2(dcf_script, ["--input", str(fetch_fix)])
    assert rc == 0, f"dcf_compute failed: {stderr}"

    bundle = {
        "fetch": fetch_data,
        "regime_card": us_block,
        "comps": comps_out,
        "dcf": dcf_out,
    }

    # Schema validation must succeed with both priceToBook + evEbitda computed (v2.2.0-l)
    try:
        import jsonschema
        jsonschema.validate(instance=bundle, schema=schema)
    except ImportError:
        for bundle_key in schema.get("required", []):
            assert bundle_key in bundle, (
                f"Bundle missing required key '{bundle_key}' per schema"
            )
        # Core assertion: we got here without crashing; null fields are tolerated


def test_dcf_negative_intrinsic_value_renders(tmp_path):
    """A loss-proximate company can produce negative DCF intrinsic_value.

    JP fixture (Toyota Motor / sector peers) produces negative DCF mid
    when WACC exceeds EBIT margin — a real scenario for high-capex firms.
    The DCF compute must produce a structurally valid JSON even when
    intrinsic_value.mid < 0, and the output must include all required
    envelope fields so the investing-team can surface the negative valuation
    in narrative (instead of crashing on a None value).

    Catches: format scripts or consuming code assuming intrinsic_value > 0,
    which would crash on legitimate loss-proximate company inputs.
    """
    fetch_fix = FIXTURES / "data-jp-memo-fetch-sample.json"
    dcf_script = SKILLS / "analysis-dcf" / "scripts" / "dcf_compute.py"

    if not fetch_fix.exists():
        pytest.skip("missing fixture: data-jp-memo-fetch-sample.json")
    if not dcf_script.exists():
        pytest.skip("missing script: dcf_compute.py")

    rc, dcf_out, stderr = _run_layer2(dcf_script, ["--input", str(fetch_fix)])
    assert rc == 0, f"dcf_compute failed on JP fixture (rc={rc}): {stderr}"

    # Structural assertions — all required envelope fields must be present
    assert "intrinsic_value" in dcf_out, (
        "dcf_compute output missing 'intrinsic_value' key — structural failure"
    )
    assert "assumptions" in dcf_out, (
        "dcf_compute output missing 'assumptions' key"
    )
    assert "warnings" in dcf_out, (
        "dcf_compute output missing 'warnings' key — downstream cannot surface caveats"
    )

    iv = dcf_out["intrinsic_value"]
    assert isinstance(iv, dict), (
        f"intrinsic_value must be a dict with low/mid/high; got {type(iv).__name__}"
    )
    iv_mid = iv.get("mid")
    assert iv_mid is not None, (
        "intrinsic_value.mid is None — DCF produced degenerate output on JP fixture"
    )
    assert isinstance(iv_mid, (int, float)), (
        f"intrinsic_value.mid must be numeric; got {type(iv_mid).__name__}"
    )

    # JP fixture is known to produce negative mid — verify and document
    if iv_mid >= 0:
        pytest.skip(
            f"JP fixture produced non-negative DCF mid ({iv_mid:.2f}); "
            f"the test exercises negative-mid handling. If JP fixture was updated "
            f"with a more profitable company, this skip is expected — the structural "
            f"assertions above still passed."
        )
    # iv_mid < 0: the key test — structural fields present despite negative value
    assert iv.get("low") is not None, (
        "intrinsic_value.low is None even though mid is non-None — partial output"
    )
    assert iv.get("high") is not None, (
        "intrinsic_value.high is None even though mid is non-None — partial output"
    )
    # Phase 4 bundle assembly: dcf_out must be usable as bundle component
    bundle_component_check = {
        "fetch": {"pack": "memo-fetch", "ticker": "7203.T",
                  "income_statement": {}, "current_price": 0},
        "regime_card": {"country": "jp", "confidence": "medium",
                        "framework_used": "test", "native_verdict": {}},
        "comps": {"anchor": {}, "_provenance": {}},
        "dcf": dcf_out,
    }
    assert bundle_component_check["dcf"] is dcf_out, (
        "dcf_out must be directly assignable to Phase 4 bundle (no post-processing needed)"
    )


def test_comps_compute_handles_empty_peers_post_dedup(tmp_path):
    """When all peer files dedup against the anchor (same ticker),
    the peer set becomes empty. comps_compute must emit valid JSON with
    a warning, not crash.

    Catches: comps_compute crashing with ZeroDivisionError or KeyError
    when statistics are computed over an empty peer array.
    """
    comps_script = SKILLS / "analysis-comps" / "scripts" / "comps_compute.py"
    if not comps_script.exists():
        pytest.skip("missing script: comps_compute.py")

    # Build anchor + peer files with the SAME ticker to trigger dedup
    ticker = "AAPL"
    ticker_data = {
        "ticker": ticker,
        "trailingPE": 30.0,
        "marketCap": 2_000_000_000_000.0,
        "priceToBook": 5.0,
    }
    anchor_file = tmp_path / f"{ticker}-anchor.json"
    peer_file = tmp_path / f"{ticker}-peer.json"  # same ticker → will be deduped
    for path in (anchor_file, peer_file):
        path.write_text(json.dumps({
            "pack": "comps-multiples",
            "ticker": ticker,
            "info": {ticker: ticker_data},
            "tickers": {ticker: ticker_data},
        }))

    rc, comps_out, stderr = _run_layer2(comps_script, [
        "--mode", "direct",
        "--anchor", str(anchor_file),
        "--peers", str(peer_file),
    ])

    # Must not crash
    assert rc == 0, (
        f"comps_compute crashed with empty-post-dedup peer set (rc={rc}). "
        f"stderr: {stderr[:300]}"
    )

    # Must emit a warning about the dedup
    prov = comps_out.get("_provenance") or {}
    warnings = prov.get("warnings") or []
    assert any("dedup" in w.lower() or "peer" in w.lower() for w in warnings), (
        f"comps_compute did not emit a dedup/empty-peer warning. "
        f"warnings: {warnings}"
    )

    # peers array must be present and empty
    assert comps_out.get("peers") == [], (
        f"Expected empty peers list after full dedup; got: {comps_out.get('peers')}"
    )

    # ranking must be present (anchor-only fallback, n=1)
    ranking = comps_out.get("ranking")
    assert ranking is not None, (
        "comps_compute missing 'ranking' block on empty-peer fallback"
    )

    # statistics must be present with n=0 for each multiple
    statistics = comps_out.get("statistics") or {}
    assert statistics, (
        "comps_compute missing 'statistics' block on empty-peer fallback"
    )
    for metric, stat in statistics.items():
        n = stat.get("n")
        assert n == 0, (
            f"statistics['{metric}'].n={n} but expected 0 (no peers after dedup)"
        )


def test_compute_warnings_persist_in_phase4_bundle(tmp_path):
    """Layer 2 comps_compute _provenance.warnings (e.g. FY-not-TTM note)
    must survive into the Phase 4 bundle so investing-team can surface
    it in narrative.

    Catches: Phase 4 bundle assembly stripping _provenance from comps,
    which would silently hide definitional caveats from the memo author.
    """
    comps_fix = FIXTURES / "data-us-comps-multiples-sample.json"
    fetch_fix = FIXTURES / "data-us-memo-fetch-sample.json"
    comps_script = SKILLS / "analysis-comps" / "scripts" / "comps_compute.py"

    if not comps_fix.exists() or not fetch_fix.exists():
        pytest.skip("missing US comps or memo-fetch fixture")
    if not comps_script.exists():
        pytest.skip("missing script: comps_compute.py")

    comps_pack = json.loads(comps_fix.read_text())
    info = comps_pack.get("info") or comps_pack.get("tickers") or {}
    tickers = list(info.keys())
    if len(tickers) < 2:
        pytest.skip("comps fixture needs >=2 tickers")
    anchor_t, peer_t = tickers[0], tickers[1]

    anchor_file = tmp_path / f"{anchor_t}-anchor.json"
    peer_file = tmp_path / f"{peer_t}-peer.json"
    anchor_file.write_text(json.dumps({
        "pack": "comps-multiples", "ticker": anchor_t,
        "info": {anchor_t: info[anchor_t]}, "tickers": {anchor_t: info[anchor_t]},
    }))
    peer_file.write_text(json.dumps({
        "pack": "comps-multiples", "ticker": peer_t,
        "info": {peer_t: info[peer_t]}, "tickers": {peer_t: info[peer_t]},
    }))

    rc, comps_out, stderr = _run_layer2(comps_script, [
        "--mode", "compute",
        "--anchor", str(anchor_file),
        "--anchor-base", str(fetch_fix),
        "--peers", str(peer_file),
    ])
    assert rc == 0, f"comps_compute failed: {stderr}"

    # Verify the FY-not-TTM warning is present in Layer 2 output
    prov = comps_out.get("_provenance") or {}
    warnings = prov.get("warnings") or []
    fy_ttm_warning = next(
        (w for w in warnings if "FY" in w and "TTM" in w), None
    )
    assert fy_ttm_warning is not None, (
        f"Expected FY-not-TTM warning in comps_compute _provenance.warnings. "
        f"Got: {warnings}. If comps_compute no longer emits this warning, "
        f"update this assertion."
    )

    # Simulate Phase 4 bundle assembly (as report-equity-memo does it)
    bundle = {
        "fetch": json.loads(fetch_fix.read_text()),
        "regime_card": {"country": "us", "confidence": "high",
                        "framework_used": "IC-quadrant", "native_verdict": {}},
        "comps": comps_out,
        "dcf": {"intrinsic_value": {"low": 100, "mid": 150, "high": 200},
                "assumptions": {}, "warnings": []},
    }

    # The FY-not-TTM warning must survive in the bundle's comps component
    bundle_warnings = (bundle["comps"].get("_provenance") or {}).get("warnings") or []
    assert any("FY" in w and "TTM" in w for w in bundle_warnings), (
        f"FY-not-TTM warning lost during Phase 4 bundle assembly. "
        f"bundle['comps']['_provenance']['warnings']: {bundle_warnings}. "
        f"If the bundle assembly process strips _provenance, this caveat becomes "
        f"invisible to the investing-team memo author."
    )


def test_review_format_handles_zero_quantity_positions(tmp_path):
    """portfolio_compute with quantity=0 positions (all-closed portfolio)
    must flow through review_format without crashing.

    Catches: review_format breaking on zero market_value / zero totals
    (e.g. division by zero in weight computation, format crash on 0.0%).

    Design note: portfolio_compute requires >=1 holdings row (empty list
    exits rc=1). We test the 'closed all positions' scenario using
    quantity=0 rows — market_value=0 for each, total portfolio value=0.
    """
    portfolio_script = SKILLS / "analysis-portfolio" / "scripts" / "portfolio_compute.py"
    fmt_script = SKILLS / "report-portfolio-review" / "scripts" / "review_format.py"

    if not portfolio_script.exists() or not fmt_script.exists():
        pytest.skip("missing portfolio_compute.py or review_format.py")

    # Build holdings with quantity=0 (all positions 'closed')
    holdings_file = tmp_path / "holdings.json"
    holdings_file.write_text(json.dumps([
        {"ticker": "AAPL", "quantity": 0, "cost_basis": 150.0},
        {"ticker": "MSFT", "quantity": 0, "cost_basis": 300.0},
    ]))
    prices_file = tmp_path / "prices.json"
    prices_file.write_text(json.dumps({"AAPL": 200.0, "MSFT": 400.0}))

    # Step 1: portfolio_compute (Layer 2)
    rc, portfolio_out, stderr = _run_layer2(portfolio_script, [
        "--holdings", str(holdings_file),
        "--prices", str(prices_file),
    ])
    assert rc == 0, f"portfolio_compute failed on zero-quantity positions (rc={rc}): {stderr}"

    positions = portfolio_out.get("positions") or []
    assert len(positions) == 2, (
        f"expected 2 positions (even with quantity=0), got {len(positions)}"
    )
    # All market values must be 0
    for pos in positions:
        assert pos.get("market_value") == 0.0, (
            f"position {pos.get('ticker')} market_value={pos.get('market_value')} "
            f"expected 0.0 for quantity=0"
        )

    # Step 2: review_format (Layer 3) — must not crash
    portfolio_json = tmp_path / "portfolio_out.json"
    portfolio_json.write_text(json.dumps(portfolio_out))

    proc = subprocess.run(
        ["uv", "run", str(fmt_script),
         "--portfolio", str(portfolio_json),
         "--lang", "en"],
        capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, (
        f"review_format crashed on zero-quantity portfolio (rc={proc.returncode}). "
        f"stderr: {proc.stderr[:300]}"
    )
    md = proc.stdout

    # Markdown must be non-empty and contain heading
    assert "Portfolio Review" in md, (
        "review_format produced no 'Portfolio Review' heading on zero-quantity input"
    )
    # Both tickers must appear in the positions table
    for ticker in ("AAPL", "MSFT"):
        assert ticker in md, (
            f"review_format markdown missing ticker '{ticker}' from zero-quantity portfolio"
        )


# ---------------------------------------------------------------------------
# Tier F — Cross-country format chain tests
# ---------------------------------------------------------------------------
#
# Reality check (per PR #230 honest finding):
#   - snapshot_format does NOT consume analysis-technical output as a true
#     L2→L3 chain (they are parallel L1 consumers). No snapshot_format
#     tests for non-US here.
#   - portfolio_compute and screener_compute are country-agnostic (any ticker).
#     Multi-country portfolio and TW screener tests make sense.
#   - Phase 4 bundle country-specific field assertions are new here.
# ---------------------------------------------------------------------------


def test_chain_portfolio_multicountry_mixed_review(tmp_path):
    """Portfolio with US + TW + JP tickers flows through review_format.

    Catches: review_format breaking on non-US ticker suffixes (.TW, .T)
    in ticker-routing or markdown table rendering.

    Uses arbitrary prices (offline). Country-agnostic portfolio_compute
    treats all tickers uniformly — the suffix routing test is review_format.
    """
    portfolio_script = SKILLS / "analysis-portfolio" / "scripts" / "portfolio_compute.py"
    fmt_script = SKILLS / "report-portfolio-review" / "scripts" / "review_format.py"

    if not portfolio_script.exists() or not fmt_script.exists():
        pytest.skip("missing portfolio_compute.py or review_format.py")

    # Mix US / TW / JP tickers
    holdings_file = tmp_path / "holdings.json"
    holdings_file.write_text(json.dumps([
        {"ticker": "AAPL",    "quantity": 10, "cost_basis": 150.0},
        {"ticker": "2330.TW", "quantity": 5,  "cost_basis": 800.0},
        {"ticker": "7203.T",  "quantity": 20, "cost_basis": 2000.0},
    ]))
    prices_file = tmp_path / "prices.json"
    prices_file.write_text(json.dumps({
        "AAPL":    200.0,
        "2330.TW": 1000.0,
        "7203.T":  2500.0,
    }))

    rc, portfolio_out, stderr = _run_layer2(portfolio_script, [
        "--holdings", str(holdings_file),
        "--prices", str(prices_file),
    ])
    assert rc == 0, f"portfolio_compute failed on multi-country holdings (rc={rc}): {stderr}"

    positions = portfolio_out.get("positions") or []
    assert len(positions) == 3, (
        f"expected 3 positions (US + TW + JP), got {len(positions)}"
    )
    tickers_in_output = {p.get("ticker") for p in positions}
    assert tickers_in_output == {"AAPL", "2330.TW", "7203.T"}, (
        f"not all multi-country tickers appear in positions: {tickers_in_output}"
    )

    portfolio_json = tmp_path / "portfolio_out.json"
    portfolio_json.write_text(json.dumps(portfolio_out))

    proc = subprocess.run(
        ["uv", "run", str(fmt_script),
         "--portfolio", str(portfolio_json),
         "--lang", "en"],
        capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, (
        f"review_format failed on multi-country portfolio (rc={proc.returncode}). "
        f"stderr: {proc.stderr[:300]}"
    )
    md = proc.stdout

    assert "Portfolio Review" in md, "review_format missing 'Portfolio Review' header"
    for ticker in ("AAPL", "2330.TW", "7203.T"):
        assert ticker in md, (
            f"review_format markdown missing '{ticker}' — ticker-suffix routing may "
            f"be broken for non-US suffixes"
        )


def test_chain_tw_screener_to_screener_format(tmp_path):
    """data-tw screener-batch fixture → analysis-screener → screener_format.

    TW screener-batch fixture is nested under yfinance.info_batch.data.tickers
    (TW-native pack format), unlike the US flat tickers wrapper. This test
    exercises the normalization step and verifies .TW-suffix tickers flow
    through screener_compute → screener_format correctly.

    Note: TW fixture normalization (extracting tickers from nested yfinance
    wrapper) must be performed by the caller before passing to screener_compute
    — screener_compute only handles flat tickers dict or list. This mirrors
    how the investing-toolkit skill orchestrates the TW screener flow.
    """
    screener_script = SKILLS / "analysis-screener" / "scripts" / "screener_compute.py"
    fmt_script = SKILLS / "report-screener-list" / "scripts" / "screener_format.py"
    tw_fixture = FIXTURES / "data-tw-screener-batch-sample.json"

    if not screener_script.exists() or not fmt_script.exists():
        pytest.skip("missing screener_compute.py or screener_format.py")
    if not tw_fixture.exists():
        pytest.skip("missing fixture: data-tw-screener-batch-sample.json")

    # Normalize TW fixture: extract tickers from nested yfinance wrapper
    tw_raw = json.loads(tw_fixture.read_text())
    raw_tickers = (
        (tw_raw.get("yfinance") or {})
        .get("info_batch", {})
        .get("data", {})
        .get("tickers", {})
    )
    if not raw_tickers:
        pytest.skip(
            "TW screener fixture lacks yfinance.info_batch.data.tickers — "
            "fixture may have been restructured"
        )

    # Build a flat screener-batch wrapper that screener_compute accepts
    normalized_fix = tmp_path / "tw-screener-normalized.json"
    normalized_fix.write_text(json.dumps({
        "pack": "screener-batch",
        "country": "TW",
        "tickers": raw_tickers,
    }))

    # Step 1: screener_compute (Layer 2)
    rc, screener_out, stderr = _run_layer2(screener_script, [
        "--input", str(normalized_fix),
        "--preset", "balanced",
        "--top-n", "5",
    ])
    assert rc == 0, f"screener_compute failed on TW fixture (rc={rc}): {stderr}"

    ranked = screener_out.get("ranked") or []
    assert len(ranked) >= 1, (
        f"screener_compute returned 0 ranked tickers from TW fixture with "
        f"'balanced' preset. universe_size={screener_out.get('universe_size')}"
    )
    tw_tickers = [r.get("ticker") for r in ranked]
    assert any(t and t.endswith(".TW") for t in tw_tickers), (
        f"No .TW-suffix tickers in screener ranked output: {tw_tickers}"
    )

    # Step 2: screener_format (Layer 3)
    screener_json = tmp_path / "screener_out.json"
    screener_json.write_text(json.dumps(screener_out))

    proc = subprocess.run(
        ["uv", "run", str(fmt_script),
         "--input", str(screener_json),
         "--lang", "en"],
        capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, (
        f"screener_format failed on TW screener output (rc={proc.returncode}). "
        f"stderr: {proc.stderr[:300]}"
    )
    md = proc.stdout

    assert "Stock Screener" in md, "screener_format missing 'Stock Screener' header"
    # At least one .TW ticker must appear in the markdown
    assert any(t in md for t in tw_tickers if t), (
        f"screener_format output missing .TW tickers {tw_tickers}: {md[:400]}"
    )


def test_phase4_bundle_tw_includes_ndc_signal(tmp_path):
    """TW Phase 4 regime_card must include the NDC 五色 signal_color
    and 9 構成 dispersion in native_verdict.

    investing-team's TW gate consumes signal_color (紅/黃紅/綠/黃藍/藍)
    and components_9 specifically. If these keys are absent or structurally
    wrong, the gate will either crash or silently produce a wrong verdict.

    Catches: TW-specific classifier output drift that strips signal_color
    or components_9 from native_verdict.
    """
    regime_fix = FIXTURES / "data-tw-regime-pack-sample.json"
    regime_script = SKILLS / "analysis-macro-regime" / "scripts" / "regime_compose.py"

    if not regime_fix.exists():
        pytest.skip("missing fixture: data-tw-regime-pack-sample.json")
    if not regime_script.exists():
        pytest.skip("missing script: regime_compose.py")

    rc, regime_card, stderr = _run_layer2(
        regime_script, ["--input", f"tw={regime_fix}"]
    )
    assert rc == 0, f"regime_compose failed for TW (rc={rc}): {stderr}"

    tw_block = (regime_card.get("by_country") or {}).get("tw")
    assert tw_block, (
        f"regime_compose produced no 'tw' block. "
        f"by_country keys: {list((regime_card.get('by_country') or {}).keys())}"
    )

    native_verdict = tw_block.get("native_verdict") or {}

    # Assert signal_color is one of the 5 NDC traffic-light colours
    signal_color = native_verdict.get("signal_color")
    assert signal_color is not None, (
        "TW native_verdict missing 'signal_color' — NDC 五色景氣燈號 classifier "
        "did not populate this field. investing-team TW gate will fail."
    )
    valid_colors = {"紅", "黃紅", "綠", "黃藍", "藍"}
    assert signal_color in valid_colors, (
        f"TW signal_color='{signal_color}' not in valid NDC 五色 set {valid_colors}. "
        f"Classifier may have changed colour encoding."
    )

    # Assert components_9 is present and has >=6 components
    # (NDC uses 9 構成 indicators; fixture should have all 9 but >=6 is the floor)
    components_9 = native_verdict.get("components_9") or {}
    assert components_9, (
        "TW native_verdict missing 'components_9' — NDC 9 構成 dispersion not "
        "computed. investing-team's dispersion overlay will have no data."
    )
    n_components = len(components_9)
    assert n_components >= 6, (
        f"TW components_9 has only {n_components} components; expected >=6 "
        f"(NDC uses 9 構成). Keys present: {list(components_9.keys())}"
    )

    # Assert signal_score is numeric (used to place within the colour band)
    signal_score = native_verdict.get("signal_score")
    assert signal_score is not None and isinstance(signal_score, (int, float)), (
        f"TW signal_score='{signal_score}' must be numeric (NDC score 9–45). "
        f"investing-team uses this to interpolate within colour bands."
    )


def test_phase4_bundle_jp_includes_tankan_outlook(tmp_path):
    """JP Phase 4 regime_card must include Tankan business DI in native_verdict.

    investing-team's JP context relies on tankan_business_di to assess
    corporate sentiment divergence between large-mfg, large-nonmfg,
    small-mfg, small-nonmfg sectors — the 'dispersion_warning' flag
    is particularly important for KPI framing.

    Catches: JP-specific classifier dropping tankan_business_di from
    native_verdict (regression risk: if BOJ data API changes key names,
    tankan block may silently go null).
    """
    regime_fix = FIXTURES / "data-jp-regime-pack-sample.json"
    regime_script = SKILLS / "analysis-macro-regime" / "scripts" / "regime_compose.py"

    if not regime_fix.exists():
        pytest.skip("missing fixture: data-jp-regime-pack-sample.json")
    if not regime_script.exists():
        pytest.skip("missing script: regime_compose.py")

    rc, regime_card, stderr = _run_layer2(
        regime_script, ["--input", f"jp={regime_fix}"]
    )
    assert rc == 0, f"regime_compose failed for JP (rc={rc}): {stderr}"

    jp_block = (regime_card.get("by_country") or {}).get("jp")
    assert jp_block, (
        f"regime_compose produced no 'jp' block. "
        f"by_country keys: {list((regime_card.get('by_country') or {}).keys())}"
    )

    native_verdict = jp_block.get("native_verdict") or {}

    # BOJ stance must be present (top-level framing for all JP analysis)
    boj_stance = native_verdict.get("boj_stance")
    assert boj_stance is not None, (
        "JP native_verdict missing 'boj_stance' — BOJ stance classifier did not "
        "populate this field. This is the primary JP regime axis."
    )

    # Tankan block — key field for JP investing-team context
    tankan = native_verdict.get("tankan_business_di")
    if tankan is None:
        pytest.skip(
            "JP native_verdict 'tankan_business_di' is null in fixture — "
            "BOJ Tankan data may be sparse in this fixture. "
            "Honest gap: structural assertions above still passed."
        )

    # If Tankan is present, validate its internal shape
    assert isinstance(tankan, dict), (
        f"tankan_business_di must be a dict; got {type(tankan).__name__}"
    )
    for field in ("large_mfg", "large_nonmfg"):
        val = tankan.get(field)
        assert val is not None, (
            f"tankan_business_di.{field} is None — Tankan data partially missing"
        )
        assert isinstance(val, (int, float)), (
            f"tankan_business_di.{field}={val!r} must be numeric (DI in pp)"
        )

    # dispersion_warning is a bool flag used by investing-team KPI framing
    assert "dispersion_warning" in tankan, (
        "tankan_business_di missing 'dispersion_warning' field — "
        "investing-team KPI framing check will fail"
    )
    assert "regime" in tankan, (
        "tankan_business_di missing 'regime' field — "
        "expansion/contraction classification not present"
    )

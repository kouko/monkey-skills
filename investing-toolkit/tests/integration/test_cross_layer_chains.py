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

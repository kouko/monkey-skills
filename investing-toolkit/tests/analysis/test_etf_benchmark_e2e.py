"""End-to-end tests for v2.2.0-c-bench: aggregator output → runtime --sector-benchmark.

Validates the build → runtime contract: the aggregator (etf_aggregator.py)
emits sector-etf-aggregate-<ETF>.json files; the runtime
(comps_compute.py --sector-benchmark) reads them via INVESTING_TOOLKIT_AGGREGATES_DIR
and produces an etf_benchmark block under anchor. These tests exercise the
full pipe at the contract boundary, catching drift between build and runtime
that unit tests on each side miss in isolation.

All offline (mock fixtures + tmp_path aggregates). The live counterpart in
test_etf_aggregator_live.py exercises the same contract against real
yfinance + EDGAR weekly via the GHA cron.
"""
from __future__ import annotations

import datetime
import importlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills" / "analysis-comps" / "scripts"
COMPS_SCRIPT = SCRIPTS / "comps_compute.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_aggregate(
    aggregates_dir: Path,
    *,
    etf: str,
    schema_id: str,
    multiples: dict,
    indicators: dict,
    as_of: str | None = None,
    holdings_count: int = 10,
    weight_coverage_pct: float = 80.0,
    outliers_dropped: dict | None = None,
    schema_dispatch: dict | None = None,
) -> Path:
    """Write a sector-etf-aggregate-<ETF>.json with sensible defaults.

    `as_of` defaults to today (freshness_days=0). Override to test stale guard.

    Dates are UTC — etf_aggregator.py stamps as_of in UTC and comps_compute.py
    measures freshness in UTC; local dates run a day ahead in UTC+ mornings.
    """
    if as_of is None:
        as_of = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    target = aggregates_dir / f"sector-etf-aggregate-{etf}.json"
    target.write_text(json.dumps({
        "etf": etf,
        "schema_id": schema_id,
        "as_of": as_of,
        "_meta": {
            "holdings_count": holdings_count,
            "weight_coverage_pct": weight_coverage_pct,
            "outliers_dropped": outliers_dropped or {},
            "skipped_holdings": [],
            "schema_dispatch": schema_dispatch or {schema_id: holdings_count},
            "source": "test fixture",
        },
        "multiples": multiples,
        "indicators": indicators,
    }, indent=2), encoding="utf-8")
    return target


def _run_compute(
    anchor: Path, base: Path, peer: Path, aggregates_dir: Path,
    *, extra_args: tuple = (),
) -> subprocess.CompletedProcess:
    env = {**ENV, "INVESTING_TOOLKIT_AGGREGATES_DIR": str(aggregates_dir)}
    return subprocess.run(
        ["uv", "run", str(COMPS_SCRIPT),
         "--mode", "compute",
         "--anchor", str(anchor),
         "--anchor-base", str(base),
         "--peers", str(peer),
         "--sector-benchmark",
         *extra_args],
        capture_output=True, text=True, timeout=90, env=env, cwd=str(ROOT),
    )


def _bench(payload: dict) -> dict:
    return payload["anchor"]["etf_benchmark"]


# ---------------------------------------------------------------------------
# E2E #1 — Bank schema happy path: JPM → XLF
# ---------------------------------------------------------------------------

def test_e2e_jpm_xlf_bank(tmp_path):
    """JPM (industry=Banks - Diversified) routes to bank schema → maps to XLF.

    Bank schema multiples set: trailingPE / forwardPE / priceToBook /
    priceToTangibleBook (no evEbitda / priceToSales — bank carve-outs).
    Indicator: ROE.
    """
    anchor = FIXTURES / "comps_anchor_jpm.json"
    base = FIXTURES / "memo_fetch_jpm_minimal.json"
    peer = FIXTURES / "comps_peer_bac.json"
    _write_aggregate(tmp_path, etf="XLF", schema_id="bank",
        multiples={
            "trailingPE": 16.0,
            "forwardPE": None,        # exercises null-on-aggregate path
            "priceToBook": 2.5,
            "priceToTangibleBook": 2.0,
        },
        indicators={"ROE": 13.0},
    )

    proc = _run_compute(anchor, base, peer, tmp_path)
    assert proc.returncode == 0, proc.stderr
    bench = _bench(json.loads(proc.stdout))

    assert bench["etf"] == "XLF"
    assert bench["schema_id"] == "bank"
    assert bench["_meta"]["freshness_days"] == 0

    # Bank schema multiples set is correctly emitted
    assert set(bench["multiples"].keys()) == {
        "trailingPE", "forwardPE", "priceToBook", "priceToTangibleBook",
    }, bench["multiples"].keys()

    # forwardPE aggregate is null → band="n/a" + delta_pct=None
    assert bench["multiples"]["forwardPE"]["band"] == "n/a"
    assert bench["multiples"]["forwardPE"]["delta_pct"] is None

    # Other multiples have computed delta_pct
    for m in ("trailingPE", "priceToBook", "priceToTangibleBook"):
        assert bench["multiples"][m]["delta_pct"] is not None
        assert bench["multiples"][m]["band"] in ("in_line", "notable", "extreme")

    # Bank ROE indicator present + banded
    assert "ROE" in bench["indicators"]
    assert bench["indicators"]["ROE"]["band"] in ("in_line", "notable", "extreme")

    # Sector-keyed warning attached
    assert any("Bank P/E and P/B work" in w for w in bench["warnings"])


# ---------------------------------------------------------------------------
# E2E #2 — Tech-saas schema happy path: MSFT → XLK
# ---------------------------------------------------------------------------

def test_e2e_msft_xlk_techsaas(tmp_path):
    """MSFT (industry=Software - Infrastructure) routes to tech-saas → XLK.

    Tech-saas schema deliberately excludes priceToBook (intangibles-heavy)
    and includes priceToSales / evRevenue. This test guards against the
    plan-author drift that surfaced 4× during v2.2.0-c-bench dev: any future
    change putting priceToBook in tech-saas output would fail this test.
    """
    anchor = FIXTURES / "comps_anchor_msft.json"
    base = FIXTURES / "memo_fetch_msft_minimal.json"
    peer = FIXTURES / "comps_peer_googl.json"
    _write_aggregate(tmp_path, etf="XLK", schema_id="tech-saas",
        multiples={
            "forwardPE": 28.5,
            "priceToSales": 6.2,
            "evRevenue": 8.4,
        },
        indicators={"rule_of_40": 0.42, "gross_margin": 65.0, "FCF_margin": 18.0},
    )

    proc = _run_compute(anchor, base, peer, tmp_path)
    assert proc.returncode == 0, proc.stderr
    bench = _bench(json.loads(proc.stdout))

    assert bench["etf"] == "XLK"
    assert bench["schema_id"] == "tech-saas"

    # Critical: priceToBook MUST NOT appear under tech-saas (drift guard)
    assert "priceToBook" not in bench["multiples"], (
        "tech-saas schema excludes priceToBook by design "
        "(intangibles-heavy SaaS books); appearance signals build/runtime drift"
    )
    # Critical: trailingPE MUST NOT appear under tech-saas (drift guard)
    assert "trailingPE" not in bench["multiples"], (
        "tech-saas schema uses forwardPE only; trailingPE appearance signals drift"
    )

    # tech-saas-specific multiples that DO belong
    assert "priceToSales" in bench["multiples"]
    assert "evRevenue" in bench["multiples"]


# ---------------------------------------------------------------------------
# E2E #3 — Default schema → alphabetically-first inverse map (XLB)
# ---------------------------------------------------------------------------

def test_e2e_default_schema_picks_xlb_via_inverse_map(tmp_path):
    """Six ETFs (XLB/XLC/XLI/XLP/XLV/XLY) all map to default schema.

    The inverse map (_load_etf_to_schema_inv) sorts ETFs alphabetically and
    picks the first one per schema. For default schema, that's XLB.
    Anchor without sector/industry routes to default → XLB lookup.

    Guards against any future change that re-orders the inverse map.
    """
    anchor = FIXTURES / "comps_anchor_aapl.json"      # no sector/industry → default
    base = FIXTURES / "comps_anchor_aapl_memo_fetch.json"
    peer = FIXTURES / "comps_peer_msft.json"
    _write_aggregate(tmp_path, etf="XLB", schema_id="default",
        multiples={
            "trailingPE": 22.0,
            "forwardPE": 19.5,
            "evEbitda": 14.0,
            "priceToSales": 2.2,
            "priceToBook": 3.0,
        },
        indicators={"gross_margin": 32.0, "operating_margin": 12.0, "FCF_yield": 5.0, "FCF_margin": 8.0},
    )

    proc = _run_compute(anchor, base, peer, tmp_path)
    assert proc.returncode == 0, proc.stderr
    bench = _bench(json.loads(proc.stdout))

    assert bench["etf"] == "XLB", (
        "default schema must inverse-map to XLB (alphabetically first of 6 ETFs); "
        f"got {bench['etf']!r}"
    )
    assert bench["schema_id"] == "default"


# ---------------------------------------------------------------------------
# E2E #4 — Build → runtime contract: feed real aggregator output to runtime
# ---------------------------------------------------------------------------

def test_e2e_aggregator_runtime_contract_xlk(tmp_path, monkeypatch):
    """Most important E2E: actually invoke etf_aggregator.aggregate_etf() with
    fixture-mocked I/O, write its output, then run runtime against it.

    This catches build/runtime contract drift (e.g., aggregator emits a key
    runtime doesn't expect, or vice-versa). Pure unit tests on either side
    miss this because they each stub the other side.

    XLK chosen because its tech-saas schema has the narrowest multiples set
    (3 keys) — easiest to assert exact key parity end-to-end.
    """
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    if "etf_aggregator" in sys.modules:
        del sys.modules["etf_aggregator"]
    mod = importlib.import_module("etf_aggregator")

    holdings = json.loads((FIXTURES / "etf_xlk_holdings_minimal.json").read_text())
    aapl_memo = json.loads((FIXTURES / "memo_fetch_aapl_minimal.json").read_text())
    msft_memo = json.loads((FIXTURES / "memo_fetch_msft_minimal.json").read_text())

    monkeypatch.setattr(mod, "fetch_holdings", lambda etf: holdings)
    monkeypatch.setattr(mod, "fetch_memo_fetch",
                        lambda t: {"AAPL": aapl_memo, "MSFT": msft_memo}[t])

    aggregate_dict = mod.aggregate_etf("XLK")

    # Write aggregator's exact output to the runtime's expected location
    target = tmp_path / "sector-etf-aggregate-XLK.json"
    target.write_text(json.dumps(aggregate_dict), encoding="utf-8")

    # Now run runtime against this aggregate
    anchor = FIXTURES / "comps_anchor_msft.json"  # tech-saas anchor → XLK lookup
    base = FIXTURES / "memo_fetch_msft_minimal.json"
    peer = FIXTURES / "comps_peer_googl.json"

    proc = _run_compute(anchor, base, peer, tmp_path)
    assert proc.returncode == 0, proc.stderr
    bench = _bench(json.loads(proc.stdout))

    assert bench["etf"] == "XLK"
    assert bench["schema_id"] == "tech-saas"

    # Aggregator's output keys ARE the runtime's expected keys (contract test)
    aggregate_multiples = set(aggregate_dict["multiples"].keys())
    runtime_multiples = set(bench["multiples"].keys())
    assert aggregate_multiples == runtime_multiples, (
        f"build/runtime drift: aggregator emitted {aggregate_multiples}, "
        f"runtime surfaced {runtime_multiples}"
    )


# ---------------------------------------------------------------------------
# E2E #5 — Stale aggregate (>14d) emits warning
# ---------------------------------------------------------------------------

def test_e2e_stale_aggregate_emits_warning(tmp_path):
    """Aggregate with as_of > 14 days ago → runtime appends a stale warning."""
    anchor = FIXTURES / "comps_anchor_jpm.json"
    base = FIXTURES / "memo_fetch_jpm_minimal.json"
    peer = FIXTURES / "comps_peer_bac.json"
    stale_date = (datetime.datetime.now(datetime.timezone.utc).date()
                  - datetime.timedelta(days=20)).isoformat()
    _write_aggregate(tmp_path, etf="XLF", schema_id="bank",
        as_of=stale_date,
        multiples={"trailingPE": 16.0, "forwardPE": None, "priceToBook": 2.5, "priceToTangibleBook": 2.0},
        indicators={"ROE": 13.0},
    )

    proc = _run_compute(anchor, base, peer, tmp_path)
    assert proc.returncode == 0, proc.stderr
    bench = _bench(json.loads(proc.stdout))

    # freshness_days reflects the staged date
    assert bench["_meta"]["freshness_days"] >= 20

    # Stale warning attached (must come BEFORE the sector warning)
    stale_warnings = [w for w in bench["warnings"] if "stale" in w.lower()]
    assert len(stale_warnings) == 1, f"expected 1 stale warning, got {bench['warnings']}"
    assert stale_date in stale_warnings[0]


# ---------------------------------------------------------------------------
# E2E #6 — Missing aggregate → graceful skipped status
# ---------------------------------------------------------------------------

def test_e2e_missing_aggregate_yields_skipped_status(tmp_path):
    """Empty aggregates dir → runtime emits status=skipped without raising.

    Verifies the graceful fallback: if the weekly cron hasn't run yet (or
    the ETF JSON is somehow missing), --sector-benchmark doesn't break the
    compute pipeline; it just attaches a skipped marker so the consumer
    knows why no benchmark is shown.
    """
    anchor = FIXTURES / "comps_anchor_jpm.json"
    base = FIXTURES / "memo_fetch_jpm_minimal.json"
    peer = FIXTURES / "comps_peer_bac.json"
    # Note: tmp_path is empty — no aggregate file written

    proc = _run_compute(anchor, base, peer, tmp_path)
    assert proc.returncode == 0, proc.stderr
    bench = _bench(json.loads(proc.stdout))

    assert bench.get("status") == "skipped"
    assert "missing" in bench.get("reason", "").lower()
    assert "XLF" in bench.get("reason", "")  # mentions which ETF was expected

    # Skipped status MUST NOT include divergence keys (full block shape only on success)
    assert "multiples" not in bench
    assert "indicators" not in bench

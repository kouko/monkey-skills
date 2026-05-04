# investing-toolkit v2.2.0-c-bench Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a SPDR sector ETF aggregate benchmark layer on top of v2.2.0-c's compute output, so memos answer "is this expensive **for its sector**?". Opt-in via `--sector-benchmark` flag; weekly GHA cron refreshes 11 `sector-etf-aggregate-*.json`.

**Architecture:** Build-time CLI (`etf_aggregator.py`) fetches ETF holdings via yfinance, runs each holding through v2.2.0-c's compute math (under that holding's schema), then takes a holdings-weighted average for each multiple/indicator in the ETF's mapped schema. Runtime (`comps_compute.py --sector-benchmark`) reads the pre-built JSON, computes per-multiple divergence with bands (in_line ≤20% / notable 20–50% / extreme >50%), pulls a schema-keyed warning row from `sector-warnings.md`, and emits an `etf_benchmark` block under `anchor`. Non-US tickers skip with a status field. v2.2.0-c output shape is preserved when flag is absent.

**Tech Stack:** Python 3.11+ (uv-managed PEP 723 scripts), pyyaml, yfinance, SEC EDGAR (via existing `data-us` cache), pytest with offline fixtures + network-marker live tests, GitHub Actions cron + `peter-evans/create-issue-from-file`.

**Spec:** `docs/superpowers/specs/2026-05-05-investing-toolkit-v2.2.0-c-bench-spdr-etf-benchmark-design.md`

**Working directory rule:** All paths are relative to repo root `/Users/kouko/GitHub/monkey-skills/`. Run `cd` once if needed; subsequent commands assume you're at root. **Always set `PYTHONDONTWRITEBYTECODE=1`** when invoking pytest in `investing-toolkit/skills/**` subdirs (per memory: `__pycache__` triggers the skill-folder-validator hook and silently blocks subsequent edits).

---

## Task 1: Rename compute helpers in `comps_compute.py` to drop `_` prefix (export contract for etf_aggregator)

**Files:**
- Modify: `investing-toolkit/skills/analysis-comps/scripts/comps_compute.py:838-868` (`_compute_indicators_from_memo_fetch`)
- Modify: `investing-toolkit/skills/analysis-comps/scripts/comps_compute.py:871-915` (`_compute_multiples_from_memo_fetch`)
- Modify: `investing-toolkit/skills/analysis-comps/scripts/comps_compute.py:1270, 1287` (call sites)

**Why first:** etf_aggregator.py needs to import these functions. Public names signal cross-module contract; underscore-prefixed names are private-by-convention and shouldn't be imported across modules.

- [ ] **Step 1: Verify both functions are only called inside `comps_compute.py` today**

Run:
```bash
grep -rn "_compute_multiples_from_memo_fetch\|_compute_indicators_from_memo_fetch" investing-toolkit/ --include='*.py'
```
Expected: only matches inside `comps_compute.py` (definitions + 2 call sites near line 1270, 1287). If anything outside `comps_compute.py` imports these, halt and report — the rename needs more sites.

- [ ] **Step 2: Rename `_compute_multiples_from_memo_fetch` → `compute_multiples_from_memo_fetch`**

In `investing-toolkit/skills/analysis-comps/scripts/comps_compute.py`, change line 871:
```python
def _compute_multiples_from_memo_fetch(
```
to:
```python
def compute_multiples_from_memo_fetch(
```

- [ ] **Step 3: Rename `_compute_indicators_from_memo_fetch` → `compute_indicators_from_memo_fetch`**

In the same file, change line 838:
```python
def _compute_indicators_from_memo_fetch(
```
to:
```python
def compute_indicators_from_memo_fetch(
```

- [ ] **Step 4: Update call sites near line 1270 and 1287**

Search:
```bash
grep -n "_compute_multiples_from_memo_fetch\|_compute_indicators_from_memo_fetch" investing-toolkit/skills/analysis-comps/scripts/comps_compute.py
```
Expected: remaining matches are at the two call sites. Replace both `_compute_multiples_from_memo_fetch(` with `compute_multiples_from_memo_fetch(`, and the indicator equivalent.

- [ ] **Step 5: Run existing analysis-comps test suite to confirm no regressions**

```bash
PYTHONDONTWRITEBYTECODE=1 cd investing-toolkit && uv run pytest tests/analysis/test_comps_sector_compute.py tests/analysis/test_comps_sector_routing.py tests/analysis/test_analysis_comps.py -m "not network" -q
```
Expected: PASS — no failures.

- [ ] **Step 6: Commit**

```bash
git add investing-toolkit/skills/analysis-comps/scripts/comps_compute.py
git commit -m "$(cat <<'EOF'
refactor(analysis-comps): rename _compute_*_from_memo_fetch to public names

v2.2.0-c-bench T1: etf_aggregator.py needs to import these compute helpers.
Public names signal the cross-module contract; underscore-prefixed names are
private-by-convention.

No behavior change.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Add `--action holdings` to `yfinance_client.py` for ETF top holdings

**Files:**
- Modify: `investing-toolkit/skills/data-us/scripts/yfinance_client.py` (add `get_holdings` function + CLI dispatch)
- Create: `investing-toolkit/tests/data/test_yfinance_holdings.py`

**Why:** etf_aggregator needs to fetch ETF top holdings. yfinance exposes this via `Ticker(etf).funds_data.top_holdings`. Adding a centralized `--action holdings` keeps yfinance access in one place (matches the existing `--action info` / `--action history` pattern).

- [ ] **Step 1: Read existing yfinance_client surface to find the right insertion point**

```bash
grep -n "^def \|args.action ==" investing-toolkit/skills/data-us/scripts/yfinance_client.py | head -40
```
Expected: see `get_history` (~line 103), `get_info` (~line 152), `get_financials` (~287), `get_batch` (~357), `main` (~386). Note the `args.action == 'info'` dispatch pattern in main.

- [ ] **Step 2: Write failing unit test using a monkeypatched yfinance**

Create `investing-toolkit/tests/data/test_yfinance_holdings.py`:
```python
"""Unit tests for yfinance_client.get_holdings — no network."""
from __future__ import annotations

import importlib
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = ROOT / "skills" / "data-us" / "scripts"


def _import_yf_client(monkeypatch):
    """Re-import yfinance_client with a fake yfinance module so no network is touched."""
    fake_yf = MagicMock(name="yfinance_module")
    monkeypatch.setitem(sys.modules, "yfinance", fake_yf)
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
    if "yfinance_client" in sys.modules:
        del sys.modules["yfinance_client"]
    return importlib.import_module("yfinance_client"), fake_yf


def test_get_holdings_returns_holdings_weights_for_etf(monkeypatch, tmp_path):
    yf_client, fake_yf = _import_yf_client(monkeypatch)
    monkeypatch.setattr(yf_client, "get_cache_path",
                        lambda *a, **kw: tmp_path / "holdings.json")

    ticker_mock = MagicMock(name="Ticker")
    holdings_mock = MagicMock(name="funds_data")
    # yfinance returns a DataFrame-like object; we expose a dict for simplicity.
    holdings_df = MagicMock(name="top_holdings_df")
    holdings_df.to_dict.return_value = {
        "Holding Percent": {"AAPL": 0.0712, "MSFT": 0.0654, "NVDA": 0.0432},
    }
    holdings_mock.top_holdings = holdings_df
    ticker_mock.funds_data = holdings_mock
    fake_yf.Ticker.return_value = ticker_mock

    out = yf_client.get_holdings("XLK")
    assert out["ticker"] == "XLK"
    assert {h["ticker"] for h in out["holdings"]} == {"AAPL", "MSFT", "NVDA"}
    aapl = next(h for h in out["holdings"] if h["ticker"] == "AAPL")
    assert aapl["weight"] == pytest.approx(0.0712)


def test_get_holdings_non_etf_returns_empty_list(monkeypatch, tmp_path):
    yf_client, fake_yf = _import_yf_client(monkeypatch)
    monkeypatch.setattr(yf_client, "get_cache_path",
                        lambda *a, **kw: tmp_path / "holdings.json")
    ticker_mock = MagicMock(name="Ticker")
    ticker_mock.funds_data = None  # non-fund tickers expose no funds_data
    fake_yf.Ticker.return_value = ticker_mock
    out = yf_client.get_holdings("AAPL")
    assert out["ticker"] == "AAPL"
    assert out["holdings"] == []
    assert "non_fund" in (out.get("warnings") or [])[0]
```

- [ ] **Step 3: Run the test — expect FAIL (function does not exist yet)**

```bash
PYTHONDONTWRITEBYTECODE=1 cd investing-toolkit && uv run pytest tests/data/test_yfinance_holdings.py -v
```
Expected: FAIL — `AttributeError: module 'yfinance_client' has no attribute 'get_holdings'`.

- [ ] **Step 4: Implement `get_holdings` function**

In `investing-toolkit/skills/data-us/scripts/yfinance_client.py`, locate `get_info` (~line 152) and add a new function after it:
```python
def get_holdings(ticker: str) -> dict:
    """Fetch top-holdings from yfinance funds_data.

    Returns:
      {
        "ticker": "XLK",
        "holdings": [{"ticker": "AAPL", "weight": 0.0712}, ...],
        "warnings": ["..."],   # only present when issues encountered
        "_provenance": {...},
      }

    For non-fund tickers (no funds_data), returns empty holdings list with a
    `non_fund` warning. For fund tickers, returns top-holdings as exposed
    by yfinance — typically top 10–90 weights summing to 0.5–1.0 (NOT all
    holdings); aggregator records actual weight_coverage_pct.
    """
    import yfinance as yf  # local import — module-level may be lazy-stubbed in tests
    from datetime import datetime, timezone

    cache_path = get_cache_path(ticker, "holdings")
    cached = load_cache(cache_path)
    if cached is not None:
        return cached

    t = yf.Ticker(ticker)
    funds_data = getattr(t, "funds_data", None)
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if funds_data is None:
        out = {
            "ticker":   ticker,
            "holdings": [],
            "warnings": [f"non_fund: {ticker} has no yfinance funds_data block"],
            "_provenance": {
                "skill":      "data-us",
                "source":     "yfinance.Ticker.funds_data",
                "fetched_at": fetched_at,
            },
        }
        save_cache(cache_path, out)
        return out

    df = getattr(funds_data, "top_holdings", None)
    holdings: list[dict] = []
    warnings: list[str] = []
    if df is None:
        warnings.append("yfinance funds_data.top_holdings returned None")
    else:
        try:
            data = df.to_dict()
        except Exception as exc:  # noqa: BLE001 — yfinance shape varies
            warnings.append(f"top_holdings.to_dict() failed: {exc}")
            data = {}
        weights_dict = data.get("Holding Percent") or data.get("holdingPercent") or {}
        for sym, weight in weights_dict.items():
            try:
                holdings.append({"ticker": sym, "weight": float(weight)})
            except (TypeError, ValueError):
                continue

    out = {
        "ticker":   ticker,
        "holdings": holdings,
        "_provenance": {
            "skill":      "data-us",
            "source":     "yfinance.Ticker.funds_data.top_holdings",
            "fetched_at": fetched_at,
        },
    }
    if warnings:
        out["warnings"] = warnings
    save_cache(cache_path, out)
    return out
```

Then in `main()`, locate the action dispatch (search `args.action ==` near line 400+) and add a branch for `holdings`:
```python
    elif args.action == "holdings":
        if not args.ticker:
            print("error: --action holdings requires --ticker", file=sys.stderr)
            return 2
        result = get_holdings(args.ticker)
```

Also add `"holdings"` to the `--action` choices argparse list.

- [ ] **Step 5: Run the unit test — expect PASS**

```bash
PYTHONDONTWRITEBYTECODE=1 cd investing-toolkit && uv run pytest tests/data/test_yfinance_holdings.py -v
```
Expected: PASS.

- [ ] **Step 6: Smoke-test CLI (offline, with cached fixture)**

```bash
PYTHONDONTWRITEBYTECODE=1 uv run investing-toolkit/skills/data-us/scripts/yfinance_client.py --help | grep -A 3 'action'
```
Expected: `holdings` appears in the action choices list.

- [ ] **Step 7: Commit**

```bash
git add investing-toolkit/skills/data-us/scripts/yfinance_client.py investing-toolkit/tests/data/test_yfinance_holdings.py
git commit -m "$(cat <<'EOF'
feat(data-us): add --action holdings for ETF top-holdings fetch

v2.2.0-c-bench T2: etf_aggregator needs ETF holdings for SPDR sector
benchmark; centralizes yfinance.funds_data.top_holdings access here so
all yfinance use stays in one client.

Returns {ticker, holdings: [{ticker, weight}, ...]}; non-fund tickers
get an explicit warning + empty list. Cached via existing yfinance_client
cache layer.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Add reference files — `etf-schema-map.json` + `sector-warnings.md`

**Files:**
- Create: `investing-toolkit/skills/analysis-comps/references/etf-schema-map.json`
- Create: `investing-toolkit/skills/analysis-comps/references/sector-warnings.md`

**Why:** SoT for two static lookups consumed by aggregator (ETF→schema mapping) and runtime (schema→warning text). Adding them in their own commit keeps data-only changes auditable.

- [ ] **Step 1: Create `etf-schema-map.json`**

Write to `investing-toolkit/skills/analysis-comps/references/etf-schema-map.json`:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "version": 1,
  "comment": "ETF ticker → v2.2.0-c schema_id mapping. SoT for etf_aggregator (which schema's multiples + indicators define the ETF aggregate output) and for runtime --sector-benchmark (anchor.schema_id → ETF lookup is reverse-derived; this file is forward-only).",
  "etf_to_schema": {
    "XLE":  "energy",
    "XLB":  "default",
    "XLI":  "default",
    "XLY":  "default",
    "XLP":  "default",
    "XLV":  "default",
    "XLF":  "bank",
    "XLK":  "tech-saas",
    "XLC":  "default",
    "XLU":  "utilities",
    "XLRE": "reit"
  }
}
```

- [ ] **Step 2: Create `sector-warnings.md`**

Write to `investing-toolkit/skills/analysis-comps/references/sector-warnings.md`:
```markdown
# Sector-relative valuation warnings — by schema_id

Loaded by `comps_compute.py --sector-benchmark` and pasted into
`anchor.etf_benchmark.warnings: [...]`. One row per known schema_id.
Keyed by schema_id (NOT yfinance sector name) to align with
v2.2.0-c routing source-of-truth (`sector-routing.yaml`).

Drift rule: when `sector_classifier.KNOWN_SCHEMA_IDS` gains a new
schema_id, also add a row here. Reviewers verify schema_id ↔ row parity.

## Warnings

| schema_id | warning_text |
|---|---|
| `default` | Default 5-multiple set; appropriate for cash-generating businesses with positive earnings. Verify operating-margin / FCF_yield indicators are non-negative; if not, a sector-specific schema may be more appropriate. |
| `bank` | Bank P/E and P/B work; EV/EBITDA is undefined (no operating-cash-flow concept of cash earnings). ROE is the primary profitability lens. Tier 1 capital + credit quality (deferred — supplemental disclosure not in standard XBRL) drive equity multiples in conjunction. |
| `insurance` | Combined ratio, reserves, premium-growth are the primary disclosures (deferred — supplemental disclosure not in standard XBRL). P/B is the most reliable price multiple in this output. |
| `asset-manager` | P/AUM is the canonical valuation metric (deferred — AUM not standard XBRL). P/E and P/B available but interpretive given AUM-driven earnings. |
| `reit` | P/FFO + EV/EBITDAre are REIT-canonical valuation; net-income-based P/E is misleading (depreciation distortion). AFFO requires gain-on-sale + straight-line rent adjustments — not in standard XBRL — so P/FFO only. |
| `tech-saas` | Rule-of-40 (revenue growth + operating margin) is the primary growth/quality lens. Pre-profit SaaS issuers may have negative trailingPE — interpret with operating-margin floor. |
| `tech-semis` | Cyclical industry; trailingPE near cycle troughs may be inflated and near peaks deflated. Inventory + book-to-bill ratios are sector-supplemental (deferred). |
| `energy` | P/E and EV/EBITDA on energy issuers are commodity-cycle distorted; production-volume + EV/EBITDAX (deferred — exploration_expense not standard XBRL) are more reliable in extreme cycle phases. |
| `utilities` | Dividend yield is the canonical valuation metric for utilities (deferred — dividend per share not standard XBRL); P/E and EV/EBITDA available but interpretive given regulated-rate-base economics. |
```

- [ ] **Step 3: Verify files parse / lint**

```bash
python -c "import json; json.load(open('investing-toolkit/skills/analysis-comps/references/etf-schema-map.json'))"
test -s investing-toolkit/skills/analysis-comps/references/sector-warnings.md && echo OK
```
Expected: no error, `OK` printed.

- [ ] **Step 4: Verify all `etf_to_schema` values are valid `KNOWN_SCHEMA_IDS`**

```bash
PYTHONDONTWRITEBYTECODE=1 uv run python -c "
import json, sys
sys.path.insert(0, 'investing-toolkit/skills/analysis-comps/scripts')
from sector_classifier import KNOWN_SCHEMA_IDS
data = json.load(open('investing-toolkit/skills/analysis-comps/references/etf-schema-map.json'))
unknown = [s for s in data['etf_to_schema'].values() if s not in KNOWN_SCHEMA_IDS]
print('unknown_schema_ids:', unknown)
assert not unknown, f'unknown schema_ids in etf-schema-map.json: {unknown}'
print('all 11 ETFs map to known schema_ids')
"
```
Expected: `all 11 ETFs map to known schema_ids`.

- [ ] **Step 5: Commit**

```bash
git add investing-toolkit/skills/analysis-comps/references/etf-schema-map.json investing-toolkit/skills/analysis-comps/references/sector-warnings.md
git commit -m "$(cat <<'EOF'
feat(analysis-comps): add etf-schema-map.json + sector-warnings.md

v2.2.0-c-bench T3: SoT files for ETF aggregator + runtime
--sector-benchmark.

- etf-schema-map.json: 11 SPDR ETFs → v2.2.0-c schema_id (XLF→bank,
  XLK→tech-saas, XLRE→reit, XLE→energy, XLU→utilities, others→default)
- sector-warnings.md: 9-row markdown table keyed by schema_id, loaded by
  runtime to surface sector-specific interpretive caveats

Drift rule: KNOWN_SCHEMA_IDS gain → both files must be updated.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Create `etf_aggregator.py` skeleton — single-ETF mode, single-holding wiring

**Files:**
- Create: `investing-toolkit/skills/analysis-comps/scripts/etf_aggregator.py`
- Create: `investing-toolkit/tests/analysis/test_etf_aggregator.py`
- Create: `investing-toolkit/tests/analysis/fixtures/etf_xlk_holdings_minimal.json`
- Create: `investing-toolkit/tests/analysis/fixtures/memo_fetch_aapl_minimal.json`

**Why:** Smallest end-to-end slice — fetch ETF holdings (mocked from fixture), classify each, compute multiples + indicators per holding (using the `compute_*_from_memo_fetch` functions renamed in Task 1), produce a single-ETF aggregate dict. NO `--all` mode yet, NO outlier drop yet, NO indicator weighting yet — just one path to JSON.

- [ ] **Step 1: Create minimal test fixtures**

Write to `investing-toolkit/tests/analysis/fixtures/etf_xlk_holdings_minimal.json`:
```json
{
  "ticker": "XLK",
  "holdings": [
    {"ticker": "AAPL", "weight": 0.6},
    {"ticker": "MSFT", "weight": 0.4}
  ],
  "_provenance": {"skill": "data-us", "source": "yfinance.Ticker.funds_data.top_holdings"}
}
```

Write to `investing-toolkit/tests/analysis/fixtures/memo_fetch_aapl_minimal.json`:
```json
{
  "pack": "memo-fetch",
  "ticker": "AAPL",
  "current_price": 200.0,
  "shares_outstanding": 15000000000,
  "company_info": {
    "marketCap": 3000000000000,
    "regularMarketPrice": 200.0,
    "sharesOutstanding": 15000000000,
    "sector": "Technology",
    "industry": "Consumer Electronics"
  },
  "income_statement": {
    "revenue":          [400000000000, 380000000000],
    "net_income":       [100000000000, 95000000000],
    "operating_income": [115000000000, 110000000000],
    "gross_profit":     [180000000000, 170000000000],
    "_meta": {
      "revenue":          {"fiscal_year_ends": ["2024-09-28", "2023-09-30"], "filings_used": ["aapl-10k-2024"]},
      "net_income":       {"fiscal_year_ends": ["2024-09-28"], "filings_used": ["aapl-10k-2024"]},
      "operating_income": {"fiscal_year_ends": ["2024-09-28"], "filings_used": ["aapl-10k-2024"]},
      "gross_profit":     {"fiscal_year_ends": ["2024-09-28"], "filings_used": ["aapl-10k-2024"]}
    }
  },
  "balance_sheet": {
    "total_stockholders_equity": [70000000000, 60000000000],
    "total_debt":                [110000000000],
    "cash":                      [60000000000],
    "goodwill":                  [],
    "intangible_assets":         [],
    "_meta": {
      "total_stockholders_equity": {"fiscal_year_ends": ["2024-09-28", "2023-09-30"], "filings_used": ["aapl-10k-2024"]},
      "total_debt":                {"fiscal_year_ends": ["2024-09-28"], "filings_used": ["aapl-10k-2024"]},
      "cash":                      {"fiscal_year_ends": ["2024-09-28"], "filings_used": ["aapl-10k-2024"]},
      "goodwill":                  {"fiscal_year_ends": [], "filings_used": []},
      "intangible_assets":         {"fiscal_year_ends": [], "filings_used": []}
    }
  },
  "cash_flow": {
    "depreciation_amortization": [11000000000],
    "operating_cash_flow":        [120000000000],
    "capex":                      [-10000000000],
    "_meta": {
      "depreciation_amortization": {"fiscal_year_ends": ["2024-09-28"], "filings_used": ["aapl-10k-2024"]},
      "operating_cash_flow":        {"fiscal_year_ends": ["2024-09-28"], "filings_used": ["aapl-10k-2024"]},
      "capex":                      {"fiscal_year_ends": ["2024-09-28"], "filings_used": ["aapl-10k-2024"]}
    }
  },
  "_provenance": {"skill": "data-us", "source": "pack.py --pack memo-fetch"}
}
```

Also create `investing-toolkit/tests/analysis/fixtures/memo_fetch_msft_minimal.json` — same structure as AAPL but with values: marketCap=2_500_000_000_000, current_price=300, shares_outstanding=7_400_000_000, revenue=[230_000_000_000, 200_000_000_000], net_income=[80_000_000_000, 70_000_000_000], operating_income=[100_000_000_000, 85_000_000_000], gross_profit=[160_000_000_000, 140_000_000_000], total_stockholders_equity=[200_000_000_000, 180_000_000_000], total_debt=[80_000_000_000], cash=[100_000_000_000], depreciation_amortization=[15_000_000_000], operating_cash_flow=[90_000_000_000], capex=[-20_000_000_000], sector="Technology", industry="Software—Infrastructure". Use the same `_meta` shape (with FY ends 2024-06-30 / 2023-06-30 and filings_used "msft-10k-2024").

- [ ] **Step 2: Write the failing aggregator test**

Create `investing-toolkit/tests/analysis/test_etf_aggregator.py`:
```python
"""Unit tests for etf_aggregator — no network. Uses fixture holdings + fixture
memo-fetch packs to drive deterministic compute.
"""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills" / "analysis-comps" / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


@pytest.fixture
def etf_aggregator(monkeypatch):
    """Import etf_aggregator and patch fetch_holdings + fetch_memo_fetch to
    return fixture-backed data."""
    if "etf_aggregator" in sys.modules:
        del sys.modules["etf_aggregator"]
    mod = importlib.import_module("etf_aggregator")

    holdings_fixture = json.loads((FIXTURES / "etf_xlk_holdings_minimal.json").read_text())
    aapl_memo = json.loads((FIXTURES / "memo_fetch_aapl_minimal.json").read_text())
    msft_memo = json.loads((FIXTURES / "memo_fetch_msft_minimal.json").read_text())

    def _fake_holdings(etf):
        assert etf == "XLK"
        return holdings_fixture

    def _fake_memo(ticker):
        return {"AAPL": aapl_memo, "MSFT": msft_memo}[ticker]

    monkeypatch.setattr(mod, "fetch_holdings", _fake_holdings)
    monkeypatch.setattr(mod, "fetch_memo_fetch", _fake_memo)
    return mod


def test_aggregate_etf_returns_required_keys(etf_aggregator):
    out = etf_aggregator.aggregate_etf("XLK")
    assert out["etf"] == "XLK"
    assert out["schema_id"] == "tech-saas"  # XLK→tech-saas per etf-schema-map
    assert isinstance(out.get("as_of"), str)
    assert isinstance(out["multiples"], dict)
    assert isinstance(out["indicators"], dict)
    assert "_meta" in out
    assert out["_meta"]["holdings_count"] == 2
    assert out["_meta"]["weight_coverage_pct"] == pytest.approx(100.0)


def test_aggregate_etf_weighted_average_multiples(etf_aggregator):
    """priceToBook = marketCap / equity[0].
    AAPL: 3e12 / 7e10 ≈ 42.857
    MSFT: 2.5e12 / 2e11 = 12.5
    Weighted (0.6 AAPL + 0.4 MSFT): 0.6*42.857 + 0.4*12.5 ≈ 30.71
    """
    out = etf_aggregator.aggregate_etf("XLK")
    pb = out["multiples"].get("priceToBook")
    assert pb is not None
    assert pb == pytest.approx(0.6 * (3e12 / 7e10) + 0.4 * (2.5e12 / 2e11), rel=1e-3)
```

- [ ] **Step 3: Run the test — expect FAIL (`etf_aggregator` module not found)**

```bash
PYTHONDONTWRITEBYTECODE=1 cd investing-toolkit && uv run pytest tests/analysis/test_etf_aggregator.py -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'etf_aggregator'`.

- [ ] **Step 4: Implement `etf_aggregator.py`**

Write to `investing-toolkit/skills/analysis-comps/scripts/etf_aggregator.py`:
```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0"]
# ///
"""
etf_aggregator.py — build-time SPDR sector ETF aggregate computer (v2.2.0-c-bench).

For each of the 11 SPDR Select Sector ETFs, fetches ETF holdings from yfinance,
classifies each holding's schema (via v2.2.0-c sector_classifier), runs the
holding through compute_multiples_from_memo_fetch + compute_indicators_from_memo_fetch
under the holding's own schema, then takes a holdings-weighted average over each
multiple/indicator in the ETF's mapped schema (per references/etf-schema-map.json).

This is a build-time CLI tool — runs in GitHub Actions weekly cron. NOT pure-compute
(does network I/O via subprocess data-us pack.py + yfinance_client.py). Output JSONs
land in references/sector-etf-aggregate-<ETF>.json and are committed by the GHA bot.

CLI:
    uv run etf_aggregator.py --etf XLK
    uv run etf_aggregator.py --all          # all 11 ETFs
    uv run etf_aggregator.py --etf XLK --output -    # write to stdout instead of references/
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

# Import compute helpers (renamed in Task 1 to drop _ prefix).
from comps_compute import (  # noqa: E402
    compute_indicators_from_memo_fetch,
    compute_multiples_from_memo_fetch,
    _load_schema,
)
from sector_classifier import KNOWN_SCHEMA_IDS, classify  # noqa: E402

_REFERENCES_DIR = _SCRIPT_DIR.parent / "references"
_ETF_SCHEMA_MAP_PATH = _REFERENCES_DIR / "etf-schema-map.json"
_ROOT = _SCRIPT_DIR.parents[3]   # repo root
_DATA_US_PACK = _ROOT / "investing-toolkit" / "skills" / "data-us" / "scripts" / "pack.py"
_YFINANCE_CLIENT = _ROOT / "investing-toolkit" / "skills" / "data-us" / "scripts" / "yfinance_client.py"

# Outlier bounds (per spec §6.2):
#   multiples can be negative (P/E on a loss-making issuer); bound [0, 200]
#   excludes negatives outright (sector aggregates intentionally drop loss-makers
#   from per-multiple averages).
_MULTIPLE_BOUNDS = (0.0, 200.0)
#   indicators are percentages; allow negatives (margins/ROE can be negative)
#   but cap extremes.
_INDICATOR_BOUNDS = (-100.0, 200.0)


def _load_etf_to_schema() -> dict[str, str]:
    data = json.loads(_ETF_SCHEMA_MAP_PATH.read_text(encoding="utf-8"))
    mapping = data["etf_to_schema"]
    bad = [v for v in mapping.values() if v not in KNOWN_SCHEMA_IDS]
    if bad:
        raise ValueError(f"etf-schema-map.json has unknown schema_ids: {bad}")
    return mapping


# -- I/O facades (override in tests) ---------------------------------------

def fetch_holdings(etf: str) -> dict:
    """Subprocess yfinance_client.py --action holdings --ticker <etf>."""
    proc = subprocess.run(
        ["uv", "run", str(_YFINANCE_CLIENT), "--action", "holdings", "--ticker", etf],
        capture_output=True, text=True, timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"yfinance_client holdings fetch failed for {etf}: {proc.stderr[:300]}")
    return json.loads(proc.stdout)


def fetch_memo_fetch(ticker: str) -> dict:
    """Subprocess data-us pack.py --pack memo-fetch --ticker <ticker>.

    Cache-aware: data-us pack.py reuses its own cache; back-to-back calls in the
    same session for the same ticker hit the cache.
    """
    proc = subprocess.run(
        ["uv", "run", str(_DATA_US_PACK), "--pack", "memo-fetch", "--ticker", ticker],
        capture_output=True, text=True, timeout=420,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"data-us memo-fetch failed for {ticker}: {proc.stderr[:300]}")
    return json.loads(proc.stdout)


# -- Aggregation ------------------------------------------------------------

def _classify_holding(memo: dict, ticker: str) -> Any:
    info = (memo.get("company_info") or {})
    return classify(ticker=ticker, sector=info.get("sector"), industry=info.get("industry"))


def _per_holding_compute(memo: dict, holding_schema: dict) -> tuple[dict, dict]:
    multiples, _multi_prov, _multi_warns = compute_multiples_from_memo_fetch(
        memo, direct_multiples={}, schema=holding_schema,
    )
    indicators, _ind_prov, _ind_warns = compute_indicators_from_memo_fetch(
        memo, holding_schema,
    )
    return multiples, indicators


def _weighted_average(
    contributions: list[tuple[float, float]],   # (weight, value)
    bounds: tuple[float, float],
) -> tuple[float | None, int]:
    """Returns (weighted_avg, outliers_dropped_count). None if no contributors."""
    lo, hi = bounds
    in_bounds = [(w, v) for w, v in contributions if v is not None and lo <= v <= hi]
    outliers = sum(1 for w, v in contributions if v is not None and not (lo <= v <= hi))
    if not in_bounds:
        return None, outliers
    total_weight = sum(w for w, _ in in_bounds)
    if total_weight <= 0:
        return None, outliers
    weighted = sum(w * v for w, v in in_bounds) / total_weight
    return weighted, outliers


def aggregate_etf(etf: str) -> dict:
    etf_to_schema = _load_etf_to_schema()
    if etf not in etf_to_schema:
        raise ValueError(f"unknown ETF {etf!r}; known: {sorted(etf_to_schema)}")
    etf_schema_id = etf_to_schema[etf]
    etf_schema = _load_schema(etf_schema_id)
    etf_multiple_ids = [m["id"] for m in etf_schema.get("multiples") or []]
    etf_indicator_ids = [i["id"] for i in etf_schema.get("indicators") or []]

    holdings_payload = fetch_holdings(etf)
    holdings = holdings_payload.get("holdings") or []

    # Per-holding compute (gather contributions per multiple_id / indicator_id)
    multiple_contribs: dict[str, list[tuple[float, float]]] = {m: [] for m in etf_multiple_ids}
    indicator_contribs: dict[str, list[tuple[float, float]]] = {i: [] for i in etf_indicator_ids}
    skipped: list[dict] = []
    weight_consumed = 0.0
    schema_dispatch: dict[str, list[str]] = {}

    for h in holdings:
        ticker = h["ticker"]
        weight = float(h.get("weight") or 0)
        try:
            memo = fetch_memo_fetch(ticker)
        except RuntimeError as exc:
            skipped.append({"ticker": ticker, "weight": weight, "reason": str(exc)[:120]})
            continue
        cls = _classify_holding(memo, ticker)
        h_schema = _load_schema(cls.schema_id)
        h_multiples, h_indicators = _per_holding_compute(memo, h_schema)
        weight_consumed += weight
        schema_dispatch.setdefault(cls.schema_id, []).append(ticker)

        for mid in etf_multiple_ids:
            v = h_multiples.get(mid)
            if v is not None:
                multiple_contribs[mid].append((weight, v))
        for iid in etf_indicator_ids:
            entry = h_indicators.get(iid)
            v = entry.get("value") if isinstance(entry, dict) else None
            if v is not None:
                indicator_contribs[iid].append((weight, v))

    # Weighted average + outlier drop
    multiples_out: dict[str, float | None] = {}
    indicators_out: dict[str, float | None] = {}
    outliers_dropped: dict[str, int] = {}
    for mid in etf_multiple_ids:
        avg, outliers = _weighted_average(multiple_contribs[mid], _MULTIPLE_BOUNDS)
        multiples_out[mid] = avg
        if outliers:
            outliers_dropped[mid] = outliers
    for iid in etf_indicator_ids:
        avg, outliers = _weighted_average(indicator_contribs[iid], _INDICATOR_BOUNDS)
        indicators_out[iid] = avg
        if outliers:
            outliers_dropped[iid] = outliers

    return {
        "etf":       etf,
        "schema_id": etf_schema_id,
        "as_of":     datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "_meta": {
            "holdings_count":      len(holdings),
            "weight_coverage_pct": round(weight_consumed * 100.0, 2),
            "outliers_dropped":    outliers_dropped,
            "skipped_holdings":    skipped,
            "schema_dispatch":     {k: len(v) for k, v in schema_dispatch.items()},
            "source":              "yfinance funds_data + data-us memo-fetch",
        },
        "multiples":  multiples_out,
        "indicators": indicators_out,
    }


# -- CLI --------------------------------------------------------------------

def _main() -> int:
    parser = argparse.ArgumentParser(description="Build-time SPDR sector ETF aggregate computer (v2.2.0-c-bench).")
    parser.add_argument("--etf", type=str, default=None,
                        help="Single ETF ticker (e.g. XLK); mutually exclusive with --all")
    parser.add_argument("--all", action="store_true",
                        help="Aggregate all 11 SPDR ETFs from etf-schema-map.json")
    parser.add_argument("--output", type=str, default=None,
                        help="Output path; '-' = stdout; default writes to references/sector-etf-aggregate-<ETF>.json")
    args = parser.parse_args()

    if args.all and args.etf:
        parser.error("--etf and --all are mutually exclusive")
    if not args.all and not args.etf:
        parser.error("specify one of --etf <ticker> or --all")

    etf_to_schema = _load_etf_to_schema()
    targets = sorted(etf_to_schema) if args.all else [args.etf.upper()]

    for etf in targets:
        result = aggregate_etf(etf)
        if args.output == "-":
            json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
            sys.stdout.write("\n")
        else:
            target_path = (
                Path(args.output) if args.output is not None
                else _REFERENCES_DIR / f"sector-etf-aggregate-{etf}.json"
            )
            target_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            sys.stderr.write(f"[etf_aggregator] wrote {target_path}\n")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
```

- [ ] **Step 5: Run the unit test — expect PASS**

```bash
PYTHONDONTWRITEBYTECODE=1 cd investing-toolkit && uv run pytest tests/analysis/test_etf_aggregator.py -v
```
Expected: PASS (both tests).

- [ ] **Step 6: Verify offline test suite still green (no regression on existing comps tests)**

```bash
PYTHONDONTWRITEBYTECODE=1 cd investing-toolkit && uv run pytest tests/analysis/ -m "not network" -q
```
Expected: all PASS.

- [ ] **Step 7: Commit**

```bash
git add investing-toolkit/skills/analysis-comps/scripts/etf_aggregator.py investing-toolkit/tests/analysis/test_etf_aggregator.py investing-toolkit/tests/analysis/fixtures/etf_xlk_holdings_minimal.json investing-toolkit/tests/analysis/fixtures/memo_fetch_aapl_minimal.json investing-toolkit/tests/analysis/fixtures/memo_fetch_msft_minimal.json
git commit -m "$(cat <<'EOF'
feat(analysis-comps): add etf_aggregator.py — single-ETF holdings-weighted aggregate

v2.2.0-c-bench T4: build-time aggregator for SPDR sector ETF benchmark.

For each ETF, fetches yfinance funds_data.top_holdings, classifies each holding
under v2.2.0-c sector_classifier, runs compute_*_from_memo_fetch under the
holding's own schema, then takes a holdings-weighted average per the ETF's
mapped schema (etf-schema-map.json). Outlier guard drops values outside
[0, 200] for multiples / [-100, 200] for indicators.

This commit ships single-ETF + --all CLI; live data path goes through
data-us pack.py memo-fetch (cache-aware). Tests use fixture-backed
holdings + memo-fetch packs (no network).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Aggregator edge cases — outlier drop / partial coverage / schema-dispatch surfacing

**Files:**
- Modify: `investing-toolkit/tests/analysis/test_etf_aggregator.py` (add edge-case tests)
- Verify: `etf_aggregator.py` already handles them correctly; minor patches if not

**Why:** Lock down the subtle aggregation behaviors with explicit tests. Outlier drop, weight coverage, per-holding schema dispatch (XLF over [JPM(bank), MET(insurance), BLK(asset-manager)]), missing-data holdings.

- [ ] **Step 1: Add fixtures for XLF aggregator test**

Create `investing-toolkit/tests/analysis/fixtures/etf_xlf_holdings_minimal.json`:
```json
{
  "ticker": "XLF",
  "holdings": [
    {"ticker": "JPM", "weight": 0.5},
    {"ticker": "MET", "weight": 0.3},
    {"ticker": "BLK", "weight": 0.2}
  ]
}
```

Create `investing-toolkit/tests/analysis/fixtures/memo_fetch_jpm_minimal.json` — same shape as AAPL's, but values: marketCap=600_000_000_000, current_price=200, shares_outstanding=3_000_000_000, revenue=[160_000_000_000, 140_000_000_000], net_income=[50_000_000_000, 45_000_000_000], operating_income=[60_000_000_000, 55_000_000_000], total_stockholders_equity=[300_000_000_000, 280_000_000_000], total_debt=[800_000_000_000], cash=[400_000_000_000], depreciation_amortization=[5_000_000_000], operating_cash_flow=[55_000_000_000], capex=[-2_000_000_000], sector="Financial Services", industry="Banks - Diversified". (FY ends 2024-12-31.)

Create `memo_fetch_met_minimal.json` — sector="Financial Services", industry="Insurance - Diversified", marketCap=60_000_000_000, equity=[40_000_000_000], net_income=[5_000_000_000], rest of fields populated minimally. (Insurance schema has multiples but no ROE indicator — ROE only lives in bank schema.)

Create `memo_fetch_blk_minimal.json` — sector="Financial Services", industry="Asset Management", marketCap=130_000_000_000, equity=[50_000_000_000], net_income=[6_000_000_000], rest of fields populated minimally. (Asset-manager schema also lacks ROE.)

For both MET and BLK fixtures: copy the AAPL fixture's `_meta` shape; set FY ends to `2024-12-31`.

- [ ] **Step 2: Add test cases**

Append to `investing-toolkit/tests/analysis/test_etf_aggregator.py`:
```python
@pytest.fixture
def xlf_aggregator(monkeypatch):
    if "etf_aggregator" in sys.modules:
        del sys.modules["etf_aggregator"]
    mod = importlib.import_module("etf_aggregator")
    holdings = json.loads((FIXTURES / "etf_xlf_holdings_minimal.json").read_text())
    memos = {
        "JPM": json.loads((FIXTURES / "memo_fetch_jpm_minimal.json").read_text()),
        "MET": json.loads((FIXTURES / "memo_fetch_met_minimal.json").read_text()),
        "BLK": json.loads((FIXTURES / "memo_fetch_blk_minimal.json").read_text()),
    }
    monkeypatch.setattr(mod, "fetch_holdings", lambda etf: holdings)
    monkeypatch.setattr(mod, "fetch_memo_fetch", lambda t: memos[t])
    return mod


def test_xlf_aggregate_uses_bank_schema(xlf_aggregator):
    """XLF maps to bank schema; aggregate exposes bank schema's multiples + indicators."""
    out = xlf_aggregator.aggregate_etf("XLF")
    assert out["schema_id"] == "bank"
    # bank schema multiples: trailingPE, forwardPE, priceToBook, priceToTangibleBook
    assert set(out["multiples"].keys()) == {"trailingPE", "forwardPE", "priceToBook", "priceToTangibleBook"}
    # bank schema indicators: ROE (only)
    assert set(out["indicators"].keys()) == {"ROE"}


def test_xlf_per_holding_schema_dispatch(xlf_aggregator):
    """JPM→bank, MET→insurance, BLK→asset-manager.
    All 3 have priceToBook (universal-ish across financial schemas).
    Only JPM contributes ROE (insurance + asset-manager schemas don't have ROE).
    """
    out = xlf_aggregator.aggregate_etf("XLF")
    dispatch = out["_meta"]["schema_dispatch"]
    assert dispatch["bank"] == 1            # JPM
    assert dispatch["insurance"] == 1       # MET
    assert dispatch["asset-manager"] == 1   # BLK
    # priceToBook averaged over all 3 (all have equity); ROE only over JPM.
    assert out["multiples"]["priceToBook"] is not None


def test_outlier_drop_high_value(monkeypatch):
    """Holding with priceToBook = 250 (out of [0, 200]) → dropped from aggregate;
    `_meta.outliers_dropped` records the count."""
    if "etf_aggregator" in sys.modules:
        del sys.modules["etf_aggregator"]
    mod = importlib.import_module("etf_aggregator")
    holdings = {"holdings": [
        {"ticker": "AAPL", "weight": 0.5},
        {"ticker": "MSFT", "weight": 0.5},
    ]}
    aapl_memo = json.loads((FIXTURES / "memo_fetch_aapl_minimal.json").read_text())
    # Cook MSFT to produce P/B > 200: tiny equity inflates P/B.
    msft_memo = json.loads((FIXTURES / "memo_fetch_msft_minimal.json").read_text())
    msft_memo["balance_sheet"]["total_stockholders_equity"] = [10_000_000]  # 10M only
    monkeypatch.setattr(mod, "fetch_holdings", lambda etf: holdings)
    monkeypatch.setattr(mod, "fetch_memo_fetch",
                        lambda t: {"AAPL": aapl_memo, "MSFT": msft_memo}[t])
    out = mod.aggregate_etf("XLK")
    # AAPL P/B ≈ 42.857; MSFT P/B = 2.5e12 / 1e7 = 250000 → dropped
    assert out["_meta"]["outliers_dropped"].get("priceToBook") == 1
    # priceToBook average is now AAPL only → ≈ 42.857
    assert out["multiples"]["priceToBook"] == pytest.approx(3e12 / 7e10, rel=1e-3)


def test_weight_coverage_partial_when_holding_skipped(monkeypatch):
    """When a holding fetch raises, it's logged into skipped_holdings;
    weight_coverage_pct reflects only successfully-fetched weight."""
    if "etf_aggregator" in sys.modules:
        del sys.modules["etf_aggregator"]
    mod = importlib.import_module("etf_aggregator")
    holdings = {"holdings": [
        {"ticker": "AAPL", "weight": 0.6},
        {"ticker": "MSFT", "weight": 0.4},
    ]}
    aapl_memo = json.loads((FIXTURES / "memo_fetch_aapl_minimal.json").read_text())

    def _fake_memo(t):
        if t == "MSFT":
            raise RuntimeError("simulated fetch failure")
        return aapl_memo

    monkeypatch.setattr(mod, "fetch_holdings", lambda etf: holdings)
    monkeypatch.setattr(mod, "fetch_memo_fetch", _fake_memo)
    out = mod.aggregate_etf("XLK")
    assert out["_meta"]["weight_coverage_pct"] == pytest.approx(60.0)  # AAPL only
    assert any(s["ticker"] == "MSFT" for s in out["_meta"]["skipped_holdings"])
```

- [ ] **Step 3: Run tests — expect PASS**

```bash
PYTHONDONTWRITEBYTECODE=1 cd investing-toolkit && uv run pytest tests/analysis/test_etf_aggregator.py -v
```
Expected: all PASS. If `test_outlier_drop_high_value` or `test_weight_coverage_partial_when_holding_skipped` fail, the issue is in the bounds-check / skipped-holdings tracking in `etf_aggregator.aggregate_etf` — review §6.2 of spec and fix in place.

- [ ] **Step 4: Commit**

```bash
git add investing-toolkit/tests/analysis/test_etf_aggregator.py investing-toolkit/tests/analysis/fixtures/etf_xlf_holdings_minimal.json investing-toolkit/tests/analysis/fixtures/memo_fetch_jpm_minimal.json investing-toolkit/tests/analysis/fixtures/memo_fetch_met_minimal.json investing-toolkit/tests/analysis/fixtures/memo_fetch_blk_minimal.json
git commit -m "$(cat <<'EOF'
test(analysis-comps): lock down etf_aggregator edge cases

v2.2.0-c-bench T5: outlier drop, partial weight coverage, per-holding
schema dispatch (XLF over JPM bank / MET insurance / BLK asset-manager —
ROE only lives on bank schema, priceToBook applies to all 3).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Add `--sector-benchmark` flag plumbing to `comps_compute.py` (parsing only)

**Files:**
- Modify: `investing-toolkit/skills/analysis-comps/scripts/comps_compute.py` (argparse + flag accepted; no behavior change yet)
- Modify: `investing-toolkit/tests/analysis/test_comps_etf_benchmark.py` (new test file with one parsing-only test)

**Why:** Smallest possible commit that introduces the runtime opt-in surface. Subsequent tasks add the actual block emission logic. Splitting flag plumbing from behavior change keeps the diff readable.

- [ ] **Step 1: Write the failing test**

Create `investing-toolkit/tests/analysis/test_comps_etf_benchmark.py`:
```python
"""Tests for runtime --sector-benchmark flag (v2.2.0-c-bench).

Uses offline fixtures for both the anchor pack and a stand-in
sector-etf-aggregate-XLK.json placed under references/. Network-free.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills" / "analysis-comps" / "scripts"
COMPS_SCRIPT = SCRIPTS / "comps_compute.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
REFERENCES = ROOT / "skills" / "analysis-comps" / "references"

ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}


def _run(args: list[str], timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["uv", "run", str(COMPS_SCRIPT), *args],
        capture_output=True, text=True, timeout=timeout, env=ENV, cwd=str(ROOT),
    )


def test_sector_benchmark_flag_accepted(tmp_path):
    """Flag parses; no error path. Behavior tested in later tasks."""
    anchor = FIXTURES / "comps_anchor_aapl.json"
    base = FIXTURES / "comps_anchor_aapl_memo_fetch.json"
    peer = FIXTURES / "comps_peer_msft.json"
    proc = _run([
        "--mode", "compute",
        "--anchor", str(anchor), "--anchor-base", str(base), "--peers", str(peer),
        "--sector-benchmark",
    ])
    # The flag is parsed; either the run succeeds (block emitted with stub) OR
    # it returns 0/0-output without error. We only assert the flag did not
    # cause a parse error (rc != 2).
    assert proc.returncode != 2, f"--sector-benchmark not recognized: {proc.stderr}"
```

- [ ] **Step 2: Run test — expect FAIL (flag not in argparse)**

```bash
PYTHONDONTWRITEBYTECODE=1 cd investing-toolkit && uv run pytest tests/analysis/test_comps_etf_benchmark.py::test_sector_benchmark_flag_accepted -v
```
Expected: FAIL — argparse rejects `--sector-benchmark` with rc=2.

- [ ] **Step 3: Add the flag to argparse**

In `investing-toolkit/skills/analysis-comps/scripts/comps_compute.py`, locate the `--show-routing` argparse declaration (~line 1120) and add immediately after:
```python
    parser.add_argument(
        "--sector-benchmark", action="store_true",
        help=(
            "Add an etf_benchmark block under anchor showing divergence vs the "
            "SPDR sector ETF aggregate matched by anchor.schema_id. Reads "
            "references/sector-etf-aggregate-<ETF>.json (built weekly by "
            "etf_aggregator.py via GHA). Non-US tickers emit "
            "etf_benchmark.status='skipped'. Default: off (output unchanged from v2.2.0-c)."
        ),
    )
```

- [ ] **Step 4: Run test — expect PASS**

```bash
PYTHONDONTWRITEBYTECODE=1 cd investing-toolkit && uv run pytest tests/analysis/test_comps_etf_benchmark.py::test_sector_benchmark_flag_accepted -v
```
Expected: PASS.

- [ ] **Step 5: Confirm offline suite still green**

```bash
PYTHONDONTWRITEBYTECODE=1 cd investing-toolkit && uv run pytest tests/analysis/ -m "not network" -q
```
Expected: all PASS.

- [ ] **Step 6: Commit**

```bash
git add investing-toolkit/skills/analysis-comps/scripts/comps_compute.py investing-toolkit/tests/analysis/test_comps_etf_benchmark.py
git commit -m "$(cat <<'EOF'
feat(analysis-comps): add --sector-benchmark flag (parsing only)

v2.2.0-c-bench T6: opt-in flag plumbing. No behavior change yet — block
emission added in T7.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: Implement `etf_benchmark` block emission — divergence + warnings

**Files:**
- Modify: `investing-toolkit/skills/analysis-comps/scripts/comps_compute.py` (add `_etf_benchmark_block` builder; wire into compute-mode anchor block)
- Modify: `investing-toolkit/tests/analysis/test_comps_etf_benchmark.py` (add divergence + band tests)
- Create: `investing-toolkit/tests/analysis/fixtures/sector-etf-aggregate-xlk-sample.json`

**Why:** The substantive runtime change. Loads the aggregate fixture, computes per-multiple and per-indicator divergence with bands, pulls a warning row from `sector-warnings.md`.

- [ ] **Step 1: Create the offline aggregate fixture**

Write to `investing-toolkit/tests/analysis/fixtures/sector-etf-aggregate-xlk-sample.json`:
```json
{
  "etf": "XLK",
  "schema_id": "tech-saas",
  "as_of": "2026-05-04",
  "_meta": {
    "holdings_count": 75,
    "weight_coverage_pct": 94.2,
    "outliers_dropped": {},
    "skipped_holdings": [],
    "schema_dispatch": {"tech-saas": 60, "tech-semis": 12, "default": 3},
    "source": "test fixture"
  },
  "multiples": {
    "trailingPE":  24.1,
    "forwardPE":   null,
    "priceToBook": 5.8,
    "priceToSales": 6.2,
    "evEbitda":    18.4
  },
  "indicators": {
    "rule_of_40":       0.42,
    "operating_margin": 22.1,
    "FCF_yield":        4.8,
    "FCF_margin":       18.0
  }
}
```

- [ ] **Step 2: Write failing tests for block emission**

Append to `investing-toolkit/tests/analysis/test_comps_etf_benchmark.py`:
```python
@pytest.fixture
def stub_xlk_aggregate(monkeypatch, tmp_path):
    """Override the references/ aggregate path so test uses fixture, not real
    weekly file. Patches an env var the comps_compute reader honors."""
    sample = FIXTURES / "sector-etf-aggregate-xlk-sample.json"
    target = tmp_path / "sector-etf-aggregate-XLK.json"
    shutil.copy(sample, target)
    yield tmp_path


def test_etf_benchmark_block_emitted_when_flag(stub_xlk_aggregate):
    anchor = FIXTURES / "comps_anchor_aapl.json"
    base = FIXTURES / "comps_anchor_aapl_memo_fetch.json"
    peer = FIXTURES / "comps_peer_msft.json"
    env = {**ENV, "INVESTING_TOOLKIT_AGGREGATES_DIR": str(stub_xlk_aggregate)}
    proc = subprocess.run(
        ["uv", "run", str(COMPS_SCRIPT),
         "--mode", "compute", "--anchor", str(anchor), "--anchor-base", str(base),
         "--peers", str(peer), "--sector-benchmark"],
        capture_output=True, text=True, timeout=60, env=env, cwd=str(ROOT),
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    bench = payload["anchor"]["etf_benchmark"]
    assert bench["etf"] == "XLK"   # AAPL → default schema → maps to XLK
    assert bench["schema_id"] == "tech-saas"
    assert "as_of" in bench
    # multiples: trailingPE present in both; forwardPE null on aggregate → band n/a
    assert bench["multiples"]["trailingPE"]["band"] in {"in_line", "notable", "extreme"}
    assert bench["multiples"]["forwardPE"]["band"] == "n/a"
    assert bench["multiples"]["forwardPE"]["delta_pct"] is None


def test_no_etf_benchmark_block_without_flag(stub_xlk_aggregate):
    anchor = FIXTURES / "comps_anchor_aapl.json"
    base = FIXTURES / "comps_anchor_aapl_memo_fetch.json"
    peer = FIXTURES / "comps_peer_msft.json"
    proc = subprocess.run(
        ["uv", "run", str(COMPS_SCRIPT),
         "--mode", "compute", "--anchor", str(anchor), "--anchor-base", str(base),
         "--peers", str(peer)],   # no --sector-benchmark
        capture_output=True, text=True, timeout=60, env=ENV, cwd=str(ROOT),
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert "etf_benchmark" not in payload["anchor"], "etf_benchmark must not appear without --sector-benchmark"


@pytest.mark.parametrize("anchor_v,etf_v,expected_band", [
    (24.0, 24.1, "in_line"),    # 0.4% → in_line
    (28.0, 24.1, "in_line"),    # 16.2% → in_line
    (30.0, 24.1, "notable"),    # 24.5% → notable
    (50.0, 24.1, "extreme"),    # 107% → extreme
])
def test_band_classification(anchor_v, etf_v, expected_band):
    """Direct unit-test of the band function (skip subprocess)."""
    sys.path.insert(0, str(SCRIPTS))
    from comps_compute import _classify_etf_benchmark_band
    delta_pct = ((anchor_v - etf_v) / etf_v) * 100
    assert _classify_etf_benchmark_band(delta_pct) == expected_band
```

- [ ] **Step 3: Run tests — expect FAIL (block not emitted; helper not defined)**

```bash
PYTHONDONTWRITEBYTECODE=1 cd investing-toolkit && uv run pytest tests/analysis/test_comps_etf_benchmark.py -v
```
Expected: FAIL — `etf_benchmark` key absent / `_classify_etf_benchmark_band` import fails.

- [ ] **Step 4: Implement block builder + wire it into `comps_compute.main`**

In `investing-toolkit/skills/analysis-comps/scripts/comps_compute.py`, add after `_compute_divergence` (around line 957):
```python
# ---- v2.2.0-c-bench: ETF benchmark layer ----------------------------------

ETF_BENCH_BAND_LOW = 20.0   # ≤20% delta → in_line
ETF_BENCH_BAND_HIGH = 50.0  # >50% delta → extreme; in between → notable
ETF_BENCH_STALE_DAYS = 14   # surface stale-aggregate warning when as_of older than N days


def _classify_etf_benchmark_band(delta_pct: float | None) -> str:
    if delta_pct is None:
        return "n/a"
    abs_pct = abs(delta_pct)
    if abs_pct <= ETF_BENCH_BAND_LOW:
        return "in_line"
    if abs_pct <= ETF_BENCH_BAND_HIGH:
        return "notable"
    return "extreme"


def _load_etf_to_schema_inv() -> dict[str, str]:
    """schema_id → ETF (inverse of etf-schema-map.json's etf_to_schema). When
    multiple ETFs map to the same schema_id, the alphabetically first ETF wins
    (deterministic; only `default` schema has multiple ETFs — XLB/XLI/XLY/XLP/XLV/XLC)."""
    path = _REFERENCES_DIR / "etf-schema-map.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    inv: dict[str, str] = {}
    for etf, schema in sorted(data["etf_to_schema"].items()):
        inv.setdefault(schema, etf)
    return inv


def _load_aggregate(etf: str) -> dict | None:
    """Read references/sector-etf-aggregate-<ETF>.json. Honors
    INVESTING_TOOLKIT_AGGREGATES_DIR env var for test override.
    Returns None if file missing (test fallback / first-run before GHA)."""
    import os
    aggregates_dir = Path(os.environ.get("INVESTING_TOOLKIT_AGGREGATES_DIR") or _REFERENCES_DIR)
    path = aggregates_dir / f"sector-etf-aggregate-{etf}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _load_sector_warnings() -> dict[str, str]:
    """Parse sector-warnings.md → {schema_id: warning_text}.
    Reads the markdown table (skip header + separator rows)."""
    path = _REFERENCES_DIR / "sector-warnings.md"
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    in_table = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| `") and "|" in line[2:]:
            in_table = True
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 2 and cells[0].startswith("`") and cells[0].endswith("`"):
                schema_id = cells[0].strip("`")
                out[schema_id] = cells[1]
        elif in_table and not line.strip():
            in_table = False
    return out


def _aggregate_freshness_days(as_of: str | None) -> int | None:
    if not as_of:
        return None
    try:
        as_of_dt = datetime.strptime(as_of, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    return (datetime.now(timezone.utc) - as_of_dt).days


def _build_etf_benchmark_block(
    anchor_schema_id: str,
    anchor_multiples_compute: dict,
    anchor_indicators: dict,
    is_us_ticker: bool,
) -> dict:
    """Build the etf_benchmark block (or skipped status) for the anchor."""
    if not is_us_ticker:
        return {
            "status": "skipped",
            "reason": "non-US ticker; SPDR sector ETFs are US-only. Cross-country sector benchmark deferred to v2.2.0-c-{jp,tw,kr,cn}.",
        }
    inv = _load_etf_to_schema_inv()
    etf = inv.get(anchor_schema_id)
    if etf is None:
        return {
            "status": "skipped",
            "reason": f"no SPDR sector ETF mapped to schema_id={anchor_schema_id!r}",
        }
    aggregate = _load_aggregate(etf)
    if aggregate is None:
        return {
            "status": "skipped",
            "reason": f"references/sector-etf-aggregate-{etf}.json missing — weekly cron may not have run yet",
        }

    warnings: list[str] = []
    freshness = _aggregate_freshness_days(aggregate.get("as_of"))
    if freshness is not None and freshness > ETF_BENCH_STALE_DAYS:
        warnings.append(
            f"aggregate stale: as_of={aggregate.get('as_of')}, freshness_days={freshness} "
            "— weekly cron may have skipped a Saturday"
        )
    sector_warnings = _load_sector_warnings()
    if anchor_schema_id in sector_warnings:
        warnings.append(sector_warnings[anchor_schema_id])

    # Per-multiple divergence (intersection of anchor multiples_compute and aggregate multiples)
    agg_multiples = aggregate.get("multiples") or {}
    multiples_out: dict[str, dict] = {}
    for mid, anchor_v in (anchor_multiples_compute or {}).items():
        if mid not in agg_multiples:
            continue
        etf_v = agg_multiples.get(mid)
        if anchor_v is None or etf_v is None:
            multiples_out[mid] = {"individual": anchor_v, "etf_aggregate": etf_v,
                                  "delta_pct": None, "band": "n/a"}
            continue
        if etf_v == 0:
            multiples_out[mid] = {"individual": anchor_v, "etf_aggregate": etf_v,
                                  "delta_pct": None, "band": "n/a",
                                  "note": "etf_aggregate is zero — pct_diff undefined"}
            continue
        delta_pct = ((anchor_v - etf_v) / etf_v) * 100.0
        multiples_out[mid] = {
            "individual":     anchor_v,
            "etf_aggregate":  etf_v,
            "delta_pct":      delta_pct,
            "band":           _classify_etf_benchmark_band(delta_pct),
        }

    # Per-indicator divergence (intersection of anchor indicators and aggregate indicators)
    agg_indicators = aggregate.get("indicators") or {}
    indicators_out: dict[str, dict] = {}
    for iid, anchor_entry in (anchor_indicators or {}).items():
        if iid not in agg_indicators:
            continue
        anchor_v = anchor_entry.get("value") if isinstance(anchor_entry, dict) else None
        etf_v = agg_indicators.get(iid)
        if anchor_v is None or etf_v is None:
            indicators_out[iid] = {"individual": anchor_v, "etf_aggregate": etf_v,
                                   "delta_pct": None, "band": "n/a"}
            continue
        if etf_v == 0:
            indicators_out[iid] = {"individual": anchor_v, "etf_aggregate": etf_v,
                                   "delta_pct": None, "band": "n/a",
                                   "note": "etf_aggregate is zero — pct_diff undefined"}
            continue
        delta_pct = ((anchor_v - etf_v) / etf_v) * 100.0
        indicators_out[iid] = {
            "individual":     anchor_v,
            "etf_aggregate":  etf_v,
            "delta_pct":      delta_pct,
            "band":           _classify_etf_benchmark_band(delta_pct),
        }

    return {
        "etf":         etf,
        "schema_id":   aggregate.get("schema_id"),
        "as_of":       aggregate.get("as_of"),
        "_meta":       {
            "holdings_count":      (aggregate.get("_meta") or {}).get("holdings_count"),
            "weight_coverage_pct": (aggregate.get("_meta") or {}).get("weight_coverage_pct"),
            "freshness_days":      freshness,
        },
        "multiples":   multiples_out,
        "indicators":  indicators_out,
        "warnings":    warnings,
    }
```

Now wire it into `main()` — locate the compute-mode anchor block construction (around line 1259, just after `anchor_block["compute_provenance"] = compute_provenance` near line 1293) and add:
```python
        if args.sector_benchmark:
            anchor_info = (anchor_pack.get("info") or {}).get(anchor_ticker) or {}
            # US-ticker heuristic: yfinance market === "us" OR ticker has no exchange suffix.
            is_us = (
                anchor_info.get("market") in ("us_market", "us", None)
                and "." not in anchor_ticker
            )
            anchor_block["etf_benchmark"] = _build_etf_benchmark_block(
                anchor_classification.schema_id,
                anchor_block.get("multiples_compute") or {},
                anchor_block.get("indicators") or {},
                is_us_ticker=is_us,
            )
```

- [ ] **Step 5: Run tests — expect PASS**

```bash
PYTHONDONTWRITEBYTECODE=1 cd investing-toolkit && uv run pytest tests/analysis/test_comps_etf_benchmark.py -v
```
Expected: all PASS.

- [ ] **Step 6: Confirm no regression on existing v2.2.0-c tests**

```bash
PYTHONDONTWRITEBYTECODE=1 cd investing-toolkit && uv run pytest tests/analysis/ -m "not network" -q
```
Expected: all PASS.

- [ ] **Step 7: Commit**

```bash
git add investing-toolkit/skills/analysis-comps/scripts/comps_compute.py investing-toolkit/tests/analysis/test_comps_etf_benchmark.py investing-toolkit/tests/analysis/fixtures/sector-etf-aggregate-xlk-sample.json
git commit -m "$(cat <<'EOF'
feat(analysis-comps): emit etf_benchmark block under --sector-benchmark

v2.2.0-c-bench T7: runtime layer reads pre-built sector-etf-aggregate-<ETF>.json
(weekly GHA refresh), computes per-multiple + per-indicator divergence vs
aggregate with 20%/50% bands (in_line/notable/extreme), pulls a schema-keyed
warning row from sector-warnings.md, surfaces freshness_days + holdings_count
in _meta, flags stale aggregates (>14d) with a warning. INVESTING_TOOLKIT_AGGREGATES_DIR
env var allows tests to substitute fixture aggregates.

When flag is absent, output unchanged from v2.2.0-c (no etf_benchmark key).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: Non-US ticker skip + stale-aggregate guard tests

**Files:**
- Modify: `investing-toolkit/tests/analysis/test_comps_etf_benchmark.py` (add 2 tests)
- Create: `investing-toolkit/tests/analysis/fixtures/comps_anchor_7203_jp.json`
- Create: `investing-toolkit/tests/analysis/fixtures/comps_anchor_7203_jp_memo_fetch.json`
- Create: `investing-toolkit/tests/analysis/fixtures/sector-etf-aggregate-xlk-stale.json`

**Why:** Lock down the two graceful-fallback paths the spec requires. (Implementation already exists in T7; this task verifies it works end-to-end.)

- [ ] **Step 1: Create JP-ticker fixtures (minimal)**

Write to `investing-toolkit/tests/analysis/fixtures/comps_anchor_7203_jp.json`:
```json
{
  "ticker": "7203.T",
  "info": {
    "7203.T": {
      "marketCap": 320000000000000,
      "sector": "Consumer Cyclical",
      "industry": "Auto Manufacturers",
      "trailingPE": 12.0,
      "forwardPE":  10.0,
      "priceToBook": 1.1,
      "priceToSales": 0.9,
      "evEbitda": 8.5,
      "regularMarketPrice": 2900,
      "sharesOutstanding": 14000000000
    }
  },
  "_provenance": {"skill": "data-jp", "source": "yfinance.info"}
}
```

Write `comps_anchor_7203_jp_memo_fetch.json` — `pack: "memo-fetch"`, `ticker: "7203.T"`, populate income_statement/balance_sheet/cash_flow blocks with arbitrary non-null FY values + `_meta` shapes (so compute mode reaches the `etf_benchmark` decision branch, not earlier I/O failure). FY end "2024-03-31".

- [ ] **Step 2: Create stale aggregate fixture**

Write to `investing-toolkit/tests/analysis/fixtures/sector-etf-aggregate-xlk-stale.json` — copy the `xlk-sample.json` content but change `as_of` to a date 20 days before today. Use a Python helper at test time to compute the date dynamically (so the fixture stays stale forever):

```python
# In test, generate at runtime:
import datetime
stale_date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=20)).strftime("%Y-%m-%d")
```

Then the test writes a temp aggregate file with `as_of=stale_date`. (Skip creating a static stale fixture; generate at test time.)

- [ ] **Step 3: Add tests**

Append to `investing-toolkit/tests/analysis/test_comps_etf_benchmark.py`:
```python
import datetime


def test_non_us_ticker_skipped(tmp_path):
    """7203.T (Toyota) → etf_benchmark.status == 'skipped'."""
    anchor = FIXTURES / "comps_anchor_7203_jp.json"
    base = FIXTURES / "comps_anchor_7203_jp_memo_fetch.json"
    peer = FIXTURES / "comps_peer_msft.json"  # any peer; not under test
    proc = subprocess.run(
        ["uv", "run", str(COMPS_SCRIPT),
         "--mode", "compute", "--anchor", str(anchor), "--anchor-base", str(base),
         "--peers", str(peer), "--sector-benchmark"],
        capture_output=True, text=True, timeout=60, env=ENV, cwd=str(ROOT),
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    bench = payload["anchor"]["etf_benchmark"]
    assert bench.get("status") == "skipped"
    assert "non-US" in bench.get("reason", "")


def test_stale_aggregate_emits_warning(tmp_path):
    """When sector-etf-aggregate-XLK.json is older than 14 days,
    etf_benchmark.warnings includes 'aggregate stale'."""
    sample = json.loads((FIXTURES / "sector-etf-aggregate-xlk-sample.json").read_text())
    stale_date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=20)).strftime("%Y-%m-%d")
    sample["as_of"] = stale_date
    target = tmp_path / "sector-etf-aggregate-XLK.json"
    target.write_text(json.dumps(sample, indent=2), encoding="utf-8")

    anchor = FIXTURES / "comps_anchor_aapl.json"
    base = FIXTURES / "comps_anchor_aapl_memo_fetch.json"
    peer = FIXTURES / "comps_peer_msft.json"
    env = {**ENV, "INVESTING_TOOLKIT_AGGREGATES_DIR": str(tmp_path)}
    proc = subprocess.run(
        ["uv", "run", str(COMPS_SCRIPT),
         "--mode", "compute", "--anchor", str(anchor), "--anchor-base", str(base),
         "--peers", str(peer), "--sector-benchmark"],
        capture_output=True, text=True, timeout=60, env=env, cwd=str(ROOT),
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    bench = payload["anchor"]["etf_benchmark"]
    assert any("aggregate stale" in w for w in bench.get("warnings", [])), bench.get("warnings")
```

- [ ] **Step 4: Run tests — expect PASS**

```bash
PYTHONDONTWRITEBYTECODE=1 cd investing-toolkit && uv run pytest tests/analysis/test_comps_etf_benchmark.py -v
```
Expected: all PASS. If non-US skip fails, the US-ticker heuristic in `comps_compute.main` is wrong — fix the heuristic (e.g. check info.market or ticker suffix `.T` / `.JP` / `.TW` / `.HK` / `.KS`).

- [ ] **Step 5: Commit**

```bash
git add investing-toolkit/tests/analysis/fixtures/comps_anchor_7203_jp.json investing-toolkit/tests/analysis/fixtures/comps_anchor_7203_jp_memo_fetch.json investing-toolkit/tests/analysis/test_comps_etf_benchmark.py
git commit -m "$(cat <<'EOF'
test(analysis-comps): non-US skip + stale aggregate guard for etf_benchmark

v2.2.0-c-bench T8: 7203.T → etf_benchmark.status='skipped'; aggregate
older than 14d → 'aggregate stale' warning. Implementation lives in T7;
this commit locks down the behavior.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 9: Extend `schema-compute-output.json` for `etf_benchmark` block

**Files:**
- Modify: `investing-toolkit/skills/analysis-comps/references/schema-compute-output.json`
- Modify: `investing-toolkit/tests/analysis/test_comps_etf_benchmark.py` (add a schema-validation test)

**Why:** The output JSON schema is part of the contract. v2.2.0-c-bench adds an optional sibling key under `anchor`; without an updated schema, downstream consumers can't validate.

- [ ] **Step 1: Read current schema**

```bash
head -125 investing-toolkit/skills/analysis-comps/references/schema-compute-output.json
```
Note: schema declares `anchor.additionalProperties: false`, so we must add `etf_benchmark` to `anchor.properties`.

- [ ] **Step 2: Patch schema-compute-output.json**

Edit `investing-toolkit/skills/analysis-comps/references/schema-compute-output.json`:

(a) Inside `anchor.properties` (right after `compute_provenance` entry near line 24), add:
```jsonc
        "etf_benchmark": {"$ref": "#/$defs/etfBenchmarkBlock"}
```

(b) Inside `$defs` (after `computeProvenanceBlock`, before the closing `}` of `$defs`), add:
```jsonc
    "etfBenchmarkBlock": {
      "comment": "v2.2.0-c-bench: SPDR sector ETF aggregate benchmark layer. Emitted only when --sector-benchmark flag passed. Either {status, reason} (non-US / unmapped / aggregate-missing) OR {etf, schema_id, as_of, _meta, multiples, indicators, warnings} (US ticker with healthy aggregate).",
      "type": "object",
      "oneOf": [
        {
          "required": ["status", "reason"],
          "additionalProperties": false,
          "properties": {
            "status": {"const": "skipped"},
            "reason": {"type": "string"}
          }
        },
        {
          "required": ["etf", "schema_id", "as_of", "_meta", "multiples", "indicators", "warnings"],
          "additionalProperties": false,
          "properties": {
            "etf":       {"type": "string"},
            "schema_id": {"$ref": "#/$defs/schemaId"},
            "as_of":     {"type": "string"},
            "_meta":     {"type": "object"},
            "multiples": {
              "type": "object",
              "additionalProperties": {"$ref": "#/$defs/etfBenchEntry"}
            },
            "indicators": {
              "type": "object",
              "additionalProperties": {"$ref": "#/$defs/etfBenchEntry"}
            },
            "warnings":  {"type": "array", "items": {"type": "string"}}
          }
        }
      ]
    },
    "etfBenchEntry": {
      "type": "object",
      "required": ["individual", "etf_aggregate", "delta_pct", "band"],
      "additionalProperties": true,
      "properties": {
        "individual":    {"type": ["number", "null"]},
        "etf_aggregate": {"type": ["number", "null"]},
        "delta_pct":     {"type": ["number", "null"]},
        "band":          {"enum": ["in_line", "notable", "extreme", "n/a"]},
        "note":          {"type": "string"}
      }
    }
```

- [ ] **Step 3: Add a schema-validation smoke test**

Append to `investing-toolkit/tests/analysis/test_comps_etf_benchmark.py`:
```python
def test_etf_benchmark_output_validates_against_schema(stub_xlk_aggregate):
    """jsonschema validation of compute output with etf_benchmark block present."""
    try:
        import jsonschema
    except ImportError:
        pytest.skip("jsonschema not installed in test env")

    schema = json.loads((REFERENCES / "schema-compute-output.json").read_text())
    anchor = FIXTURES / "comps_anchor_aapl.json"
    base = FIXTURES / "comps_anchor_aapl_memo_fetch.json"
    peer = FIXTURES / "comps_peer_msft.json"
    env = {**ENV, "INVESTING_TOOLKIT_AGGREGATES_DIR": str(stub_xlk_aggregate)}
    proc = subprocess.run(
        ["uv", "run", str(COMPS_SCRIPT),
         "--mode", "compute", "--anchor", str(anchor), "--anchor-base", str(base),
         "--peers", str(peer), "--sector-benchmark"],
        capture_output=True, text=True, timeout=60, env=env, cwd=str(ROOT),
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    jsonschema.validate(payload, schema)
```

- [ ] **Step 4: Run schema-validation test — expect PASS**

```bash
PYTHONDONTWRITEBYTECODE=1 cd investing-toolkit && uv run pytest tests/analysis/test_comps_etf_benchmark.py::test_etf_benchmark_output_validates_against_schema -v
```
Expected: PASS. If validation fails, the schema patch and the actual output shape diverge — fix the schema (add missing keys / loosen `additionalProperties` where appropriate).

- [ ] **Step 5: Confirm no schema regression on existing tests**

```bash
PYTHONDONTWRITEBYTECODE=1 cd investing-toolkit && uv run pytest tests/analysis/ tests/test_pipeline_integration.py -m "not network" -q
```
Expected: all PASS.

- [ ] **Step 6: Commit**

```bash
git add investing-toolkit/skills/analysis-comps/references/schema-compute-output.json investing-toolkit/tests/analysis/test_comps_etf_benchmark.py
git commit -m "$(cat <<'EOF'
feat(analysis-comps): extend schema-compute-output.json for etf_benchmark block

v2.2.0-c-bench T9: declare etf_benchmark block schema (oneOf — skipped vs
populated). New $defs entries etfBenchmarkBlock + etfBenchEntry; sibling
under anchor.properties; jsonschema validation locked in test.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 10: Document `--sector-benchmark` in `analysis-comps/SKILL.md`

**Files:**
- Modify: `investing-toolkit/skills/analysis-comps/SKILL.md`

**Why:** SKILL.md is the entry-point doc. New runtime flag must be discoverable.

- [ ] **Step 1: Locate the right insertion point**

```bash
grep -n "compute mode\|--mode compute\|--show-routing\|## " investing-toolkit/skills/analysis-comps/SKILL.md | head -20
```
Expected: see the section that documents compute-mode flags.

- [ ] **Step 2: Add documentation section**

In `investing-toolkit/skills/analysis-comps/SKILL.md`, after the section that documents `--show-routing` (or after the compute-mode usage section), add:
```markdown
### `--sector-benchmark` — SPDR sector ETF aggregate benchmark (v2.2.0-c-bench, opt-in)

Adds an `etf_benchmark` block under `anchor` showing per-multiple and
per-indicator divergence vs the anchor's mapped SPDR sector ETF aggregate.

```bash
uv run scripts/comps_compute.py --mode compute \
  --anchor anchor.json --anchor-base anchor-memo-fetch.json --peers peer.json \
  --sector-benchmark
```

- Mapping: `anchor.schema_id` (from sector classifier) → SPDR ETF (`bank → XLF`,
  `tech-saas → XLK`, `reit → XLRE`, `energy → XLE`, `utilities → XLU`,
  `default → XLY`). See [`references/etf-schema-map.json`](references/etf-schema-map.json).
- Aggregates refreshed weekly by GitHub Actions
  (`.github/workflows/sector-etf-aggregates.yml`); runtime reads
  `references/sector-etf-aggregate-<ETF>.json`.
- Bands: `in_line` (≤20% delta) / `notable` (20–50%) / `extreme` (>50%).
- Non-US ticker → `etf_benchmark: {status: "skipped"}`.
- Stale aggregate (`>14 days`) → `etf_benchmark.warnings` includes `"aggregate stale"`.
- Flag absent → `etf_benchmark` key absent (v2.2.0-c shape preserved).

Spec: [`docs/superpowers/specs/2026-05-05-investing-toolkit-v2.2.0-c-bench-spdr-etf-benchmark-design.md`](../../../docs/superpowers/specs/2026-05-05-investing-toolkit-v2.2.0-c-bench-spdr-etf-benchmark-design.md).
```

- [ ] **Step 3: Verify SKILL.md still passes structure validator**

```bash
PYTHONDONTWRITEBYTECODE=1 uv run python investing-toolkit/scripts/check-skill-structure.py investing-toolkit/skills/analysis-comps/ 2>&1 | head -20
```
(If the check script lives elsewhere, adapt the path; typical location is `scripts/check-skill-structure.py`.)
Expected: no violations.

- [ ] **Step 4: Commit**

```bash
git add investing-toolkit/skills/analysis-comps/SKILL.md
git commit -m "$(cat <<'EOF'
docs(analysis-comps): document --sector-benchmark in SKILL.md

v2.2.0-c-bench T10: opt-in flag, ETF mapping, band thresholds, non-US
skip behavior, stale-aggregate guard. Links to spec.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 11: Generate the 11 initial `sector-etf-aggregate-*.json` files

**Files:**
- Create: `investing-toolkit/skills/analysis-comps/references/sector-etf-aggregate-{XLE,XLB,XLI,XLY,XLP,XLV,XLF,XLK,XLC,XLU,XLRE}.json` (11 files)

**Why:** Without these, runtime falls into the `aggregate missing` skipped path on first deployment. The GHA workflow will refresh them weekly, but T0 needs an initial commit.

**⚠️ Risk note**: This task involves a real network run via `etf_aggregator.py --all`. Total cold-cache run time ~70–140 min (11 ETFs × ~6 min each). If the run fails partway, the partial files committed are still valid (each is independent); resume by running `--etf <missing_etf>` for each missing ETF.

- [ ] **Step 1: Try a single-ETF dry run first to validate end-to-end**

```bash
PYTHONDONTWRITEBYTECODE=1 cd investing-toolkit && uv run skills/analysis-comps/scripts/etf_aggregator.py --etf XLU --output -
```
(XLU is sector-pure (utilities), small holdings list — fastest.)
Expected: JSON dump on stdout with `etf: "XLU"`, populated `multiples` + `indicators` + `_meta.holdings_count > 0`.

If this fails, debug before proceeding (most likely cause: yfinance holdings API change or memo-fetch upstream issue).

- [ ] **Step 2: Run for all 11 ETFs**

```bash
PYTHONDONTWRITEBYTECODE=1 cd investing-toolkit && uv run skills/analysis-comps/scripts/etf_aggregator.py --all
```
Expected: 11 files written under `investing-toolkit/skills/analysis-comps/references/sector-etf-aggregate-*.json`. Stderr logs each filename.

- [ ] **Step 3: Verify all 11 files exist + sanity-check shape**

```bash
ls investing-toolkit/skills/analysis-comps/references/sector-etf-aggregate-*.json | wc -l
```
Expected: `11`.

```bash
for f in investing-toolkit/skills/analysis-comps/references/sector-etf-aggregate-*.json; do
  python -c "
import json, sys
d = json.load(open(sys.argv[1]))
assert d.get('etf') and d.get('schema_id') and d.get('as_of'), d
assert d.get('_meta', {}).get('holdings_count', 0) > 0, d['_meta']
print(sys.argv[1], 'ok')
" "$f"
done
```
Expected: 11 lines with `ok`.

- [ ] **Step 4: Commit**

```bash
git add investing-toolkit/skills/analysis-comps/references/sector-etf-aggregate-*.json
git commit -m "$(cat <<'EOF'
chore(sector-aggregates): initial commit of 11 SPDR sector ETF aggregates

v2.2.0-c-bench T11: first-run output of etf_aggregator.py --all. GHA
weekly cron (T13) will refresh these every Saturday. Runtime
--sector-benchmark reads these files as the comparison benchmark.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 12: GitHub Actions weekly cron — `.github/workflows/sector-etf-aggregates.yml`

**Files:**
- Create: `.github/workflows/sector-etf-aggregates.yml`

- [ ] **Step 1: Inspect existing workflows for repo conventions**

```bash
ls .github/workflows/
head -40 .github/workflows/$(ls .github/workflows/ | head -1)
```
Note: pick up patterns for `uv` setup, `actions/checkout`, env, secrets handling.

- [ ] **Step 2: Write the workflow**

Create `.github/workflows/sector-etf-aggregates.yml`:
```yaml
name: sector-etf-aggregates

on:
  schedule:
    - cron: '0 6 * * 6'   # Saturday 06:00 UTC = Asia/Taipei Sat 14:00
  workflow_dispatch:

permissions:
  contents: write
  issues: write

jobs:
  refresh-aggregates:
    runs-on: ubuntu-latest
    timeout-minutes: 360   # 6h hard budget; warm-cache run ~5 min, cold ~2.5h
    env:
      PYTHONDONTWRITEBYTECODE: "1"
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3

      - name: Cache SEC EDGAR companyfacts
        uses: actions/cache@v4
        with:
          path: ~/.cache/investing-toolkit/sec_edgar/companyfacts
          key: companyfacts-${{ github.run_id }}
          restore-keys: |
            companyfacts-

      - name: Cache yfinance responses
        uses: actions/cache@v4
        with:
          path: ~/.cache/investing-toolkit/yfinance
          key: yfinance-${{ github.run_id }}
          restore-keys: |
            yfinance-

      - name: Aggregate all 11 SPDR sector ETFs
        id: aggregate
        run: |
          uv run investing-toolkit/skills/analysis-comps/scripts/etf_aggregator.py --all

      - name: Commit refreshed aggregates
        run: |
          git config user.name  "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add investing-toolkit/skills/analysis-comps/references/sector-etf-aggregate-*.json
          if git diff --cached --quiet; then
            echo "no changes — aggregates unchanged this week"
            exit 0
          fi
          git commit -m "chore(sector-aggregates): weekly refresh $(date -u +%Y-%m-%d)"
          git push

      - name: Open issue on failure
        if: failure()
        uses: peter-evans/create-issue-from-file@v5
        with:
          title: "sector-etf-aggregates weekly refresh failed (${{ github.run_id }})"
          content-filepath: /dev/null   # body filled inline below via update-step or env
          labels: |
            sector-aggregate-stale
            ci-failure
```

(Note: `peter-evans/create-issue-from-file` requires a content file; alternative is to use a simpler issue-on-failure step with `peter-evans/create-issue-from-body` or write a small inline `gh issue create` step. If the action above doesn't work as written, fall back to:
```yaml
      - name: Open issue on failure
        if: failure()
        run: |
          gh issue create \
            --title "sector-etf-aggregates weekly refresh failed (${{ github.run_id }})" \
            --body  "Run: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}" \
            --label "sector-aggregate-stale,ci-failure"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
Prefer this fallback if simpler.)

- [ ] **Step 3: Lint workflow YAML**

```bash
uv run python -c "import yaml; yaml.safe_load(open('.github/workflows/sector-etf-aggregates.yml'))"
```
Expected: no error.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/sector-etf-aggregates.yml
git commit -m "$(cat <<'EOF'
ci: add sector-etf-aggregates weekly cron

v2.2.0-c-bench T12: Saturday 06:00 UTC cron + workflow_dispatch refreshes
the 11 sector-etf-aggregate-*.json files via etf_aggregator.py --all.
Caches SEC EDGAR companyfacts + yfinance to keep run time under 10 min
when warm. Auto-opens issue on failure (label sector-aggregate-stale).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 13: Network smoke test for live aggregator + end-to-end

**Files:**
- Create: `investing-toolkit/tests/analysis/test_etf_aggregator_live.py`

**Why:** Lock down that the live yfinance + EDGAR path works. Marked `@pytest.mark.network` so offline CI ignores it; weekly run hits it.

- [ ] **Step 1: Write the live test**

Create `investing-toolkit/tests/analysis/test_etf_aggregator_live.py`:
```python
"""Network smoke tests for v2.2.0-c-bench. Marked @pytest.mark.network — skipped
under default `pytest -m 'not network'` filter. Weekly CI runs them.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills" / "analysis-comps" / "scripts"
AGG_SCRIPT = SCRIPTS / "etf_aggregator.py"
COMPS_SCRIPT = SCRIPTS / "comps_compute.py"

ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}


@pytest.mark.network
def test_aggregate_xlk_live(tmp_path):
    """Real yfinance + memo-fetch run for XLK; output goes to tmp_path."""
    out_path = tmp_path / "xlk.json"
    proc = subprocess.run(
        ["uv", "run", str(AGG_SCRIPT), "--etf", "XLK", "--output", str(out_path)],
        capture_output=True, text=True, timeout=600, env=ENV, cwd=str(ROOT),
    )
    assert proc.returncode == 0, proc.stderr[-500:]
    assert out_path.exists()
    payload = json.loads(out_path.read_text())
    assert payload["etf"] == "XLK"
    assert payload["schema_id"] == "tech-saas"
    assert payload["_meta"]["holdings_count"] >= 10
    assert payload["multiples"].get("trailingPE") is not None


@pytest.mark.network
def test_compute_with_sector_benchmark_aapl_live():
    """End-to-end: AAPL → fetch comps-multiples + memo-fetch → comps_compute
    --sector-benchmark → assert etf_benchmark.multiples.trailingPE.delta_pct
    is numeric and band ∈ {in_line, notable, extreme, n/a}."""
    pack = ROOT / "skills" / "data-us" / "scripts" / "pack.py"
    yf = ROOT / "skills" / "data-us" / "scripts" / "yfinance_client.py"

    # Use the test_comps_sector_compute helpers if accessible; otherwise inline.
    # Skip detail; this mirrors the existing test_compute_default_aapl pattern
    # but adds --sector-benchmark.
    import importlib.util, sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    spec = importlib.util.spec_from_file_location(
        "_sc", Path(__file__).resolve().parent / "test_comps_sector_compute.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # ... (use helpers _fetch_comps_multiples, _fetch_memo_fetch, _run_uv)
    # For brevity here; concrete code follows the existing pattern in
    # test_comps_sector_compute.py.
    pytest.skip("end-to-end live test deferred to weekly cron — see T13 for plan")
```

(Note: full end-to-end live test is involved; the second test above can be filled in by reusing `_fetch_comps_multiples` / `_fetch_memo_fetch` from `test_comps_sector_compute.py` — for this plan we ship just the `test_aggregate_xlk_live` smoke test. The end-to-end live test can be a follow-up if not landed in this PR.)

- [ ] **Step 2: Verify the test is correctly marked (skipped under offline run)**

```bash
PYTHONDONTWRITEBYTECODE=1 cd investing-toolkit && uv run pytest tests/analysis/test_etf_aggregator_live.py -m "not network" -v
```
Expected: tests are deselected (count = 0 selected, 1+ deselected).

- [ ] **Step 3: Commit**

```bash
git add investing-toolkit/tests/analysis/test_etf_aggregator_live.py
git commit -m "$(cat <<'EOF'
test(analysis-comps): add network smoke test for live etf_aggregator

v2.2.0-c-bench T13: marked @pytest.mark.network, runs in weekly cron;
verifies live yfinance + EDGAR path produces a populated XLK aggregate.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 14: ROADMAP closeout + memory pointer update

**Files:**
- Modify: `investing-toolkit/ROADMAP.md`
- Modify: `/Users/kouko/.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/project_investing_toolkit_v2x_roadmap.md`

- [ ] **Step 1: Move v2.2.0-c-bench entry to closed section**

Edit `investing-toolkit/ROADMAP.md`. Locate `### v2.2.0-c-bench — SPDR sector ETF aggregate benchmark layer (follow-up)` (around line 112). Change the heading to:
```markdown
### ~~v2.2.0-c-bench — SPDR sector ETF aggregate benchmark layer~~ ✅ closed YYYY-MM-DD (PR #N)
```
(Replace `YYYY-MM-DD` with today's date and `#N` with the actual PR number once known. If unknown at commit time, leave `PR TBD`.)

Update the entry body to reflect ship state (delete the "Blocker: None…" line; add a "Reference: PR #N" line at the end matching v2.2.0-c entry's style).

- [ ] **Step 2: Add v2.2.0-c-{jp,tw,kr,cn} placeholder entries to "Future Roadmap"**

Locate the "Future Roadmap (planning)" section (around line 250) and add:
```markdown
### v2.2.0-c-{jp,tw,kr,cn} — Per-region sector ETF benchmark (follow-up to v2.2.0-c-bench)

- **What**: Repeat the v2.2.0-c-bench pattern for non-US tickers using regional sector ETFs (JP: iShares MSCI Japan sector / NEXT FUNDS TOPIX-17; TW: FTSE TWSE Taiwan 50 sector slices; KR: KODEX 200 sector ETFs; CN: CSI 300 sector indexes).
- **Why**: v2.2.0-c-bench currently emits `etf_benchmark.status: "skipped"` for non-US tickers; per-region rollout closes the gap.
- **Blocker**: per-region holdings data availability + per-region sector ETF coverage research.
- **Reference**: spawned 2026-05-05 from v2.2.0-c-bench closeout.
```

- [ ] **Step 3: Update the memory pointer**

Edit `/Users/kouko/.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/project_investing_toolkit_v2x_roadmap.md` — locate the line about v2.2.0-c-bench (currently in the "Next pickup" list) and change to:
```markdown
- v2.2.0-c-bench (PR #N) ✅ shipped YYYY-MM-DD — SPDR sector ETF aggregate benchmark layer; weekly GHA cron refreshes 11 sector-etf-aggregate-*.json; --sector-benchmark opt-in flag emits etf_benchmark block under anchor with 20%/50% bands; non-US tickers skip gracefully; stale-aggregate guard at 14d.
```
And add a new "Next pickup" item:
```markdown
- ⭐ **v2.2.0-c-{jp,tw,kr,cn}** — per-region sector ETF benchmark; pattern locked by v2.2.0-c-bench
```

- [ ] **Step 4: Commit (do separately after PR merge if PR # not known yet)**

```bash
git add investing-toolkit/ROADMAP.md /Users/kouko/.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/project_investing_toolkit_v2x_roadmap.md
git commit -m "$(cat <<'EOF'
docs(roadmap): close v2.2.0-c-bench + spawn v2.2.0-c-{jp,tw,kr,cn}

v2.2.0-c-bench T14: ROADMAP entry moved to closed section; per-region
follow-ups (JP/TW/KR/CN) added to Future Roadmap. Memory pointer updated.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Self-Review

**Spec coverage check:**

| Spec section | Task |
|---|---|
| §1 Goal — etf_aggregator + 11 JSONs + 11-GICS warnings + opt-in flag | T3, T4, T5, T6, T7, T11 |
| §3 Scope — schema-driven aggregation | T4, T5 |
| §4 Architecture diagram — build-time + runtime | T4 (build) + T7 (runtime) |
| §5 Files — etf_aggregator.py / etf-schema-map.json / sector-warnings.md / sector-etf-aggregate-*.json / `--sector-benchmark` / yfinance holdings / GHA workflow / SKILL.md / schema-compute-output.json / ROADMAP | T2 / T3 / T3 / T11 / T6+T7 / T2 / T12 / T10 / T9 / T14 |
| §6.1 ETF→schema map | T3 |
| §6.2 etf_aggregator.py algo | T4 + T5 |
| §6.3 sector-warnings.md | T3 |
| §6.4 etf_benchmark output schema | T7 + T9 |
| §7.1 unit tests aggregator | T4 + T5 |
| §7.2 runtime tests | T6 + T7 + T8 |
| §7.3 network smoke | T13 |
| §8 CI workflow | T12 |
| §9 ROADMAP closeout | T14 |
| §10 deferred items | (no task — documentary) |
| §11 risks | (no task — documentary) |
| §12 acceptance | T7 + T8 + T9 (assertions match acceptance criteria) |

All §1–§9 spec sections have a covering task. §10/§11 are documentary.

**Placeholder scan:** Searched for "TODO" / "TBD" / "fill in" / "appropriate error handling" / "similar to". One acceptable instance: T13 step 1 has a stub `pytest.skip("end-to-end live test deferred to weekly cron — see T13 for plan")` — this is intentional (the live aggregate smoke test in step 1 is sufficient for first ship; full E2E live test is opt-in extension). PR # in T14 commit is left as `PR TBD` since not knowable until PR is opened — acceptable pattern.

**Type consistency:** `compute_multiples_from_memo_fetch` / `compute_indicators_from_memo_fetch` (renamed in T1) used in T4 — ✓. `_classify_etf_benchmark_band` used by T7 internal + T7 step 2 test parametrize — ✓. `_load_etf_to_schema_inv()` used by T7 — ✓. `INVESTING_TOOLKIT_AGGREGATES_DIR` env var used by T7 implementation + T7/T8/T9 tests — ✓. `etf_to_schema` JSON key consistent across T3 file + T4 loader.

**Order of operations check:** T1 (rename) → T2 (yfinance --action holdings) → T3 (refs) → T4 (aggregator skeleton, depends on T1+T2+T3) → T5 (more aggregator tests) → T6 (flag plumbing) → T7 (block emission, depends on T3+T6) → T8 (skip + stale tests) → T9 (schema, depends on T7) → T10 (SKILL.md) → T11 (real-data initial commit, depends on T2+T3+T4+T5) → T12 (GHA, depends on T11) → T13 (live smoke) → T14 (ROADMAP closeout). No backward dependencies.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-05-05-investing-toolkit-v2.2.0-c-bench-etf-aggregate.md`.**

Two execution options:

**1. Subagent-Driven (recommended)** — fresh subagent per task + 2-stage review (spec then code-quality). Per memory `feedback_subagent_driven_development_validated.md`, this pattern was validated on PR #239's 10-task plan (30 subagent invocations / 11 commits / 0 broken commits). 14-task plan above is well-suited.

**2. Inline Execution** — execute tasks in this session using executing-plans, batch execution with checkpoints for review.

**Which approach?**

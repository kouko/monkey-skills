# investing-toolkit v2.2.0-c — Sector Multiples + SPDR ETF Benchmark Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend `analysis-comps --mode compute` with US sector classification, sector-specific multiples (ROE / Rule-of-40 / P/FFO), and weekly-refreshed SPDR sector ETF aggregate benchmark with per-multiple divergence bands.

**Architecture:** Two new scripts (`sector_classifier.py` + `etf_aggregator.py`) under `analysis-comps/scripts/`; two new reference files (`sector-overrides.json` + `sector-warnings.md`) plus 11 ETF-aggregate JSON files (flat in `references/` per skill folder convention); new `--sector-benchmark` CLI flag in `comps_compute.py` that emits a backward-compatible `sector` block. Build-time aggregator runs weekly via GitHub Actions.

**Tech Stack:** Python 3.10+ (PEP 723 self-contained scripts), pytest, yfinance (existing dependency), SEC EDGAR companyfacts (via existing `data-us/scripts/pack.py`).

**Spec:** [`docs/superpowers/specs/2026-05-05-investing-toolkit-v2.2.0-c-sector-multiples-design.md`](../specs/2026-05-05-investing-toolkit-v2.2.0-c-sector-multiples-design.md)

---

## File Structure

**New files** (all flat — no nested subfolders per `CLAUDE.md` skill folder rule):

```
investing-toolkit/skills/analysis-comps/
├── scripts/
│   ├── sector_classifier.py        # T2-T3
│   └── etf_aggregator.py           # T5
└── references/
    ├── sector-overrides.json       # T1
    ├── sector-warnings.md          # T1
    └── sector-etf-aggregate-{XLE,XLB,XLI,XLY,XLP,XLV,XLF,
                              XLK,XLC,XLU,XLRE}.json  # T8

investing-toolkit/tests/
├── analysis/
│   ├── test_sector_classifier.py   # T2-T3
│   └── test_etf_aggregator.py      # T5
└── data/fixtures/
    └── sector-etf-aggregate-{XLK,XLF,XLRE}-sample.json  # T8

.github/workflows/
└── sector-etf-aggregates.yml       # T8
```

**Modified files**:

- `investing-toolkit/skills/analysis-comps/scripts/comps_compute.py` (T4 helpers, T7 `--sector-benchmark` wiring)
- `investing-toolkit/skills/analysis-comps/references/schema-compute-output.json` (T6 sector block schema)
- `investing-toolkit/skills/analysis-comps/SKILL.md` (T10 doc)
- `investing-toolkit/tests/integration/test_cross_layer_chains.py` (T9 6 new integration tests)
- `investing-toolkit/ROADMAP.md` (T10 closeout)
- `~/.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/project_investing_toolkit_v2x_roadmap.md` (T10 memory pointer)

---

## Task Dependency Graph

```
T1 (refs scaffolding)
  ├─→ T2 (classifier core: override file)
  │     └─→ T3 (classifier yfinance routing)
  │           ├─→ T5 (etf_aggregator uses classifier)
  │           └─→ T7 (comps_compute uses classifier)
  ├─→ T7 (warnings file loaded by comps_compute)
T4 (sector multiple helpers in comps_compute)
  └─→ T7 (comps_compute calls helpers)
T5 (etf_aggregator)
  └─→ T8 (GHA + seed JSONs)
T6 (schema)
  └─→ T7 (compute emits per schema)
T7 (comps_compute --sector-benchmark) ──→ T9 (integration tests)
T8 (workflow + fixtures)               ──┘
T9 ─→ T10 (SKILL.md + ROADMAP)
```

10 tasks total. Each task = one commit (some have 2 if test + impl split makes sense). Subagent-driven-development per `feedback_subagent_driven_development_validated.md`.

---

## Task 1: Reference file scaffolding

**Files:**
- Create: `investing-toolkit/skills/analysis-comps/references/sector-overrides.json`
- Create: `investing-toolkit/skills/analysis-comps/references/sector-warnings.md`
- Test: `investing-toolkit/tests/analysis/test_sector_classifier.py` (just the schema validation slice)

- [ ] **Step 1: Write the failing test for sector-overrides.json schema**

Create `investing-toolkit/tests/analysis/test_sector_classifier.py` (initial scaffolding):

```python
"""Tests for analysis-comps sector classifier and references."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REFS = Path(__file__).parents[2] / "skills" / "analysis-comps" / "references"


def test_sector_overrides_json_well_formed():
    """sector-overrides.json must parse + each entry has required fields."""
    overrides = json.loads((REFS / "sector-overrides.json").read_text())
    required_keys = {"gics", "sub_industry", "etf", "exclude_specific_multiples", "reason"}
    assert "BRK.A" in overrides
    assert "BRK.B" in overrides
    assert "META" in overrides
    assert "SQ" in overrides
    assert "AMZN" in overrides
    for ticker, entry in overrides.items():
        assert required_keys <= entry.keys(), f"{ticker} missing fields"
        assert entry["etf"] in {"XLE", "XLB", "XLI", "XLY", "XLP", "XLV",
                                "XLF", "XLK", "XLC", "XLU", "XLRE"}
        assert isinstance(entry["exclude_specific_multiples"], bool)
        assert isinstance(entry["reason"], str) and entry["reason"]


def test_sector_warnings_md_has_11_gics_rows():
    """sector-warnings.md must contain a row per GICS L1."""
    text = (REFS / "sector-warnings.md").read_text()
    expected_etfs = {"XLE", "XLB", "XLI", "XLY", "XLP", "XLV",
                     "XLF", "XLK", "XLC", "XLU", "XLRE"}
    for etf in expected_etfs:
        assert etf in text, f"sector-warnings.md missing row for {etf}"
```

- [ ] **Step 2: Run test, verify FAIL**

```bash
cd investing-toolkit
PYTHONDONTWRITEBYTECODE=1 uv run --no-project pytest tests/analysis/test_sector_classifier.py -v
```

Expected: FAIL — `FileNotFoundError` on both reference files.

- [ ] **Step 3: Create sector-overrides.json**

Write `investing-toolkit/skills/analysis-comps/references/sector-overrides.json`:

```json
{
  "BRK.A": {
    "gics": "Financial Services",
    "sub_industry": "Conglomerate",
    "etf": "XLF",
    "exclude_specific_multiples": true,
    "reason": "Multi-sector conglomerate; ROE driven by insurance float + non-financial operating businesses. Bank-style ROE comparison would be misleading."
  },
  "BRK.B": {
    "gics": "Financial Services",
    "sub_industry": "Conglomerate",
    "etf": "XLF",
    "exclude_specific_multiples": true,
    "reason": "Same as BRK.A (Class B share)."
  },
  "META": {
    "gics": "Technology",
    "sub_industry": "Software—Application",
    "etf": "XLK",
    "exclude_specific_multiples": false,
    "reason": "yfinance routes META to Communication Services > Internet Content & Information; widely benchmarked vs IT peers (advertising-driven SaaS economics)."
  },
  "SQ": {
    "gics": "Financial Services",
    "sub_industry": "Financial Data & Stock Exchanges",
    "etf": "XLF",
    "exclude_specific_multiples": false,
    "reason": "yfinance routes Block (SQ) to Software—Infrastructure; business is fintech / payment processing, more comparable to financial peers."
  },
  "AMZN": {
    "gics": "Technology",
    "sub_industry": "Internet Retail / Cloud",
    "etf": "XLK",
    "exclude_specific_multiples": false,
    "reason": "yfinance routes AMZN to Consumer Cyclical > Internet Retail; AWS cloud business material to valuation, IT-relative comparison preferred."
  }
}
```

- [ ] **Step 4: Create sector-warnings.md**

Write `investing-toolkit/skills/analysis-comps/references/sector-warnings.md`:

```markdown
# Sector Warning Matrix (v2.2.0-c)

Source-of-truth for `comps_compute.py --sector-benchmark` warnings. One row per GICS L1
(11 rows, aligned to SPDR Select Sector ETFs). Loaded at runtime; pluck by classification
result and append to `sector.warnings: [...]`.

| GICS L1 | ETF | Sub-industry trigger | Warning text |
|---|---|---|---|
| Energy | XLE | (any) | "P/E and EV/EBITDA on energy issuers are commodity-cycle distorted; prefer P/CF or production-volume multiples (deferred to v2.2.0-c²)." |
| Basic Materials | XLB | (any) | "Materials issuers exhibit cyclical earnings; trailingPE near cycle peaks/troughs is misleading. Default 5 are computable but interpret with caution." |
| Industrials | XLI | (any) | "" |
| Consumer Cyclical | XLY | (any) | "" |
| Consumer Defensive | XLP | (any) | "" |
| Healthcare | XLV | (any) | "Default 5 vary widely across pharma / biotech / services / devices subsectors; biotech often has negative earnings making P/E meaningless. Cash burn metrics deferred to v2.2.0-c²." |
| Financial Services | XLF | starts with `Banks` | "" |
| Financial Services | XLF | other | "trailingPE and priceToSales for non-bank Financials (insurance / asset management / capital markets) require sub-industry-specific KPIs (Combined Ratio / AUM); not applied in this output (deferred to v2.2.0-c²)." |
| Technology | XLK | (any) | "" |
| Communication Services | XLC | (any) | "Heterogeneous: telcos (capital-heavy, EV/EBITDA-relevant) vs media (mixed) vs interactive (tech-like). Sub-industry-aware multiples deferred to v2.2.0-c²." |
| Utilities | XLU | (any) | "Dividend yield is the canonical valuation metric for utilities but not yet computed in this output (deferred to v2.2.0-c²); P/E and EV/EBITDA available but interpretive." |
| Real Estate | XLRE | starts with `REIT` | "" |
| Real Estate | XLRE | other | "Non-REIT real estate issuers (real estate services / development) do not get P/FFO; use default 5 with caution." |

## Loading convention

`comps_compute.py` reads this file at runtime; matches by:
1. `classification.gics` → row(s) for that GICS L1
2. If multiple rows exist for the same GICS, match `classification.sub_industry` against the trigger column (substring match, case-insensitive)
3. Empty warning text → row contributes nothing to `sector.warnings`
```

- [ ] **Step 5: Run test, verify PASS, commit**

```bash
cd investing-toolkit
PYTHONDONTWRITEBYTECODE=1 uv run --no-project pytest tests/analysis/test_sector_classifier.py -v
```

Expected: 2 PASSED.

```bash
git add investing-toolkit/skills/analysis-comps/references/sector-overrides.json \
        investing-toolkit/skills/analysis-comps/references/sector-warnings.md \
        investing-toolkit/tests/analysis/test_sector_classifier.py
git commit -m "feat(analysis-comps): scaffold sector-overrides.json + sector-warnings.md (v2.2.0-c T1)"
```

---

## Task 2: sector_classifier.py — override file + GICS→ETF map

**Files:**
- Create: `investing-toolkit/skills/analysis-comps/scripts/sector_classifier.py`
- Modify: `investing-toolkit/tests/analysis/test_sector_classifier.py` (add classifier tests)

- [ ] **Step 1: Write failing tests for override file lookup + GICS→ETF map**

Append to `investing-toolkit/tests/analysis/test_sector_classifier.py`:

```python
import sys

SCRIPTS = Path(__file__).parents[2] / "skills" / "analysis-comps" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sector_classifier import (  # noqa: E402
    classify,
    GICS_TO_ETF,
    UnclassifiableTickerError,
)


def test_gics_to_etf_map_covers_11_sectors():
    expected = {
        "Energy": "XLE", "Basic Materials": "XLB", "Industrials": "XLI",
        "Consumer Cyclical": "XLY", "Consumer Defensive": "XLP",
        "Healthcare": "XLV", "Financial Services": "XLF", "Technology": "XLK",
        "Communication Services": "XLC", "Utilities": "XLU", "Real Estate": "XLRE",
    }
    assert GICS_TO_ETF == expected


def test_classify_override_file_brk_b():
    """BRK.B is in override file → uses file entry, exclude_specific_multiples=true."""
    result = classify("BRK.B")
    assert result["gics"] == "Financial Services"
    assert result["sub_industry"] == "Conglomerate"
    assert result["etf"] == "XLF"
    assert result["provenance"] == "override_file"
    assert result["exclude_specific_multiples"] is True


def test_classify_override_file_meta():
    """META is in override file → IT not Comm Services."""
    result = classify("META")
    assert result["etf"] == "XLK"
    assert result["provenance"] == "override_file"
    assert result["exclude_specific_multiples"] is False


def test_classify_cli_flag_wins_over_override_file():
    """CLI flag --sector-override 'Energy' wins over file lookup."""
    result = classify("META", override_cli="Energy")
    assert result["gics"] == "Energy"
    assert result["etf"] == "XLE"
    assert result["provenance"] == "cli_flag"
    # No --sub-industry-override → conservative default
    assert result["sub_industry"] == "user-override"
    assert result["exclude_specific_multiples"] is True


def test_classify_cli_flag_invalid_gics_raises():
    with pytest.raises(UnclassifiableTickerError, match="invalid GICS"):
        classify("AAPL", override_cli="NotARealSector")
```

- [ ] **Step 2: Run tests, verify FAIL**

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --no-project pytest tests/analysis/test_sector_classifier.py -v
```

Expected: ImportError on `sector_classifier` module.

- [ ] **Step 3: Create sector_classifier.py with skeleton + override lookup + CLI flag**

Write `investing-toolkit/skills/analysis-comps/scripts/sector_classifier.py`:

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["yfinance>=0.2.40"]
# ///
"""
Sector classifier for analysis-comps --sector-benchmark mode.

Maps a US-listed equity ticker to one of the 11 SPDR Select Sector ETFs
(XLE/XLB/XLI/XLY/XLP/XLV/XLF/XLK/XLC/XLU/XLRE) using:
  1. CLI flag override (--sector-override <gics>)
  2. Override file (references/sector-overrides.json)
  3. yfinance info.sector + info.industry
  4. Else: UnclassifiableTickerError (e.g. non-US, yfinance returns None)

The classifier also decides whether sector-specific multiples (ROE / Rule-of-40 / P/FFO)
apply, via sub-industry substring matching on info.industry.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, TypedDict

REFS_DIR = Path(__file__).parent.parent / "references"
OVERRIDES_PATH = REFS_DIR / "sector-overrides.json"

GICS_TO_ETF: dict[str, str] = {
    "Energy": "XLE",
    "Basic Materials": "XLB",
    "Industrials": "XLI",
    "Consumer Cyclical": "XLY",
    "Consumer Defensive": "XLP",
    "Healthcare": "XLV",
    "Financial Services": "XLF",
    "Technology": "XLK",
    "Communication Services": "XLC",
    "Utilities": "XLU",
    "Real Estate": "XLRE",
}


class ClassificationResult(TypedDict):
    gics: str
    sub_industry: str
    etf: str
    provenance: str  # "cli_flag" | "override_file" | "yfinance_info"
    exclude_specific_multiples: bool


class UnclassifiableTickerError(ValueError):
    """Raised when ticker cannot be classified (non-US, yfinance returns None, etc.)."""


def _load_overrides() -> dict[str, dict]:
    if not OVERRIDES_PATH.exists():
        return {}
    return json.loads(OVERRIDES_PATH.read_text())


def classify(
    ticker: str,
    override_cli: Optional[str] = None,
    sub_industry_cli: Optional[str] = None,
) -> ClassificationResult:
    """Classify ticker. See module docstring for lookup order."""
    # Path 1: CLI flag
    if override_cli:
        if override_cli not in GICS_TO_ETF:
            raise UnclassifiableTickerError(
                f"invalid GICS for --sector-override: {override_cli!r}; "
                f"must be one of {sorted(GICS_TO_ETF)}"
            )
        sub_industry = sub_industry_cli or "user-override"
        return ClassificationResult(
            gics=override_cli,
            sub_industry=sub_industry,
            etf=GICS_TO_ETF[override_cli],
            provenance="cli_flag",
            exclude_specific_multiples=(sub_industry_cli is None),
        )

    # Path 2: override file
    overrides = _load_overrides()
    if ticker in overrides:
        entry = overrides[ticker]
        return ClassificationResult(
            gics=entry["gics"],
            sub_industry=entry["sub_industry"],
            etf=entry["etf"],
            provenance="override_file",
            exclude_specific_multiples=entry["exclude_specific_multiples"],
        )

    # Path 3: yfinance — implemented in T3
    return _classify_via_yfinance(ticker)


def _classify_via_yfinance(ticker: str) -> ClassificationResult:
    """Stub — implemented in Task 3."""
    raise UnclassifiableTickerError(
        f"yfinance classification not yet implemented (T3); ticker={ticker!r}"
    )
```

- [ ] **Step 4: Run tests, verify PASS**

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --no-project pytest tests/analysis/test_sector_classifier.py -v
```

Expected: 7 PASSED (2 from T1 + 5 new).

- [ ] **Step 5: Commit**

```bash
git add investing-toolkit/skills/analysis-comps/scripts/sector_classifier.py \
        investing-toolkit/tests/analysis/test_sector_classifier.py
git commit -m "feat(analysis-comps): sector_classifier override file + GICS map (v2.2.0-c T2)"
```

---

## Task 3: sector_classifier.py — yfinance industry routing matrix

**Files:**
- Modify: `investing-toolkit/skills/analysis-comps/scripts/sector_classifier.py:_classify_via_yfinance`
- Modify: `investing-toolkit/tests/analysis/test_sector_classifier.py` (add 13-row routing matrix tests)

- [ ] **Step 1: Write failing tests for yfinance routing matrix**

Append to `tests/analysis/test_sector_classifier.py`:

```python
from unittest.mock import patch, MagicMock


def _yf_info(sector: str, industry: str) -> MagicMock:
    """Mock yfinance Ticker(...).info dict."""
    mock = MagicMock()
    mock.info = {"sector": sector, "industry": industry, "country": "United States"}
    return mock


@pytest.mark.parametrize("yf_sector,yf_industry,expected_etf,expected_specific", [
    # (yfinance sector, yfinance industry, expected ETF, expects sector-specific multiple?)
    ("Energy",                "Oil & Gas Integrated",         "XLE",  False),
    ("Basic Materials",       "Steel",                        "XLB",  False),
    ("Industrials",           "Aerospace & Defense",          "XLI",  False),
    ("Consumer Cyclical",     "Auto Manufacturers",           "XLY",  False),
    ("Consumer Defensive",    "Discount Stores",              "XLP",  False),
    ("Healthcare",            "Drug Manufacturers—General",   "XLV",  False),
    ("Financial Services",    "Banks—Diversified",            "XLF",  True),   # bank → ROE
    ("Financial Services",    "Banks—Regional",               "XLF",  True),   # bank → ROE
    ("Financial Services",    "Insurance—Property & Casualty","XLF",  False),  # not bank
    ("Financial Services",    "Asset Management",             "XLF",  False),  # not bank
    ("Technology",            "Software—Infrastructure",      "XLK",  True),   # any IT → Rule-of-40
    ("Communication Services","Telecom Services",             "XLC",  False),
    ("Utilities",             "Utilities—Regulated Electric", "XLU",  False),
    ("Real Estate",           "REIT—Diversified",             "XLRE", True),   # REIT → P/FFO
    ("Real Estate",           "Real Estate Services",         "XLRE", False),  # not REIT
])
def test_classify_via_yfinance_routing(yf_sector, yf_industry, expected_etf, expected_specific):
    """13-row yfinance industry routing matrix."""
    # Use a ticker NOT in override file (e.g. XYZTEST)
    with patch("sector_classifier.yf.Ticker", return_value=_yf_info(yf_sector, yf_industry)):
        result = classify("XYZTEST")
    assert result["etf"] == expected_etf
    assert result["gics"] == yf_sector
    assert result["sub_industry"] == yf_industry
    assert result["provenance"] == "yfinance_info"
    if expected_specific:
        assert result["exclude_specific_multiples"] is False
    else:
        assert result["exclude_specific_multiples"] is True


def test_classify_yfinance_non_us_raises():
    """Non-US ticker per yfinance country field → UnclassifiableTickerError."""
    mock = MagicMock()
    mock.info = {"sector": "Technology", "industry": "Semiconductors", "country": "Japan"}
    with patch("sector_classifier.yf.Ticker", return_value=mock):
        with pytest.raises(UnclassifiableTickerError, match="non-US"):
            classify("XYZTEST")


def test_classify_yfinance_missing_sector_raises():
    """yfinance returns None or no sector → UnclassifiableTickerError."""
    mock = MagicMock()
    mock.info = {"sector": None, "industry": None, "country": "United States"}
    with patch("sector_classifier.yf.Ticker", return_value=mock):
        with pytest.raises(UnclassifiableTickerError, match="missing sector"):
            classify("XYZTEST")


def test_classify_yfinance_unknown_gics_raises():
    """yfinance returns a sector not in our GICS_TO_ETF map → raises."""
    mock = MagicMock()
    mock.info = {"sector": "MysteryNewSector", "industry": "X", "country": "United States"}
    with patch("sector_classifier.yf.Ticker", return_value=mock):
        with pytest.raises(UnclassifiableTickerError, match="unknown GICS"):
            classify("XYZTEST")
```

- [ ] **Step 2: Run tests, verify FAIL**

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --no-project pytest tests/analysis/test_sector_classifier.py -v
```

Expected: 18 collected, 5 PASS (T2), 13 FAIL (parametrized), 3 FAIL (non-US / missing / unknown).

- [ ] **Step 3: Implement `_classify_via_yfinance`**

Replace stub in `sector_classifier.py`:

```python
import yfinance as yf  # at top of file

# Sub-industry routing rules: (gics, industry_substring → triggers sector-specific multiple)
_BANK_SUBSTRING = "Banks"     # case-sensitive substring match on info.industry
_REIT_SUBSTRING = "REIT"


def _triggers_specific_multiple(gics: str, sub_industry: str) -> bool:
    """Decide whether sector-specific multiple applies (ROE / Rule-of-40 / P/FFO)."""
    if gics == "Technology":
        return True  # any IT issuer → Rule-of-40
    if gics == "Financial Services" and sub_industry.startswith(_BANK_SUBSTRING):
        return True  # banks only → ROE
    if gics == "Real Estate" and sub_industry.startswith(_REIT_SUBSTRING):
        return True  # REITs only → P/FFO
    return False


def _classify_via_yfinance(ticker: str) -> ClassificationResult:
    info = yf.Ticker(ticker).info or {}
    country = info.get("country") or ""
    if country and country != "United States":
        raise UnclassifiableTickerError(
            f"non-US ticker (country={country!r}); SPDR sector ETFs are US-only"
        )
    sector = info.get("sector")
    industry = info.get("industry") or ""
    if not sector:
        raise UnclassifiableTickerError(
            f"yfinance returned missing sector for {ticker!r}"
        )
    if sector not in GICS_TO_ETF:
        raise UnclassifiableTickerError(
            f"unknown GICS {sector!r} from yfinance; not in GICS_TO_ETF map"
        )
    triggers = _triggers_specific_multiple(sector, industry)
    return ClassificationResult(
        gics=sector,
        sub_industry=industry,
        etf=GICS_TO_ETF[sector],
        provenance="yfinance_info",
        exclude_specific_multiples=not triggers,
    )
```

- [ ] **Step 4: Run tests, verify PASS**

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --no-project pytest tests/analysis/test_sector_classifier.py -v
```

Expected: 22 PASSED.

- [ ] **Step 5: Commit**

```bash
git add investing-toolkit/skills/analysis-comps/scripts/sector_classifier.py \
        investing-toolkit/tests/analysis/test_sector_classifier.py
git commit -m "feat(analysis-comps): sector_classifier yfinance routing matrix (v2.2.0-c T3)"
```

---

## Task 4: Sector-specific multiple compute helpers

**Files:**
- Modify: `investing-toolkit/skills/analysis-comps/scripts/comps_compute.py` (add 3 helpers near existing `_compute_multiples_from_memo_fetch`)
- Modify: `investing-toolkit/tests/analysis/test_analysis_comps.py` (add unit tests for 3 helpers)

- [ ] **Step 1: Write failing tests for the 3 sector-specific multiple helpers**

Append to `tests/analysis/test_analysis_comps.py` (use existing fixture `aapl_memo_fetch_pack` if present, or build minimal):

```python
def test_compute_roe_jpm_like_fixture():
    """ROE = NI[0] / Equity[0] from memo-fetch raw fields."""
    from analysis_comps_helpers import _compute_roe  # adjusted below
    memo = {
        "income_statement": {
            "net_income": {"USD": [{"val": 49000_000_000.0, "fy_end": "2024-12-31"}]}
        },
        "balance_sheet": {
            "total_stockholders_equity": {"USD": [{"val": 320000_000_000.0, "fy_end": "2024-12-31"}]}
        },
    }
    val, meta = _compute_roe(memo)
    assert abs(val - 0.153125) < 1e-6
    assert meta["net_income"]["fiscal_year_ends"] == ["2024-12-31"]
    assert meta["total_stockholders_equity"]["fiscal_year_ends"] == ["2024-12-31"]


def test_compute_roe_missing_equity_returns_none():
    memo = {"income_statement": {"net_income": {"USD": [{"val": 1.0, "fy_end": "2024-12-31"}]}},
            "balance_sheet": {}}
    val, meta = _compute_roe(memo)
    assert val is None


def test_compute_rule_of_40_aapl_like():
    """Rule-of-40 = (Rev[0]/Rev[1] - 1) + (OpInc[0]/Rev[0])."""
    from analysis_comps_helpers import _compute_rule_of_40
    memo = {
        "income_statement": {
            "total_revenue": {"USD": [
                {"val": 391000_000_000.0, "fy_end": "2024-09-28"},
                {"val": 383000_000_000.0, "fy_end": "2023-09-30"},
            ]},
            "operating_income": {"USD": [
                {"val": 123000_000_000.0, "fy_end": "2024-09-28"},
            ]},
        }
    }
    val, meta = _compute_rule_of_40(memo)
    growth = 391000.0 / 383000.0 - 1
    margin = 123000.0 / 391000.0
    assert abs(val - (growth + margin)) < 1e-6


def test_compute_rule_of_40_single_year_returns_none():
    """Need 2 FY of revenue for growth → if only 1, return None."""
    from analysis_comps_helpers import _compute_rule_of_40
    memo = {"income_statement": {
        "total_revenue": {"USD": [{"val": 1.0, "fy_end": "2024-09-28"}]},
        "operating_income": {"USD": [{"val": 0.5, "fy_end": "2024-09-28"}]},
    }}
    val, _ = _compute_rule_of_40(memo)
    assert val is None


def test_compute_price_to_ffo_o_like():
    """P/FFO = marketCap / (NI[0] + D&A[0]) for REIT."""
    from analysis_comps_helpers import _compute_price_to_ffo
    memo = {
        "income_statement": {"net_income": {"USD": [{"val": 800_000_000.0, "fy_end": "2024-12-31"}]}},
        "cash_flow": {"depreciation_amortization": {"USD": [{"val": 1200_000_000.0, "fy_end": "2024-12-31"}]}},
    }
    market_cap = 50_000_000_000.0
    val, meta = _compute_price_to_ffo(memo, market_cap)
    assert abs(val - 25.0) < 1e-6  # 50e9 / 2e9 = 25
```

NOTE on import `from analysis_comps_helpers`: we will expose helpers from `comps_compute.py` via direct module import (the test path-sets `SCRIPTS` to scripts/ in conftest or sys.path). Adjust import in test to `from comps_compute import _compute_roe, _compute_rule_of_40, _compute_price_to_ffo` if existing tests use that pattern. **Implementer**: check `tests/analysis/conftest.py` for the import pattern and match it.

- [ ] **Step 2: Run tests, verify FAIL**

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --no-project pytest tests/analysis/test_analysis_comps.py -v -k "compute_roe or compute_rule_of_40 or compute_price_to_ffo"
```

Expected: ImportError or AttributeError for the 3 helpers.

- [ ] **Step 3: Add helpers to comps_compute.py**

Insert after the existing `_cf_concept_filings` helper in `investing-toolkit/skills/analysis-comps/scripts/comps_compute.py`:

```python
def _compute_roe(memo: dict) -> tuple[float | None, dict]:
    """ROE = NI[0] / Equity[0]. Returns (value, meta) with fiscal_year_ends."""
    inc = memo.get("income_statement", {})
    bs = memo.get("balance_sheet", {})
    ni_arr = (inc.get("net_income") or {}).get("USD") or []
    eq_arr = (bs.get("total_stockholders_equity") or {}).get("USD") or []
    if not ni_arr or not eq_arr:
        return None, {}
    ni = ni_arr[0].get("val")
    eq = eq_arr[0].get("val")
    if ni is None or not eq:
        return None, {}
    meta = {
        "net_income": {"fiscal_year_ends": [ni_arr[0].get("fy_end")]},
        "total_stockholders_equity": {"fiscal_year_ends": [eq_arr[0].get("fy_end")]},
    }
    return ni / eq, meta


def _compute_rule_of_40(memo: dict) -> tuple[float | None, dict]:
    """Rule-of-40 = (Rev[0]/Rev[1] - 1) + (OpInc[0]/Rev[0]). Needs ≥2 FY of revenue."""
    inc = memo.get("income_statement", {})
    rev_arr = (inc.get("total_revenue") or {}).get("USD") or []
    op_arr = (inc.get("operating_income") or {}).get("USD") or []
    if len(rev_arr) < 2 or not op_arr:
        return None, {}
    r0 = rev_arr[0].get("val")
    r1 = rev_arr[1].get("val")
    op = op_arr[0].get("val")
    if not r0 or not r1 or op is None:
        return None, {}
    growth = r0 / r1 - 1
    margin = op / r0
    meta = {
        "total_revenue": {"fiscal_year_ends": [rev_arr[0].get("fy_end"), rev_arr[1].get("fy_end")]},
        "operating_income": {"fiscal_year_ends": [op_arr[0].get("fy_end")]},
    }
    return growth + margin, meta


def _compute_price_to_ffo(memo: dict, market_cap: float | None) -> tuple[float | None, dict]:
    """P/FFO = marketCap / (NI[0] + D&A[0]). For REIT issuers."""
    if not market_cap:
        return None, {}
    inc = memo.get("income_statement", {})
    cf = memo.get("cash_flow", {})
    ni_arr = (inc.get("net_income") or {}).get("USD") or []
    da_arr = (cf.get("depreciation_amortization") or {}).get("USD") or []
    if not ni_arr or not da_arr:
        return None, {}
    ni = ni_arr[0].get("val")
    da = da_arr[0].get("val")
    if ni is None or da is None:
        return None, {}
    ffo = ni + da
    if not ffo:
        return None, {}
    meta = {
        "net_income": {"fiscal_year_ends": [ni_arr[0].get("fy_end")]},
        "depreciation_amortization": {"fiscal_year_ends": [da_arr[0].get("fy_end")]},
    }
    return market_cap / ffo, meta
```

NOTE: the exact `memo` dict shape (income_statement / balance_sheet / cash_flow with `<concept>: {USD: [{val, fy_end}, ...]}`) matches the v2.2.0-l memo-fetch fixture. **Implementer**: verify against `tests/data/fixtures/data-us-memo-fetch-AAPL.json` before coding to confirm key paths.

- [ ] **Step 4: Run tests, verify PASS**

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --no-project pytest tests/analysis/test_analysis_comps.py -v -k "compute_roe or compute_rule_of_40 or compute_price_to_ffo"
```

Expected: 5 PASSED.

- [ ] **Step 5: Commit**

```bash
git add investing-toolkit/skills/analysis-comps/scripts/comps_compute.py \
        investing-toolkit/tests/analysis/test_analysis_comps.py
git commit -m "feat(analysis-comps): sector-specific multiple helpers (roe/rule_of_40/price_to_ffo) (v2.2.0-c T4)"
```

---

## Task 5: etf_aggregator.py — holdings-weighted aggregator

**Files:**
- Create: `investing-toolkit/skills/analysis-comps/scripts/etf_aggregator.py`
- Create: `investing-toolkit/tests/analysis/test_etf_aggregator.py`

- [ ] **Step 1: Write failing tests for aggregator algorithm**

Create `investing-toolkit/tests/analysis/test_etf_aggregator.py`:

```python
"""Tests for analysis-comps etf_aggregator (holdings-weighted SPDR sector ETF aggregate)."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

SCRIPTS = Path(__file__).parents[2] / "skills" / "analysis-comps" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from etf_aggregator import (  # noqa: E402
    _weighted_average,
    _is_outlier,
    aggregate_holdings,
    OUTLIER_BOUNDS,
)


def test_weighted_average_simple():
    """Weighted average drops nulls + uses non-null weight sum as denominator."""
    holdings = [
        {"ticker": "A", "weight": 0.5, "trailingPE": 20.0},
        {"ticker": "B", "weight": 0.3, "trailingPE": 30.0},
        {"ticker": "C", "weight": 0.2, "trailingPE": None},   # null → skip
    ]
    result = _weighted_average(holdings, "trailingPE")
    expected = (0.5 * 20.0 + 0.3 * 30.0) / (0.5 + 0.3)  # excludes C
    assert abs(result - expected) < 1e-6


def test_weighted_average_drops_outliers():
    """Multiples outside OUTLIER_BOUNDS dropped before averaging."""
    holdings = [
        {"ticker": "A", "weight": 0.5, "trailingPE": 25.0},
        {"ticker": "B", "weight": 0.5, "trailingPE": 500.0},  # > 200 upper bound
    ]
    result = _weighted_average(holdings, "trailingPE")
    assert abs(result - 25.0) < 1e-6  # only A contributes


def test_is_outlier_negative_dropped():
    assert _is_outlier(-1.0, "trailingPE") is True
    assert _is_outlier(0.5, "trailingPE") is False
    assert _is_outlier(150.0, "trailingPE") is False
    assert _is_outlier(250.0, "trailingPE") is True


def test_aggregate_holdings_canned_input():
    """End-to-end aggregate over canned holdings list — deterministic."""
    holdings = [
        {"ticker": "AAPL", "weight": 0.13, "trailingPE": 28.0,
         "priceToBook": 50.0, "priceToSales": 7.5, "evEbitda": 22.0},
        {"ticker": "MSFT", "weight": 0.12, "trailingPE": 32.0,
         "priceToBook": 12.0, "priceToSales": 12.0, "evEbitda": 23.0},
    ]
    result = aggregate_holdings(holdings, etf="XLK")
    assert result["etf"] == "XLK"
    assert result["holdings_count"] == 2
    expected_pe = (0.13 * 28.0 + 0.12 * 32.0) / 0.25
    assert abs(result["weighted_multiples"]["trailingPE"] - expected_pe) < 1e-6
    assert result["_meta"]["weight_coverage_pct"] == 100.0


def test_aggregate_holdings_logs_outliers():
    holdings = [
        {"ticker": "A", "weight": 0.5, "trailingPE": 25.0, "priceToBook": 5.0},
        {"ticker": "B", "weight": 0.5, "trailingPE": 999.0, "priceToBook": 4.0},
    ]
    result = aggregate_holdings(holdings, etf="XLK")
    assert result["_meta"]["outliers_dropped"]["trailingPE"] == 1
    assert result["_meta"]["outliers_dropped"]["priceToBook"] == 0
```

- [ ] **Step 2: Run tests, verify FAIL**

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --no-project pytest tests/analysis/test_etf_aggregator.py -v
```

Expected: ImportError on `etf_aggregator` module.

- [ ] **Step 3: Create etf_aggregator.py**

Write `investing-toolkit/skills/analysis-comps/scripts/etf_aggregator.py`:

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["yfinance>=0.2.40"]
# ///
"""
SPDR Sector ETF aggregate computer for analysis-comps --sector-benchmark.

Inputs: ETF ticker (XLE/XLB/.../XLRE)
Outputs: holdings-weighted aggregate JSON written to
         analysis-comps/references/sector-etf-aggregate-<ETF>.json

Build-time only — invoked by .github/workflows/sector-etf-aggregates.yml weekly cron.
Runtime callers (comps_compute.py) read the JSON files directly.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import yfinance as yf

REFS_DIR = Path(__file__).parent.parent / "references"
DATA_US_PACK = (
    Path(__file__).parents[3] / "skills" / "data-us" / "scripts" / "pack.py"
)

# All multiple keys we may aggregate. Default 5 + sector-specific.
MULTIPLE_KEYS = (
    "trailingPE", "priceToBook", "priceToSales", "evEbitda",
    "roe", "rule_of_40", "price_to_ffo",
)
OUTLIER_BOUNDS = {
    "trailingPE": (0.0, 200.0),
    "priceToBook": (0.0, 200.0),
    "priceToSales": (0.0, 200.0),
    "evEbitda": (0.0, 200.0),
    "roe": (-1.0, 2.0),         # ROE in [-100%, +200%] sane range
    "rule_of_40": (-1.0, 3.0),  # Rule-of-40 in [-100%, +300%]
    "price_to_ffo": (0.0, 200.0),
}

ALL_ETFS = ("XLE", "XLB", "XLI", "XLY", "XLP", "XLV",
            "XLF", "XLK", "XLC", "XLU", "XLRE")


def _is_outlier(value: float, multiple_key: str) -> bool:
    lo, hi = OUTLIER_BOUNDS[multiple_key]
    return value < lo or value > hi


def _weighted_average(holdings: list[dict], multiple_key: str) -> float | None:
    num = 0.0
    denom = 0.0
    for h in holdings:
        v = h.get(multiple_key)
        if v is None or _is_outlier(v, multiple_key):
            continue
        num += h["weight"] * v
        denom += h["weight"]
    if denom == 0:
        return None
    return num / denom


def aggregate_holdings(holdings: list[dict], etf: str) -> dict:
    """Pure aggregator — caller supplies a list of {ticker, weight, <multiples>}."""
    weighted = {}
    outliers_dropped = {}
    for key in MULTIPLE_KEYS:
        weighted[key] = _weighted_average(holdings, key)
        outliers_dropped[key] = sum(
            1 for h in holdings
            if h.get(key) is not None and _is_outlier(h[key], key)
        )

    weight_total = sum(h["weight"] for h in holdings)
    return {
        "etf": etf,
        "as_of": date.today().isoformat(),
        "holdings_count": len(holdings),
        "_meta": {
            "source": "yfinance funds_data + data-us memo-fetch",
            "outliers_dropped": outliers_dropped,
            "weight_coverage_pct": round(weight_total * 100, 2),
        },
        "weighted_multiples": weighted,
    }


def _fetch_etf_holdings(etf: str) -> list[tuple[str, float]]:
    """Return list of (ticker, weight) from yfinance funds_data.top_holdings."""
    fd = yf.Ticker(etf).funds_data
    df = fd.top_holdings  # pandas DataFrame with index=ticker, column 'Holding Percent' as fraction
    return [(idx, float(row["Holding Percent"])) for idx, row in df.iterrows()]


def _fetch_holding_multiples(ticker: str) -> dict | None:
    """Run data-us pack.py memo-fetch + classifier; extract default 5 + sector-specific."""
    proc = subprocess.run(
        ["uv", "run", str(DATA_US_PACK), "--pack", "memo-fetch", "--ticker", ticker],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        sys.stderr.write(f"[etf_aggregator] memo-fetch failed for {ticker}: {proc.stderr}\n")
        return None
    try:
        memo = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None

    sys.path.insert(0, str(Path(__file__).parent))
    from sector_classifier import classify, UnclassifiableTickerError
    from comps_compute import _compute_roe, _compute_rule_of_40, _compute_price_to_ffo

    result = {"ticker": ticker}
    info = memo.get("info", {}).get(ticker, {})
    for k in ("trailingPE", "priceToBook", "priceToSales", "evEbitda"):
        result[k] = info.get(k)

    try:
        cls = classify(ticker)
    except UnclassifiableTickerError:
        return None  # non-US ADR (NXPI / ASML) — skip silently

    if not cls["exclude_specific_multiples"]:
        if cls["gics"] == "Financial Services":
            result["roe"], _ = _compute_roe(memo)
        elif cls["gics"] == "Technology":
            result["rule_of_40"], _ = _compute_rule_of_40(memo)
        elif cls["gics"] == "Real Estate":
            result["price_to_ffo"], _ = _compute_price_to_ffo(memo, info.get("marketCap"))

    return result


def aggregate_etf(etf: str) -> dict:
    """Fetch ETF holdings → fetch each holding's multiples → return aggregate dict."""
    raw = _fetch_etf_holdings(etf)
    holdings: list[dict] = []
    for ticker, weight in raw:
        m = _fetch_holding_multiples(ticker)
        if m is None:
            continue
        m["weight"] = weight
        holdings.append(m)
    return aggregate_holdings(holdings, etf=etf)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--etf", choices=ALL_ETFS, help="Single ETF to aggregate")
    parser.add_argument("--all", action="store_true", help="Aggregate all 11 ETFs")
    args = parser.parse_args()

    if not args.etf and not args.all:
        parser.error("must specify --etf <ETF> or --all")

    targets = ALL_ETFS if args.all else (args.etf,)
    REFS_DIR.mkdir(exist_ok=True)
    for etf in targets:
        agg = aggregate_etf(etf)
        out = REFS_DIR / f"sector-etf-aggregate-{etf}.json"
        out.write_text(json.dumps(agg, indent=2))
        print(f"wrote {out} ({agg['holdings_count']} holdings)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests, verify PASS**

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --no-project pytest tests/analysis/test_etf_aggregator.py -v
```

Expected: 5 PASSED (the unit tests cover pure compute; network paths covered in T8 smoke test).

- [ ] **Step 5: Commit**

```bash
git add investing-toolkit/skills/analysis-comps/scripts/etf_aggregator.py \
        investing-toolkit/tests/analysis/test_etf_aggregator.py
git commit -m "feat(analysis-comps): etf_aggregator holdings-weighted compute (v2.2.0-c T5)"
```

---

## Task 6: Schema extension — sector block

**Files:**
- Modify: `investing-toolkit/skills/analysis-comps/references/schema-compute-output.json`
- Modify: `investing-toolkit/tests/analysis/test_analysis_comps.py` (add schema validation tests)

- [ ] **Step 1: Write failing test for sector block schema validation**

Append to `tests/analysis/test_analysis_comps.py`:

```python
import jsonschema  # already in test deps


def _load_schema():
    return json.loads(
        (Path(__file__).parents[2] / "skills" / "analysis-comps" / "references"
         / "schema-compute-output.json").read_text()
    )


def test_schema_accepts_sector_block_aapl_shape():
    schema = _load_schema()
    output = {
        # default 5 — minimal v2.2.0-b shape, types matter not the values
        "trailingPE":  {"value": 28.0, "_meta": {}},
        "priceToBook": {"value": 7.2,  "_meta": {}},
        "priceToSales":{"value": 8.1,  "_meta": {}},
        "evEbitda":    {"value": 21.0, "_meta": {}},
        "forwardPE":   {"value": 25.1, "_meta": {}},
        "sector": {
            "classification": {
                "gics": "Technology",
                "sub_industry": "Software—Infrastructure",
                "etf": "XLK",
                "provenance": "yfinance_info"
            },
            "specific_multiples": {
                "rule_of_40": {"value": 0.58, "_meta": {}}
            },
            "etf_aggregate": {
                "as_of": "2026-05-04",
                "trailingPE": 24.1, "priceToBook": 5.8, "priceToSales": 6.2,
                "evEbitda": 18.4, "rule_of_40": 0.42,
                "_meta": {"holdings_count": 75, "freshness_days": 1, "weight_coverage_pct": 94.2}
            },
            "divergence": {
                "trailingPE": {"individual": 28.0, "etf": 24.1, "delta_pct": 16.2, "band": "in_line"}
            },
            "warnings": []
        }
    }
    jsonschema.validate(instance=output, schema=schema)


def test_schema_accepts_sector_skipped_for_non_us():
    schema = _load_schema()
    output = {
        "trailingPE": {"value": 12.0, "_meta": {}}, "priceToBook": {"value": 1.5, "_meta": {}},
        "priceToSales": {"value": 0.9, "_meta": {}}, "evEbitda": {"value": 8.0, "_meta": {}},
        "forwardPE": {"value": 11.0, "_meta": {}},
        "sector": {"status": "skipped", "reason": "non-US ticker"}
    }
    jsonschema.validate(instance=output, schema=schema)


def test_schema_accepts_no_sector_key_backward_compat():
    """Without --sector-benchmark, sector key absent — schema must still validate."""
    schema = _load_schema()
    output = {
        "trailingPE": {"value": 28.0, "_meta": {}},
        "priceToBook": {"value": 7.2, "_meta": {}},
        "priceToSales": {"value": 8.1, "_meta": {}},
        "evEbitda": {"value": 21.0, "_meta": {}},
        "forwardPE": {"value": 25.1, "_meta": {}},
    }
    jsonschema.validate(instance=output, schema=schema)
```

- [ ] **Step 2: Run tests, verify FAIL**

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --no-project pytest tests/analysis/test_analysis_comps.py::test_schema_accepts_sector_block_aapl_shape -v
```

Expected: schema validation error — `sector` key not in current schema.

- [ ] **Step 3: Extend schema-compute-output.json**

Read the existing file with the Read tool first to find the right insertion point, then add the `sector` property to the top-level `properties` block. Add at the end of the existing properties (before `"required"`):

```json
    "sector": {
      "oneOf": [
        {
          "type": "object",
          "required": ["status", "reason"],
          "properties": {
            "status": {"type": "string", "const": "skipped"},
            "reason": {"type": "string"}
          },
          "additionalProperties": false
        },
        {
          "type": "object",
          "required": ["classification", "etf_aggregate", "divergence", "warnings"],
          "properties": {
            "classification": {
              "type": "object",
              "required": ["gics", "sub_industry", "etf", "provenance"],
              "properties": {
                "gics": {"type": "string"},
                "sub_industry": {"type": "string"},
                "etf": {"type": "string", "enum": ["XLE","XLB","XLI","XLY","XLP","XLV","XLF","XLK","XLC","XLU","XLRE"]},
                "provenance": {"type": "string", "enum": ["cli_flag","override_file","yfinance_info"]}
              }
            },
            "specific_multiples": {
              "type": "object",
              "additionalProperties": {
                "type": "object",
                "required": ["value", "_meta"],
                "properties": {
                  "value": {"type": ["number", "null"]},
                  "_meta": {"type": "object"}
                }
              }
            },
            "etf_aggregate": {
              "type": "object",
              "required": ["as_of", "_meta"],
              "properties": {
                "as_of": {"type": "string"},
                "trailingPE":   {"type": ["number", "null"]},
                "priceToBook":  {"type": ["number", "null"]},
                "priceToSales": {"type": ["number", "null"]},
                "evEbitda":     {"type": ["number", "null"]},
                "roe":          {"type": ["number", "null"]},
                "rule_of_40":   {"type": ["number", "null"]},
                "price_to_ffo": {"type": ["number", "null"]},
                "_meta": {"type": "object"}
              }
            },
            "divergence": {
              "type": "object",
              "additionalProperties": {
                "type": "object",
                "required": ["individual", "etf", "delta_pct", "band"],
                "properties": {
                  "individual": {"type": ["number", "null"]},
                  "etf": {"type": ["number", "null"]},
                  "delta_pct": {"type": ["number", "null"]},
                  "band": {"type": "string", "enum": ["in_line", "notable", "extreme"]}
                }
              }
            },
            "warnings": {"type": "array", "items": {"type": "string"}}
          }
        }
      ]
    }
```

The `sector` key should NOT be in the top-level `required` list (optional / absent without flag).

- [ ] **Step 4: Run tests, verify PASS**

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --no-project pytest tests/analysis/test_analysis_comps.py -v -k schema
```

Expected: 3 PASSED.

- [ ] **Step 5: Commit**

```bash
git add investing-toolkit/skills/analysis-comps/references/schema-compute-output.json \
        investing-toolkit/tests/analysis/test_analysis_comps.py
git commit -m "feat(analysis-comps): extend schema-compute-output with sector block (v2.2.0-c T6)"
```

---

## Task 7: comps_compute.py — `--sector-benchmark` flag wiring

**Files:**
- Modify: `investing-toolkit/skills/analysis-comps/scripts/comps_compute.py`
- Modify: `investing-toolkit/tests/analysis/test_analysis_comps.py`

- [ ] **Step 1: Write failing tests for the new flag wiring**

Append to `tests/analysis/test_analysis_comps.py`:

```python
def test_compute_without_sector_flag_unchanged_shape(tmp_path):
    """Backward compat: no --sector-benchmark → no `sector` key in output."""
    # Use existing v2.2.0-b AAPL fixture pattern (caller wires --anchor-base)
    # Implementer: reuse existing test helper that runs comps_compute --mode compute
    # and assert "sector" not in output
    output = _run_comps_compute_mode_compute_aapl(tmp_path)
    assert "sector" not in output


def test_compute_with_sector_flag_emits_sector_block_aapl(tmp_path):
    output = _run_comps_compute_mode_compute_aapl(tmp_path, sector_benchmark=True)
    assert output["sector"]["classification"]["etf"] == "XLK"
    assert output["sector"]["classification"]["provenance"] in {"override_file", "yfinance_info"}
    # AAPL is Technology → rule_of_40 specific_multiple
    assert "rule_of_40" in output["sector"]["specific_multiples"]
    assert output["sector"]["divergence"]["trailingPE"]["band"] in {"in_line", "notable", "extreme"}


def test_compute_with_sector_flag_non_us_skipped(tmp_path):
    """7203.T (Toyota) → sector.status == 'skipped'."""
    output = _run_comps_compute_mode_compute_for_ticker(tmp_path, "7203.T", sector_benchmark=True)
    assert output["sector"]["status"] == "skipped"


def test_compute_with_sector_flag_brk_b_excludes_specific(tmp_path):
    """BRK.B has exclude_specific_multiples=true via override file."""
    output = _run_comps_compute_mode_compute_for_ticker(tmp_path, "BRK.B", sector_benchmark=True)
    assert output["sector"]["specific_multiples"] == {}


def test_divergence_band_thresholds():
    """20% / 50% boundaries — direct unit test on _classify_sector_divergence_band."""
    from comps_compute import _classify_sector_divergence_band
    assert _classify_sector_divergence_band(15.0) == "in_line"     # |15%| ≤ 20
    assert _classify_sector_divergence_band(-15.0) == "in_line"
    assert _classify_sector_divergence_band(25.0) == "notable"     # 20 < |25%| ≤ 50
    assert _classify_sector_divergence_band(-49.9) == "notable"
    assert _classify_sector_divergence_band(60.0) == "extreme"     # > 50%
```

The helper `_run_comps_compute_mode_compute_aapl` and `_run_comps_compute_mode_compute_for_ticker` should follow the pattern of existing `--mode compute` tests in `test_analysis_comps.py`. **Implementer**: search the file for the existing helper that runs `--mode compute` end-to-end and add a `sector_benchmark` kwarg.

- [ ] **Step 2: Run tests, verify FAIL**

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --no-project pytest tests/analysis/test_analysis_comps.py -v -k "sector or divergence_band"
```

Expected: AttributeError on `_classify_sector_divergence_band` + KeyError on `output["sector"]`.

- [ ] **Step 3: Implement `--sector-benchmark` wiring in comps_compute.py**

Add to `comps_compute.py` (helpers near the top of compute section):

```python
def _classify_sector_divergence_band(delta_pct: float) -> str:
    """Sector-relative divergence band: 20% / 50% boundaries."""
    abs_d = abs(delta_pct)
    if abs_d <= 20.0:
        return "in_line"
    if abs_d <= 50.0:
        return "notable"
    return "extreme"


def _load_sector_etf_aggregate(etf: str) -> dict | None:
    """Read pre-computed ETF aggregate JSON from references/. None if missing."""
    path = Path(__file__).parent.parent / "references" / f"sector-etf-aggregate-{etf}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def _load_sector_warnings_for(gics: str, sub_industry: str) -> list[str]:
    """Read sector-warnings.md, pluck rows matching gics + (substring sub_industry)."""
    path = Path(__file__).parent.parent / "references" / "sector-warnings.md"
    if not path.exists():
        return []
    out = []
    for line in path.read_text().splitlines():
        if not line.startswith("|") or "GICS L1" in line or line.startswith("|---"):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 4:
            continue
        row_gics, _row_etf, row_trigger, row_warning = parts[0], parts[1], parts[2], parts[3]
        if row_gics != gics:
            continue
        if row_trigger == "(any)":
            if row_warning and row_warning != '""':
                out.append(row_warning.strip('"'))
            continue
        if row_trigger == "other":
            # rendered after specific triggers; treat as fallback
            if row_warning and row_warning != '""':
                out.append(row_warning.strip('"'))
            continue
        if row_trigger.startswith("starts with"):
            prefix = row_trigger.split("`")[1]  # extract from `starts with `Banks``
            if sub_industry.startswith(prefix):
                if row_warning and row_warning != '""':
                    out.append(row_warning.strip('"'))
    return out


def _build_sector_block(
    ticker: str,
    memo: dict,
    direct_multiples: dict,
    market_cap: float | None,
    override_cli: str | None = None,
) -> dict:
    """Construct sector block. Returns {} if classification fails (caller decides what to do)."""
    sys.path.insert(0, str(Path(__file__).parent))
    from sector_classifier import classify, UnclassifiableTickerError

    try:
        cls = classify(ticker, override_cli=override_cli)
    except UnclassifiableTickerError as e:
        return {"status": "skipped", "reason": str(e)}

    block: dict = {"classification": dict(cls), "specific_multiples": {}, "warnings": []}

    if not cls["exclude_specific_multiples"]:
        if cls["gics"] == "Financial Services":
            v, m = _compute_roe(memo)
            if v is not None:
                block["specific_multiples"]["roe"] = {"value": v, "_meta": m}
        elif cls["gics"] == "Technology":
            v, m = _compute_rule_of_40(memo)
            if v is not None:
                block["specific_multiples"]["rule_of_40"] = {"value": v, "_meta": m}
        elif cls["gics"] == "Real Estate":
            v, m = _compute_price_to_ffo(memo, market_cap)
            if v is not None:
                block["specific_multiples"]["price_to_ffo"] = {"value": v, "_meta": m}

    agg = _load_sector_etf_aggregate(cls["etf"])
    block["etf_aggregate"] = agg or {"as_of": None, "_meta": {"freshness_days": None}}

    block["divergence"] = {}
    if agg:
        for key in ("trailingPE", "priceToBook", "priceToSales", "evEbitda"):
            indiv = direct_multiples.get(key)
            etf_v = agg.get("weighted_multiples", {}).get(key)
            if indiv is None or etf_v is None or etf_v == 0:
                continue
            delta_pct = (indiv / etf_v - 1) * 100
            block["divergence"][key] = {
                "individual": indiv,
                "etf": etf_v,
                "delta_pct": round(delta_pct, 2),
                "band": _classify_sector_divergence_band(delta_pct),
            }
        # specific_multiples divergence
        for key, entry in block["specific_multiples"].items():
            indiv = entry["value"]
            etf_v = agg.get("weighted_multiples", {}).get(key)
            if indiv is None or etf_v is None or etf_v == 0:
                continue
            delta_pct = (indiv / etf_v - 1) * 100
            block["divergence"][key] = {
                "individual": indiv,
                "etf": etf_v,
                "delta_pct": round(delta_pct, 2),
                "band": _classify_sector_divergence_band(delta_pct),
            }

    block["warnings"] = _load_sector_warnings_for(cls["gics"], cls["sub_industry"])
    return block
```

Add the CLI flag in the existing `main()`:

```python
    parser.add_argument(
        "--sector-benchmark",
        action="store_true",
        help="Emit sector classification + SPDR sector ETF aggregate divergence (US-only)",
    )
    parser.add_argument(
        "--sector-override",
        help="Manually override GICS L1 (one of: Energy / Basic Materials / Industrials / "
             "Consumer Cyclical / Consumer Defensive / Healthcare / Financial Services / "
             "Technology / Communication Services / Utilities / Real Estate)",
    )
```

In the `--mode compute` execution path (after `_compute_multiples_from_memo_fetch` + divergence calc), add:

```python
    if args.sector_benchmark:
        market_cap = direct_multiples.get("marketCap")  # if compute path stashes it; else fetch from anchor info
        sector_block = _build_sector_block(
            ticker=anchor_ticker,
            memo=anchor_memo,
            direct_multiples=direct_multiples,
            market_cap=market_cap,
            override_cli=args.sector_override,
        )
        output["sector"] = sector_block
```

**Implementer note**: the variable names (`anchor_ticker`, `anchor_memo`, `direct_multiples`, `output`) must match the actual variable names in the existing main(). Read the function first.

- [ ] **Step 4: Run tests, verify PASS**

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --no-project pytest tests/analysis/test_analysis_comps.py -v
```

Expected: all sector-related tests PASS; existing v2.2.0-b tests still PASS (backward compat).

Also run the full offline suite:

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --no-project pytest -m "not network" -v
```

Expected: 0 failures.

- [ ] **Step 5: Commit**

```bash
git add investing-toolkit/skills/analysis-comps/scripts/comps_compute.py \
        investing-toolkit/tests/analysis/test_analysis_comps.py
git commit -m "feat(analysis-comps): comps_compute --sector-benchmark flag (v2.2.0-c T7)"
```

---

## Task 8: GHA workflow + seed aggregate JSONs + integration fixtures

**Files:**
- Create: `.github/workflows/sector-etf-aggregates.yml`
- Create: `investing-toolkit/skills/analysis-comps/references/sector-etf-aggregate-{XLE,XLB,XLI,XLY,XLP,XLV,XLF,XLK,XLC,XLU,XLRE}.json` (11 files — initial seed via local run)
- Create: `investing-toolkit/tests/data/fixtures/sector-etf-aggregate-{XLK,XLF,XLRE}-sample.json` (3 fixtures for integration tests)

- [ ] **Step 1: Create the GHA workflow**

Write `.github/workflows/sector-etf-aggregates.yml`:

```yaml
name: sector-etf-aggregates (weekly refresh)

on:
  schedule:
    - cron: '0 6 * * 6'  # Saturday 06:00 UTC = Asia/Taipei Sat 14:00
  workflow_dispatch:

jobs:
  refresh:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      issues: write
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
      - uses: astral-sh/setup-uv@v3
      - name: Cache SEC EDGAR companyfacts
        uses: actions/cache@v4
        with:
          path: ~/.cache/investing-toolkit/sec_edgar
          key: sec-edgar-companyfacts-${{ github.run_number }}
          restore-keys: sec-edgar-companyfacts-
      - name: Run aggregator (all 11 ETFs)
        env:
          USER_AGENT: "investing-toolkit-bot kouko@github (sec_edgar weekly refresh)"
        run: |
          uv run investing-toolkit/skills/analysis-comps/scripts/etf_aggregator.py --all
      - name: Commit + push if changed
        run: |
          git config user.name "investing-toolkit-bot"
          git config user.email "actions@github.com"
          git add investing-toolkit/skills/analysis-comps/references/sector-etf-aggregate-*.json
          if git diff --cached --quiet; then
            echo "No aggregate changes."
            exit 0
          fi
          git commit -m "chore(sector-aggregates): weekly refresh $(date -u +%Y-%m-%d)"
          git push
      - name: Open issue on failure
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `sector-etf-aggregates failed on ${new Date().toISOString().slice(0,10)}`,
              body: `Run: ${context.serverUrl}/${context.repo.owner}/${context.repo.repo}/actions/runs/${context.runId}`,
              labels: ['sector-aggregate-stale']
            })
```

- [ ] **Step 2: Run aggregator locally to seed 11 JSON files**

```bash
cd /Users/kouko/GitHub/monkey-skills
PYTHONDONTWRITEBYTECODE=1 uv run investing-toolkit/skills/analysis-comps/scripts/etf_aggregator.py --all
```

Expected: 11 files written to `investing-toolkit/skills/analysis-comps/references/sector-etf-aggregate-*.json`. This may take ~30-60 minutes (full ~825 SEC EDGAR fetches with cache). If you hit rate-limit or other errors, run per-ETF (`--etf XLK`) instead, fixing one at a time.

Verify all 11 exist:

```bash
ls investing-toolkit/skills/analysis-comps/references/sector-etf-aggregate-*.json | wc -l
```

Expected: `11`.

- [ ] **Step 3: Build offline fixtures from the 3 representative ETFs**

The integration tests must NOT depend on the production aggregate JSONs (which refresh weekly and would cause flaky tests). Snapshot 3 ETFs as fixtures:

```bash
cp investing-toolkit/skills/analysis-comps/references/sector-etf-aggregate-XLK.json \
   investing-toolkit/tests/data/fixtures/sector-etf-aggregate-XLK-sample.json
cp investing-toolkit/skills/analysis-comps/references/sector-etf-aggregate-XLF.json \
   investing-toolkit/tests/data/fixtures/sector-etf-aggregate-XLF-sample.json
cp investing-toolkit/skills/analysis-comps/references/sector-etf-aggregate-XLRE.json \
   investing-toolkit/tests/data/fixtures/sector-etf-aggregate-XLRE-sample.json
```

- [ ] **Step 4: Verify offline pytest suite is still green**

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --no-project pytest -m "not network" -v
```

Expected: all PASS, no regressions.

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/sector-etf-aggregates.yml \
        investing-toolkit/skills/analysis-comps/references/sector-etf-aggregate-*.json \
        investing-toolkit/tests/data/fixtures/sector-etf-aggregate-*-sample.json
git commit -m "feat(analysis-comps): GHA weekly aggregates + 11 seed JSONs + 3 fixtures (v2.2.0-c T8)"
```

---

## Task 9: Cross-layer integration tests

**Files:**
- Modify: `investing-toolkit/tests/integration/test_cross_layer_chains.py`

- [ ] **Step 1: Add 6 new integration tests**

Append to `tests/integration/test_cross_layer_chains.py`:

```python
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1].parent
COMPS = ROOT / "skills" / "analysis-comps" / "scripts" / "comps_compute.py"
FIXTURES = ROOT / "tests" / "data" / "fixtures"


def _run_comps(anchor_path, anchor_base_path, peers_path, *, sector_benchmark: bool):
    """Run comps_compute via subprocess; return parsed output dict."""
    cmd = [
        "uv", "run", str(COMPS),
        "--mode", "compute",
        "--anchor", str(anchor_path),
        "--anchor-base", str(anchor_base_path),
        "--peers", str(peers_path),
    ]
    if sector_benchmark:
        cmd.append("--sector-benchmark")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


@pytest.mark.usefixtures("_seed_sector_aggregate_xlk")
def test_us_compute_with_sector_benchmark_aapl():
    """AAPL → Technology → XLK → rule_of_40 + 5-multiple divergence."""
    out = _run_comps(
        FIXTURES / "data-us-comps-multiples-AAPL.json",
        FIXTURES / "data-us-memo-fetch-AAPL.json",
        FIXTURES / "data-us-comps-multiples-MSFT.json",
        sector_benchmark=True,
    )
    assert out["sector"]["classification"]["etf"] == "XLK"
    assert "rule_of_40" in out["sector"]["specific_multiples"]
    assert out["sector"]["divergence"]["trailingPE"]["band"] in {"in_line", "notable", "extreme"}


@pytest.mark.usefixtures("_seed_sector_aggregate_xlf")
def test_us_compute_with_sector_benchmark_jpm():
    out = _run_comps(
        FIXTURES / "data-us-comps-multiples-JPM.json",
        FIXTURES / "data-us-memo-fetch-JPM.json",
        FIXTURES / "data-us-comps-multiples-BAC.json",
        sector_benchmark=True,
    )
    assert out["sector"]["classification"]["etf"] == "XLF"
    assert "roe" in out["sector"]["specific_multiples"]


@pytest.mark.usefixtures("_seed_sector_aggregate_xlre")
def test_us_compute_with_sector_benchmark_o():
    out = _run_comps(
        FIXTURES / "data-us-comps-multiples-O.json",
        FIXTURES / "data-us-memo-fetch-O.json",
        FIXTURES / "data-us-comps-multiples-WPC.json",
        sector_benchmark=True,
    )
    assert out["sector"]["classification"]["etf"] == "XLRE"
    assert "price_to_ffo" in out["sector"]["specific_multiples"]


@pytest.mark.usefixtures("_seed_sector_aggregate_xlf")
def test_us_compute_with_sector_benchmark_brk_b_excludes():
    out = _run_comps(
        FIXTURES / "data-us-comps-multiples-BRK.B.json",
        FIXTURES / "data-us-memo-fetch-BRK.B.json",
        FIXTURES / "data-us-comps-multiples-JPM.json",
        sector_benchmark=True,
    )
    assert out["sector"]["classification"]["provenance"] == "override_file"
    assert out["sector"]["specific_multiples"] == {}


def test_compute_skip_sector_for_non_us():
    out = _run_comps(
        FIXTURES / "data-jp-comps-multiples-7203.json",
        FIXTURES / "data-jp-memo-fetch-7203.json",
        FIXTURES / "data-jp-comps-multiples-7267.json",
        sector_benchmark=True,
    )
    assert out["sector"]["status"] == "skipped"


def test_compute_without_sector_flag_unchanged():
    """Backward compat: same input as v2.2.0-b integration test, no `sector` key."""
    out = _run_comps(
        FIXTURES / "data-us-comps-multiples-AAPL.json",
        FIXTURES / "data-us-memo-fetch-AAPL.json",
        FIXTURES / "data-us-comps-multiples-MSFT.json",
        sector_benchmark=False,
    )
    assert "sector" not in out
```

The `_seed_sector_aggregate_*` fixtures (autouse=False) copy the sample fixture into `references/` so the runtime read finds it. Add these to `tests/integration/conftest.py`:

```python
import shutil
from pathlib import Path

import pytest

REFS = Path(__file__).parents[1].parent / "skills" / "analysis-comps" / "references"
FIXTURES = Path(__file__).parents[1] / "data" / "fixtures"


@pytest.fixture
def _seed_sector_aggregate_xlk():
    src = FIXTURES / "sector-etf-aggregate-XLK-sample.json"
    dst = REFS / "sector-etf-aggregate-XLK.json"
    backup = dst.read_bytes() if dst.exists() else None
    shutil.copy(src, dst)
    yield
    if backup is not None:
        dst.write_bytes(backup)


@pytest.fixture
def _seed_sector_aggregate_xlf():
    src = FIXTURES / "sector-etf-aggregate-XLF-sample.json"
    dst = REFS / "sector-etf-aggregate-XLF.json"
    backup = dst.read_bytes() if dst.exists() else None
    shutil.copy(src, dst)
    yield
    if backup is not None:
        dst.write_bytes(backup)


@pytest.fixture
def _seed_sector_aggregate_xlre():
    src = FIXTURES / "sector-etf-aggregate-XLRE-sample.json"
    dst = REFS / "sector-etf-aggregate-XLRE.json"
    backup = dst.read_bytes() if dst.exists() else None
    shutil.copy(src, dst)
    yield
    if backup is not None:
        dst.write_bytes(backup)
```

**Implementer note**: if the test fixture files for JPM / O / BRK.B / 7203 / etc do not exist yet, generate them via the existing fixture-generation pattern (`uv run skills/data-us/scripts/pack.py --pack <pack> --ticker <T>` → write to `tests/data/fixtures/data-us-<pack>-<T>.json`). The standard fixture set already includes AAPL + MSFT (per v2.2.0-l fixture work). Generate the missing 6 ahead of writing the integration tests.

- [ ] **Step 2: Run new integration tests, verify PASS**

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --no-project pytest tests/integration/test_cross_layer_chains.py -v -k "sector or skip_sector or without_sector"
```

Expected: 6 PASSED.

- [ ] **Step 3: Run full offline pytest suite**

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --no-project pytest -m "not network" -v
```

Expected: all PASS, suite up from baseline 377 → ~398.

- [ ] **Step 4: Commit**

```bash
git add investing-toolkit/tests/integration/test_cross_layer_chains.py \
        investing-toolkit/tests/integration/conftest.py \
        investing-toolkit/tests/data/fixtures/data-us-*-{JPM,O,BRK.B}*.json \
        investing-toolkit/tests/data/fixtures/data-jp-*-7203*.json \
        investing-toolkit/tests/data/fixtures/data-jp-*-7267*.json \
        investing-toolkit/tests/data/fixtures/data-us-*-{BAC,WPC}*.json
git commit -m "test(analysis-comps): 6 sector-benchmark integration tests + fixtures (v2.2.0-c T9)"
```

(Adjust the fixture filename glob to whatever was actually generated in Step 1's prep.)

---

## Task 10: SKILL.md update + ROADMAP closeout + memory pointer

**Files:**
- Modify: `investing-toolkit/skills/analysis-comps/SKILL.md`
- Modify: `investing-toolkit/ROADMAP.md`
- Modify: `~/.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/project_investing_toolkit_v2x_roadmap.md`

- [ ] **Step 1: Update SKILL.md — document new flag + override mechanism**

Read `investing-toolkit/skills/analysis-comps/SKILL.md` first; locate the "Modes" or "CLI" section. Append a new subsection:

```markdown
### Sector benchmark mode (`--sector-benchmark`, US-only, opt-in)

Adds a `sector` block to compute output containing:
- Classification to one of 11 SPDR Select Sector ETFs (XLE/XLB/XLI/XLY/XLP/XLV/XLF/XLK/XLC/XLU/XLRE)
- Sector-specific multiples for 3 sectors:
  - **XLF banks** (`info.industry` starts with `Banks`) → `roe`
  - **XLK** (any IT) → `rule_of_40`
  - **XLRE REITs** (`info.industry` starts with `REIT`) → `price_to_ffo`
- Per-multiple divergence vs ETF holdings-weighted aggregate, classified into `in_line` (≤20%) / `notable` (20–50%) / `extreme` (>50%) bands
- Sector-specific warnings (loaded from `references/sector-warnings.md`)

ETF aggregates pre-computed weekly via `.github/workflows/sector-etf-aggregates.yml`. Runtime reads `references/sector-etf-aggregate-<ETF>.json` (no live fetch).

Override yfinance classification via `--sector-override <gics>` CLI flag or `references/sector-overrides.json` (BRK.A/B, META, SQ, AMZN preset).

Non-US tickers emit `sector.status: "skipped"`. Without `--sector-benchmark`, output is identical to the v2.2.0-b shape (no `sector` key).
```

- [ ] **Step 2: Update ROADMAP.md — close v2.2.0-c, add follow-ups**

Edit `investing-toolkit/ROADMAP.md`:

a. Move §"v2.2.0-c — Sector-adjusted multiples for Comps" out of "Future Roadmap (planning)" into a new versioned section near the top (under whatever current "Released" sections exist):

```markdown
## v2.2.0-c — Sector multiples + SPDR ETF benchmark (released YYYY-MM-DD)

Closed via PR #XXX. Adds `analysis-comps --sector-benchmark` (US-only): 11-GICS classification → SPDR ETF, sector-specific multiples (roe / rule_of_40 / price_to_ffo) for 3 sectors, holdings-weighted ETF aggregate (weekly GHA refresh), per-multiple divergence (20% / 50% bands), override file + CLI flag + per-ticker provenance. Non-US tickers explicitly skipped. Backward compatible: `sector` key absent without flag.

**Deferred to v2.2.0-c²**: 6 sectors with missing XBRL fields (Energy EV/EBITDAX, Insurance Combined Ratio, Asset Mgr P/AUM, Health Care Cash Burn, Utilities Div Yield, Comm Services sub-industry split).

**Deferred to v2.2.0-c-{jp,tw,kr,cn}**: regional sector ETF benchmark for non-US markets.
```

b. In the still-open "Future Roadmap" section, REPLACE the v2.2.0-c entry with:

```markdown
### v2.2.0-c² — Six-sector specific multiple coverage

- **What**: Add sector-specific multiples for the 6 sectors deferred from v2.2.0-c (Energy / Insurance / Asset Mgr / Health Care / Utilities / Comm Services).
- **Why**: Default 5 are misleading on these sectors; v2.2.0-c only handled the 3 sectors whose data was available within v2.2.0-l raw fields.
- **Files**: requires extending `data-us/scripts/pack.py` `DCF_CONCEPT_MAPPING` with new XBRL chains (OCF / Capex / Exploration Expense / Dividend per share); analysis-comps sector_classifier sub-industry rules expanded.
- **Blocker**: new XBRL concepts research per sector.

### v2.2.0-c-{jp,tw,kr,cn} — Regional sector ETF benchmarks

- **What**: Per-country sector ETF benchmark (JP iShares MSCI / NEXT FUNDS TOPIX-17 sectors; TW / KR / CN: TBD).
- **Why**: v2.2.0-c is US-only. Cross-country sector relative valuation needs region-native ETF universes.
- **Blocker**: per-country sector ETF identification + holdings access.
```

- [ ] **Step 3: Update memory pointer**

Append to `~/.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/project_investing_toolkit_v2x_roadmap.md` index entry:

Edit `~/.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/MEMORY.md` line for `[investing-toolkit v2.1.0+ Future Roadmap]` to reflect v2.2.0-c closed (date + PR #).

Update `project_investing_toolkit_v2x_roadmap.md` body: add v2.2.0-c to closed-2026-05-XX entries; add v2.2.0-c² + v2.2.0-c-{jp,tw,kr,cn} to spawned-future entries; refresh suite passed count.

- [ ] **Step 4: Run full suite + verify SKILL structure compliance**

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --no-project pytest -m "not network" -v
PYTHONDONTWRITEBYTECODE=1 uv run scripts/check-skill-structure.py
PYTHONDONTWRITEBYTECODE=1 uv run scripts/check-script-sync.py
```

Expected: all green, no skill-folder-structure violations (the 11 aggregate JSONs sit flat in `references/`, satisfying the no-nested-subfolder rule).

- [ ] **Step 5: Commit**

```bash
git add investing-toolkit/skills/analysis-comps/SKILL.md \
        investing-toolkit/ROADMAP.md
git commit -m "docs(analysis-comps): v2.2.0-c closeout — SKILL.md + ROADMAP versioning (T10)"
```

(Memory file edit is local to `~/.claude/...`, not committed to repo.)

---

## Final acceptance gate

After all 10 tasks committed, before opening PR:

- [ ] `PYTHONDONTWRITEBYTECODE=1 uv run --no-project pytest -m "not network" -v` → all green
- [ ] `PYTHONDONTWRITEBYTECODE=1 uv run scripts/check-skill-structure.py` → green (no nested subfolder violations)
- [ ] `PYTHONDONTWRITEBYTECODE=1 uv run scripts/check-script-sync.py` → green (no cross-skill duplication added)
- [ ] All 10 commits use kebab-case scopes per `feedback_cc_type_whitelist.md`: `feat(analysis-comps)`, `test(analysis-comps)`, `docs(analysis-comps)` — never `analysis_comps`
- [ ] Acceptance criteria from spec §12 verified manually:
  - AAPL → XLK + rule_of_40 ✓
  - JPM → XLF + roe ✓
  - O → XLRE + price_to_ffo ✓
  - BRK.B → override_file + empty specific_multiples ✓
  - 7203.T → status=skipped ✓
  - No flag → no sector key ✓
  - 11 aggregate JSONs exist ✓
  - GHA workflow_dispatch dry-run succeeds (optional manual verify) ✓
- [ ] PR description includes the spec link + acceptance ✓ checks

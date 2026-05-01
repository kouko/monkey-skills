---
name: analysis-dcf
description: >-
  Pure compute 3-stage DCF on pre-fetched data JSON. Input: --input
  <pack-json-path> from data-{country}/pack.py --pack memo-fetch. Output:
  intrinsic value range JSON with 3×3 sensitivity (WACC × terminal growth).
  DCF 内在価値純計算層。DCF 內在價值純計算層。
---

# analysis-dcf

Pure-compute Layer 2 skill in the v2.0.0 three-layer architecture
(data → analysis → report). Implements the Damodaran 2012 *Investment
Valuation* Ch.12 3-stage DCF and reports a 3×3 WACC × terminal-growth
sensitivity table with Graham-Dodd-Klarman verdict thresholds.

Reference template: `references/dcf-template.md`

## Layer 2 Contract — NO I/O

This skill performs **zero network or external file I/O** beyond reading
the single `--input <json-path>` argument. No SEC EDGAR / MOPS / yfinance /
FRED clients are imported here. Fetching is the responsibility of the
caller — typically `data-{country}/pack.py --pack memo-fetch`.

```
data-{country}/pack.py --pack memo-fetch  →  pre-fetched JSON
                                              ↓
                                       analysis-dcf (this skill)
                                              ↓
                                       intrinsic value JSON
```

Callers (e.g. `report-equity-memo`) compose this skill with the data layer.

## Input Contract

`--input <path>` must point to a JSON file produced by
`data-{country}/pack.py --pack memo-fetch`. Minimum shape:

```json
{
  "ticker": "AAPL",
  "income_statement": {
    "revenue":     [r_t0, r_t-1, ...],   // most-recent-first, $M
    "net_income":  [...],                 // optional
    "ebit":        [...]                  // optional, preferred over net_income
  },
  "cash_flow": {
    "fcf":   [...],                       // optional; used to derive reinvestment
    "capex": [...]
  },
  "balance_sheet": {
    "total_debt": [td_t0, ...],
    "cash":       [cash_t0, ...]
  },
  "shares_outstanding": 15728000000,      // absolute count
  "current_price": 175.0                   // optional; for margin-of-safety
}
```

Both the `data-us` (SEC EDGAR XBRL facts) and `data-tw` (MOPS t164sb04 /
sb05 / sb03) shapes conform — `pack.py --pack memo-fetch` is responsible
for normalising into this contract.

## CLI

```
uv run scripts/dcf_compute.py --input <path> [overrides...]
```

All assumption parameters can be overridden; otherwise they are derived
from the input JSON:

| Override flag           | Default behaviour                                         |
|-------------------------|-----------------------------------------------------------|
| `--wacc`                | base WACC (default 0.085)                                 |
| `--wacc-low/--wacc-high`| sensitivity bounds (default `wacc ± wacc-step`)           |
| `--wacc-step`           | sensitivity grid step (default 0.01 = 1pp)                |
| `--terminal-g`          | base terminal growth (default 0.025)                      |
| `--terminal-g-low/high` | sensitivity bounds (default `g ± g-step`)                 |
| `--g-step`              | sensitivity grid step (default 0.005 = 0.5pp)             |
| `--growth-1-5`          | stage-1 growth (default = clamped historical revenue CAGR)|
| `--growth-6-10`         | stage-2 growth (default = `growth_1_5 × 0.5`, floor 2.5%) |
| `--ebit-margin`         | derived from EBIT/revenue or NI/revenue                   |
| `--tax-rate`            | default 0.21 (US federal)                                 |
| `--reinvestment-rate`   | derived from `1 − FCF / EBIT(1−t)`; fallback 0.30         |

## Output Contract

```json
{
  "ticker": "AAPL",
  "intrinsic_value": { "low": 142.10, "mid": 168.50, "high": 198.30 },
  "sensitivity_table": {
    "wacc_axis":        [0.075, 0.085, 0.095],
    "terminal_g_axis":  [0.020, 0.025, 0.030],
    "table":            [[...,...,...], [...,$BASE,...], [...,...,...]]
  },
  "verdict_thresholds": {
    "buy_threshold_grade_a": 117.95,
    "buy_threshold_grade_b": 101.10,
    "buy_threshold_grade_c":  84.25,
    "hold_threshold":        193.78,
    "sell_threshold":        193.78,
    "rule": "BUY if price ≤ intrinsic × (1 − MoS); ..."
  },
  "current_price":          175.00,
  "margin_of_safety_base":  -0.0386,
  "assumptions":            { ... full assumption echo ... },
  "warnings":               [ "terminal_g > 4% — ..." ],
  "_provenance": {
    "input_path":  "/tmp/aapl-memo-fetch.json",
    "computed_at": "2026-05-01T03:00:00Z",
    "framework":   "Damodaran 2012 Investment Valuation Ch.12 (3-stage DCF)",
    "layer":       "analysis (pure compute, no I/O)"
  }
}
```

## Computation Summary

### FCF projection (year 1..10)

```
Revenue_t = Revenue_{t-1} × (1 + growth_t)        // stage-1 (1..5), stage-2 (6..10)
EBIT_t    = Revenue_t × EBIT_margin
FCF_t     = EBIT_t × (1 − tax) × (1 − reinvestment)
PV(FCF_t) = FCF_t / (1 + WACC)^t
```

### Terminal value (Stage 3, year 10+)

```
TV     = FCF_10 × (1 + g) / (WACC − g)
PV(TV) = TV / (1 + WACC)^10
```

### Equity value and intrinsic per-share

```
Equity        = Σ PV(FCF_t) + PV(TV) − Net debt
Intrinsic/sh  = Equity / Shares outstanding
```

### Sensitivity (3×3, varying WACC by `--wacc-step` and g by `--g-step`)

The corners are reported as the `intrinsic_value` band:

| corner | grid cell             | `intrinsic_value` field |
|--------|-----------------------|-------------------------|
| bear   | high WACC, low g      | `low`                   |
| base   | center                | `mid`                   |
| bull   | low WACC, high g      | `high`                  |

## Verdict Thresholds (Graham & Dodd / Klarman)

```
BUY   if current_price ≤ intrinsic_value × (1 − MoS_factor)
HOLD  if current_price ≤ intrinsic_value × 1.15
SELL  if current_price > intrinsic_value × 1.15

MoS_factor:
  Grade A conviction → 0.30
  Grade B conviction → 0.40
  Grade C conviction → 0.50
```

Conviction grade is set by the `domain-teams:investing-team` analyst
during memo generation, not by this skill. All three thresholds are
emitted; the caller selects.

## Attribution Corrections (built-in warnings)

The script emits `warnings[]` for any of:

1. **Terminal growth ≥ WACC** — degenerate; clamped internally.
2. **Terminal growth > 4%** — likely double-counts inflation already in
   WACC. Use real GDP growth or lower (typically 1–3%); ≤ risk-free rate.
3. **Stage-1 growth > 20%** — verify ROIC × reinvestment supports it.
4. **Low reinvestment with high growth** — implies high ROIC; verify the
   capital-light claim.

## Cross-Plugin Handoff

This skill outputs JSON only. Memo composition and prose verdict belong
upstream:

```
data-{country}:pack.py --pack memo-fetch
  → analysis-dcf (this skill, pure compute)
  → report-equity-memo (orchestrates full memo)
       → domain-teams:investing-team (variant perception, conviction)
       → domain-teams:docs-team (formatting, optional)
```

This skill never delegates and never writes files; it prints JSON to
stdout and returns.

---

## i18n footer

- 日本語: pack.py が事前取得した JSON を入力として、3-stage DCF を純計算する
  Layer 2 スキル。WACC × 永続成長率の 3×3 感応度表を含む内在価値帯を出力
  する。**ネットワーク・外部 I/O 一切なし**。
- 繁體中文: 對 pack.py 預先抓取的 JSON 進行純計算的 3 階段 DCF（Layer 2）。
  輸出包含 WACC × 終值成長率 3×3 敏感度表的內在價值區間。**無任何網路 /
  外部 I/O**。
- English: Pure-compute Layer 2 DCF over pre-fetched pack.py JSON. Emits
  intrinsic value range with 3×3 WACC × terminal-growth sensitivity. **No
  network or external file I/O.**

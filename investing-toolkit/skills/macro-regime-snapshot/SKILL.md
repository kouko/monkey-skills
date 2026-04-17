---
name: macro-regime-snapshot
description: Diagnose the current macro regime using country macro skills. Maps key indicators to the Investment Clock phase and Hedgeye GIP quadrant, then outputs a regime call with asset-class tilts. Supports US, Japan, and global (side-by-side) regions.
---

# macro-regime-snapshot

Fast macro regime call using the Investment Clock (IC) + Hedgeye GIP framework. Delegates data fetching to country-specific macro skills (`us-macro`, `japan-macro`), maps to IC 2x2 phase, cross-checks with GIP quadrant, and outputs a structured regime call with 3 asset-class tilts.

Full IC and GIP framework details: see `domain-teams:investing-team` standards/investment-macro-regime.md. This skill is the **data layer** — it fetches and maps. Analysis and conviction judgments belong to investing-team.

---

## Inputs

| Input | Values | Default |
|-------|--------|---------|
| `region` | `us` / `japan` / `global` | `us` |
| `date_context` | Optional override (e.g. "as of 2026-03") | latest available |

---

## How It Works

### Step 1 — Fetch macro indicators via country skills

Route to the appropriate country macro skill based on `region`:

- **`region=us`** — Use the `us-macro` skill to fetch US indicators (FRED 8-series: T10Y2Y, DGS10, DGS2, FEDFUNDS, CPIAUCSL, CPILFESL, GDPC1, INDPRO). Then proceed to Step 2.
- **`region=japan`** — Use the `japan-macro` skill to fetch Japan indicators (BOJ + e-Stat series: CPI, Core CPI, GDP, Industrial Production, BOJ Policy Rate, JGB 10Y, Unemployment, Tankan DI, etc.). Then proceed to Step 2.
- **`region=global`** — Fetch both `us-macro` and `japan-macro` in parallel. Then produce **side-by-side regime calls** — one IC phase per country, plus a combined divergence note. Proceed to Step 2 for each country independently.

### Step 2 — Map to IC 2x2 grid

Compute direction (rising / falling) for Growth proxy (INDPRO MoM rate-of-change) and Inflation proxy (CPIAUCSL YoY rate-of-change):

```
              Inflation Rising    Inflation Falling
Growth Rising     IC Phase 2           IC Phase 1
                (Overheat)           (Recovery)
Growth Falling    IC Phase 3           IC Phase 4
                (Stagflation)        (Reflation)
```

**Japan note**: Japan's uniquely low inflation regime means "Inflation Rising" in Japan may still be below 2%. Apply the IC framework to the **direction of change** (rate-of-change), not the absolute level. A move from 0.5% to 1.5% is "Inflation Rising" even though the level remains below most developed-market norms.

### Step 3 — Cross-check with Hedgeye GIP quadrant

Use rate-of-change (not level) for both GDP and Inflation:
- Quad 1: GDP+ Inflation+
- Quad 2: GDP+ Inflation-
- Quad 3: GDP- Inflation-
- Quad 4: GDP- Inflation+

GIP is a cross-check, not an override. Note any IC/GIP divergence.

### Step 4 — Output regime call

Produce structured markdown (see Output Format below).

---

## Data Sources

- **US**: via `us-macro` skill (FRED 8 indicators)
- **Japan**: via `japan-macro` skill (BOJ + e-Stat 13 indicators)
- Reference framework: `references/investment-clock-cheatsheet.md`

---

## Output Format

```markdown
## Macro Regime Snapshot — {date}

**IC Phase**: {1 Recovery / 2 Overheat / 3 Stagflation / 4 Reflation}
**GIP Quadrant**: {Quad 1-4 label}
**Divergence**: {IC and GIP agree / note if divergent}

### Key Indicators

| Indicator | Latest | Prior | Direction |
|-----------|--------|-------|-----------|
| INDPRO MoM | ... | ... | Rising / Falling |
| CPI YoY | ... | ... | Rising / Falling |
| Core CPI YoY | ... | ... | Rising / Falling |
| 10Y-2Y Spread | ... | ... | Steepening / Flattening |
| FEDFUNDS | ... | ... | — |

### Asset-Class Tilts

| Asset Class | Tilt | Rationale |
|-------------|------|-----------|
| Equities | ... | ... |
| Fixed Income | ... | ... |
| Commodities | ... | ... |

### Confidence Note
{Data lag note + any missing series + confidence level: High / Medium / Low}
```

---

## Limitations

FRED data has publication lags:
- CPI: ~2–3 weeks after reference month
- GDP (GDPC1): ~1 month (advance estimate)
- INDPRO: ~3–4 weeks after reference month

The regime call reflects the latest **available** data, not real-time conditions. Always note the reference dates of the most recent observations in the confidence note.

---

## Attribution

IC + GIP framework details and regime playbooks are maintained in:
`domain-teams:investing-team` → standards/investment-macro-regime.md

This skill is the data layer. For full analysis, conviction ratings, and portfolio-level implications, route to `domain-teams:investing-team`.

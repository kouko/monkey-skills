---
name: macro-regime-snapshot
description: Diagnose the current macro regime using FRED data. Maps key indicators to the Investment Clock phase and Hedgeye GIP quadrant, then outputs a regime call with asset-class tilts.
---

# macro-regime-snapshot

Fast macro regime call using the Investment Clock (IC) + Hedgeye GIP framework. Fetches FRED series via the data-fetcher agent, maps to IC 2x2 phase, cross-checks with GIP quadrant, and outputs a structured regime call with 3 asset-class tilts.

Full IC and GIP framework details: see `domain-teams:investing-team` standards/investment-macro-regime.md. This skill is the **data layer** — it fetches and maps. Analysis and conviction judgments belong to investing-team.

---

## Inputs

| Input | Values | Default |
|-------|--------|---------|
| `region` | `us` / `global` | `us` |
| `date_context` | Optional override (e.g. "as of 2026-03") | latest available |

---

## How It Works

### Step 1 — Launch data-fetcher agent

Fetch the following FRED series. Use the data-fetcher launch template from `../../agents/data-fetcher.md`.

```
### Fetch Requests
- python3 {base_path}/fred_client.py --series T10Y2Y,DGS10,DGS2,FEDFUNDS --periods 24
- python3 {base_path}/fred_client.py --series CPIAUCSL,CPILFESL --periods 24
- python3 {base_path}/fred_client.py --series GDPC1,INDPRO --periods 12
```

| Series | Meaning |
|--------|---------|
| T10Y2Y | 10Y–2Y yield spread (yield curve) |
| DGS10 | 10-year Treasury yield |
| DGS2 | 2-year Treasury yield |
| CPIAUCSL | CPI headline (YoY) |
| CPILFESL | CPI core (YoY) |
| GDPC1 | Real GDP (quarterly) |
| INDPRO | Industrial Production Index |
| FEDFUNDS | Effective Fed Funds rate |

### Step 2 — Map to IC 2x2 grid

Compute direction (rising / falling) for Growth proxy (INDPRO MoM rate-of-change) and Inflation proxy (CPIAUCSL YoY rate-of-change):

```
              Inflation Rising    Inflation Falling
Growth Rising     IC Phase 2           IC Phase 1
                (Overheat)           (Recovery)
Growth Falling    IC Phase 3           IC Phase 4
                (Stagflation)        (Reflation)
```

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

- FRED via `../../scripts/fred_client.py` (through data-fetcher agent)
- Reference framework: `../../references/investment-clock-cheatsheet.md`

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

---
name: macro-regime-snapshot
description: >-
  Diagnose the current macro regime across US/JP/TW/KR/CN using country macro
  skills. Maps each country's growth + inflation direction to the Investment
  Clock (IC) phase + Hedgeye GIP quadrant, decomposes US real rates (breakeven
  + TIPS), and outputs a 5-block dashboard (Macro Summary / Yield Curve /
  Real Rate / IC+GIP Regime / Asset-Class Tilts) with LSEG-style signal labels
  (Expansion/Contraction, Accommodative/Restrictive). Data + aggregation layer.
---

# macro-regime-snapshot

Five-country macro regime call using the Investment Clock (IC) +
Hedgeye GIP framework, extended with an LSEG-style real-rate
decomposition block for the US. Delegates all raw data fetching to
country-specific macro skills (`us-macro`, `japan-macro`, `taiwan-macro`,
`korea-macro`, `china-macro`) — does not call scripts directly. Maps
each country's Growth + Inflation direction to an IC phase + GIP
quadrant, then outputs a dashboard with asset-class tilts.

Full IC + GIP framework details + per-country proxy mapping:
`references/investment-clock-cheatsheet.md`. This skill is the
**aggregation layer** — analysis conviction, ISQ gating, and memo-grade
commentary belong in `domain-teams:investing-team`.

---

## Inputs

| Parameter | Required | Default | Values |
|-----------|----------|---------|--------|
| `region` | no | `us` | `us` / `japan` / `taiwan` / `korea` / `china` / `global` / `asia-pac` / `all` / free-form comma list (e.g. `us,taiwan`) |
| `date_context` | no | latest | Optional override (e.g. "as of 2026-03") |

### Region expansion

| Value | Countries |
|-------|-----------|
| `us` | US only |
| `japan` | Japan only |
| `taiwan` | Taiwan only |
| `korea` | Korea only |
| `china` | China only |
| `global` | US + Japan (backward-compat default for pre-v1.9.0 callers) |
| `asia-pac` | Japan + Taiwan + Korea + China |
| `all` | US + Japan + Taiwan + Korea + China |
| `us,korea` etc. | Free-form comma list |

Each selected country produces its own independent 5-block dashboard;
multi-country invocations append a **Cross-Market Divergence** note
at the end.

---

## How It Works

### Step 1 — Route region(s) to country macro skills

| Country | Route to | Indicator groups required |
|---------|----------|---------------------------|
| US | `us-macro` | `rates`, `inflation`, `nowcast`, `real-rates` |
| Japan | `japan-macro` | `rates`, `inflation`, `growth` (景気動向指数 CI), `forex` |
| Taiwan | `taiwan-macro` | `rates`, `inflation`, `cycle` (NDC 景氣燈號) |
| Korea | `korea-macro` | `rates`, `inflation`, `cycle` (K253 CI) |
| China | `china-macro` | `rates`, `inflation`, `growth` (三大数据) |

Invoke each country skill in parallel when multi-country regions are
requested.

### Step 2 — Extract per-country Growth + Inflation direction

Use the **v1.7.0 monthly GDP proxies** (not raw IPI) for the Growth
axis. See `references/investment-clock-cheatsheet.md` §"Per-country
proxy mapping" for the canonical series.

| Country | Growth proxy (monthly) | Inflation proxy |
|---------|------------------------|-----------------|
| US | `nowcast.CFNAI` primary + `nowcast.WEI` secondary | `CPIAUCSL` YoY, check vs prior 3-month average |
| JP | `coincident-index` CI (景気動向指数) | 全国CPI YoY |
| TW | `cycle.signal` 景氣燈號 numeric score (1-9) | CPI YoY |
| KR | `coincident-cycle` K253 (동행지수순환변동치) | K401 CPI YoY |
| CN | `industrial-yoy` primary (+ 4-component raw overlay) | CPI YoY |

Compute direction: compare latest reading vs prior 3-month average.
- **Rising**: latest > prior-3m by ≥ half a standard deviation (or
  ≥ 0.1 for normalised indices like CFNAI)
- **Falling**: latest < prior-3m by same threshold
- **Flat**: within the band (note as Stagnation signal)

### Step 3 — Map to IC 2×2 + GIP quadrant

```
              Inflation Rising    Inflation Falling
Growth Rising     IC Phase 2           IC Phase 1
                (Overheat)           (Recovery)
Growth Falling    IC Phase 3           IC Phase 4
                (Stagflation)        (Reflation)
```

GIP quadrant (Hedgeye): same 2×2 but using rate-of-change (2nd
derivative) instead of level direction. IC and GIP can disagree — note
any divergence.

**Country-specific notes**:
- **JP**: Japan's low-inflation regime means "Inflation Rising" may
  still be below 2%. Apply IC to **direction of change**, not level.
- **CN**: CN growth direction uses `industrial-yoy` per v1.7.1 decision
  (no market consensus on composite synthesis — Li Keqiang obsolete,
  SF Fed CAT quarterly, GS/Bloomberg proprietary). Overlay the other
  three Tier-2 components (`retail-yoy`, `fai-yoy`, `services-production-yoy`)
  as supporting context, flag if components disagree.
- **TW**: 五色景氣燈號 score is already a pre-aggregated signal (NDC
  publishes monthly). Score ≥ 32 (綠燈+) = Rising; < 23 (黃藍燈) = Falling.

### Step 4 — Real-rate decomposition (US only)

Pull from us-macro `real-rates` group:

| Tenor | Nominal | Breakeven | Real (market) | Signal |
|-------|---------|-----------|---------------|--------|
| 5Y | DGS5 | T5YIE | DFII5 | see threshold below |
| 10Y | DGS10 | T10YIE | DFII10 | see threshold below |

**Identity check**: `Nominal ≈ Breakeven + Real (DFII)`. If mismatch
> 5 bp, note possible liquidity-premium adjustment.

**Signal thresholds (per-tenor, applied to DFIIxx)**:
- `< 0%` → **Accommodative**
- `0% ≤ x < 1.5%` → **Neutral**
- `≥ 1.5%` → **Restrictive**

For non-US countries emit: "Real-rate decomposition not available — no
developed TIPS/linker series in free data sources. JP JGBi could be
added via MoF scraper in a future release."

### Step 5 — Output 5-block dashboard

Produce one per-country block group, then a cross-market note if
multi-country. See **Output Format** below.

---

## Data Sources

| Country | Via skill | Free | Notes |
|---------|-----------|------|-------|
| US | `us-macro` (29 FRED series) | ✓ | includes new `real-rates` group (T5YIE/T10YIE/DFII5/DFII10) |
| Japan | `japan-macro` (22 BOJ + e-Stat series) | ✓ | 景気動向指数 CI trio from e-Stat |
| Taiwan | `taiwan-macro` (30 series, 4 scripts) | ✓ | NDC 景氣燈號 pre-aggregated |
| Korea | `korea-macro` (54 series via BOK ECOS-KEYSTAT) | ✓ | K253 CI pre-aggregated |
| China | `china-macro` (34 series, NBS + PBOC) | ✓ | 三大数据 raw components |

Reference framework: `references/investment-clock-cheatsheet.md`.

---

## Output Format

```markdown
# Macro Regime Snapshot — {Region} — {date}

## {Country 1} Dashboard

### Block 1 — Macro Summary
| Indicator | Latest | Prior | Direction | Signal |
|-----------|--------|-------|-----------|--------|
| Growth proxy (CFNAI / CI / signal / industrial-yoy) | … | … | Rising / Falling | Expansion / Contraction / Stagnation |
| CPI YoY | …% | …% | Rising / Falling | Above target / At target / Below target |
| Unemployment | …% | …% | Rising / Falling | Tight / Balanced / Slack |
| Policy rate | …% | …% | — | Accommodative / Neutral / Restrictive |

### Block 2 — Yield Curve Snapshot
| Tenor | Yield | vs Prior | Notes |
|-------|-------|----------|-------|
| 2Y | …% | … bp | |
| 5Y | …% | … bp | |
| 10Y | …% | … bp | |
| 30Y | …% | … bp | |

**Slope**: 2s10s = … bp / 3M10Y = … bp
**Curve shape**: Normal / Flat / Inverted / Humped

### Block 3 — Real Rate Decomposition   ← (US only)
| Tenor | Nominal | Breakeven | Real (DFII) | Signal |
|-------|---------|-----------|-------------|--------|
| 5Y | …% | …% | …% | Accommodative / Neutral / Restrictive |
| 10Y | …% | …% | …% | Accommodative / Neutral / Restrictive |

(For non-US: "Real-rate decomposition not available — no developed
TIPS/linker series in free data sources.")

### Block 4 — IC + GIP Regime Call
**IC Phase**: {1 Recovery / 2 Overheat / 3 Stagflation / 4 Reflation}
**GIP Quadrant**: {Quad 1-4 label}
**Divergence**: {agreement / note if divergent}

### Block 5 — Asset-Class Tilts
| Asset Class | Tilt | Rationale |
|-------------|------|-----------|
| Equities | Overweight / Neutral / Underweight | (IC phase mapping) |
| Fixed Income | … | … |
| Commodities | … | … |

### Confidence Note
{Data lag note + any missing series + confidence level: High / Medium / Low}

---

## {Country 2} Dashboard
… (repeat Blocks 1-5) …

---

## Cross-Market Divergence   ← (only for multi-country)
2-3 sentences on whether country regimes align or diverge, and what
that implies (e.g. "US in Phase 2 Overheat while CN in Phase 4 Reflation
— classic USD-strength / EM-headwind setup").
```

---

## Limitations

- **Publication lags**: CPI ~2-3 weeks, CFNAI ~3 weeks, CI ~5-6 weeks,
  country macro-proxies ~4-8 weeks after reference month. Always cite
  reference dates in the Confidence Note.
- **No real-rate block for non-US**: JGBi / KTBi / linkers not wired
  in v1.9.0. Deferred to v1.10.0+.
- **CN no consensus composite**: `industrial-yoy` is the primary Growth
  proxy but the 4 components (industrial/retail/fai/services) often
  disagree month-to-month — flag in output when they diverge > 2%.
- **Signal thresholds are heuristics**: the 1.5% restrictive line for
  DFII is calibrated to post-2003 history + Fed r* framing; other bands
  (Expansion/Contraction for CFNAI) use standard-deviation bands. See
  cheatsheet for full rationale.

---

## Attribution

IC + GIP framework details and regime playbooks are maintained in:
`domain-teams:investing-team` → standards/investment-macro-regime.md.

Real-rate / signal-label pattern inspired by the LSEG partner-built
`macro-rates-monitor` skill in Anthropic's financial-services-plugins
repo (ported from paid MCP to free FRED data).

This skill is the aggregation layer. For full analysis, conviction
ratings, ISQ gating, and portfolio-level implications, route to
`domain-teams:investing-team`.

---
name: analysis-macro-regime
description: >-
  Pure-compute Investment Clock + Hedgeye GIP regime classification across
  US/JP/TW/KR/CN. Input: --input <country=path,country=path,...> macro
  indicator JSONs from data-{country}/pack.py --pack regime-pack. Output:
  regime card JSON.
---

# analysis-macro-regime

> **Layer 2 (Analysis) — pure compute, NO I/O.** This skill consumes
> pre-fetched macro indicator JSONs (one per country) and classifies each
> country into an Investment Clock (IC) phase + Hedgeye GIP quadrant. It
> does NOT call any data source; all fetching happens upstream in
> `data-{country}/pack.py --pack regime-pack`.

Five-country macro regime classifier (US / JP / TW / KR / CN) using the
Investment Clock + Hedgeye GIP framework, extended with US real-rate
decomposition (breakeven + TIPS). Input JSONs follow the regime-pack
contract from each `data-{country}` skill. Output is a structured
regime-card JSON suitable for downstream report skills (e.g.
`report-equity-memo`, `report-portfolio-review`).

Framework + per-country threshold details:
`references/investment-clock-cheatsheet.md` + `references/thresholds-{country}.md`.

This skill is the **classification layer** — analysis conviction, ISQ
gating, and memo-grade commentary belong in `domain-teams:investing-team`.

---

## Inputs / Outputs

### CLI

```bash
uv run scripts/regime_compose.py \
  --input us=/tmp/us-regime.json,jp=/tmp/jp-regime.json,tw=/tmp/tw-regime.json,kr=/tmp/kr-regime.json,cn=/tmp/cn-regime.json \
  > /tmp/regime-card.json
```

### `--input` contract

Comma-separated `country=path` pairs. Each `path` points to a JSON
emitted by `data-{country}/pack.py --pack regime-pack`. Country codes:
`us` / `jp` / `tw` / `kr` / `cn`. Any subset is allowed (single country
to all five).

### Per-country regime-pack JSON shape (consumed)

```json
{
  "country": "us",
  "series": {
    "GDPC1": [2.1, 2.4, 2.5, ...],     // growth proxy (latest last)
    "CPIAUCSL": [3.2, 3.0, 2.8, ...],   // inflation proxy
    "DGS10": [4.5, 4.3, 4.2, ...],      // nominal 10Y (US/JP only)
    "T10YIE": [2.4, 2.3, 2.2, ...]      // breakeven (US only — for real-rate block)
  },
  "_provenance": { "fetched_at": "...", "source": "FRED" }
}
```

The classifier uses the **last 4 readings** of each series (latest +
prior 3-month average) to compute direction. Series naming follows the
country's primary source (FRED for US, BOJ/eStat for JP, NDC/CBC for
TW, ECOS for KR, NBS/PBOC for CN). See `references/proxy-series-map.md`
for the full mapping.

### Output JSON

```json
{
  "schema_version": "1.0",
  "countries": {
    "us": {
      "growth_direction": "rising" | "falling" | "flat",
      "inflation_direction": "rising" | "falling" | "flat",
      "ic_quadrant": "1-recovery" | "2-overheat" | "3-stagflation" | "4-reflation",
      "gip_regime": "quad1" | "quad2" | "quad3" | "quad4",
      "real_rates": {                             // US only — null elsewhere
        "nominal_10y": 4.2,
        "breakeven_10y": 2.2,
        "real_10y": 2.0,
        "signal": "moderately-restrictive"
      },
      "confidence": "high" | "medium" | "low",
      "notes": ["data lag note", ...]
    },
    "jp": { ... },
    "tw": { ... },
    "kr": { ... },
    "cn": { ... }
  },
  "cross_country_consensus": {
    "ic_alignment": "aligned" | "divergent",
    "regimes_present": ["2-overheat", "4-reflation"],
    "note": "US Phase 2 / CN Phase 4 — classic USD-strength setup"
  },
  "_provenance": {
    "computed_at": "2026-05-01T...",
    "input_countries": ["us", "jp", ...],
    "skill": "analysis-macro-regime"
  }
}
```

---

## How It Works

### Step 1 — Per-country direction extraction

For each country in `--input`, read the regime-pack JSON and compute
**growth direction** + **inflation direction** by comparing the latest
reading to the prior 3-month average:

| Direction | Rule |
|---|---|
| **Rising** | latest > prior-3m by ≥ ½ stdev (or ≥ 0.1 for normalised indices like CFNAI) |
| **Falling** | latest < prior-3m by same threshold |
| **Flat** | within the band (Stagnation signal) |

Per-country growth + inflation proxies (canonical, v1.7.0+):

| Country | Growth proxy | Inflation proxy |
|---|---|---|
| US | `nowcast.CFNAI` primary + `WEI` secondary, fallback `GDPC1` | `CPIAUCSL` YoY |
| JP | `coincident-index` (景気動向指数 CI) | 全国 CPI YoY |
| TW | `cycle.signal` (NDC 五色景氣燈號 1-9 score) | CPI YoY |
| KR | `coincident-cycle` K253 (동행지수순환변동치) | K401 CPI YoY |
| CN | `industrial-yoy` primary + 3-component overlay | CPI YoY |

The classifier reads whichever series key the regime-pack provides —
script tolerates multiple naming conventions (`GDPC1` / `gdp` /
`growth.industrial-yoy` etc.) via a country-specific resolver.

### Step 2 — Map to IC 2×2 + GIP quadrant

```
              Inflation Rising    Inflation Falling
Growth Rising     IC Phase 2           IC Phase 1
                (Overheat)           (Recovery)
Growth Falling    IC Phase 3           IC Phase 4
                (Stagflation)        (Reflation)
```

GIP quadrant uses the same 2×2 (Hedgeye Quad 1-4 ≅ IC Phase 1-4 in this
implementation; v2.0.0 keeps the simple mapping — second-derivative
divergence is documented in `references/investment-clock-cheatsheet.md`
but not auto-flagged).

**Country-specific notes** (preserved from v1.x):
- **JP**: low-inflation regime — apply IC to **direction of change**, not
  level. "Inflation Rising" may still be below 2%.
- **CN**: `industrial-yoy` is the primary Growth proxy; 4-component
  overlay (industrial / retail / fai / services) flagged when components
  disagree by > 2%.
- **TW**: 五色景氣燈號 score is pre-aggregated by NDC. Score ≥ 32
  (綠燈+) = Rising; < 23 (黃藍燈) = Falling.

### Step 3 — US real-rate decomposition

If the US regime-pack provides `T10YIE` (10Y breakeven) and `DGS10`
(nominal 10Y), compute the real-rate block:

```
Real_10y = Nominal_10y − Breakeven_10y   (Fisher decomposition)
```

If `DFII10` (TIPS yield) is also provided, use it directly as the
market real rate and emit identity check `|Nominal − Breakeven − DFII| ≤ 5 bp`.

US signal thresholds (four-tier, applied to real_10y):
- `< 0%` → **accommodative**
- `0% ≤ x < 1.0%` → **neutral**
- `1.0% ≤ x < 1.75%` → **moderately-restrictive**
- `≥ 1.75%` → **clearly-restrictive**

JP / TW / KR / CN: real-rate block emits `null` with a `notes` entry
explaining the gap (no free CPI-linker market for TW/CN; KR ECOS API
key required; JP supported in v1.10.0 via ECB/Tankan/JGBi but not in
the v2.0.0 minimum-viable regime-pack — deferred).

### Step 4 — Cross-country consensus

If `--input` contains > 1 country, emit a `cross_country_consensus`
block summarising IC alignment ("aligned" if all countries share the
same quadrant; "divergent" otherwise) + a 1-sentence interpretive note
(e.g. "US Phase 2 Overheat / CN Phase 4 Reflation — USD-strength
setup").

---

## Cross-country coverage grid (5 × 9 signals)

Per-country availability for the 9 signals classifier consumes. ✅ = fetched
upstream (regime-pack provides via free primary source); ⚠️ = partial /
proxy / URL-only; ❌ = not available. See `references/thresholds-{country}.md`
for per-country regime calibration (targets, bands, r*, structural caveats).

| Signal | US | JP | TW | KR | CN |
|--------|----|----|----|----|----|
| Growth proxy (monthly) | ✅ CFNAI + WEI | ✅ 内閣府 CI | ✅ NDC 五色燈號 | ✅ K253 | ⚠️ industrial-yoy + overlay |
| Inflation (CPI YoY) | ✅ CPIAUCSL | ✅ cpi-all-items | ✅ cpi-yoy | ✅ K401 | ✅ cpi-yoy |
| Policy rate | ✅ DFEDTARU | ✅ policy-rate | ✅ rediscount | ✅ K041 | ✅ LPR-1y/5y |
| Yield curve (2s10s) | ✅ DGS2/DGS10 | ✅ jgb-2y/10y | ⚠️ CBC 5Y/10Y | ✅ ktb-3y/10y | ⚠️ CGB 10Y |
| Real rate (market) | ✅ T10YIE+DFII10 | ⚠️ deferred v2.0.0 | ❌ no linker | ❌ ECOS key | ❌ no linker |
| PMI | ✅ OECD CLI proxy | ⚠️ URL-only | ✅ NDC pmi-mfg/nmi | ⚠️ URL-only | ✅ Caixin+NBS |
| Swap spread | ✅ DGS3MO−SOFR | ❌ no equiv | ❌ | ❌ | ❌ |
| FX | ✅ DXY | ✅ usd-jpy | ✅ usd-twd | ✅ krw-usd K151 | ✅ cny-usd |
| Equity | ✅ S&P 500 | ✅ TOPIX/N225 | ✅ TAIEX | ✅ KOSPI | ✅ CSI300 |

This skill consumes whatever the regime-pack provides; missing optional
signals degrade gracefully (e.g. real-rate block emits `null` for
non-US countries, US in v2.0.0 always supported).

---

## Limitations

- **Pure compute** — no caching, no fetch, no retries. Upstream data
  freshness is the regime-pack's responsibility.
- **Direction-only IC**: GIP second-derivative divergence is documented
  but not auto-flagged in v2.0.0. Use `references/investment-clock-cheatsheet.md`
  for manual interpretation.
- **CN no consensus composite**: `industrial-yoy` is the headline
  Growth direction; 4-component disagreement (> 2%) is flagged in
  `notes`.
- **Signal thresholds are heuristics**: per-country threshold files
  (`references/thresholds-{country}.md`) document calibration vintages
  and primary sources. Re-read before making a regime call.
- **JP real-rate deferred**: v1.10.0's C+D+E framework (ECB ex-post +
  Tankan + JGBi auction) is not in the v2.0.0 minimum regime-pack.
  Signalled as `null` with `notes`. Restore in v2.1+ once the data-jp
  regime-pack contract stabilises.

---

## References

- `references/investment-clock-cheatsheet.md` — IC + GIP framework,
  per-country proxy mapping, real-rate interpretation, signal-label
  glossary, threshold provenance
- `references/recalibration-protocol.md` — when & how to re-verify
  threshold files against primary sources
- `references/thresholds-us.md` — Fed 2% target, CBO NROU ~4.4%, HLW /
  Lubik-Matthes / NY Fed r* estimates, real-rate four-tier thresholds
- `references/thresholds-japan.md` — BOJ 2% target, JILPT NAIRU
  ~3.5-3.6%, BOJ WP24-J-09 r* = -0.25%, deflation-legacy caveats
- `references/thresholds-taiwan.md` — CBC 彈性定義, 景氣對策信號 5-color
  scoring, TAIEX tech concentration
- `references/thresholds-korea.md` — BOK 2% target, KDI NAIRU
  ~3.0-3.5%, KOSPI Samsung+SK Hynix concentration
- `references/thresholds-china.md` — 3% State Council target,
  multi-rate PBOC framework, property deleveraging overhang

---

## Attribution

IC + GIP framework details and regime playbooks are maintained in:
`domain-teams:investing-team` → `standards/investment-macro-regime.md`.

Real-rate / signal-label pattern inspired by the LSEG partner-built
`macro-rates-monitor` skill in Anthropic's financial-services-plugins
repo (ported from paid MCP to free FRED data).

This skill is the classification layer. For full analysis, conviction
ratings, ISQ gating, and portfolio-level implications, route to
`domain-teams:investing-team` via a `report-*` skill.

---

## i18n

| Language | Term mapping |
|---|---|
| English | Investment Clock / regime / quadrant |
| 繁體中文 | 投資時鐘 / 景氣循環階段 / 象限 |
| 日本語 | インベストメント・クロック / 景気局面 / 象限 |

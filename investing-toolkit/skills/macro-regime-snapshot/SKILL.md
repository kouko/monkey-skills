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

### Step 1 — Route region(s) to country macro skills + load country thresholds

| Country | Route to | Indicator groups required | Threshold reference |
|---------|----------|---------------------------|---------------------|
| US | `us-macro` | `rates`, `inflation`, `nowcast`, `real-rates`, `pmi`, `swap-spreads` | `references/thresholds-us.md` |
| Japan | `japan-macro` | `rates`, `inflation`, `growth` (景気動向指数 CI), `forex`, `real-rates` | `references/thresholds-japan.md` |
| Taiwan | `taiwan-macro` | `rates`, `inflation`, `cycle` (NDC 景氣燈號) | `references/thresholds-taiwan.md` |
| Korea | `korea-macro` | `rates`, `inflation`, `cycle` (K253 CI) | `references/thresholds-korea.md` |
| China | `china-macro` | `rates`, `inflation`, `growth` (三大数据) | `references/thresholds-china.md` |

Invoke each country skill in parallel when multi-country regions are
requested. **Load the corresponding `references/thresholds-{country}.md`
file** for each selected country — this file contains the
country-specific:

- Inflation target + tolerance band + Above/At/Below-target thresholds
- NAIRU estimate + Tight/Balanced/Slack unemployment bands
- Policy rate + nominal + real neutral-rate estimate
- Real-rate block availability + thresholds (v1.10.0: US + JP;
  TW/KR/CN "N/A")
- PMI group availability (v1.10.0: US fetched via OECD CLI; JP/TW/KR/CN
  URL-only reference)
- Swap-spread block availability (v1.10.0: US-only T-SOFR 3M proxy;
  others omitted)
- Structural regime notes (deflation legacy / tech concentration /
  property deleveraging / etc.)
- Country-specific IC sector tilt adjustments
- Primary-source URLs + citations for audit

**Do NOT apply US thresholds to non-US countries** — e.g. JP NAIRU is
~3.5% (not US's 4.4%); CN inflation target is 3% (not 2%); TW uses
flexible definition (not a rigid target). Always read the per-country
threshold file before classifying signals.

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

### Step 4 — Rate Stress Dashboard

**v1.10.0 rename + restructure**: Block 4 (formerly "Real Rate Decomposition")
is now a Rate Stress Dashboard containing two sub-blocks — 4a Real Rate
Decomposition (expanded from US-only to US + JP) and 4b Swap Spread
(US-only money-market liquidity proxy, new).

#### 4a. Real Rate Decomposition

**US sub-block** (unchanged from v1.9.0): 5Y + 10Y nominal / breakeven /
real / signal, fetched via `us-macro` → `real-rates` group (T5YIE,
T10YIE, DFII5, DFII10, DGS5, DGS10).

| Tenor | Nominal | Breakeven | Real (market) | Signal |
|-------|---------|-----------|---------------|--------|
| 5Y | DGS5 | T5YIE | DFII5 | see threshold below |
| 10Y | DGS10 | T10YIE | DFII10 | see threshold below |

**Identity check**: `Nominal ≈ Breakeven + Real (DFII)`. If mismatch
> 5 bp, note possible liquidity-premium adjustment.

**US signal thresholds (four-tier, per-tenor, applied to DFIIxx — 2025-2026 calibration)**:
- `< 0%` → **Accommodative**
- `0% ≤ x < 1.0%` → **Neutral** (around HLW r* minus term premium)
- `1.0% ≤ x < 1.75%` → **Moderately Restrictive** (matches Williams' "modestly restrictive" language, Dec 2025 / Jan 2026 speeches)
- `≥ 1.75%` → **Clearly Restrictive** (above FOMC long-run dot upper range; full headwind)

The four-tier split respects the post-COVID r* debate: HLW (2025) = 0.75%,
Lubik-Matthes = 1.68%, FOMC SEP longer-run real median = 1.0%. A single
cut-off isn't defensible given this spread. See
`references/investment-clock-cheatsheet.md` § "Real-Rate Interpretation"
and `references/thresholds-us.md` for sources + calibration audit.

**JP sub-block** (new v1.10.0 — multi-source C+D+E framework):

Fetched via `japan-macro` → `real-rates` group (`ecb_client` monthly
ex-post + `boj_client` Tankan survey + `jgbi-auction-history.yml`
anchor):

| Series | Source | Cadence | Role |
|--------|--------|---------|------|
| `real-10y-monthly` | ECB ex-post monthly (10Y JGB nominal − 全国CPI YoY) | Monthly | Continuous signal (ex-post caveat) |
| `real-10y-auction` | MoF JGBi auction-weighted anchor | Quarterly | Forward-looking anchor point |
| `inflation-tankan-1y` | BOJ Tankan 企業物価見通し 1-year | Quarterly | Expectation complement |
| `inflation-tankan-3y` | BOJ Tankan 企業物価見通し 3-year | Quarterly | Medium-term expectation |
| `inflation-tankan-5y` | BOJ Tankan 企業物価見通し 5-year | Quarterly | Long-term expectation |

**JP signal thresholds** calibrated to BOJ r* = -0.25% (WP24-J-09 mean):
see `references/thresholds-japan.md` § "Real Rate Decomposition (v1.10.0)"
for the full C+D+E framework + thresholds.

**TW / KR / CN**: N/A for real-rate decomposition. Each country has no
developed free inflation-linked bond market:
- **TW**: no public CPI-linker market
- **KR**: ECOS BOK linker series require free API key (deferred to v1.10.1+)
- **CN**: no public CPI-linker market

Emit: "Real-rate decomposition not available — {country-specific reason}."

#### 4b. Swap Spread (US-only v1.10.0)

Treasury-SOFR 3M spread (DGS3MO − SOFR30DAYAVG) as a **money-market
liquidity proxy**. Fetched via `us-macro` → `swap-spreads` group.

See `../us-macro/references/us-macro-indicators.md` § Swap Spread section
for the "NOT a full term swap spread" caveat — the true 10Y term swap
spread requires licensed Bloomberg / Reuters / ICE data; the T-SOFR 3M
proxy captures **money-market liquidity stress**, not term-structure
dislocation.

| Spread | Signal |
|--------|--------|
| < 20 bp | Normal |
| 20 ≤ x < 50 bp | Elevated |
| ≥ 50 bp | Stressed (GFC / COVID / SVB breach levels) |

Use **monthly average** rather than quarter-end spot (post-QT window-
dressing distorts spot readings 10-15 bp at quarter-end). Threshold
provenance: see `references/investment-clock-cheatsheet.md` § "Swap
Spread Threshold Provenance (v1.10.0)".

**JP / TW / KR / CN**: no equivalent free-tier SOFR-like benchmark;
section omitted.

### Step 5 — Output 5-block dashboard

Produce one per-country block group, then a cross-market note if
multi-country. See **Output Format** below.

---

## Data Sources

| Country | Via skill | Free | Notes |
|---------|-----------|------|-------|
| US | `us-macro` (29+ FRED series) | ✓ | v1.9.0 `real-rates` (T5YIE/T10YIE/DFII5/DFII10) + v1.10.0 `pmi` (OECD CLI `USALOLITOAASTSAM`) + `swap-spreads` (DGS3MO − SOFR30DAYAVG) |
| Japan | `japan-macro` (22+ BOJ + e-Stat series) | ✓ | 景気動向指数 CI trio + v1.10.0 `real-rates` group (ECB ex-post monthly + BOJ Tankan + JGBi auction history) |
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
| PMI / Business cycle | US: OECD CLI amplitude ; JP/TW/KR/CN: N/A (see URL cross-reference) | … | Rising / Flat / Falling | Expansion / Near-neutral / Contraction (US); URL-only (others) |

**PMI per-country data availability**:
- **US**: OECD CLI (`USALOLITOAASTSAM`) fetched via `us-macro` → `pmi` group (ISM / S&P Global not on FRED)
- **JP**: Jibun Bank Composite PMI — licensed; URL reference only (https://www.pmi.spglobal.com/ or https://www.jibunbank.co.jp/)
- **TW**: 中経院 (CIER) PMI / 中華採購與供應管理協會 PMI — URL only (https://www.cier.edu.tw/)
- **KR**: 한국경제연구원 (KERI) BSI / S&P Global Korea PMI — URL only
- **CN**: Caixin Manufacturing + NBS 官方 PMI — v1.11.0+ candidate (akshare); v1.10.0 N/A with URL reference

Signal thresholds + direction classification: see `references/investment-clock-cheatsheet.md`
§ "PMI Signal Glossary (v1.10.0)".

### Block 2 — Yield Curve Snapshot
| Tenor | Yield | vs Prior | Notes |
|-------|-------|----------|-------|
| 2Y | …% | … bp | |
| 5Y | …% | … bp | |
| 10Y | …% | … bp | |
| 30Y | …% | … bp | |

**Slope**: 2s10s = … bp / 3M10Y = … bp
**Curve shape**: Normal / Flat / Inverted / Humped

### Block 3 — Rate Stress Dashboard

#### 3a. Real Rate Decomposition

**US** (v1.9.0, unchanged):
| Tenor | Nominal | Breakeven | Real (DFII) | Signal |
|-------|---------|-----------|-------------|--------|
| 5Y | …% | …% | …% | Accommodative / Neutral / Moderately Restrictive / Clearly Restrictive |
| 10Y | …% | …% | …% | Accommodative / Neutral / Moderately Restrictive / Clearly Restrictive |

**Japan** (v1.10.0 new — C+D+E multi-source):
| Series | Latest | Prior | Signal |
|--------|--------|-------|--------|
| Real 10Y monthly (ex-post) | …% | …% | Accommodative / Neutral / Restrictive vs r* = -0.25% |
| Real 10Y JGBi auction anchor | …% | …% | (quarterly anchor) |
| Tankan expectations 1Y / 3Y / 5Y | …% / …% / …% | … | Anchored / Drifting |

(For TW / KR / CN: "Real-rate decomposition not available — no
developed free CPI-linker market (TW/CN) or ECOS API key required
(KR, deferred to v1.10.1+).")

#### 3b. Swap Spread (US-only v1.10.0)

| Spread | Latest (monthly avg) | Prior | Signal |
|--------|----------------------|-------|--------|
| T-Bill 3M − SOFR30DAYAVG | … bp | … bp | Normal (<20 bp) / Elevated (20-50) / Stressed (>50) |

(For JP / TW / KR / CN: "Swap-spread proxy not available — no
equivalent free-tier SOFR-like benchmark.")

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
- **Real-rate block coverage (v1.10.0)**: US (unchanged) + JP (new,
  C+D+E multi-source via ecb_client + boj_client + JGBi auction history).
  TW/CN have no free CPI-linker market; KR ECOS linker requires API key
  (deferred to v1.10.1+).
- **Swap-spread block (v1.10.0)**: US-only T-Bill 3M − SOFR30DAYAVG
  money-market liquidity proxy (NOT a full term swap spread — that
  requires licensed data). No equivalent free benchmark for JP/TW/KR/CN.
- **PMI coverage (v1.10.0)**: US only via OECD CLI (`USALOLITOAASTSAM`)
  as proxy — ISM / S&P Global not on FRED. JP/TW/KR/CN kept as URL-only
  references (licensed / out-of-scope); CN Caixin + NBS PMI via akshare
  is a v1.11.0+ candidate.
- **CN no consensus composite**: `industrial-yoy` is the primary Growth
  proxy but the 4 components (industrial/retail/fai/services) often
  disagree month-to-month — flag in output when they diverge > 2%.
- **Signal thresholds are heuristics, not dogma**: calibration vintages
  are documented in per-country threshold files
  (`references/thresholds-{country}.md`). Values should be revised as
  FOMC dot plot, BOJ 展望, BOK 통화정책방향 updates arrive. Re-read the
  threshold file for each country before each regime call.

---

## References

Framework + country calibration:

- `references/investment-clock-cheatsheet.md` — IC + GIP framework,
  per-country proxy mapping, real-rate interpretation, signal-label
  glossary, threshold provenance
- `references/recalibration-protocol.md` — when & how to re-verify
  threshold files against primary sources (triggers, cadence,
  source tiers, native-language priority)
- `research/grounding-v1.9.0.md` — **primary-source audit trail**
  for 5-country threshold calibration (2026-04-18, 5 parallel
  native-language grounding agents; found & fixed 19 🔴 + 16 ⚠️
  corrections across US/JP/TW/KR/CN)
- `references/thresholds-us.md` — Fed 2% target, CBO NROU ~4.4%, HLW
  / Lubik-Matthes / NY Fed r* estimates, real-rate four-tier thresholds
- `references/thresholds-japan.md` — BOJ 2% target (no band), JILPT
  NAIRU ~3.5-3.6%, BOJ WP24-J-09 r* = -0.25% mean, deflation-legacy
  caveats, post-YCC regime
- `references/thresholds-taiwan.md` — CBC 彈性定義, 景氣對策信號 5-color
  scoring (9-45 composite), TAIEX ~65% tech + TSMC ~40%
- `references/thresholds-korea.md` — BOK 2% target, KDI NAIRU ~3.0-3.5%,
  KOSPI Samsung + SK Hynix ~30%, household-debt 105% GDP caveat
- `references/thresholds-china.md` — 3% State Council target (ceiling
  not center), 5.5% 城鎮調查失業率 target, multi-rate PBOC framework,
  property deleveraging structural overhang, Phase-3/4 default regime

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

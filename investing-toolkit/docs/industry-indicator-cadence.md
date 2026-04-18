# Industry Indicator Cadence — Five-Country Cross-Market Reference

Cross-country comparison of **industry-level** (sector) indicator coverage,
release frequencies, and publication lags across the five macro skills
(US / JP / TW / KR / CN). Complements the
[Monthly GDP Proxy Framework](../skills/using-investing-toolkit/SKILL.md#cross-market-monthly-gdp-proxy-framework)
which covers aggregate macro; this document is about **sector-level
granularity**.

## Why cadence matters

Release frequency + publication lag determines what investment horizon a
skill's data can support:

- **Daily / weekly** data → actionable for **short-term trading**
- **Monthly** data → useful for **tactical allocation** (months-quarters)
- **Quarterly** data → only usable for **long-horizon decisions** (year+)

A sector indicator that releases with a 6-week lag cannot drive a monthly
rebalance decision — by the time you see the signal, the cycle has already
moved. This matters most for semiconductor-heavy KR/JP portfolios where
the chip cycle turns quickly.

---

## Five-country coverage matrix

| Country | Coverage grade | Sector groups in skill | Notable gaps |
|---------|---------------|------------------------|--------------|
| **US** | ⭐⭐⭐ Complete | 7 groups + ETF map (housing/industrials/energy/financials/consumer/tech/ppi) | None — FRED covers every imaginable sector |
| **JP** | ⭐⭐ Scattered | `machine-orders`, `tertiary-index`, `retail-sales`, `service-sales`, TANKAN DI | No systematic sector partition; sectors bundled into `growth` / `consumption` |
| **CN** | ⭐⭐ Skewed | `realestate` (4 presets), `services` (1 preset) + 三大數據 | NBS tree 2908 leaves: 49 two-digit industries (steel/auto/chemicals/semi/pharma) captured in `docs/` but **not exposed as presets** |
| **TW** | ⭐⭐ Aggregate-only | IPI, manufacturing-yoy, retail-yoy, export-orders, import/export-PI, NDC signal-components | stat.gov.tw has 20 manufacturing mid-categories (electronics, chemicals, steel, etc.) not exposed |
| **KR** | ⭐ Thinnest | `manufacturing` (K201) only | **K202-K210 (inventory / shipment / operating rate / services production / retail / wholesale / credit cards)** all in KEYSTAT but unexposed |

---

## Cadence tiers (cross-country)

Sorted fastest → slowest:

### Tier 1 — Daily (T+1 business day)
| Country | Indicators |
|---------|-----------|
| US | `DCOILWTICO` (WTI crude), `DHHNGSP` (Henry Hub natgas), `BAMLH0A0HYM2` (HY credit spread) |

### Tier 2 — Weekly (~1 week)
| Country | Indicators |
|---------|-----------|
| US | `MORTGAGE30US` (30Y fixed mortgage) |

### Tier 3 — Monthly-fast (~15 days after month-end)
| Country | Indicators |
|---------|-----------|
| **CN** | **三大數據 package** (`industrial-yoy` / `retail-yoy` / `fai-yoy`), `services-production-yoy`, real-estate quartet (`realestate-investment-yoy` / `housing-sales-*` / `realestate-funding-yoy`) |

NBS publishes the entire package around the 15-20th of each month. This is the **world's fastest monthly macro release cadence** for a major economy.

### Tier 4 — Monthly-medium (~3-4 weeks)
| Country | Indicators |
|---------|-----------|
| US | `PERMIT`, `HOUST`, `DGORDER`, `INDPRO`, `RSAFS`, `UMCSENT`, `CES3133440001`, `PCUAINFOAINFO`, `PCUOMFGOMFG` |
| TW | `ipi`, `manufacturing-yoy`, `retail-yoy`, `export-orders`, `cpi`, price indices |

### Tier 5 — Monthly-slow (~5-8 weeks)
| Country | Indicators |
|---------|-----------|
| JP | `machine-orders`, `tertiary-index`, `service-sales`, `coincident-index`, `leading-index`, `lagging-index` |
| KR | `manufacturing` K201 (and all K202-K210 candidates if added), `ipi`, `coincident-cycle`, `leading-cycle` |
| TW | `signal` (景氣燈號 — 6-8 weeks because NDC waits for all 9 component inputs), `signal-components`, `leading-index`, `coincident-index` |
| US | `CSUSHPISA` (Case-Shiller housing — ~2 months) |

### Tier 6 — Quarterly
| Country | Indicators |
|---------|-----------|
| JP | `tankan` (Business Conditions DI), quarterly survey |
| All | GDP series (KR `gdp-qoq`, US `GDPC1`, TW `gdp-yoy`, JP `gdp`, CN `gdp-yoy`) |

### Tier 7 — Annual
| Country | Indicators |
|---------|-----------|
| KR | `population` (K451), `aging-ratio` (K460), `fertility-rate` (K461) — demographics |

---

## Per-country detail

### 🇺🇸 US — Most complete, best-tiered
`us-macro` is the only skill with **explicit sector groups mapped to sector ETFs**:

| Group | ETF | Key indicators | Cadence |
|-------|-----|---------------|---------|
| `housing` | XLRE, XHB | PERMIT, HOUST, CSUSHPISA, MORTGAGE30US | Monthly-medium (CS ~2mo) |
| `industrials` | XLI | DGORDER, INDPRO | Monthly-medium |
| `energy` | XLE | DCOILWTICO, DHHNGSP | Daily |
| `financials` | XLF | BAMLH0A0HYM2 | Daily |
| `consumer` | XLY, XLP | RSAFS, UMCSENT | Monthly-medium |
| `tech` | XLK | CES3133440001 (semi employment), PCUAINFOAINFO | Monthly-medium |
| `ppi` | cross-sector | PCUOMFGOMFG | Monthly-medium |

**Investment-horizon fit**: Short-term (daily energy/credit) through tactical (monthly sector data). US FRED is the only truly multi-timescale sector data source.

### 🇯🇵 JP — Deep but slow
Industry-level data exists but is scattered across groups rather than systematised:

- **Manufacturing capex cycle**: `machine-orders` (機械受注) — ~6 weeks lag
- **Services sector**: `tertiary-index` (第3次産業活動指数) + `service-sales` — ~6 weeks
- **Retail**: `retail-sales` — ~4 weeks
- **Business conditions**: `tankan` DI quarterly — broken down by sector (large manufacturing / large non-manufacturing / SME variants)

**Character**: Slow release but **very low revision rate**. Suitable for medium-horizon fundamental analysis, not short-term trading.

### 🇨🇳 CN — Fastest but narrow skill exposure
NBS publishes at world-leading ~15-day lag. Current `china-macro` skill exposes:

- `realestate`: 4 presets (investment / sales area / sales value / funding) — the most complete real-estate sector coverage of any skill
- `services`: 1 preset (`services-production-yoy`)
- **Hidden in `docs/nbs-indicator-catalog.md`**: 2908 leaf indicators across 49 two-digit industries (GBT 4754), 月度/季度/年度 tree fully captured but not exposed as presets

**Expansion potential**: Largest by far. The NBS tree has granular sector indicators (汽車產量 / 粗鋼產量 / 水泥產量 / 半導體晶圓 / 醫藥 / 紡織) that would fit a v1.9.0 Tier-B expansion.

### 🇹🇼 TW — Aggregate-only; CI trio well-covered
`taiwan-macro` exposes aggregate industry data but no manufacturing sub-categories:

- `ipi`, `manufacturing-yoy` (aggregate only)
- `retail-yoy` (aggregate)
- `export-orders` (外銷訂單 — 3-4 week lag, particularly important for semi cycle)
- `import-pi`, `export-pi` (price indices)
- `signal` / `leading-index` / `coincident-index` (NDC/DGBAS CI pre-aggregated)

**stat.gov.tw has 20 manufacturing mid-categories** (電子零組件, 化學材料, 鋼鐵, 機械, 食品, 紡織, 塑膠, 石油煉製, etc.) accessible via their hidden chart JSON endpoint but **not exposed as presets**.

### 🇰🇷 KR — Thinnest coverage; highest expansion ratio
Currently only `manufacturing` (K201) at sector level. The BOK ECOS KEYSTAT catalogue (see `skills/korea-macro/docs/bok-ecos-keystat-catalog.md`) contains 10+ industry candidates already identified:

| KEYSTAT | Indicator (KR) | English |
|---------|---------------|---------|
| K202 | 재고 | Manufacturing inventory |
| K203 | 출하 | Manufacturing shipment |
| K204 | 가동률 | Manufacturing operating rate |
| K205 | 서비스업생산지수 | Services production (KR's tertiary index) |
| K206 | 소매판매액지수 | Retail sales |
| K207 | 도소매업 | Wholesale + retail aggregate |
| K210 | 신용카드 사용액 | Credit card usage |
| K213 | 설비투자 선행 | Machinery orders ex-ship (leading capex) |
| K215 | 자본재생산 | Capital goods production |
| K216 | 건설기성액 | Construction completion value |
| K217 | 건설수주액 | Construction orders value |

All accessible via `FinanceDataReader` with no API key. Adding these as `industry` group presets is the **lowest-effort / highest-leverage expansion** in the roadmap.

---

## Investment-horizon matching

| Horizon | Best countries | Reason |
|---------|---------------|--------|
| **Short-term (week-month)** | US / CN | Daily data (US) + 15-day monthly release (CN) + complete sector detail |
| **Medium-term (quarter-year)** | JP / TW / KR | Slower release but very low revision rates; data quality over speed |
| **Long-term (year+)** | All five | Aggregates + demographics (KR) + GDP breakdowns all suitable |

**Regime-change signals**:
- **Earliest turning-point detection**: US daily (credit spread, oil, mortgage rate)
- **Fastest monthly cross-check**: CN 三大數據 (~15d)
- **Most reliable confirmation**: JP TANKAN + machine-orders (~6w but low noise)

---

## Expansion roadmap

| Version | Scope | Effort |
|---------|-------|--------|
| **v1.8.1 (candidate)** | **KR industry expansion** — add K202-K207, K210, K213, K215-K217 as `industry` group (~10 new presets) | ~30 min; pure preset addition, uses existing `fdr_client.py` |
| **v1.9.0 (candidate)** | **CN NBS sector expansion** — expose 20-30 high-value industry presets from the 2908-leaf NBS tree (semi, auto, steel, cement, pharma, textiles) | Half-day; builds on `skills/china-macro/docs/nbs-indicator-catalog.md` |
| **v1.9.0+ (candidate)** | **TW manufacturing sub-categories** — 20 mid-categories via stat.gov.tw JSON | Medium; requires `statgov_client.py` revision |
| **v2.0.0+ (tentative)** | **JP industry granularity** — e-Stat industry classification | Medium |
| **N/A** | US — already complete | — |

Priority recommendation:
1. **KR** (v1.8.1) — highest leverage, lowest effort, fixes the thinnest skill
2. **CN** (v1.9.0) — largest addressable data set; the NBS catalogue investment is already done
3. Others — lower priority, can wait for specific investment-research need

---

## Cross-references

- Per-country sector coverage details:
  - `skills/us-macro/SKILL.md` — ETF mapping section
  - `skills/japan-macro/references/indicators-growth.md`
  - `skills/taiwan-macro/references/indicators-cycle.md` — 景氣燈號 context
  - `skills/korea-macro/docs/bok-ecos-keystat-catalog.md` — K202-K210 candidates
  - `skills/china-macro/docs/nbs-indicator-catalog.md` — 2908-leaf full tree
- Aggregate monthly-GDP-proxy counterpart:
  - `skills/using-investing-toolkit/SKILL.md` § Cross-market Monthly GDP Proxy Framework

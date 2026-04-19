# PMI / 采购经理指数

5 Purchasing Managers' Index series — **3 NBS 官方 + 2 Caixin / S&P
Global** — covering China's manufacturing and services cycle. NBS
官方 via `nbs_client` (primary source); Caixin via `akshare_client`
(`index_pmi_*_cx` endpoint, eastmoney-backed).

**Signal thresholds** (standard diffusion index convention): `> 52`
Expansion / `50-52` Near-neutral / `< 50` Contraction.

See §**Caixin vs NBS methodology delta** at the bottom for divergence
interpretation and historical regime shifts.

---

## pmi-manufacturing: NBS 制造业 PMI / Official Manufacturing PMI

- **Series code**: nbs_client (NBS new-SPA API; legacy akshare route `macro_china_pmi` col 制造业-指数)
- **Source**: 国家统计局 NBS (National Bureau of Statistics) + 中国物流与采购联合会 CFLP
- **Unit**: Index (50 = expansion/contraction dividing line)
- **Frequency**: Monthly
- **Publication lag**: Published on the last day of the reference month (fastest of all PMIs)
- **History**: From 2005 (240+ observations)

**What it measures**: The official manufacturing Purchasing Managers'
Index. Survey of purchasing managers at 3,000+ manufacturing firms
across China, conducted by NBS in partnership with CFLP. Composite of
new orders, output, employment, supplier delivery times, and inventories.

**How to interpret**:
- Above 50 → Manufacturing sector expanding MoM. Readings above 51 are
  meaningfully expansionary.
- Below 50 → Manufacturing contracting. Readings below 49 are
  meaningfully contractionary.
- The sub-indices (new export orders, new orders, finished goods
  inventory) provide compositional signal. New export orders below
  new orders → external demand weaker than internal.

**Market significance**: ⭐⭐⭐
The first major Chinese data point of every month (released same-day
as month-end), making it highly market-moving. Moves CSI 300,
industrial metals, AUD/USD. A sustained print below 50 combined with
weak Caixin PMI is a recession-like signal that typically triggers
policy-easing bets.

**When to use**: Manufacturing-cycle timing, commodity demand reads,
China reopening/slowdown narrative construction, leading-indicator
input for GDP now-casts.

**China-specific context**:
- Sample is weighted toward large and state-owned enterprises — the
  official PMI tends to run higher than Caixin during periods of
  preferential SOE credit or government infrastructure stimulus.
- Sub-50 prints have been frequent in 2023-2025, reflecting the
  property-chain unwind and manufacturing overcapacity (solar, EV,
  steel). A reading consistently near 49 is the 2024-2025 baseline,
  not an alarming outlier.
- Chinese New Year pushes February PMI lower (seasonality). Some
  analysts watch the seasonally-adjusted NBS release, though the
  unadjusted print is headline.

**Common pitfalls**:
- NBS PMI and Caixin PMI can diverge meaningfully — the gap itself is
  a signal about SOE vs POE dynamics (see below), not noise.
- The 50 line is a MoM signal, not a level signal. A PMI of 50.5 does
  not mean manufacturing is strong — only that it grew slightly vs the
  prior month. Cumulative drift matters.
- Sample rotation and weight revisions occasionally create small step
  changes; NBS does not always revise the full history.

---

## pmi-non-manufacturing: NBS 非制造业 PMI / Official Non-Manufacturing PMI

- **Series code**: nbs_client (NBS new-SPA API; legacy akshare route `macro_china_pmi` col 非制造业-指数)
- **Source**: 国家统计局 NBS + CFLP
- **Unit**: Index (50 = expansion/contraction dividing line)
- **Frequency**: Monthly
- **Publication lag**: Published on the last day of the reference month (jointly with manufacturing PMI)
- **History**: From 2007 (220+ observations)

**What it measures**: The official non-manufacturing PMI — covers
services and construction. Survey of 4,000+ firms. Provides the
services-side signal that manufacturing PMI misses.

**How to interpret**:
- Services component — primary services-sector sentiment gauge. Key
  for catering, travel, financial services, retail-adjacent segments.
- Construction component — reads the property/infrastructure cycle
  directly. During 2023-2025 the construction sub-index has been
  materially weaker than services, reflecting the property drag.
- Aggregate above 50 → non-manufacturing expanding; below 50 → contracting.

**Market significance**: ⭐⭐
Important complement to manufacturing PMI. The services recovery
narrative (esp. post-covid reopening) was tracked primarily here.
Moves Chinese consumer-cyclical equities and construction-related names.

**When to use**: Services-recovery tracking, construction-cycle
monitoring, property-chain health assessment, consumer-discretionary
sector timing.

**China-specific context**:
- The services and construction sub-readings often diverge sharply —
  reporters often headline the composite, but the split is the useful
  read.
- Construction sub-index bottomed out near 47-48 during the 2023-2024
  property stress and has been the drag on the non-manufacturing
  composite.
- Travel and catering drive seasonality — National Day Golden Week
  and Spring Festival lift the services reading in relevant months.

**Common pitfalls**:
- The composite number blends two very different sub-economies
  (services, construction) — always check the split.
- Services sub-index weighting favours government/SOE-linked services
  (logistics, telecoms, banking) over consumer-facing services —
  household-consumption reads should cross-check against retail sales
  and catering revenue.

---

## pmi-composite: NBS 综合 PMI 产出指数 / Official Composite PMI Output

- **Series code**: nbs_client (NBS new-SPA API)
- **Source**: 国家统计局 NBS + CFLP
- **Unit**: Index (50 = expansion/contraction dividing line)
- **Frequency**: Monthly
- **Publication lag**: Published on the last day of the reference month (jointly with Mfg + Non-Mfg PMI)
- **History**: From 2017 (~100 observations)

**What it measures**: A weighted composite of the manufacturing-
production sub-index and the non-manufacturing business-activity
sub-index, giving a single-number read of the whole-economy
cycle-phase. Weight construction mirrors the manufacturing vs services
GVA shares.

**How to interpret**:
- Above 50 → Overall economy expanding MoM. Composite > 52 signals
  clearly above-trend activity.
- Below 50 → Overall economy contracting — historically rare outside
  2020-02 COVID shock and brief 2022-Apr Shanghai lockdown drawdown.
- The gap between `pmi-composite` and the underlying `pmi-manufacturing`
  / `pmi-non-manufacturing` reveals which side (goods vs services) is
  driving the headline direction.

**Market significance**: ⭐⭐
Less market-moving than the headline manufacturing PMI because it is
a derived aggregate, but widely cited in official commentary as the
whole-economy 景气 reading. Useful cross-check against the monthly
GDP-proxy trio (industrial + retail + FAI + services-production).

**When to use**: Single-number whole-economy cycle read; confirmation
signal for regime-shift calls; cross-reference with monthly GDP proxy.

---

## caixin-mfg-pmi: Caixin 制造业 PMI / Caixin Manufacturing PMI

- **Series code**: akshare:index_pmi_man_cx (column: 制造业PMI)
- **Source**: Caixin + S&P Global (previously IHS Markit, partnership
  since 2015 — replaced the earlier HSBC/Markit China Manufacturing PMI)
- **Unit**: Index (50 = expansion/contraction dividing line)
- **Frequency**: Monthly
- **Publication lag**: 1st business day of the following month
- **History**: From 2014-04 (140+ observations)

**What it measures**: Survey of ~430 purchasing managers at private
manufacturing firms across China, concentrated in SMEs and export-
oriented private enterprises. Composite of new orders, output,
employment, supplier delivery times, and inventories. The Caixin
sample is materially smaller than NBS (≥ 3000) but sector- and
ownership-skewed differently, making it the "private economy" proxy.

**How to interpret**: Same diffusion-index convention as NBS. Above 52
meaningfully expansionary, below 50 meaningfully contractionary. The
**Caixin vs NBS delta** (see bottom section) is itself a diagnostic
signal.

**Market significance**: ⭐⭐⭐
Released 1st business day after month-end, one day ahead of NBS
release-timing convention historically — it frequently sets the
market-open tone for the month. Given SME / export-oriented sample
bias, Caixin PMI often **leads NBS by 1-2 months** around regime
turning points.

**When to use**: Private-sector manufacturing cycle read; cross-check
against NBS official PMI; early warning at turning points; export
demand diagnostic (given sample bias toward exporters).

---

## caixin-svc-pmi: Caixin 服务业 PMI / Caixin Services PMI

- **Series code**: akshare:index_pmi_ser_cx (column: 服务业PMI)
- **Source**: Caixin + S&P Global
- **Unit**: Index (50 = expansion/contraction dividing line)
- **Frequency**: Monthly
- **Publication lag**: 3rd business day of the following month
- **History**: From 2014-04 (140+ observations)

**What it measures**: Survey of ~400 purchasing managers at private
services firms — transport, retail, hospitality, consumer services,
business services. Private-sector concentrated, distinct from NBS
non-manufacturing PMI which blends services + construction and leans
SOE/government-linked.

**How to interpret**: Same diffusion-index convention. Above 52
expansionary; below 50 contractionary. A Caixin Services reading well
above NBS Non-Mfg composite indicates private consumer/services
vitality ahead of SOE/infrastructure cycle.

**Market significance**: ⭐⭐
Primary private-sector services read; useful complement to Caixin Mfg
PMI to triangulate the private economy. Moves consumer-discretionary
and services names in HK/mainland equity markets.

**When to use**: Private-sector services recovery tracking; consumer-
discretionary sector timing; cross-check with NBS non-mfg split
(services sub-index vs construction sub-index); post-COVID reopening
narrative.

---

## Caixin vs NBS methodology delta

**Sample composition**:

| Attribute | NBS 官方 | Caixin / S&P Global |
|-----------|---------|---------------------|
| Sample size | ≥ 3000 firms (mfg) + 4000 (non-mfg) | ~430 firms (mfg) + ~400 (services) |
| Ownership skew | Large + SOE concentrated | SME + 民营 (private) concentrated |
| Export orientation | Broad (SOE + domestic heavy industry) | Export-oriented manufacturers over-weighted |
| Surveyor | NBS + CFLP (中国物流与采购联合会) | Caixin + S&P Global (since 2015) |
| Release cadence | Last day of reference month | 1st business day (mfg) / 3rd business day (svc) |

**Divergence as signal**:

- **NBS > Caixin**: State-sector strength (SOE infrastructure demand,
  preferential credit to large firms, policy-bank lending). Common
  during stimulus-led recovery phases. Example: 2023-2024 property-
  downturn phase, state infrastructure offsetting private-sector
  weakness.

- **NBS < Caixin**: Private-sector / export demand ahead of
  SOE/infrastructure cycle. Common in early external-demand recoveries
  or when SME-facing easing (SME loan quotas, LPR cuts) bites faster
  than SOE pipeline. Example: late-2016 export recovery.

- **Lead-lag relationship**: Caixin tends to **lead NBS by 1-2 months**
  around regime turning points because SME purchasing-manager
  decision cycles respond faster to order-book changes than SOE
  planning cycles. Not deterministic — confirm with 3-month rolling
  average.

**Historical regime shifts**:

- **2015 匯改 (8·11 devaluation aftermath)**: Caixin Mfg PMI broke
  below 50 in mid-2015 and stayed sub-50 for 9 months; NBS held
  just above 50 for longer. Private-sector export competitiveness
  pressure visible in Caixin first.
- **2020-02 COVID shock**: Both indices hit historical lows
  synchronously — Caixin Mfg 40.3, NBS Mfg 35.7 in Feb 2020. The NBS
  trough was actually deeper due to larger-firm shutdown impact and
  Hubei concentration.
- **2022-04 Shanghai lockdown**: Caixin Mfg dropped to 46.0, NBS Mfg
  to 47.4 — Caixin again slightly weaker, reflecting private-SME and
  export-oriented firm pain in Yangtze River Delta.
- **2023-2025 property unwind**: Caixin Mfg oscillated 48-51, NBS
  Mfg 49-50 — the two converged around the 50 line as both state
  and private manufacturing stagnated under property-demand drag.
- **2024-2025 recovery**: Caixin rebounded faster in 2024-Q2 / 2025-Q1
  on external-demand pickup; NBS lagged by 1-2 months, consistent
  with SME-first cycle-turn interpretation.

**Cross-reference**: For regime-phase signal classification, see
`thresholds-china.md` in the `macro-regime-snapshot` skill.

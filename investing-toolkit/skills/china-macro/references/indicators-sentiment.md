# Sentiment / 景气 (PMI)

---

## pmi-manufacturing: NBS 制造业 PMI / Official Manufacturing PMI

- **Series code**: akshare:macro_china_pmi (column: 制造业-指数)
- **Source**: 国家统计局 NBS (National Bureau of Statistics) + 中国物流与采购联合会 CFLP via akshare
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

- **Series code**: akshare:macro_china_pmi (column: 非制造业-指数)
- **Source**: 国家统计局 NBS + CFLP via akshare
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

## pmi-caixin-manufacturing: 财新制造业 PMI / Caixin Manufacturing PMI

- **Series code**: akshare:macro_china_cx_pmi_yearly (via investing.com calendar mirror)
- **Source**: Caixin Media + S&P Global (previously IHS Markit) via akshare
- **Unit**: Index (50 = expansion/contraction dividing line)
- **Frequency**: Monthly
- **Publication lag**: Published on the first business day of the following month (one day after NBS PMI)
- **History**: From 2011 under Caixin branding (earlier HSBC PMI history available)

**What it measures**: Manufacturing PMI from a survey of ~500
manufacturers, conducted by S&P Global on behalf of Caixin. Smaller
sample than NBS but skewed toward private, export-oriented, and SME
manufacturers — the "private economy" cross-check to the official
(SOE-tilted) NBS reading.

**How to interpret**:
- Above 50 → Private-sector manufacturing expanding. More sensitive
  to external demand than NBS.
- Caixin < NBS → Private firms stressed more than SOEs. Typically
  reflects credit allocation bias toward SOEs, preferential SOE
  infrastructure demand, or export weakness.
- Caixin > NBS → Unusual; typically signals export pickup ahead of
  SOE/infrastructure recovery.

**Market significance**: ⭐⭐⭐
Often more market-moving than NBS PMI for international investors
because it captures the private-sector and export-oriented segments
that matter most for the China growth story. Moves CSI 300, Hang
Seng, and industrial metals.

**When to use**: Private-sector manufacturing tracking, export-
orientation signals, SOE vs POE divergence analysis, global
goods-cycle reads.

**China-specific context**:
- The NBS-Caixin divergence (官方 vs 财新) is itself one of the most
  watched macro signals. A sustained gap of 2+ points implies a
  two-track economy: state-led investment vs private demand.
- Prior history as "HSBC PMI" (pre-2015) and "HSBC/Markit PMI" creates
  branding confusion — the series is continuous but the sponsoring
  media company changed.
- The S&P Global methodology is aligned with the global PMI family
  (eurozone, UK, US), making Caixin PMI the natural comparable for
  cross-country reads.

**Common pitfalls**:
- The akshare mirror for this series pulls from investing.com's free
  calendar feed and can be **~8 months stale** during maintenance
  gaps. For same-day reads, check Caixin's own English-language press
  release.
- Small sample (~500 firms vs 3,000+ for NBS) means higher single-month
  noise. Use 3-month averages for trend reads.
- The survey over-represents coastal export hubs — inland manufacturing
  conditions may be worse than the Caixin reading suggests.

---

## pmi-caixin-services: 财新服务业 PMI / Caixin Services PMI

- **Series code**: akshare:macro_china_cx_services_pmi_yearly (via investing.com calendar mirror)
- **Source**: Caixin Media + S&P Global via akshare
- **Unit**: Index (50 = expansion/contraction dividing line)
- **Frequency**: Monthly
- **Publication lag**: Published on the third business day of the following month (two days after Caixin manufacturing PMI)
- **History**: From 2005 (220+ observations)

**What it measures**: Services PMI from a survey of ~400 private
service-sector companies. Captures transportation, real estate,
financial services, IT, consumer services, and business services.
Private-sector counterpart to the NBS non-manufacturing services
component.

**How to interpret**:
- Above 50 → Private services expanding. Positive for consumer
  discretionary, internet platforms (Meituan, JD services), logistics.
- Below 50 → Private services contracting. Typically signals consumer
  confidence erosion.
- Services readings have generally held above 50 in 2024-2025 even
  when manufacturing was weak, reflecting catering and travel
  recovery — the "K-shaped" post-covid pattern.

**Market significance**: ⭐⭐
Important services-side read. Moves Chinese internet and consumer
equities but less widely watched than Caixin manufacturing. Combined
with Caixin manufacturing, forms the Caixin Composite PMI (watched
alongside JPMorgan Global Services PMI).

**When to use**: Chinese consumer-services tracking, internet-platform
demand signals, services-recovery narrative construction.

**China-specific context**:
- Services sub-economy in China has been relatively resilient in
  2024-2025 even as manufacturing and property weakened — this series
  reflects that resilience.
- Coverage of internet-economy services (food delivery, ride-hailing)
  is limited — direct platform data is more granular.

**Common pitfalls**:
- Same ~8 month staleness caveat for the akshare/investing.com route.
- The services PMI and the NBS non-manufacturing services component
  are not directly comparable — different samples, different weights.
- Services-PMI strength co-existing with retail-sales weakness during
  2024-2025 highlighted the goods-vs-services divide in Chinese
  consumption — do not infer retail strength from services PMI alone.

---

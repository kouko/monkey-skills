# Inflation / 물가

---

## cpi: 소비자물가 총지수 / Consumer Price Index

- **Series code**: K401 (ECOS-KEYSTAT)
- **Source**: Bank of Korea (Statistics Korea data) via FinanceDataReader
- **Unit**: Index (base year 2020 = 100)
- **Frequency**: Monthly
- **Publication lag**: ~3-4 weeks after reference month (released around 2nd-3rd of following month)
- **History**: From 1965 (735 observations)

**What it measures**: The broadest measure of consumer price inflation in
Korea, covering food, housing, transportation, education, medical care,
and other goods and services. Headline CPI as compiled by Statistics Korea
(통계청).

**How to interpret**:
- Rising (accelerating YoY) → Inflation broadening. May prompt BOK to
  consider tightening. Negative for duration assets (bonds), pressures
  consumer purchasing power.
- Falling (decelerating YoY) → Disinflation. Opens room for BOK to hold
  or ease. Positive for bonds and equity valuations.

**Market significance**: ⭐⭐⭐
Korea's primary inflation gauge. The BOK targets CPI inflation at 2% YoY
(explicit inflation targeting since 1998). CPI exceeding 3% triggers
heightened BOK vigilance. The release moves KOSPI, KTB yields, and KRW.

**When to use**: Investment Clock inflation axis, BOK policy prediction (2% target), real return calculation, purchasing power analysis.

**Korea-specific context**:
- Korea adopted inflation targeting in 1998 after the Asian Financial Crisis.
  The current target is 2% (since 2016), aligned with major central banks.
- Korea's CPI basket is revised every 5 years based on the Household Income
  and Expenditure Survey. Current base year: 2020 = 100.
- Korea's "core CPI" definition: excludes agricultural products and petroleum
  products (농산물및석유류). This differs from:
  - **US core CPI**: Excludes all food and energy
  - **Japan core CPI**: Excludes fresh food only (生鮮食品)
  - **Taiwan core CPI**: Excludes fruits, vegetables, and energy (蔬果及能源)
- Government-administered prices (electricity, gas, public transport) can
  suppress CPI temporarily. Korea has used electricity price freezes during
  commodity price surges.

**Common pitfalls**:
- ECOS KEYSTAT provides index levels, not YoY rates. Compute YoY yourself:
  `(current / year_ago - 1) * 100`.
- Base year changes (every 5 years) create level discontinuities but YoY
  rates are continuous.
- Korean CPI is published by Statistics Korea (통계청) but distributed via
  BOK ECOS. The publishing agency is Statistics Korea, not the BOK.

---

## core-cpi: 근원 CPI / Core CPI (농산물및석유류제외)

- **Series code**: K405 (ECOS-KEYSTAT)
- **Source**: Bank of Korea (Statistics Korea data) via FinanceDataReader
- **Unit**: Index (same base as headline CPI)
- **Frequency**: Monthly
- **Publication lag**: Same as headline CPI
- **History**: From 1975 (615 observations)

**What it measures**: CPI excluding agricultural products and petroleum
products (농산물및석유류). Strips out the most volatile components to
reveal underlying inflation trend.

**How to interpret**:
- Rising → Underlying inflation pressure building. Stronger signal than
  headline CPI for sustained price pressures. This is what the BOK watches
  most closely for policy decisions.
- Falling → Underlying inflation cooling. Important for BOK policy outlook.

**Market significance**: ⭐⭐⭐
More relevant than headline CPI for monetary policy analysis because it
removes weather-driven agricultural price volatility and global oil price
pass-through. The BOK explicitly references core CPI in policy statements.

**When to use**: Underlying inflation trend assessment, BOK policy reaction function input, cross-country core CPI comparison (note different exclusion definitions per country).

**Korea-specific context**:
- Korea's core CPI excludes **agricultural products** (농산물) broadly and
  **petroleum products** (석유류), not all food and energy. Processed food,
  dining out, electricity, and gas remain in core CPI.
- This definition reflects Korea's susceptibility to: (1) seasonal
  agricultural price swings (monsoon/typhoon-driven), and (2) global oil
  price volatility (Korea imports ~97% of its energy).

**Common pitfalls**:
- Korea "core CPI" ≠ US "core CPI" ≠ Japan "core CPI" ≠ Taiwan "core CPI".
  Cross-country core CPI comparisons require understanding the different
  exclusion definitions.
- Index levels, not YoY rates. Same caveat as headline CPI.

---

## ppi: 생산자물가 총지수 / Producer Price Index

- **Series code**: K402 (ECOS-KEYSTAT)
- **Source**: Bank of Korea via FinanceDataReader
- **Unit**: Index (base year 2020 = 100)
- **Frequency**: Monthly
- **Publication lag**: ~4 weeks after reference month
- **History**: From 1965 (734 observations)

**What it measures**: Price changes at the producer/wholesale level in
Korea. Covers domestically produced goods and services at the first
commercial transaction point.

**How to interpret**:
- Rising → Upstream cost pressure. Leads CPI by 2-4 months as wholesale
  prices transmit to retail prices. Signals margin pressure for downstream
  businesses.
- Falling → Upstream disinflation. Eases cost pressure, positive for
  corporate margins.

**Market significance**: ⭐⭐
Leading indicator for CPI. Less market-moving than CPI itself, but
important for understanding the inflation pipeline. Korea's PPI is heavily
influenced by imported raw material prices and the KRW/USD exchange rate.

**When to use**: CPI leading indicator (2-4 month lead), corporate margin pressure assessment, upstream cost tracking, yen/won depreciation pass-through analysis.

**Korea-specific context**:
- Korea imports ~97% of its energy and a significant share of raw materials
  and intermediate goods. PPI is therefore highly correlated with global
  commodity prices and KRW/USD.
- The PPI-to-CPI transmission is partially dampened by government price
  controls on electricity and gas. The Korea Electric Power Corporation
  (KEPCO) has absorbed massive losses during commodity price surges to
  limit CPI impact.
- PPI includes services since the 2015 revision, making it broader than
  older versions that covered only goods.

**Common pitfalls**:
- PPI is more volatile than CPI. Monthly swings are common and may not
  indicate a trend change.
- PPI reflects producer prices, not consumer prices. The correlation with
  CPI depends on pricing power and government price controls.

---

## import-pi: 수입물가 총지수 / Import Price Index

- **Series code**: K403 (ECOS-KEYSTAT)
- **Source**: Bank of Korea via FinanceDataReader
- **Unit**: Index (base year 2020 = 100)
- **Frequency**: Monthly
- **Publication lag**: ~3-4 weeks after reference month
- **History**: From 1965

**What it measures**: Price changes of imported goods into Korea, denominated
in KRW. Captures the combined effect of global commodity prices, KRW/USD
exchange rate movements, and global trade conditions.

**How to interpret**:
- Rising → Imported cost pressure building. Higher input costs for Korea's
  manufacturing sector. Often driven by KRW depreciation, rising oil prices,
  or global supply chain disruptions.
- Falling → Imported deflation. Eases input costs. Can reflect KRW
  appreciation, falling commodity prices, or weak global demand.

**Market significance**: ⭐⭐
Korea is a major importer of energy and raw materials. Import prices are
a critical input to margin analysis for Korean manufacturers and a leading
indicator for PPI.

**When to use**: Import cost pressure monitoring, KRW pass-through analysis, commodity price impact assessment, manufacturing input cost tracking.

**Korea-specific context**:
- Korea's import mix is heavily weighted toward crude oil and gas (~25%),
  semiconductors and electronics (~20%), and raw materials/chemicals.
- KRW depreciation directly amplifies import price pressure. The BOK
  watches import prices as part of its "exchange rate pass-through" analysis.
- Samsung, SK Hynix, and Hyundai/Kia are both major exporters and importers
  (importing components and raw materials). Margins depend on the export
  PI / import PI ratio.

**Common pitfalls**:
- The index is KRW-denominated. Disentangling FX effects from underlying
  global price changes requires cross-referencing with the KRW/USD rate.
- Import price spikes during oil shocks can be dramatic but transitory.

---

## export-pi: 수출물가 총지수 / Export Price Index

- **Series code**: K404 (ECOS-KEYSTAT)
- **Source**: Bank of Korea via FinanceDataReader
- **Unit**: Index (base year 2020 = 100)
- **Frequency**: Monthly
- **Publication lag**: ~3-4 weeks after reference month
- **History**: From 1965

**What it measures**: Price changes of exported goods from Korea, denominated
in KRW. Reflects Korea's export competitiveness and global demand conditions
for key exports (semiconductors, automobiles, ships, petrochemicals).

**How to interpret**:
- Rising → Korea's exports fetching higher prices. Can reflect strong global
  demand, supply constraints, or KRW depreciation.
- Falling → Export pricing power weakening. Can signal inventory glut,
  competitive pressure, or global demand slowdown.

**Market significance**: ⭐⭐
Korea is the world's leading exporter of memory semiconductors, a top-5
shipbuilder, and a major auto exporter. Export price trends signal the
health of Korea's dominant industries.

**When to use**: Export competitiveness tracking, terms of trade computation, semiconductor pricing cycle signal, KRW impact on export revenue.

**Korea-specific context**:
- The terms of trade (export PI / import PI) is a key metric. Improving
  terms of trade → more purchasing power per unit exported.
- Semiconductor prices (DRAM, NAND) are a major driver of Korea's export
  price index. The semiconductor supercycle directly impacts this index.
- Korean shipbuilders receive orders denominated in USD. KRW appreciation
  compresses export PI in KRW terms even when USD prices are stable.

**Common pitfalls**:
- Export PI captures average price across all exports. Semiconductor pricing
  can be masked by stable or declining prices in other categories.
- Korea's export structure is concentrated: top-5 categories (semiconductors,
  autos, ships, petrochemicals, steel) account for ~60% of total exports.

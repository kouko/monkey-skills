# Inflation / 物價系

---

## cpi: 消費者物價指數 Consumer Price Index

- **Preset**: cpi
- **Source**: DGBAS (主計總處) — `cpispl.xls`
- **Unit**: Index (base year varies; current base = 105 年 / 2016 = 100)
- **Frequency**: Monthly
- **Publication lag**: ~3-4 weeks after reference month (released around 5th of each month)
- **URL**: `https://ws.dgbas.gov.tw/001/Upload/463/relfile/10315/2649/cpispl.xls`

**What it measures**: The broadest measure of consumer price inflation in
Taiwan, covering food, clothing, housing, transportation, medical care,
education, and other goods and services. Headline CPI.

**How to interpret**:
- Rising (accelerating YoY) → Inflation broadening. May prompt CBC to
  consider tightening. Negative for duration assets (bonds), pressures
  consumer purchasing power.
- Falling (decelerating YoY) → Disinflation. Opens room for CBC to hold
  or ease. Positive for bonds and equity valuations.

**Market significance**: ⭐⭐⭐
Taiwan's primary inflation gauge. The CBC monitors CPI closely when making
rate decisions, though Taiwan's inflation has historically been lower and
more stable than in the US or Japan. CPI exceeding 3% YoY is considered
unusually high for Taiwan and triggers policy discussion.

**Taiwan-specific context**:
- Taiwan's CPI is compiled using ROC calendar (民國年). The Excel file
  uses 民國年 in the first column. Conversion: 民國年 + 1911 = 西元年.
- Taiwan's "core CPI" definition differs from both the US and Japan:
  - **Taiwan core CPI**: Excludes fruits, vegetables, and energy (蔬果及能源)
  - **US core CPI**: Excludes food and energy
  - **Japan core CPI**: Excludes fresh food only (生鮮食品)
- Taiwan's relatively stable CPI reflects government price controls on
  utilities (electricity, water, gas) and administered prices for public
  transportation. These dampen CPI volatility but can create delayed
  adjustment when decontrolled.

**Common pitfalls**:
- The Excel file contains index levels, not YoY rates. You must compute
  YoY percentage change yourself: `(current / year_ago - 1) * 100`.
- Base year changes can create discontinuities. Check which base year
  the current series uses.
- Taiwan's CPI basket weights differ significantly from US/Japan. Housing
  weight is lower (rent is relatively stable) and food weight is higher.
- Government-administered prices (electricity, water) can create artificial
  CPI suppression followed by catch-up spikes when prices are adjusted.

---

## core-cpi: 核心CPI Core CPI (不含蔬果及能源)

- **Preset**: core-cpi
- **Source**: DGBAS (主計總處) — `cpisplexvfe.xls`
- **Unit**: Index (same base as headline CPI)
- **Frequency**: Monthly
- **Publication lag**: ~3-4 weeks after reference month
- **URL**: `https://ws.dgbas.gov.tw/001/Upload/463/relfile/10315/2649/cpisplexvfe.xls`

**What it measures**: CPI excluding fruits, vegetables, and energy (蔬果及能源).
Strips out the most volatile components to reveal underlying inflation trend.

**How to interpret**:
- Rising → Underlying inflation pressure building. Stronger signal than
  headline CPI for sustained price pressures.
- Falling → Underlying inflation cooling. Important for CBC policy outlook.

**Market significance**: ⭐⭐⭐
More relevant than headline CPI for monetary policy analysis because it
removes weather-driven food volatility and global energy price pass-through.
The CBC references core CPI in its policy statements.

**Taiwan-specific context**:
- Taiwan's core CPI excludes **fruits and vegetables** (蔬果) specifically,
  not all food. Processed food, dining out, and meat remain in core CPI.
  This reflects Taiwan's susceptibility to typhoon-driven produce price
  spikes — a seasonal pattern that is noise, not signal.
- Energy exclusion covers gasoline, natural gas, and electricity. Since
  Taiwan is a net energy importer, global oil price swings can dominate
  headline CPI but are temporary pass-throughs.

**Common pitfalls**:
- Same as headline CPI: index levels, not rates; ROC calendar; base year.
- Taiwan "core CPI" ≠ US "core CPI" ≠ Japan "core CPI". Do not compare
  directly across countries without understanding the exclusion differences.

---

## ppi: 躉售物價指數 Producer Price Index (WPI)

- **Preset**: ppi
- **Source**: DGBAS (主計總處) — `ppispl.xls`
- **Unit**: Index (base year varies)
- **Frequency**: Monthly
- **Publication lag**: ~3-4 weeks after reference month
- **URL**: `https://ws.dgbas.gov.tw/001/Upload/463/relfile/10315/2649/ppispl.xls`

**What it measures**: Wholesale/producer price index measuring price changes
of goods at the wholesale level. Taiwan officially calls this 躉售物價指數
(Wholesale Price Index), which is functionally equivalent to PPI.

**How to interpret**:
- Rising → Upstream cost pressure. Leads CPI by 3-6 months as wholesale
  prices transmit to retail prices. Signals margin pressure for downstream
  businesses.
- Falling → Upstream disinflation. Eases cost pressure, positive for
  corporate margins.

**Market significance**: ⭐⭐
Leading indicator for CPI. Less market-moving than CPI itself, but important
for understanding the inflation pipeline. Taiwan's PPI is heavily influenced
by imported commodity prices due to the economy's dependence on imported raw
materials and energy.

**Taiwan-specific context**:
- Taiwan imports ~98% of its energy and a large share of raw materials.
  PPI is therefore highly correlated with global commodity prices and the
  TWD/USD exchange rate. TWD depreciation → higher import costs → higher PPI.
- The PPI-to-CPI transmission is dampened by government price controls on
  utilities. PPI can spike while CPI remains subdued if the government
  absorbs the cost (e.g., Taiwan Power Company absorbing fuel cost increases).

**Common pitfalls**:
- PPI reflects wholesale goods prices only, not services. Taiwan's service
  sector (~60% of GDP) is not captured.
- The Excel file uses the same ROC calendar format as CPI.
- PPI is more volatile than CPI. Monthly swings of 1-2% are common and
  may not indicate a trend change.

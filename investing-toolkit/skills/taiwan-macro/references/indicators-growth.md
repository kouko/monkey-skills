# Growth / 成長系

---

## gdp-growth: 經濟成長率 GDP Growth Rate YoY%

- **Preset**: gdp-yoy
- **Source**: statgov (stat.gov.tw sid=t.1)
- **Unit**: Percent (%) — year-over-year growth rate
- **Frequency**: Quarterly
- **Publication lag**: ~6 weeks after quarter-end (advance estimate)
- **History**: 260 points from 1962Q1

**What it measures**: Taiwan's real GDP growth rate, year-over-year. The
definitive measure of economic expansion or contraction.

**How to interpret**:
- Rising (accelerating growth) → Economy strengthening. Supports corporate
  earnings and risk assets. Taiwan's trend growth rate is ~2-3%.
- Falling (decelerating growth) → Economy slowing. Growth below 2% signals
  meaningful deceleration. Negative growth is rare for Taiwan outside of
  global recessions.

**Market significance**: ⭐⭐⭐
Taiwan's GDP is the ultimate measure of economic performance, but quarterly
frequency and long publication lag reduce its real-time utility. Higher-frequency
proxies (IPI, exports, the NDC signal) often move markets before GDP confirms.
The advance estimate still generates headlines and affects CBC policy outlook.

**Taiwan-specific context**:
- Taiwan's GDP is heavily driven by exports (~70% of GDP) and particularly
  semiconductor manufacturing. A global chip demand cycle is effectively a
  Taiwan GDP cycle.
- GDP composition: services ~60%, industry ~35%, agriculture ~2%. Within
  industry, electronics manufacturing dominates.
- The stat.gov.tw data includes quarterly GDP since 1962Q1, providing
  the full post-war economic history.
- DGBAS releases multiple GDP estimates: advance (概估), revised (修正),
  and forecast (預測). The stat.gov.tw page reflects the latest published
  estimate for each quarter.

**Common pitfalls**:
- stat.gov.tw extracts data from a Highcharts hidden field, not a
  documented API. If the page redesigns, this could break.
- GDP growth rates are YoY, not QoQ annualized (which the US uses). Do not
  directly compare Taiwan YoY with US SAAR.
- Base effects from pandemic quarters (2020-2021) can distort YoY comparisons.

---

## import-pi: 進口物價指數 Import Price Index

- **Preset**: import-pi
- **Source**: DGBAS (主計總處) — `ipispl.xls`
- **Unit**: Index (base year varies)
- **Frequency**: Monthly
- **Publication lag**: ~3-4 weeks after reference month
- **URL**: `https://ws.dgbas.gov.tw/001/Upload/463/relfile/10315/2649/ipispl.xls`

**What it measures**: Price changes of imported goods into Taiwan, denominated
in NTD. Captures the combined effect of global commodity prices, foreign
exchange rate movements, and global trade conditions.

**How to interpret**:
- Rising → Imported cost pressure building. Signals higher input costs for
  Taiwan's manufacturing sector and potential PPI/CPI pressure downstream.
  Often driven by TWD depreciation, rising oil prices, or global supply
  chain bottlenecks.
- Falling → Imported deflation. Eases input costs. Can reflect TWD
  appreciation, falling commodity prices, or weak global demand.

**Market significance**: ⭐⭐
Important for understanding cost pressure on Taiwan's export-manufacturing
economy. Taiwan imports nearly all raw materials and energy, making this
index a critical input to margin analysis for the manufacturing sector.

**Taiwan-specific context**:
- Taiwan's import mix is heavily weighted toward intermediate goods and raw
  materials (semiconductors materials, petrochemicals, machinery parts,
  crude oil). Consumer goods imports are a smaller share.
- The index is NTD-denominated, so TWD/USD movements directly affect import
  prices. A 1% TWD depreciation roughly translates to ~0.5-0.7% import
  price increase, depending on the trade-weighted currency basket.

**Common pitfalls**:
- Import prices reflect a mix of volume and price effects. During global
  recessions, both import volumes and prices fall — the index captures
  only the price component.
- The transmission from import prices → PPI → CPI has variable lags
  (1-6 months depending on the commodity).

---

## export-pi: 出口物價指數 Export Price Index

- **Preset**: export-pi
- **Source**: DGBAS (主計總處) — `epispl.xls`
- **Unit**: Index (base year varies)
- **Frequency**: Monthly
- **Publication lag**: ~3-4 weeks after reference month
- **URL**: `https://ws.dgbas.gov.tw/001/Upload/463/relfile/10315/2649/epispl.xls`

**What it measures**: Price changes of exported goods from Taiwan, denominated
in NTD. Reflects Taiwan's export competitiveness and global demand conditions
for Taiwan's key exports (semiconductors, electronics, machinery).

**How to interpret**:
- Rising → Taiwan's exports fetching higher prices. Can reflect strong global
  demand, supply constraints (e.g., semiconductor shortages), or TWD
  depreciation making exports cheaper in foreign currency (but more expensive
  in NTD terms).
- Falling → Export pricing power weakening. Can signal inventory glut,
  competitive pressure, or global demand slowdown.

**Market significance**: ⭐⭐
Taiwan is the world's largest semiconductor foundry (TSMC) and a major
electronics exporter. Export price trends signal the health of Taiwan's
dominant industry and have implications for global tech supply chains.

**Taiwan-specific context**:
- Export prices are heavily weighted toward electronics and semiconductors.
  Global semiconductor cycle upswings drive export prices higher; downswings
  create deflationary pressure.
- The terms of trade (export PI / import PI ratio) is a key metric for
  Taiwan's economy. Improving terms of trade → more purchasing power per
  unit exported. Worsening terms of trade → squeezed margins for exporters.
- Export prices vs. USD-denominated global chip prices: The NTD-denominated
  index reflects both global pricing and currency effects. For pure
  semiconductor pricing trends, cross-reference with DRAM/NAND spot prices.

**Common pitfalls**:
- Export PI captures average price across all exports, not specific products.
  Semiconductor pricing can be masked by declining prices in other categories.
- Taiwan's export structure is highly concentrated — TSMC alone accounts for
  a significant share of total exports. Company-specific factors can move
  the aggregate index.

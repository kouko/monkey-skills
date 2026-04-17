# Business Cycle / 景氣系

---

## signal: 景氣對策信號 / Business Cycle Monitoring Indicator (景氣燈號)

- **Series code**: 景氣指標與燈號.csv (NDC ZIP)
- **Source**: NDC (國發會) — ZIP download from `ws.ndc.gov.tw`
- **Unit**: Composite score (9-45 range) + Color signal
- **Frequency**: Monthly
- **Publication lag**: ~6 weeks after reference month
- **History**: From 1984 (monthly)

**What it measures**: Taiwan's official business cycle monitoring system,
managed by the National Development Council. A composite score derived from
9 economic indicators is mapped to a five-color traffic light system:

| Score | Color | Signal | Meaning |
|-------|-------|--------|---------|
| 38-45 | 紅 Red | 熱絡 Hot | Economy overheating; tightening may be needed |
| 32-37 | 黃紅 Yellow-Red | 趨熱 Warming | Economy expanding strongly |
| 23-31 | 綠 Green | 穩定 Stable | Economy in healthy equilibrium |
| 17-22 | 黃藍 Yellow-Blue | 趨弱 Cooling | Economy showing signs of slowdown |
| 9-16 | 藍 Blue | 低迷 Sluggish | Economy in downturn; stimulus may be needed |

**How to interpret**:
- Score rising toward red → Overheating risk. Historically associated with
  CBC tightening cycles and equity market peaks (with a lag).
- Score falling toward blue → Recessionary conditions. Associated with CBC
  easing and equity market troughs.
- Green zone → Goldilocks conditions. Typically the longest-sustained state.

**Market significance**: ⭐⭐⭐
Taiwan's most widely cited business cycle indicator. Monthly release is
front-page financial news in Taiwan. The traffic light metaphor makes it
accessible to policymakers, media, and the general public. The score is
used by government agencies for fiscal policy planning and by the CBC as
background context for monetary policy decisions.

**When to use**: Business cycle phase identification (traffic light system), Taiwan recession probability, Investment Clock phase mapping.

**Taiwan-specific context**:
- The 9 component indicators span monetary conditions (M1B), financial
  markets (TAIEX), real activity (IPI, exports, manufacturing sales), and
  labor (overtime hours). This breadth makes it a genuine composite signal.
- The NDC also publishes leading, coincident, and lagging composite indices
  alongside the signal. The leading index is the most forward-looking.
- Data history extends back to 1982, enabling long-term cycle analysis.

**Common pitfalls**:
- The signal is a lagging composite — by the time it turns red or blue, the
  economic conditions have been in place for months. Use the leading index
  for forward-looking analysis.
- The score boundaries (9-16 = blue, etc.) are fixed thresholds that may not
  reflect structural changes in the economy over decades.
- Publication lag of ~6 weeks means the signal reflects conditions from
  nearly two months ago.

---

## signal-components: 對策信號構成項目 / Signal Components

- **Series code**: 景氣指標與燈號.csv (NDC ZIP)
- **Source**: NDC (國發會) — `景氣對策信號構成項目.csv` inside ZIP
- **Frequency**: Monthly
- **History**: From 1984 (monthly)

**What it contains**: The 9 individual component indicators that compose
the business cycle signal score:

| Component | 中文 | Description |
|-----------|------|-------------|
| M1B | 貨幣總計數M1B | Narrow money supply |
| TAIEX | 股價指數 | Taiwan stock market index |
| IPI | 工業生產指數 | Industrial Production Index (2021=100) |
| Overtime | 工業及服務業加班工時 | Overtime hours worked |
| Exports | 海關出口值 | Customs export value |
| Machinery imports | 機械及電機設備進口值 | Machinery & equipment imports |
| Manufacturing sales | 製造業銷售量指數 | Manufacturing sales volume |
| Retail/food revenue | 批發零售及餐飲業營業額 | Wholesale, retail & food revenue |

**Market significance**: ⭐⭐
The components are individually useful as activity indicators. The IPI
component is particularly valuable as it provides the Industrial Production
Index that is otherwise difficult to obtain programmatically from MOEA.

**When to use**: Component-level cycle diagnosis, signal decomposition for sector analysis, leading vs lagging component identification.

**How to use**:
- Cross-reference individual components with their dedicated indicators
  when available (e.g., M1B with CBC M2, IPI with MOEA data).
- When the composite signal is in a transition zone, examining which
  components are driving the change reveals the nature of the cycle shift.
- The machinery & equipment imports component is a capex proxy similar
  to US DGORDER.

---

## leading: 領先指標構成項目 / Leading Indicator Components

- **Series code**: 景氣指標與燈號.csv (NDC ZIP)
- **Source**: NDC (國發會) — `領先指標構成項目.csv` inside ZIP
- **Frequency**: Monthly
- **History**: From 2003 (monthly)

**What it contains**: Components of the NDC Leading Composite Index:

| Component | 中文 |
|-----------|------|
| Export orders sentiment | 外銷訂單動向指數 |
| M1B | 貨幣總計數M1B |
| TAIEX | 股價指數 |
| Employment net entry | 工業及服務業受僱員工淨進入率 |
| Building permits floor area | 建築物開工樓地板面積 |
| SEMI B/B ratio | 半導體設備接單出貨比 |
| Manufacturing PMI-like | 製造業營業氣候測驗點 |

**Market significance**: ⭐⭐
The leading index typically turns 3-6 months before the coincident index.
The SEMI B/B ratio component is unique to Taiwan and reflects the
semiconductor cycle's outsized impact on the economy.

**When to use**: Leading indicator component analysis, cycle turning point prediction, sector-level forward guidance.

---

## leading-index: 景氣領先指標 / Leading Index ex-trend (不含趨勢)

- **Series code**: sid=t.11 (stat.gov.tw)
- **Source**: statgov (stat.gov.tw)
- **Unit**: Index (composite, trend-removed)
- **Frequency**: Monthly
- **Publication lag**: ~6 weeks after reference month

**What it measures**: The NDC's composite leading index with the long-term
trend removed, published via stat.gov.tw. This is the single-number summary
of the 7 leading indicator components (export orders sentiment, M1B, TAIEX,
employment net entry, building permits, SEMI B/B ratio, manufacturing
climate). Trend removal makes the index oscillate around zero, highlighting
cyclical turning points rather than secular growth.

**How to interpret**:
- Rising → Cyclical momentum building. The economy is expected to accelerate
  over the next 3-6 months. A sustained rise from trough signals a turning
  point from contraction to expansion.
- Falling → Cyclical momentum fading. The economy is expected to decelerate.
  A sustained decline from peak signals a turning point from expansion to
  contraction.
- Zero crossings are particularly significant as regime-change signals.

**Market significance**: ⭐⭐⭐
The most forward-looking single number in Taiwan's official business cycle
toolkit. The leading index turns before the coincident index and before the
signal score, making it the earliest official signal of cycle turning points.
Institutional investors and policymakers use it as a primary input for
forward-looking economic assessment.

**When to use**: Business cycle turning point prediction, recession probability assessment, Investment Clock phase transition signal.

**Taiwan-specific context**:
- The "ex-trend" (不含趨勢) version is preferred for cycle analysis because
  the raw leading index contains a secular upward trend that masks cyclical
  movements. The trend-removed version oscillates around zero.
- The stat.gov.tw version provides a longer history than the NDC's own
  download, and is easier to programmatically access.
- Cross-reference with the NDC leading indicator components (preset: leading)
  for decomposition of which sectors are driving the signal.

**Common pitfalls**:
- The leading index can produce false signals — a brief dip that reverses
  is not a turning point. Require 3+ consecutive months of directional change
  for a confirmed turning point.
- Publication lag means the "leading" signal is based on data from ~2 months
  ago. Combine with higher-frequency proxies (export orders, TAIEX) for
  real-time assessment.
- The trend-removal methodology can be revised, causing historical revisions.

---

## coincident-index: 景氣同時指標 / Coincident Index ex-trend (不含趨勢)

- **Series code**: sid=t.11 (stat.gov.tw)
- **Source**: statgov (stat.gov.tw)
- **Unit**: Index (composite, trend-removed)
- **Frequency**: Monthly
- **Publication lag**: ~6 weeks after reference month

**What it measures**: The NDC's composite coincident index with the long-term
trend removed, published via stat.gov.tw. Summarizes current economic
conditions by combining indicators that move in tandem with the business
cycle (IPI, electricity consumption, manufacturing sales, etc.). The
trend-removed version oscillates around zero.

**How to interpret**:
- Above zero and rising → Economy in expansion phase, momentum strengthening.
- Above zero and falling → Economy still expanding but momentum fading
  (late-cycle).
- Below zero and falling → Economy in contraction, conditions worsening.
- Below zero and rising → Economy still contracting but improvement beginning
  (early recovery).

**Market significance**: ⭐⭐
The coincident index confirms where the economy is right now (as of the
reference month). Less forward-looking than the leading index, but essential
for confirming that a cycle turn has actually occurred rather than being a
false signal. The NDC uses the coincident index as the primary input for
official recession dating.

**When to use**: Current cycle phase confirmation, recession dating, expansion vs contraction assessment.

**Taiwan-specific context**:
- The coincident index is what the NDC uses to officially determine business
  cycle peaks and troughs (equivalent to the NBER's role in the US).
- Comparing the leading index vs. coincident index gap reveals how far ahead
  or behind the cycle turn is. A widening gap (leading rising, coincident
  still falling) is a classic early-recovery signal.
- The stat.gov.tw source provides both leading and coincident on the same
  page (sid=t.11), ensuring synchronized data vintages.

**Common pitfalls**:
- The coincident index confirms, it does not predict. Do not use it for
  forward-looking investment decisions — use the leading index instead.
- Like all composite indices, it can be dominated by a few large components.
  In Taiwan's case, IPI and manufacturing heavily influence the result.
- Historical revisions can retroactively change the apparent timing of
  cycle turns.

---

## signal-score: 景氣燈號分數 / Business Cycle Signal Score

- **Series code**: sid=t.11 (stat.gov.tw)
- **Source**: statgov (stat.gov.tw)
- **Unit**: Score (9-45 range, integer)
- **Frequency**: Monthly
- **Publication lag**: ~6 weeks after reference month

**What it measures**: The same composite signal score as the NDC's traffic
light system (preset: signal), but sourced from stat.gov.tw for programmatic
access. The score is derived from 9 component indicators, each scored 1-5,
yielding a composite range of 9-45 mapped to the five-color system:
9-16 = Blue, 17-22 = Yellow-Blue, 23-31 = Green, 32-37 = Yellow-Red, 38-45 = Red.

**How to interpret**:
- Score rising → Economy strengthening. Cross color boundaries for regime
  signals (e.g., crossing from green 31 to yellow-red 32 is significant).
- Score falling → Economy weakening.
- The absolute score provides more granularity than the color alone — a score
  of 23 (low green) vs 31 (high green) tells a different story despite both
  being "stable."

**Market significance**: ⭐⭐⭐
This is the numeric version of Taiwan's most famous business cycle indicator.
The stat.gov.tw source enables automated threshold-based monitoring and
historical quantitative analysis that the NDC's ZIP download format makes
more difficult. Ideal for programmatic regime detection.

**When to use**: Quantitative cycle scoring (9-45 range), historical cycle comparison, automated threshold-based regime detection.

**Taiwan-specific context**:
- The stat.gov.tw version may have a slightly different publication timing
  than the NDC's own release. Cross-reference dates if precision matters.
- For automated monitoring, the score from stat.gov.tw is easier to parse
  than extracting from the NDC ZIP file. However, the NDC ZIP contains
  the official color classification which stat.gov.tw does not.
- Historical data extends back decades, enabling quantitative analysis of
  cycle durations, amplitudes, and transition patterns.

**Common pitfalls**:
- The score is a lagging composite — by the time it signals red or blue,
  the economic conditions have been in place for months. Always pair with
  the leading index for forward-looking context.
- The fixed thresholds (9-16, 17-22, etc.) have not been updated for
  structural changes in the economy. A score of 23 today may represent
  different conditions than 23 in 1990.
- The stat.gov.tw extraction depends on the page structure remaining stable.
  If the page redesigns, the parser may break.

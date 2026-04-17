# Business Cycle / 景氣系

---

## signal: 景氣對策信號 Business Cycle Monitoring Indicator (景氣燈號)

- **Preset**: signal
- **Source**: NDC (國發會) — ZIP download from `ws.ndc.gov.tw`
- **Unit**: Composite score (9-45 range) + Color signal
- **Frequency**: Monthly
- **Publication lag**: ~6 weeks after reference month
- **Download**: ZIP containing `景氣指標與燈號.csv`

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

## signal-components: 對策信號構成項目 Signal Components

- **Preset**: signal-components
- **Source**: NDC (國發會) — `景氣對策信號構成項目.csv` inside ZIP
- **Frequency**: Monthly

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

**How to use**:
- Cross-reference individual components with their dedicated indicators
  when available (e.g., M1B with CBC M2, IPI with MOEA data).
- When the composite signal is in a transition zone, examining which
  components are driving the change reveals the nature of the cycle shift.
- The machinery & equipment imports component is a capex proxy similar
  to US DGORDER.

---

## leading: 領先指標構成項目 Leading Indicator Components

- **Preset**: leading
- **Source**: NDC (國發會) — `領先指標構成項目.csv` inside ZIP
- **Frequency**: Monthly

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

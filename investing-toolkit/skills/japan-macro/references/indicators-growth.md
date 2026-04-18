# 成長系 / Growth

Japan macro indicators -- GDP, industrial production, and business cycle gauges.
Part of `japan-macro` skill. See `indicator-index.md` for full index.

---

## gdp: 国内総生産 GDP / Gross Domestic Product

- **Series code**: discover via search (統計DB, use `--cycle quarterly`)
- **Source**: 内閣府 (Cabinet Office)
- **Unit / 単位**: QoQ annualized % change or JPY trillions
- **Frequency / 頻度**: Quarterly
- **Publication lag / 公表遅延**: ~6 weeks (1st preliminary estimate / 速報)
- **History**: From 1994 (quarterly)

**What it measures / 経済的意味**:
(EN) The total inflation-adjusted value of goods and services produced in Japan. The definitive measure of whether the Japanese economy is expanding or contracting.
(JP) 日本国内で生産された財・サービスの実質総額。日本経済の拡大・縮小を判断する最も包括的な指標。

**How to interpret / 解読方法**:
- Rising (positive QoQ) / 上昇 → Economy expanding. Supports corporate earnings and risk assets. / 経済拡大。企業収益・リスク資産を支持。
- Falling (negative QoQ) / 下落 → Economy contracting. Two consecutive negative quarters is the informal recession definition. / 経済縮小。2四半期連続マイナスは非公式の景気後退定義。

**Market significance / 市場重要度**: ⭐⭐⭐
The definitive measure of Japan's economic performance. Quarterly GDP releases move JPY, Nikkei, JGBs. Revisions between 1st and 2nd preliminary estimates frequently flip the narrative.

**When to use / 使用場面**:
Investment Clock growth axis, GIP quadrant mapping, cycle positioning,
Japan allocation weight decisions.

**Japan-specific context / 日本固有の文脈**:
Japan's GDP is heavily influenced by net exports (trade-sensitive economy),
private consumption (which has been structurally weak due to aging demographics
and stagnant wages), and government spending. GDP revisions in Japan can be
significant -- the 1st preliminary and 2nd preliminary estimates sometimes
differ by over 1 percentage point annualized.

**Common pitfalls / よくある間違い**:
- Japan GDP is published in two rounds: 1st preliminary (速報, ~45 days after quarter-end) and 2nd preliminary (確報, ~75 days). Revisions can flip the sign.
- Must use `--cycle quarterly` with estat_client.py. Monthly cycle will return no data.
- Japan GDP deflator sometimes diverges significantly from CPI due to import price effects. Do not use interchangeably.
- Nominal GDP in Japan was flat for two decades (1995-2020), so real GDP understates the deflationary period's stagnation.

---

## ip: 鉱工業生産指数 / Industrial Production Index

- **Series code**: 0502070301000090010 (統計DB)
- **Source**: 経済産業省 (METI)
- **Unit / 単位**: Index (2020 base = 100), seasonally adjusted
- **Frequency / 頻度**: Monthly
- **Publication lag / 公表遅延**: ~6 weeks after reference month
- **History**: From 1978 (578 observations)

**What it measures / 経済的意味**:
(EN) The real output volume of Japan's mining and manufacturing sectors. A high-frequency cyclical indicator that tracks industrial activity and leads broader economic turning points.
(JP) 鉱業・製造業の実質生産量を測定。景気循環を高頻度で追跡する先行指標。

**How to interpret / 解読方法**:
- Rising / 上昇 → Industrial activity expanding. Positive for cyclical equities, machinery orders, and export-oriented sectors. / 鉱工業活動の拡大。循環株・機械受注・輸出関連セクターにポジティブ。
- Falling / 下落 → Industrial activity contracting. Signals potential recession if sustained 3+ months. / 鉱工業活動の縮小。3ヶ月以上持続すれば景気後退のシグナル。

**Market significance / 市場重要度**: ⭐⭐⭐
Japan's most important high-frequency growth indicator. Manufacturing is the engine of Japan's export economy. IP trends are highly correlated with Nikkei earnings revisions and yen direction.

**When to use / 使用場面**:
Investment Clock growth proxy (higher frequency than GDP), GIP quadrant
mapping, manufacturing cycle assessment, Japan export competitiveness gauge.

**Japan-specific context / 日本固有の文脈**:
Japan's manufacturing sector is globally integrated (auto, electronics,
machinery). IP is heavily influenced by global semiconductor demand cycles,
China's economy, and auto production schedules. Natural disasters (earthquakes,
typhoons) can cause sharp one-month drops that do not reflect underlying trend.

**Common pitfalls / よくある間違い**:
- METI publishes IP alongside a "production forecast survey" (製造工業生産予測調査) for the next 2 months. The forecast is systematically optimistic -- apply a downward adjustment.
- The 2020 base index absorbed COVID disruption into the base year. Compare trends, not absolute levels, when bridging pre/post base revision data.
- IP covers manufacturing and mining only, not services (the dominant majority of Japan's GDP, 約7割、2015–2024年安定推移). A services-led recovery can coexist with flat IP.

---

## 景気動向指数 CI 三件組 / Business Cycle Composite Index trio — Japan's monthly GDP proxy

The 景気動向指数 (Index of Business Conditions) published monthly by 内閣府
is the canonical **monthly GDP proxy** for Japan. Three CI (Composite Index)
series move together — leading (先行), coincident (一致), lagging (遅行).
All three share the same 2020 base and release cycle:

| Series | Preset | What it captures |
|--------|--------|------------------|
| 一致指数 | `coincident-index` | "Temperature right now" — definitive monthly read of Japan's current cycle position |
| 先行指数 | `leading-index` | ~6-9 months ahead of coincident — composed of forward-looking sub-indices |
| 遅行指数 | `lagging-index` | ~6 months after coincident — confirms the previous phase |

Cross-market parallels: matches us-macro's `nowcast` group (GDPNow / CFNAI /
WEI / OECD CLI) and china-macro's 三大數據 monthly package.

## coincident-index: 景気動向指数（一致指数）/ Composite Coincident Index — MONTHLY GDP PROXY

- **Series code**: 0706010500000090010 (統計DB)
- **Source**: 内閣府 (Cabinet Office)
- **Unit / 単位**: Index (2020 base = 100)
- **Frequency / 頻度**: Monthly
- **Publication lag / 公表遅延**: ~6-8 weeks after reference month
- **History**: From 1985 (494 observations)

**What it measures / 経済的意味**:
(EN) The definitive monthly GDP proxy for Japan. A composite of 10 sub-indicators
(industrial production, employment, retail sales, electricity consumption, etc.)
that move in tandem with the current phase of the business cycle. Cabinet Office
uses this index to formally date recessions and expansions.
(JP) 鉱工業生産・雇用・消費など10系列を合成した景気の同時指標。景気循環の現在地を示す
「体温計」として、内閣府が毎月公表する。月次 GDP 代理指標として国内マクロ分析の事実上の標準。

**How to interpret / 解読方法**:
- Rising / 上昇 → Economy is in an expansion phase. Business conditions improving across multiple sectors simultaneously. / 景気は拡大局面。複数セクターで同時に景況感が改善。
- Falling / 下落 → Economy is in a contraction phase. Weakness spreading across sectors. / 景気は後退局面。弱さが複数セクターに波及。

**Market significance / 市場重要度**: ⭐⭐
Official business cycle phase indicator. The Cabinet Office uses this index to formally date recessions and expansions. Useful for Investment Clock phase confirmation.

**When to use / 使用場面**:
Investment Clock growth axis (most direct proxy), business cycle phase confirmation,
cross-checking IP and GDP signals, GIP quadrant mapping.

**Japan-specific context / 日本固有の文脈**:
The Cabinet Office formally declares business cycle peaks and troughs based on
this index (with significant delay -- often 12+ months after the fact). The
coincident index uses 10 component series including IP, employment, retail sales,
and electricity consumption. Japan also publishes leading and lagging composite
indexes, but the coincident index is the headline for current conditions.

**Common pitfalls / よくある間違い**:
- The coincident index level is not directly comparable across base year revisions (2020 base vs. 2015 base). Compare trends within the same base period.
- Official business cycle dating by the Cabinet Office lags substantially. The index itself is timely, but the official "this was a recession" announcement comes much later.
- The 3-month moving average direction is more informative than single-month movements, which can be noisy.
- For REAL-TIME GDP nowcasting, pair with `leading-index` — 先行 leads 一致 by 6-9 months, so today's 先行 reading hints at where 一致 will be 2 quarters out.

---

## leading-index: 景気動向指数（先行指数）/ Composite Leading Index

- **Series code**: 0706010500000090020 (統計DB)
- **Source**: 内閣府 (Cabinet Office)
- **Unit / 単位**: Index (2020 base = 100)
- **Frequency / 頻度**: Monthly
- **Publication lag / 公表遅延**: ~6-8 weeks after reference month (released together with 一致 and 遅行)
- **History**: From 1985

**What it measures / 経済的意味**:
(EN) A composite of 11 forward-looking sub-series (new housing starts, real estate loans,
consumer expectations, stock prices, inventory ratios, etc.) designed to turn 6-9 months
before the coincident index. Cabinet Office's canonical leading indicator for Japan.
(JP) 新設住宅着工、不動産向け新規貸出、消費者態度指数、株価、在庫率など11系列を合成した先行指標。
景気動向指数（一致）の転換点に6-9ヶ月先行するよう設計されている。

**How to interpret / 解読方法**:
- Rising / 上昇 → 6-9 months out, the coincident index (and GDP) likely rises. Supportive of risk assets. / 6-9ヶ月先の景気拡大を示唆。リスク資産にプラス。
- Falling / 下落 → 6-9 months out, likely contraction. Early-warning signal for recession. / 6-9ヶ月先の景気後退リスク増。リセッション警戒シグナル。
- Crossing 100 downward → historical precedent for 2-3 quarters of subsequent weakness.

**Market significance / 市場重要度**: ⭐⭐⭐
Most actionable of the CI trio for markets. Japanese fund managers watch this
ahead of BOJ policy meetings. Often moves together with TOPIX by 2-quarter lead.

**When to use / 使用場面**:
Recession risk assessment, 6-9 month forward GDP forecasting, Investment Clock
phase transition detection, GIP quadrant transition anticipation.

**Japan-specific context / 日本固有の文脈**:
Japan's leading index includes some uniquely Japanese components — notably
`中小企業売上高見通しDI` (SME sales outlook DI) which has no direct US/EU
equivalent. The **3-month diffusion index** (how many of the 11 sub-series
are rising) is frequently referenced alongside the CI level.

**Common pitfalls / よくある間違い**:
- Leading index MoM moves are noisy. Use 3-month moving average direction for trend.
- The leading index methodology was revised in 2020; pre-2020 series should not be spliced mechanically.
- A rising leading index does NOT guarantee a coincident-index upturn — signal reliability degrades in structural-break periods (COVID, 2008 GFC).
- Do not confuse CI (Composite Index, amplitude-based) with DI (Diffusion Index, breadth-based) — both are published by 内閣府 and often cited together. This preset is the CI (amplitude) version.

---

## lagging-index: 景気動向指数（遅行指数）/ Composite Lagging Index

- **Series code**: 0706010500000090030 (統計DB)
- **Source**: 内閣府 (Cabinet Office)
- **Unit / 単位**: Index (2020 base = 100)
- **Frequency / 頻度**: Monthly
- **Publication lag / 公表遅延**: ~6-8 weeks after reference month
- **History**: From 1985

**What it measures / 経済的意味**:
(EN) A composite of 9 lagging sub-series (corporate capex plans, CPI-less-fresh-food,
household consumption expenditure, unemployment rate inverted, etc.) that confirms the
business cycle phase ~6 months after the coincident peak/trough.
(JP) 法人企業設備投資、家計消費支出、完全失業率（逆サイクル）、CPI（生鮮除く）など9系列を
合成した遅行指標。景気動向指数（一致）の転換点に6ヶ月程度遅行して動く。

**How to interpret / 解読方法**:
- Lagging index keeps rising AFTER coincident peaks → confirms that the prior
  expansion phase was genuine (not a false dawn). / 一致指数のピーク後も遅行
  指数が上昇すれば、直前の景気拡大が本物だったことを事後確認。
- Lagging index turning down AFTER coincident turn → confirms a genuine cycle
  peak has occurred. / 遅行指数の下降転換は景気転換点の事後確認シグナル。
- Not useful for forward-looking investment decisions; use for CYCLE DATING.

**Market significance / 市場重要度**: ⭐
Academically important but not actionable for portfolio decisions. Used mainly
by 内閣府 and BOJ researchers for cycle-dating confirmation.

**When to use / 使用場面**:
Ex-post cycle dating (confirming a peak or trough was real), confirming that
`coincident-index` moves were genuine rather than noise, academic research.

**Japan-specific context / 日本固有の文脈**:
The lagging index is often cited AFTER the fact in 内閣府 cycle-dating
announcements to justify the official peak/trough month. It rarely moves markets on release
but is part of the CI trio package that 内閣府 publishes together.

**Common pitfalls / よくある間違い**:
- Do not use the lagging index as a forward signal. By design, it confirms what has already happened.
- Even though the lagging index includes unemployment (inverted), do not use it as a proxy for the labor market — use the raw `unemployment` preset for that.
- Some sub-series (e.g., corporate capex plans) are quarterly and interpolated to monthly; interpolation can amplify noise.

---

## machine-orders: 機械受注額 / Machine Orders

- **Series code**: 0701030000000010010 (統計DB)
- **Source**: 内閣府 (Cabinet Office)
- **Unit / 単位**: JPY 100 million (億円)
- **Frequency / 頻度**: Monthly
- **Publication lag / 公表遅延**: ~6 weeks after reference month
- **History**: From 2005 (251 observations)

**What it measures / 経済的意味**:
(EN) The value of new orders received by major machinery manufacturers from the private sector, excluding volatile orders for ships and electric power. This is Japan's most closely watched leading indicator for business investment (capex), as orders placed today become investment spending 6-9 months later.
(JP) 主要機械メーカーが民間から受注した機械の金額（船舶・電力を除く民需）。設備投資の6-9ヶ月先行指標として、日本市場で最も注目される経済指標の一つ。

**How to interpret / 解読方法**:
- Rising / 上昇 → Firms are ordering more equipment. Capex cycle upswing expected 6-9 months ahead. Positive for machinery, construction, and capital goods sectors. / 企業の設備投資意欲が旺盛。6-9ヶ月先の設備投資拡大を示唆。
- Falling / 下落 → Firms are cutting back on equipment orders. Capex downturn ahead. Negative for cyclical sectors. / 企業の設備投資抑制。景気後退の前兆となりうる。

**Market significance / 市場重要度**: ⭐⭐⭐
Japan's most important capex leading indicator. Volatile month-to-month but the trend signals corporate investment intentions 3-6 months ahead. Moves equity markets on release.

**When to use / 使用場面**:
Capex cycle forecasting, leading indicator for GDP, equity sector rotation
(machinery, construction), business cycle turning point detection.

**Japan-specific context / 日本固有の文脈**:
Machine orders are extremely volatile month-to-month (swings of +/-10% in a
single month are common) due to lumpy large-scale orders. Markets focus on the
3-month moving average and the quarterly comparison to smooth noise. The
government's quarterly forecast for machine orders is also closely watched
for guidance on the capex outlook.

**Common pitfalls / よくある間違い**:
- Single-month figures are extremely noisy. A -15% MoM decline does not necessarily signal a downturn. Always use 3-month moving averages for trend analysis.
- The headline "ships and electric power excluded" (船舶・電力を除く) is the standard measure. Total orders including ships/electric power are misleading due to occasional massive one-off orders.
- Machine orders measure the value of orders received, not shipped. There is a further lag between orders and actual investment spending.
- Do not confuse with "machine tool orders" (工作機械受注), which is published by the Japan Machine Tool Builders' Association and covers a narrower scope.

---

## tertiary-index: 第3次産業活動指数 / Tertiary Industry Activity Index

- **Series code**: 0603100300000090010 (統計DB)
- **Source**: 経済産業省 (METI)
- **Unit / 単位**: Index (2020 base = 100), seasonally adjusted
- **Frequency / 頻度**: Monthly
- **Publication lag / 公表遅延**: ~6 weeks after reference month
- **History**: From 2018 (97 observations)

**What it measures / 経済的意味**:
(EN) A real (inflation-adjusted) index measuring the output of Japan's service sector (tertiary industry), covering wholesale/retail, finance/insurance, transport, information/communications, and other services. This is the services counterpart to the Industrial Production Index.
(JP) サービス業（第3次産業）の活動量を実質ベースで測定する指数。卸小売、金融保険、運輸、情報通信等を含む。鉱工業生産指数のサービス版。

**How to interpret / 解読方法**:
- Rising / 上昇 → Service sector activity expanding. Positive for Japan's consumption-driven recovery narrative. / サービスセクターの活動拡大。消費主導の景気回復を支持。
- Falling / 下落 → Service sector activity contracting. Since services are the dominant majority of GDP (約7割、2015–2024年安定推移), broad weakness signals significant economic slowdown. / サービスセクターの活動縮小。GDPの過半数（約7割、2015–2024年安定推移）を占めるため広範な弱さは深刻な景気減速を示唆。

**Market significance / 市場重要度**: ⭐⭐
Japan's services sector activity gauge. Complements IP for a full picture of the economy. Services account for ~70% of GDP but get less market attention than manufacturing.

**When to use / 使用場面**:
Services-led recovery assessment, complement to IP for full economic picture,
IC mapping growth proxy, domestic consumption tracking, post-COVID recovery
monitoring.

**Japan-specific context / 日本固有の文脈**:
Japan's economy has gradually shifted from manufacturing to services over
decades, with services now the dominant sector (約7割 of GDP as of 2023). However, policy
attention and market focus historically skew toward manufacturing (IP, TANKAN
manufacturing DI). The Tertiary Index helps correct this manufacturing bias.
The COVID-19 pandemic caused an unprecedented collapse in service-sector
activity due to Japan's prolonged state of emergency declarations and
voluntary movement restrictions.

**Common pitfalls / よくある間違い**:
- The Tertiary Index is real (volume-based), not nominal. If service prices rise but activity is flat, the nominal sales figure (service-sales preset) may show growth while this index stays flat.
- Coverage is broad but not complete. Some service sub-sectors have poor measurement, especially newer digital services.
- Base year revisions (currently 2020 base) change component weights and can cause level shifts. The 2020 base incorporates COVID-year distortions.
- Do not confuse with the "All Industry Activity Index" (全産業活動指数), which combines both IP and Tertiary into a single measure.

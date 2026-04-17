# Japan Macro Indicators Reference / 日本マクロ指標リファレンス

Bilingual reference for indicators used by the `japan-macro` skill.
Tier 1 entries include full documentation; Tier 2 entries are brief summaries.

---

## Tier 1 -- Core Indicators (13)

---

### 無担保コールO/N物レート / Call Rate, Uncollateralized Overnight

- **Source / データソース**: BOJ API (db=FM01, code=STRDCLUCON)
- **Unit / 単位**: Percent (%)
- **Frequency / 頻度**: Daily
- **Publication lag / 公表遅延**: ~1 business day
- **Managing agency / 所管**: 日本銀行 (Bank of Japan)

**What it measures / 経済的意味**:
(EN) The weighted average interest rate at which financial institutions lend uncollateralized overnight funds in the interbank call money market. This is the BOJ's primary policy rate target, equivalent to the Federal Funds rate in the US.
(JP) 金融機関が無担保でオーバーナイト資金を貸し借りする際の加重平均金利。日銀の政策金利操作の主要ターゲットであり、米国のFF金利に相当する。

**How to interpret / 解読方法**:
- Rising / 上昇 → BOJ is tightening monetary policy. Higher short-term borrowing costs across the economy. / 日銀が金融引締めに動いている。短期借入コストが上昇。
- Falling / 下落 → BOJ is easing monetary policy. Lower borrowing costs to stimulate lending and spending. / 日銀が金融緩和に動いている。借入コスト低下で貸出・消費を刺激。

**When to use / 使用場面**:
Investment Clock monetary policy axis, DCF short-term risk-free rate proxy,
BOJ policy stance assessment, JPY carry trade cost estimation.

**Japan-specific context / 日本固有の文脈**:
Under the Negative Interest Rate Policy (マイナス金利政策, 2016-01 to 2024-03),
the call rate traded near -0.1%. In March 2024, BOJ ended negative rates and
raised the target to 0-0.1%, then to 0.25% in July 2024, and 0.5% in January
2025. This was the first tightening cycle in 17 years. The call rate had been
effectively zero or negative for over two decades, making any positive reading
historically significant.

**Common pitfalls / よくある間違い**:
- The call rate is a daily weighted average, not the BOJ's announced target range. Actual trades can deviate from the target.
- Because Japan spent 20+ years near zero, small basis-point moves (e.g., 0.1% to 0.25%) carry outsized economic significance compared to similar moves in the US.
- Do not compare absolute levels with US FEDFUNDS. Compare the direction and rate of change relative to each country's neutral rate.

---

### 基準割引率・基準貸付利率 / Basic Discount Rate and Basic Loan Rate

- **Source / データソース**: BOJ API (db=IR01)
- **Unit / 単位**: Percent (%)
- **Frequency / 頻度**: Irregular (changes with policy decisions)
- **Publication lag / 公表遅延**: Same day as policy decision
- **Managing agency / 所管**: 日本銀行 (Bank of Japan)

**What it measures / 経済的意味**:
(EN) The rate at which the BOJ lends to financial institutions through its Complementary Lending Facility. It acts as an effective ceiling for the overnight call rate, since no institution would borrow in the interbank market at a rate above what the BOJ charges directly.
(JP) 日銀が補完貸付制度を通じて金融機関に貸し付ける際の金利。コールレートの事実上の上限として機能する。

**How to interpret / 解読方法**:
- Rising / 上昇 → BOJ is raising the corridor ceiling, consistent with overall tightening. / 日銀がコリドーの上限を引き上げ。全体的な引締めと整合。
- Falling / 下落 → BOJ is lowering the ceiling, widening accommodation. / 上限引下げ。緩和スタンスの拡大。

**When to use / 使用場面**:
Understanding the BOJ's interest rate corridor system, confirming policy rate
changes alongside the call rate target, historical policy analysis.

**Japan-specific context / 日本固有の文脈**:
Under NIRP, the basic loan rate was set at 0.3%. It functions as the upper
bound of the BOJ's corridor system (complementary deposit rate is the floor).
Unlike the Fed's discount rate which carries stigma, the BOJ's facility is
designed as a routine backstop.

**Common pitfalls / よくある間違い**:
- This is NOT the main policy rate. The call rate (FM01) is the primary policy tool. The basic loan rate is the corridor ceiling.
- Changes are infrequent and lag the call rate target changes. Do not use this as a real-time policy indicator.

---

### 消費者物価指数 CPI / Consumer Price Index

- **Source / データソース**: 統計ダッシュボード (preset=cpi, indicator=0703010501010030000)
- **Unit / 単位**: YoY % change (前年同月比)
- **Frequency / 頻度**: Monthly
- **Publication lag / 公表遅延**: ~3-4 weeks after reference month
- **Managing agency / 所管**: 総務省統計局 (Ministry of Internal Affairs and Communications, Statistics Bureau)

**What it measures / 経済的意味**:
(EN) Year-over-year percentage change in the consumer price index for all items, covering the prices of goods and services purchased by households nationwide. This is Japan's headline inflation measure.
(JP) 全国の世帯が購入する商品・サービスの価格変動を測定する消費者物価指数（総合）の前年同月比。日本のヘッドライン・インフレ指標。

**How to interpret / 解読方法**:
- Rising / 上昇 → Inflation is accelerating. If sustained above BOJ's 2% target, supports hawkish policy expectations. / インフレ加速。2%目標を持続的に超えれば引締め観測を強化。
- Falling / 下落 → Disinflation or deflation risk. Supports dovish policy stance. / ディスインフレまたはデフレリスク。緩和スタンスを支持。

**When to use / 使用場面**:
Investment Clock inflation axis, BOJ policy prediction, real return
calculations, GIP quadrant mapping.

**Japan-specific context / 日本固有の文脈**:
Japan experienced chronic deflation from the late 1990s through 2021. The
BOJ's 2% inflation target (introduced 2013) was not sustainably achieved until
the post-COVID supply shock + weak yen period (2022-). Japanese CPI is heavily
influenced by administered prices (electricity, gas subsidies), food prices,
and the yen exchange rate. Government energy subsidies can distort CPI by
0.5-1.0 percentage points.

**Common pitfalls / よくある間違い**:
- The 統計DB preset returns YoY % change directly, unlike FRED CPI which returns the index level. No manual YoY calculation needed.
- Japan CPI uses a different basket weighting than US CPI. Shelter (rent) weight is much lower in Japan (~20% vs ~36% in US) because Japan has high home ownership and controlled rents.
- "Core CPI" in Japan means "less fresh food" (生鮮食品を除く), NOT "less food and energy" as in the US. The US-style core is called "core-core CPI" (生鮮食品及びエネルギーを除く) in Japan.

---

### 企業物価指数 CGPI / Corporate Goods Price Index

- **Source / データソース**: BOJ API (db=PR01, code=discover via getMetadata)
- **Unit / 単位**: YoY % change or Index (2020 base = 100)
- **Frequency / 頻度**: Monthly
- **Publication lag / 公表遅延**: ~2 weeks after reference month (published before CPI)
- **Managing agency / 所管**: 日本銀行 (Bank of Japan)

**What it measures / 経済的意味**:
(EN) The price change of goods traded between corporations at the producer level. Formerly called the Wholesale Price Index (WPI). Covers domestically produced goods, exports, and imports. It is a leading indicator for CPI because B2B price pressures eventually pass through to consumer prices.
(JP) 企業間で取引される財の価格変動を測定。旧名「卸売物価指数」。国内品、輸出品、輸入品を含む。B2B価格圧力はやがて消費者物価に転嫁されるため、CPIの先行指標。

**How to interpret / 解読方法**:
- Rising / 上昇 → Input cost pressures building for corporations. If sustained, expect pass-through to CPI with a 3-6 month lag. Margin pressure for companies without pricing power. / 企業のコスト圧力上昇。3-6ヶ月のラグでCPIに転嫁される可能性。
- Falling / 下落 → Deflationary pressure at the producer level. Eases corporate cost burden but signals weak demand. / 生産者段階のデフレ圧力。コスト負担は軽減するが需要の弱さを示唆。

**When to use / 使用場面**:
Leading indicator for CPI trajectory, corporate margin analysis,
import price pass-through assessment, yen depreciation impact analysis.

**Japan-specific context / 日本固有の文脈**:
CGPI is compiled by the BOJ (not the statistics bureau), making it unique
among major economies where the central bank directly measures producer prices.
The import component is heavily influenced by the JPY exchange rate and oil
prices. In 2022-2023, CGPI spiked to 9-10% YoY while CPI was still 3-4%,
illustrating the delayed pass-through from B2B to consumer prices.

**Common pitfalls / よくある間違い**:
- CGPI != CPI. CGPI measures business-to-business goods prices (日銀管轄); CPI measures consumer prices (総務省管轄). CGPI can spike while CPI remains flat when companies absorb input costs instead of passing them through.
- The PR01 database has multiple sub-series (domestic, export, import). Ensure you select the correct aggregate code.
- Base year revisions (currently 2020 base) change series codes. Always use getMetadata to discover the current code.

---

### 国内総生産 GDP / Gross Domestic Product

- **Source / データソース**: 統計ダッシュボード (use `--cycle quarterly`, discover via search)
- **Unit / 単位**: QoQ annualized % change or JPY trillions
- **Frequency / 頻度**: Quarterly
- **Publication lag / 公表遅延**: ~6 weeks (1st preliminary estimate / 速報)
- **Managing agency / 所管**: 内閣府 (Cabinet Office)

**What it measures / 経済的意味**:
(EN) The total inflation-adjusted value of goods and services produced in Japan. The definitive measure of whether the Japanese economy is expanding or contracting.
(JP) 日本国内で生産された財・サービスの実質総額。日本経済の拡大・縮小を判断する最も包括的な指標。

**How to interpret / 解読方法**:
- Rising (positive QoQ) / 上昇 → Economy expanding. Supports corporate earnings and risk assets. / 経済拡大。企業収益・リスク資産を支持。
- Falling (negative QoQ) / 下落 → Economy contracting. Two consecutive negative quarters is the informal recession definition. / 経済縮小。2四半期連続マイナスは非公式の景気後退定義。

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

### マネーストック M2 / Money Stock M2

- **Source / データソース**: BOJ API (db=MD02, code=discover via getMetadata)
- **Unit / 単位**: JPY 100 million (億円) or YoY % change
- **Frequency / 頻度**: Monthly
- **Publication lag / 公表遅延**: ~2 weeks after reference month
- **Managing agency / 所管**: 日本銀行 (Bank of Japan)

**What it measures / 経済的意味**:
(EN) The total amount of money held by non-financial sectors (households, corporations, local governments), including cash in circulation, demand deposits, and time deposits at domestically licensed banks. M2 is the most-watched money supply aggregate in Japan.
(JP) 非金融部門（家計・企業・地方公共団体）が保有する通貨量の総計。現金、要求払預金、定期預金を含む。日本で最も注目されるマネーサプライ指標。

**How to interpret / 解読方法**:
- Rising (accelerating YoY) / 上昇 → Money supply expanding. Can signal future inflation if velocity picks up. Accommodative monetary conditions. / マネーサプライ拡大。流通速度が上昇すれば将来のインフレを示唆。
- Falling (decelerating YoY) / 下落 → Money supply growth slowing. Tighter monetary conditions or weak credit demand. / マネーサプライ伸び鈍化。金融環境の引締めまたは信用需要の弱さ。

**When to use / 使用場面**:
Monetary conditions assessment, liquidity analysis, cross-check with BOJ
balance sheet expansion, inflation forecasting input.

**Japan-specific context / 日本固有の文脈**:
During quantitative easing (QE) and QQE (Quantitative and Qualitative
Easing), the BOJ massively expanded its balance sheet, but M2 growth remained
modest (~3-4% YoY) because banks did not proportionally increase lending.
This "pushing on a string" dynamic is a defining feature of Japan's monetary
policy trap. M2 growth accelerated during COVID fiscal transfers.

**Common pitfalls / よくある間違い**:
- M2 != Monetary Base (MB). The BOJ controls MB directly; M2 depends on bank lending behavior. Japan's MB exploded under QQE, but M2 barely moved.
- Japan uses M2 as the headline aggregate (not M3 as in the Eurozone). M3 includes Japan Post Bank deposits and is broader.
- MD02 contains multiple series. Use getMetadata to find the M2 headline aggregate code.

---

### 鉱工業生産指数 / Industrial Production Index

- **Source / データソース**: 統計ダッシュボード (preset=ip, indicator=0502070301000090010)
- **Unit / 単位**: Index (2020 base = 100), seasonally adjusted
- **Frequency / 頻度**: Monthly
- **Publication lag / 公表遅延**: ~6 weeks after reference month
- **Managing agency / 所管**: 経済産業省 (Ministry of Economy, Trade and Industry, METI)

**What it measures / 経済的意味**:
(EN) The real output volume of Japan's mining and manufacturing sectors. A high-frequency cyclical indicator that tracks industrial activity and leads broader economic turning points.
(JP) 鉱業・製造業の実質生産量を測定。景気循環を高頻度で追跡する先行指標。

**How to interpret / 解読方法**:
- Rising / 上昇 → Industrial activity expanding. Positive for cyclical equities, machinery orders, and export-oriented sectors. / 鉱工業活動の拡大。循環株・機械受注・輸出関連セクターにポジティブ。
- Falling / 下落 → Industrial activity contracting. Signals potential recession if sustained 3+ months. / 鉱工業活動の縮小。3ヶ月以上持続すれば景気後退のシグナル。

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
- IP covers manufacturing and mining only, not services (~70% of Japan's GDP). A services-led recovery can coexist with flat IP.

---

### 完全失業率 / Unemployment Rate

- **Source / データソース**: 統計ダッシュボード (preset=unemployment, indicator=0301010000020020010)
- **Unit / 単位**: Percent (%)
- **Frequency / 頻度**: Monthly
- **Publication lag / 公表遅延**: ~4 weeks after reference month
- **Managing agency / 所管**: 総務省統計局 (Ministry of Internal Affairs and Communications, Statistics Bureau)

**What it measures / 経済的意味**:
(EN) The percentage of the labor force that is unemployed and actively seeking work. Japan's official measure of labor market slack.
(JP) 労働力人口に占める完全失業者の割合。日本の労働市場の緩み度合いを測る公式指標。

**How to interpret / 解読方法**:
- Rising / 上昇 → Labor market weakening. Negative for consumption outlook and wage growth. / 労働市場の悪化。消費見通し・賃金上昇にネガティブ。
- Falling / 下落 → Labor market tightening. Positive for wage growth and consumption, but may add to inflation pressure. / 労働市場の逼迫。賃金・消費にポジティブだがインフレ圧力を助長する可能性。

**When to use / 使用場面**:
Labor market assessment, wage-price spiral risk evaluation, consumption
outlook, BOJ policy input (full employment supports normalization).

**Japan-specific context / 日本固有の文脈**:
Japan's unemployment rate is structurally low (~2.5-3.0%) compared to
Western economies due to labor hoarding practices (雇用保蔵), lifetime
employment culture, and demographic shrinkage reducing labor supply. A move
from 2.5% to 3.0% in Japan is as significant as a move from 4% to 6% in the
US. Japan's labor market slack is better measured by the jobs-to-applicants
ratio (有効求人倍率, published by MHLW) than by the unemployment rate alone.

**Common pitfalls / よくある間違い**:
- Japan's unemployment rate underestimates true slack because discouraged workers exit the labor force rather than registering as unemployed (low labor force participation rate, especially among older women historically).
- The rate barely moved during COVID (peaked at 3.1%) due to massive government employment subsidies (雇用調整助成金). This masked the true impact.
- Do not compare Japan's 2.5% with US 4% and conclude Japan's labor market is tighter. Structural and definitional differences make absolute comparison misleading.

---

### 新発10年国債利回り / 10-Year JGB Yield

- **Source / データソース**: 統計ダッシュボード (preset=jgb10y, indicator=0702020300000010020)
- **Unit / 単位**: Percent (%), month-end value
- **Frequency / 頻度**: Monthly
- **Publication lag / 公表遅延**: ~1 week after month-end
- **Managing agency / 所管**: 財務省 (Ministry of Finance) / 日本証券業協会

**What it measures / 経済的意味**:
(EN) The yield on the most recently issued 10-year Japanese Government Bond. The benchmark long-term risk-free rate for Japan, reflecting long-term inflation expectations, growth expectations, and BOJ policy outlook.
(JP) 新発10年物国債の利回り。日本の長期リスクフリーレートのベンチマーク。長期インフレ期待・成長期待・日銀政策見通しを反映。

**How to interpret / 解読方法**:
- Rising / 上昇 → Markets expect higher inflation, stronger growth, or BOJ policy normalization. Raises discount rates for equity valuations. / 市場がインフレ上昇・景気回復・日銀正常化を予想。株式バリュエーションの割引率上昇。
- Falling / 下落 → Markets expect deflation, weaker growth, or continued BOJ accommodation. Flight to safety. / デフレ・景気減速・日銀緩和継続の予想。安全資産への逃避。

**When to use / 使用場面**:
DCF discount rate for Japan equities, JPY-denominated bond allocation,
JGB-US Treasury spread analysis (for yen carry trade assessment), BOJ YCC
policy monitoring.

**Japan-specific context / 日本固有の文脈**:
Under Yield Curve Control (YCC, イールドカーブ・コントロール, 2016-2024), the
BOJ explicitly targeted the 10Y JGB yield near 0% with a tolerance band.
The band was widened from +/-0.25% to +/-0.5% (Dec 2022), then to +/-1.0%
as a "reference" (Jul 2023), before YCC was formally ended in March 2024.
During YCC, the 10Y yield was an administered rate, NOT a market-clearing
rate. Post-YCC, yields are normalizing but remain suppressed by BOJ's
massive JGB holdings (~50% of outstanding).

**Common pitfalls / よくある間違い**:
- During YCC (2016-2024), this yield did NOT reflect market expectations -- it reflected BOJ intervention. Do not use YCC-era yields for market-based analysis.
- The 統計DB returns month-end snapshots, not daily. For real-time JGB yields, use market data providers.
- JGB yields are denominated in JPY. For cross-border comparison (e.g., JPY carry trade), you must adjust for currency hedging costs (basis swap).
- BOJ still holds ~50% of outstanding JGBs. The "free float" is small, making yields less informative than in markets with deeper private-sector participation.

---

### 短観 業況判断DI / TANKAN Business Conditions DI

- **Source / データソース**: BOJ API (db=CO, code=discover via getMetadata)
- **Unit / 単位**: Diffusion Index (percentage points)
- **Frequency / 頻度**: Quarterly (March, June, September, December surveys)
- **Publication lag / 公表遅延**: ~1 week after quarter-end survey
- **Managing agency / 所管**: 日本銀行 (Bank of Japan)

**What it measures / 経済的意味**:
(EN) The TANKAN (Short-Period Economic Survey of Enterprises) is the BOJ's own quarterly survey of approximately 10,000 firms on business conditions. The headline DI = (% of firms reporting "favorable") minus (% reporting "unfavorable"). The "Large Manufacturers" DI is the most-watched number.
(JP) 短観（全国企業短期経済観測調査）は日銀が約1万社を対象に四半期ごとに実施する景況感調査。業況判断DI＝「良い」回答割合−「悪い」回答割合。「大企業製造業」のDIがヘッドライン。

**How to interpret / 解読方法**:
- DI > 0 → More firms see conditions as "favorable" than "unfavorable." Positive business sentiment. / 「良い」超。景況感はポジティブ。
- DI < 0 → More firms see conditions as "unfavorable." Negative business sentiment. / 「悪い」超。景況感はネガティブ。
- DI = 0 → Neutral threshold (not a midpoint on a scale). / ゼロは中立の閾値（スケールの中間点ではない）。

**When to use / 使用場面**:
Leading indicator for capex and earnings, corporate sentiment gauge,
BOJ policy input (TANKAN informs BOJ's economic assessment), equity market
direction for Japan-heavy portfolios.

**Japan-specific context / 日本固有の文脈**:
TANKAN is uniquely important because it is the BOJ's own survey, directly
feeding into policy decisions. The forecast DI (3 months ahead) is also
published, showing firms' own expectations. The gap between actual and
forecast DI reveals surprise direction. Large Manufacturers DI is the
headline, but Large Non-Manufacturers DI has grown in importance as
Japan's economy shifts toward services.

**Common pitfalls / よくある間違い**:
- DI > 0 does NOT mean "good economy." It means more firms say "favorable" than "unfavorable." A DI of +5 falling from +15 means conditions are still positive but deteriorating rapidly.
- The "Large Manufacturers" DI is export-sensitive and yen-sensitive. It can diverge significantly from non-manufacturers during periods of yen volatility.
- TANKAN is quarterly, not monthly. Do not try to interpolate monthly readings.
- The CO database contains many sub-series (by industry, size, item). Use getMetadata to find the specific headline DI code.

---

### USD/JPY 為替レート / USD/JPY Exchange Rate

- **Source / データソース**: BOJ API (db=FM08, code=discover via getMetadata)
- **Unit / 単位**: JPY per 1 USD
- **Frequency / 頻度**: Daily (Tokyo market)
- **Publication lag / 公表遅延**: ~1-2 business days
- **Managing agency / 所管**: 日本銀行 (Bank of Japan)

**What it measures / 経済的意味**:
(EN) The exchange rate of Japanese yen per US dollar as observed in the Tokyo foreign exchange market. The most important exchange rate for Japan's trade-dependent economy.
(JP) 東京外国為替市場におけるドル円レート。貿易依存度の高い日本経済にとって最重要の為替レート。

**How to interpret / 解読方法**:
- Rising (JPY weakening) / 上昇 → Yen depreciation against USD. Positive for Japanese exporters' earnings, but raises import costs (energy, food). Can push CGPI and eventually CPI higher. / 円安。輸出企業の収益にプラスだが輸入コスト上昇。
- Falling (JPY strengthening) / 下落 → Yen appreciation against USD. Negative for exporter competitiveness, but lowers import costs. / 円高。輸出競争力にマイナスだが輸入コスト低下。

**When to use / 使用場面**:
Japan equity analysis (exporters vs importers), import cost pass-through
assessment, carry trade profitability, cross-border capital flow analysis,
BOJ intervention risk assessment.

**Japan-specific context / 日本固有の文脈**:
USD/JPY is one of the most traded currency pairs globally. The rate is
heavily influenced by the US-Japan interest rate differential. During 2022-2024,
the rate moved from ~115 to ~160 as the Fed hiked while BOJ maintained NIRP/YCC.
The Ministry of Finance (MOF) has historically intervened (through BOJ as agent)
when moves are deemed "excessive and one-sided" -- notable interventions occurred
in September/October 2022 and April/July 2024.

**Common pitfalls / よくある間違い**:
- BOJ FM08 data is Tokyo market closing rates, not real-time. The pair trades 24 hours globally.
- A "weak yen" benefits exporters but hurts household purchasing power and domestic-oriented companies. The net GDP effect depends on the speed of the move.
- MOF intervention is conducted through the BOJ as agent. "BOJ intervention" is technically "MOF intervention via BOJ."
- FM08 contains multiple currency pairs. Use getMetadata to find the USD/JPY-specific code.

---

### 実効為替レート / Effective Exchange Rate

- **Source / データソース**: BOJ API (db=FM09, code=discover via getMetadata)
- **Unit / 単位**: Index (2020 = 100, trade-weighted)
- **Frequency / 頻度**: Monthly
- **Publication lag / 公表遅延**: ~1-2 business days after month-end
- **Managing agency / 所管**: 日本銀行 (Bank of Japan)

**What it measures / 経済的意味**:
(EN) A trade-weighted index of the yen's value against a basket of major trading partner currencies, adjusted for inflation differentials (real effective exchange rate, REER) or unadjusted (nominal effective exchange rate, NEER). Captures the yen's overall competitiveness, not just against the dollar.
(JP) 主要貿易相手国通貨に対する円の加重平均指数。インフレ格差調整済み（実質実効為替レート）と未調整（名目）がある。ドルだけでなく円の総合的な競争力を把握。

**How to interpret / 解読方法**:
- Rising / 上昇 → Yen strengthening on a trade-weighted basis. Japan's export competitiveness declining. / 円の実効的な増価。輸出競争力の低下。
- Falling / 下落 → Yen weakening on a trade-weighted basis. Export competitiveness improving but import costs rising. / 円の実効的な減価。輸出競争力は改善だが輸入コスト上昇。

**When to use / 使用場面**:
Holistic yen competitiveness assessment (better than bilateral USD/JPY),
Japan terms-of-trade analysis, historical purchasing power comparison,
structural competitiveness evaluation.

**Japan-specific context / 日本固有の文脈**:
Japan's REER hit 50-year lows in 2022-2024, meaning the yen's real
purchasing power was at levels not seen since the early 1970s. This extreme
weakness reflected two decades of low inflation in Japan while trading
partners experienced higher inflation. The REER is arguably the most
important single indicator for understanding Japan's structural
competitiveness position.

**Common pitfalls / よくある間違い**:
- NEER and REER can diverge significantly. REER adjusts for inflation differentials and is more meaningful for competitiveness analysis.
- FM09 contains both NEER and REER as separate series. Use getMetadata to select the correct one.
- The index is constructed by BIS methodology. Base year and weighting changes can cause level shifts. Focus on trends rather than absolute values.
- A falling REER does not automatically mean "good for Japan" -- it also means reduced purchasing power for imports and overseas travel.

---

### 経常収支 / Current Account Balance

- **Source / データソース**: BOJ API (db=BP01, code=discover via getMetadata)
- **Unit / 単位**: JPY 100 million (億円)
- **Frequency / 頻度**: Monthly
- **Publication lag / 公表遅延**: ~6 weeks after reference month
- **Managing agency / 所管**: 財務省 (Ministry of Finance) / 日本銀行

**What it measures / 経済的意味**:
(EN) The sum of Japan's trade balance, services balance, primary income balance (investment income from overseas assets), and secondary income balance. Measures Japan's overall economic transactions with the rest of the world.
(JP) 貿易収支・サービス収支・第一次所得収支（海外資産からの投資収益）・第二次所得収支の合計。日本と世界の経済取引の全体像を測定。

**How to interpret / 解読方法**:
- Surplus / 黒字 → Japan earns more from the world than it pays. Supports JPY demand (though with diminishing FX impact as income is often reinvested abroad). / 日本の対外収入が支出を上回る。円需要を支持（ただし所得は海外で再投資されることが多い）。
- Deficit / 赤字 → Japan pays more to the world than it earns. Potential JPY weakness factor if structural. / 日本の対外支出が収入を上回る。構造的なら円安要因。

**When to use / 使用場面**:
JPY fundamental valuation, Japan investment flow analysis, terms-of-trade
assessment, structural competitiveness evaluation.

**Japan-specific context / 日本固有の文脈**:
Japan has a structural trade deficit (since 2011 Fukushima disaster increased
energy imports) but a massive primary income surplus from overseas investments
accumulated over decades of trade surpluses. The net current account usually
remains positive thanks to investment income. This "mature creditor nation"
structure means: (1) trade balance drives short-term volatility, (2) income
balance provides structural support, (3) the FX impact is muted because
investment income is often reinvested abroad rather than repatriated.

**Common pitfalls / よくある間違い**:
- A current account surplus does NOT necessarily strengthen the yen. If the income component is reinvested overseas, there is no JPY buying flow.
- Seasonal patterns are strong (fiscal year-end in March, bonus months). Use seasonally adjusted data for trend analysis.
- BP01 contains many sub-components (trade, services, income). Use getMetadata to identify the correct total current account code.
- The data is jointly compiled by MOF and BOJ. Published by MOF in the Balance of Payments statistics.

---

## Tier 2 -- Extended Indicators (BOJ DB Series)

Brief bilingual reference for additional BOJ database series useful for
deeper Japan macro analysis.

---

### Interest Rates / 金利関連

| DB | 日本語名 | English Name | Description |
|----|---------|--------------|-------------|
| IR02 | 預金種類別店頭表示金利の平均年利率等 | Average Interest Rates Posted by Type of Deposit | Bank posted rates for ordinary, time deposits. Tracks rate pass-through to depositors. / 普通預金・定期預金の店頭金利。預金者への利上げ転嫁を追跡。 |
| IR03 | 定期預金の預入期間別平均金利 | Average Interest Rates on Time Deposits by Term | Time deposit rates by maturity. Shows term structure of deposit rates. / 期間別定期預金金利。預金の期間構造を表示。 |
| IR04 | 貸出約定平均金利 | Average Contract Interest Rates on Loans | Bank lending rates (short-term, long-term). Key for corporate borrowing cost analysis. / 銀行貸出金利（短期・長期）。企業の借入コスト分析に重要。 |

### Financial Markets / 短期金融市場・為替

| DB | 日本語名 | English Name | Description |
|----|---------|--------------|-------------|
| FM02 | 短期金融市場金利 | Short-term Money Market Rates | Repo rates, T-bill rates, CP rates. Short-end of the yield curve. / レポ・TB・CP金利。イールドカーブの短期端。 |
| FM03 | 短期金融市場残高 | Short-term Money Market Balances | Outstanding balances in money markets. Liquidity conditions gauge. / 短期金融市場残高。流動性状況の指標。 |
| FM04 | コール市場残高 | Call Money Market Outstanding | Call market volumes by participant type. Interbank liquidity depth. / 参加者別コール市場取引量。銀行間流動性の深さ。 |
| FM05 | 公社債発行・償還および現存額 | Bonds Issued, Redeemed and Outstanding | JGB and corporate bond issuance/redemption flow. Supply-demand dynamics. / 国債・社債の発行・償還フロー。需給動態。 |
| FM06 | 公社債消化状況 | Government Bond Distribution | Who is buying JGBs (banks, insurance, foreign, BOJ). Ownership structure. / JGBの購入者（銀行・保険・外国人・日銀）。保有構造。 |
| FM07 | 国債窓口販売額・窓口販売率 | Gov Bond OTC Sales | Retail JGB distribution. Minor indicator. / 個人向け国債の販売状況。 |

### Money and Credit / 預金・マネー・貸出

| DB | 日本語名 | English Name | Description |
|----|---------|--------------|-------------|
| MD01 | マネタリーベース | Monetary Base | Currency in circulation + BOJ current account balances. Directly controlled by BOJ. / 流通通貨＋日銀当座預金残高。日銀が直接制御。 |
| MD03 | マネーサーベイ | Money Survey | Consolidated balance sheet of the banking sector. / 銀行セクターの連結バランスシート。 |
| MD04 | マネーサプライ（M2+CD）増減と信用面の対応 | Money Supply Changes and Credit Counterparts | Decomposition of money supply changes by credit channel. / マネーサプライ変動の信用経路別分解。 |
| MD05 | 通貨流通高 | Currency in Circulation | Physical cash (banknotes + coins) in the economy. Japan is still cash-heavy. / 経済における現金（銀行券＋硬貨）。日本は依然現金社会。 |
| MD06 | 日銀当座預金増減要因と金融調節 | BOJ Current Account Changes and Operations | BOJ market operations detail. Tracks quantitative easing execution. / 日銀のオペレーション詳細。量的緩和の実行状況を追跡。 |
| MD07 | 準備預金額 | Reserves | Required and excess reserves at BOJ. / 日銀の法定準備預金・超過準備。 |
| MD08 | 業態別の日銀当座預金残高 | BOJ Current Account by Sector | BOJ deposits by financial institution type. QE distribution. / 金融機関タイプ別日銀当座預金。QEの配分状況。 |
| MD09 | マネタリーベースと日本銀行の取引 | Monetary Base and BOJ Transactions | Detailed MB components and BOJ transaction flows. / MBの構成要素と日銀取引フローの詳細。 |
| MD10 | 預金者別預金 | Deposits by Depositor | Deposit breakdown by holder type (household, corporate). Savings behavior. / 保有者タイプ別預金内訳。貯蓄行動の分析。 |
| MD11 | 預金・現金・貸出金 | Deposits, Cash, and Loans | Aggregate banking sector deposits, cash, and loan data. / 銀行セクター全体の預金・現金・貸出データ。 |
| MD12 | 都道府県別預金・貸出金 | Deposits and Loans by Prefecture | Regional credit conditions across 47 prefectures. / 47都道府県別の信用状況。 |
| MD13 | 貸出・預金動向 | Lending and Deposit Trends | Monthly lending and deposit growth rates. Credit cycle tracker. / 月次の貸出・預金伸び率。信用サイクルの追跡。 |
| MD14 | 定期預金の残高および新規受入高 | Time Deposits Balance and New Acceptance | Time deposit stocks and flows. Interest rate sensitivity of savers. / 定期預金の残高・新規受入。預金者の金利感応度。 |

### Loans / 貸出関連

| DB | 日本語名 | English Name | Description |
|----|---------|--------------|-------------|
| LA01 | 貸出先別貸出金 | Loans by Sector | Lending breakdown by industry sector. Credit allocation analysis. / 業種別貸出内訳。信用配分の分析。 |
| LA02 | 日本銀行貸出 | BOJ Loans | BOJ lending facilities usage. Emergency lending indicator. / 日銀貸出ファシリティの利用状況。 |
| LA03 | その他貸出残高 | Other Outstanding Loans | Non-bank lending balances. Shadow banking gauge. / ノンバンク貸出残高。シャドーバンキング指標。 |
| LA04 | コミットメントライン契約額・利用額 | Commitment Lines | Committed credit facilities and utilization. Corporate liquidity buffer. / コミットメントライン契約額と利用額。企業の流動性バッファー。 |
| LA05 | 主要銀行貸出動向アンケート調査 | Senior Loan Officer Survey | Bank lending standards survey. Credit conditions tightening/easing. / 銀行の貸出態度調査。信用条件の引締め・緩和。 |

### Balance Sheet / 金融機関バランスシート

| DB | 日本語名 | English Name | Description |
|----|---------|--------------|-------------|
| BS01 | 日本銀行勘定 | Bank of Japan Accounts | BOJ balance sheet. Total assets, JGB holdings, ETF holdings, reserves. / 日銀バランスシート。総資産・国債保有・ETF保有・準備金。 |
| BS02 | 民間金融機関の資産・負債 | Financial Institutions Accounts | Commercial bank balance sheets. Systemic health gauge. / 民間銀行バランスシート。システム健全性指標。 |

### Flow of Funds / 資金循環

| DB | 日本語名 | English Name | Description |
|----|---------|--------------|-------------|
| FF | 資金循環 | Flow of Funds | Comprehensive financial flow between sectors (household, corporate, government, overseas). Japan household financial assets (~2,100 trillion yen). / セクター間の資金フロー。日本の家計金融資産（約2,100兆円）。 |

### Prices / 物価関連

| DB | 日本語名 | English Name | Description |
|----|---------|--------------|-------------|
| PR02 | 企業向けサービス価格指数 | Services Producer Price Index (SPPI) | B2B services price index. Services inflation leading indicator. / 企業間サービス価格指数。サービスインフレの先行指標。 |
| PR03 | 製造業部門別投入・産出物価指数 | Input-Output Price Index (IOPI) | Manufacturing input vs output prices by sector. Margin pressure gauge. / 製造業の投入・産出物価。マージン圧力の指標。 |
| PR04 | 最終需要・中間需要物価指数 | Final/Intermediate Demand Price Index | Price index by demand stage. US PPI-equivalent structure. / 需要段階別物価指数。米国PPIに相当する構造。 |

### Public Finance / 財政関連

| DB | 日本語名 | English Name | Description |
|----|---------|--------------|-------------|
| PF01 | 財政資金収支 | Treasury Receipts and Payments | Government cash flow. Fiscal stance real-time tracker. / 政府キャッシュフロー。財政スタンスのリアルタイム追跡。 |
| PF02 | 政府債務 | National Government Debt | Government debt outstanding by type. Japan debt/GDP ~260%. / 種類別政府債務残高。日本の債務/GDP比率は約260%。 |

### Balance of Payments and International / 国際収支・BIS関連

| DB | 日本語名 | English Name | Description |
|----|---------|--------------|-------------|
| DER | デリバティブ取引に関する定例市場報告 | Derivatives Market Report | OTC and exchange derivatives market data. / 店頭・取引所デリバティブ市場データ。 |
| BIS | BIS国際資金取引統計 | BIS International Banking Statistics | Cross-border banking flows. Capital flow and contagion risk. / クロスボーダー銀行取引フロー。資本フロー・伝染リスク。 |

### TANKAN Detail / 短観詳細

| DB | 日本語名 | English Name | Description |
|----|---------|--------------|-------------|
| CO | 短観（各種DI・計数） | TANKAN (various DI and figures) | Full TANKAN dataset: business conditions DI by industry/size, capex plans, sales forecasts, employment conditions, financial position, lending attitude. The CO database is the richest single source of Japanese corporate sentiment data. / 短観の全データセット：業種・規模別業況判断DI、設備投資計画、売上予測、雇用判断、資金繰り、貸出態度。 |

### Other / その他

| DB | 日本語名 | English Name | Description |
|----|---------|--------------|-------------|
| OB01 | 日本銀行の対政府取引 | BOJ Transactions with Government | BOJ operations with the government sector. / 日銀の対政府取引。 |
| OB02 | 日本銀行が受入れている担保の残高 | Collateral Accepted by BOJ | Collateral pool at BOJ. Financial system stress indicator. / 日銀が受け入れた担保残高。金融システムのストレス指標。 |
| PS01 | 各種決済 | Payment Systems | Payment and settlement volumes. Financial infrastructure health. / 決済システムの取引量。金融インフラの健全性。 |
| PS02 | フェイルの発生状況 | Fails in Settlement | Settlement failures. Market stress and liquidity indicator. / 決済不履行の発生状況。市場ストレス・流動性指標。 |
| OT | その他 | Others | Miscellaneous BOJ statistics not classified elsewhere. / その他の日銀統計。 |

# 金利系 / Interest Rates

Japan macro indicators -- interest rates, policy rates, and bond yields.
Part of `japan-macro` skill. See `indicator-index.md` for full index.

---

## call-rate: 無担保コールO/N物レート / Call Rate, Uncollateralized Overnight

- **Series code**: FM01/STRDCLUCON (BOJ API)
- **Source**: 日本銀行 (Bank of Japan)
- **Unit / 単位**: Percent (%)
- **Frequency / 頻度**: Daily
- **Publication lag / 公表遅延**: ~1 business day
- **History**: From 1985 (daily)

**What it measures / 経済的意味**:
(EN) The weighted average interest rate at which financial institutions lend uncollateralized overnight funds in the interbank call money market. This is the BOJ's primary policy rate target, equivalent to the Federal Funds rate in the US.
(JP) 金融機関が無担保でオーバーナイト資金を貸し借りする際の加重平均金利。日銀の政策金利操作の主要ターゲットであり、米国のFF金利に相当する。

**How to interpret / 解読方法**:
- Rising / 上昇 → BOJ is tightening monetary policy. Higher short-term borrowing costs across the economy. / 日銀が金融引締めに動いている。短期借入コストが上昇。
- Falling / 下落 → BOJ is easing monetary policy. Lower borrowing costs to stimulate lending and spending. / 日銀が金融緩和に動いている。借入コスト低下で貸出・消費を刺激。

**Market significance / 市場重要度**: ⭐⭐⭐
Japan's primary policy rate. BOJ rate decisions are global headlines, moving JPY, JGBs, Nikkei 225, and global carry trade positions. The first rate hike in 17 years (March 2024) was the most anticipated BOJ decision in a generation.

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

## discount-rate: 基準割引率・基準貸付利率 / Basic Discount Rate and Basic Loan Rate

- **Series code**: IR01 (BOJ API)
- **Source**: 日本銀行 (Bank of Japan)
- **Unit / 単位**: Percent (%)
- **Frequency / 頻度**: Irregular (changes with policy decisions)
- **Publication lag / 公表遅延**: Same day as policy decision
- **History**: From 1882 (irregular)

**What it measures / 経済的意味**:
(EN) The rate at which the BOJ lends to financial institutions through its Complementary Lending Facility. It acts as an effective ceiling for the overnight call rate, since no institution would borrow in the interbank market at a rate above what the BOJ charges directly.
(JP) 日銀が補完貸付制度を通じて金融機関に貸し付ける際の金利。コールレートの事実上の上限として機能する。

**How to interpret / 解読方法**:
- Rising / 上昇 → BOJ is raising the corridor ceiling, consistent with overall tightening. / 日銀がコリドーの上限を引き上げ。全体的な引締めと整合。
- Falling / 下落 → BOJ is lowering the ceiling, widening accommodation. / 上限引下げ。緩和スタンスの拡大。

**Market significance / 市場重要度**: ⭐
Corridor ceiling rate. Primarily confirmatory — changes follow the call rate target. Of interest mainly for BOJ operational framework analysis.

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

## jgb10y: 新発10年国債利回り / 10-Year JGB Yield

- **Series code**: 0702020300000010020 (統計DB)
- **Source**: 財務省 / 日本証券業協会
- **Unit / 単位**: Percent (%), month-end value
- **Frequency / 頻度**: Monthly
- **Publication lag / 公表遅延**: ~1 week after month-end
- **History**: From 2013 (150 observations)

**What it measures / 経済的意味**:
(EN) The yield on the most recently issued 10-year Japanese Government Bond. The benchmark long-term risk-free rate for Japan, reflecting long-term inflation expectations, growth expectations, and BOJ policy outlook.
(JP) 新発10年物国債の利回り。日本の長期リスクフリーレートのベンチマーク。長期インフレ期待・成長期待・日銀政策見通しを反映。

**How to interpret / 解読方法**:
- Rising / 上昇 → Markets expect higher inflation, stronger growth, or BOJ policy normalization. Raises discount rates for equity valuations. / 市場がインフレ上昇・景気回復・日銀正常化を予想。株式バリュエーションの割引率上昇。
- Falling / 下落 → Markets expect deflation, weaker growth, or continued BOJ accommodation. Flight to safety. / デフレ・景気減速・日銀緩和継続の予想。安全資産への逃避。

**Market significance / 市場重要度**: ⭐⭐⭐
Japan's benchmark long-term rate. Under YCC (2016-2024), it was the most intervention-distorted sovereign yield globally. Post-YCC, its normalization path affects JPY carry trade economics, global bond supply/demand, and Japanese insurance/pension portfolio rebalancing.

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

## Extended Indicators (Tier 2)

### Interest Rates / 金利関連

| DB | 日本語名 | English Name | Description |
|----|---------|--------------|-------------|
| IR02 | 預金種類別店頭表示金利の平均年利率等 | Average Interest Rates Posted by Type of Deposit | Bank posted rates for ordinary, time deposits. Tracks rate pass-through to depositors. / 普通預金・定期預金の店頭金利。預金者への利上げ転嫁を追跡。 |
| IR03 | 定期預金の預入期間別平均金利 | Average Interest Rates on Time Deposits by Term | Time deposit rates by maturity. Shows term structure of deposit rates. / 期間別定期預金金利。預金の期間構造を表示。 |
| IR04 | 貸出約定平均金利 | Average Contract Interest Rates on Loans | Bank lending rates (short-term, long-term). Key for corporate borrowing cost analysis. / 銀行貸出金利（短期・長期）。企業の借入コスト分析に重要。 |

### Financial Markets / 短期金融市場

| DB | 日本語名 | English Name | Description |
|----|---------|--------------|-------------|
| FM02 | 短期金融市場金利 | Short-term Money Market Rates | Repo rates, T-bill rates, CP rates. Short-end of the yield curve. / レポ・TB・CP金利。イールドカーブの短期端。 |
| FM03 | 短期金融市場残高 | Short-term Money Market Balances | Outstanding balances in money markets. Liquidity conditions gauge. / 短期金融市場残高。流動性状況の指標。 |
| FM04 | コール市場残高 | Call Money Market Outstanding | Call market volumes by participant type. Interbank liquidity depth. / 参加者別コール市場取引量。銀行間流動性の深さ。 |
| FM05 | 公社債発行・償還および現存額 | Bonds Issued, Redeemed and Outstanding | JGB and corporate bond issuance/redemption flow. Supply-demand dynamics. / 国債・社債の発行・償還フロー。需給動態。 |
| FM06 | 公社債消化状況 | Government Bond Distribution | Who is buying JGBs (banks, insurance, foreign, BOJ). Ownership structure. / JGBの購入者（銀行・保険・外国人・日銀）。保有構造。 |
| FM07 | 国債窓口販売額・窓口販売率 | Gov Bond OTC Sales | Retail JGB distribution. Minor indicator. / 個人向け国債の販売状況。 |

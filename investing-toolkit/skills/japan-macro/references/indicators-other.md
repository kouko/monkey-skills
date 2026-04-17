# その他 / Other

Japan macro indicators -- money supply, business sentiment, exchange rates, and external balance.
Part of `japan-macro` skill. See `indicator-index.md` for full index.

---

## m2: マネーストック M2 / Money Stock M2

- **Series code**: MD02 (BOJ API)
- **Source**: 日本銀行 (Bank of Japan)
- **Unit / 単位**: JPY 100 million (億円) or YoY % change
- **Frequency / 頻度**: Monthly
- **Publication lag / 公表遅延**: ~2 weeks after reference month
- **History**: From 2003 (monthly, current definition)

**What it measures / 経済的意味**:
(EN) The total amount of money held by non-financial sectors (households, corporations, local governments), including cash in circulation, demand deposits, and time deposits at domestically licensed banks. M2 is the most-watched money supply aggregate in Japan.
(JP) 非金融部門（家計・企業・地方公共団体）が保有する通貨量の総計。現金、要求払預金、定期預金を含む。日本で最も注目されるマネーサプライ指標。

**How to interpret / 解読方法**:
- Rising (accelerating YoY) / 上昇 → Money supply expanding. Can signal future inflation if velocity picks up. Accommodative monetary conditions. / マネーサプライ拡大。流通速度が上昇すれば将来のインフレを示唆。
- Falling (decelerating YoY) / 下落 → Money supply growth slowing. Tighter monetary conditions or weak credit demand. / マネーサプライ伸び鈍化。金融環境の引締めまたは信用需要の弱さ。

**Market significance / 市場重要度**: ⭐
Technical monetary indicator. Less directly market-moving than in previous decades. The BOJ monitors M2 growth for financial stability but does not target it explicitly.

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

**Cross-indicator notes**:
- Japan-specific anomaly: M2 expanded sharply post-1995 while nominal GDP stagnated — opposite to textbook expectations. Expanded money funded government bond purchases (low fiscal multipliers), not private investment, during the balance sheet recession period (1990-2005).
  Source: RIETI analysis https://www.rieti.go.jp/jp/columns/s15_0010.html
  Period: 1995–2012 (quantitative easing era). Similar pattern during 2013–2020 QQE.

---

## tankan: 短観 業況判断DI / TANKAN Business Conditions DI

- **Series code**: CO (BOJ API)
- **Source**: 日本銀行 (Bank of Japan)
- **Unit / 単位**: Diffusion Index (percentage points)
- **Frequency / 頻度**: Quarterly (March, June, September, December surveys)
- **Publication lag / 公表遅延**: ~1 week after quarter-end survey
- **History**: From 1974 (quarterly)

**What it measures / 経済的意味**:
(EN) The TANKAN (Short-Period Economic Survey of Enterprises) is the BOJ's own quarterly survey of approximately 10,000 firms on business conditions. The headline DI = (% of firms reporting "favorable") minus (% reporting "unfavorable"). The "Large Manufacturers" DI is the most-watched number.
(JP) 短観（全国企業短期経済観測調査）は日銀が約1万社を対象に四半期ごとに実施する景況感調査。業況判断DI＝「良い」回答割合−「悪い」回答割合。「大企業製造業」のDIがヘッドライン。

**How to interpret / 解読方法**:
- DI > 0 → More firms see conditions as "favorable" than "unfavorable." Positive business sentiment. / 「良い」超。景況感はポジティブ。
- DI < 0 → More firms see conditions as "unfavorable." Negative business sentiment. / 「悪い」超。景況感はネガティブ。
- DI = 0 → Neutral threshold (not a midpoint on a scale). / ゼロは中立の閾値（スケールの中間点ではない）。

**Market significance / 市場重要度**: ⭐⭐⭐
Japan's most important business sentiment survey. The BOJ's own survey, released quarterly, is the definitive gauge of corporate Japan's outlook. The Large Manufacturing DI is the headline number — it moves markets on release day.

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

## usdjpy: USD/JPY 為替レート / USD/JPY Exchange Rate

- **Series code**: FM08 (BOJ API)
- **Source**: 日本銀行 (Bank of Japan)
- **Unit / 単位**: JPY per 1 USD
- **Frequency / 頻度**: Daily (Tokyo market)
- **Publication lag / 公表遅延**: ~1-2 business days
- **History**: From 1980 (monthly)

**What it measures / 経済的意味**:
(EN) The exchange rate of Japanese yen per US dollar as observed in the Tokyo foreign exchange market. The most important exchange rate for Japan's trade-dependent economy.
(JP) 東京外国為替市場におけるドル円レート。貿易依存度の高い日本経済にとって最重要の為替レート。

**How to interpret / 解読方法**:
- Rising (JPY weakening) / 上昇 → Yen depreciation against USD. Positive for Japanese exporters' earnings, but raises import costs (energy, food). Can push CGPI and eventually CPI higher. / 円安。輸出企業の収益にプラスだが輸入コスト上昇。
- Falling (JPY strengthening) / 下落 → Yen appreciation against USD. Negative for exporter competitiveness, but lowers import costs. / 円高。輸出競争力にマイナスだが輸入コスト低下。

**Market significance / 市場重要度**: ⭐⭐⭐
The world's most traded currency pair after EUR/USD. USD/JPY reflects BOJ-Fed policy divergence, risk appetite, and carry trade dynamics. Moves above 150 trigger government intervention warnings; moves below 130 signal JPY strength.

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

## reer: 実効為替レート / Effective Exchange Rate

- **Series code**: FM09 (BOJ API)
- **Source**: 日本銀行 (Bank of Japan)
- **Unit / 単位**: Index (2020 = 100, trade-weighted)
- **Frequency / 頻度**: Monthly
- **Publication lag / 公表遅延**: ~1-2 business days after month-end
- **History**: From 1970 (monthly)

**What it measures / 経済的意味**:
(EN) A trade-weighted index of the yen's value against a basket of major trading partner currencies, adjusted for inflation differentials (real effective exchange rate, REER) or unadjusted (nominal effective exchange rate, NEER). Captures the yen's overall competitiveness, not just against the dollar.
(JP) 主要貿易相手国通貨に対する円の加重平均指数。インフレ格差調整済み（実質実効為替レート）と未調整（名目）がある。ドルだけでなく円の総合的な競争力を把握。

**How to interpret / 解読方法**:
- Rising / 上昇 → Yen strengthening on a trade-weighted basis. Japan's export competitiveness declining. / 円の実効的な増価。輸出競争力の低下。
- Falling / 下落 → Yen weakening on a trade-weighted basis. Export competitiveness improving but import costs rising. / 円の実効的な減価。輸出競争力は改善だが輸入コスト上昇。

**Market significance / 市場重要度**: ⭐⭐
Trade-weighted effective exchange rate. More informative than bilateral USD/JPY for assessing Japan's overall competitiveness. The JPY REER has been near 50-year lows, reflecting structural JPY weakness.

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

## current-account: 経常収支 / Current Account Balance

- **Series code**: BP01 (BOJ API)
- **Source**: 日本銀行 (Bank of Japan)
- **Unit / 単位**: JPY 100 million (億円)
- **Frequency / 頻度**: Monthly
- **Publication lag / 公表遅延**: ~6 weeks after reference month
- **History**: From 1985 (monthly)

**What it measures / 経済的意味**:
(EN) The sum of Japan's trade balance, services balance, primary income balance (investment income from overseas assets), and secondary income balance. Measures Japan's overall economic transactions with the rest of the world.
(JP) 貿易収支・サービス収支・第一次所得収支（海外資産からの投資収益）・第二次所得収支の合計。日本と世界の経済取引の全体像を測定。

**How to interpret / 解読方法**:
- Surplus / 黒字 → Japan earns more from the world than it pays. Supports JPY demand (though with diminishing FX impact as income is often reinvested abroad). / 日本の対外収入が支出を上回る。円需要を支持（ただし所得は海外で再投資されることが多い）。
- Deficit / 赤字 → Japan pays more to the world than it earns. Potential JPY weakness factor if structural. / 日本の対外支出が収入を上回る。構造的なら円安要因。

**Market significance / 市場重要度**: ⭐⭐
Japan's broadest trade measure. Japan shifted from goods surplus to services deficit + investment income surplus. The structure of the current account (income-driven vs trade-driven) matters for JPY direction.

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

**Cross-indicator notes**:
- The traditional 「経常収支黒字→円高」relationship has structurally broken since 2011 (post-earthquake trade deficit). Japan's current account surplus now derives from overseas investment income (第一次所得収支), but reinvested earnings abroad do NOT convert to yen demand. This breaks the "current account → currency strength" textbook link.
  Source: 三井住友DSアセットマネジメント analysis, 2024-04
  Structural break: 2011–present.

---

## Extended Indicators (Tier 2)

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

### Balance of Payments and International / 国際収支・BIS関連

| DB | 日本語名 | English Name | Description |
|----|---------|--------------|-------------|
| DER | デリバティブ取引に関する定例市場報告 | Derivatives Market Report | OTC and exchange derivatives market data. / 店頭・取引所デリバティブ市場データ。 |
| BIS | BIS国際資金取引統計 | BIS International Banking Statistics | Cross-border banking flows. Capital flow and contagion risk. / クロスボーダー銀行取引フロー。資本フロー・伝染リスク。 |
| BP01 | 経常収支 | Current Account (see Tier 1 above) | Sub-components available for deeper analysis. / サブコンポーネントでより深い分析が可能。 |

### TANKAN Detail / 短観詳細

| DB | 日本語名 | English Name | Description |
|----|---------|--------------|-------------|
| CO | 短観（各種DI・計数） | TANKAN (various DI and figures) | Full TANKAN dataset: business conditions DI by industry/size, capex plans, sales forecasts, employment conditions, financial position, lending attitude. The CO database is the richest single source of Japanese corporate sentiment data. / 短観の全データセット：業種・規模別業況判断DI、設備投資計画、売上予測、雇用判断、資金繰り、貸出態度。 |

### Public Finance / 財政関連

| DB | 日本語名 | English Name | Description |
|----|---------|--------------|-------------|
| PF01 | 財政資金収支 | Treasury Receipts and Payments | Government cash flow. Fiscal stance real-time tracker. / 政府キャッシュフロー。財政スタンスのリアルタイム追跡。 |
| PF02 | 政府債務 | National Government Debt | Government debt outstanding by type. Japan debt/GDP ~260%. / 種類別政府債務残高。日本の債務/GDP比率は約260%。 |

### Other / その他

| DB | 日本語名 | English Name | Description |
|----|---------|--------------|-------------|
| OB01 | 日本銀行の対政府取引 | BOJ Transactions with Government | BOJ operations with the government sector. / 日銀の対政府取引。 |
| OB02 | 日本銀行が受入れている担保の残高 | Collateral Accepted by BOJ | Collateral pool at BOJ. Financial system stress indicator. / 日銀が受け入れた担保残高。金融システムのストレス指標。 |
| PS01 | 各種決済 | Payment Systems | Payment and settlement volumes. Financial infrastructure health. / 決済システムの取引量。金融インフラの健全性。 |
| PS02 | フェイルの発生状況 | Fails in Settlement | Settlement failures. Market stress and liquidity indicator. / 決済不履行の発生状況。市場ストレス・流動性指標。 |
| OT | その他 | Others | Miscellaneous BOJ statistics not classified elsewhere. / その他の日銀統計。 |

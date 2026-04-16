---
name: taiwan-equity-frameworks
description: Taiwan equity analysis frameworks — 三大法人/月營收/董監持股/融資融券 interpretation and TWSE disclosure taxonomy
tier: 3
layer: TW-specific
---

# Taiwan Equity Frameworks

Fully self-contained Tier 3 standard covering the **Taiwan-specific
structured disclosure layer** of investing-team analysis work: the set
of frameworks unique to Taiwan's equity markets that have no direct
equivalent in the global investment canon. This file is the SSOT for
interpretation of 三大法人 institutional flow data, 月營收 monthly
revenue disclosures, 董監持股 director shareholding / pledge data, and
融資融券 margin / short-sale balance signals.

Tier 3 because these frameworks are **cold-query hallucination hotspots**.
LLMs routinely (a) confuse 投信 (domestic mutual funds) with 外資 (foreign
investors) — entirely distinct categories with opposite signal
interpretation; (b) mis-state the 月營收 filing deadline as end-of-month
or the 15th when the statutory deadline is the **10th calendar day** of the
following month; (c) confuse 融資 (margin long — retail bullish) with 融券
(short-sale borrow — bearish) — opposite in directional signal; and
(d) cite no primary statutory source for disclosure rules when the rules
are explicitly codified in 證券交易法 and FSC administrative orders. Body
spells out each framework with enough precision to act on without the cited
sources in hand.

**Scope**: Taiwan TWSE/OTC-listed equity analysis using structured TWSE/MOPS
disclosures. Cross-asset macro regime diagnosis belongs to
`investment-macro-regime.md`; individual security valuation belongs to
`investment-security-valuation.md`; portfolio construction belongs to
`investment-portfolio-construction.md`.

Cross-reference: `protocols/taiwan-market-diagnosis.md` for the integration
workflow that sequences these four data signals into a single diagnostic pass.

## Primary Sources

- 臺灣證券交易所 (TWSE) (2024) *三大法人買賣超日報*. https://www.twse.com.tw/zh/trading/fund/T86.html. **Canonical daily institutional flow data**. The authoritative TWSE primary source for classification of the three institutional categories — 外資及陸資, 投信, 自營商 — and their daily net buy / sell aggregates. No secondary source overrides this classification.
- 公開資訊觀測站 (MOPS) (2024) *月營收資訊系統*. https://mops.twse.com.tw/mops/web/t05st10_ifrs. **Primary source for monthly revenue disclosures**. Statutory basis: 證券交易法第36條 + 金融監督管理委員會 (FSC) 台財證字令. TWSE- and OTC-listed companies must report monthly revenue by the **10th calendar day** of the following month; if the 10th falls on a holiday the next business day applies.
- 臺灣證券交易所 (TWSE) (2024) *董監事持股及質押資料查詢*. https://www.twse.com.tw/zh/company/insiderHoldings.html. **Primary source for director/supervisor shareholding and pledge ratios**. Statutory basis: 證券交易法第25條 (monthly disclosure) + 第22條之2 (pre-trade announcement required for changes ≥10% of personal holdings within 3 days before trade).
- 臺灣證券交易所 (TWSE) (2024) *融資融券餘額查詢*. https://www.twse.com.tw/zh/trading/margin/MI_MARGN.html. **Primary source for margin loan (融資) and short-sale (融券) balances**. 融資 = margin long (borrowing cash to buy shares); 融券 = short-sale borrow (borrowing shares to sell). These are OPPOSITE in directional signal. Do not conflate.
- 葉銀華 (2008) 《實踐公司治理》. 元照出版有限公司 (Angle Publishing). The canonical academic treatment of corporate governance for Taiwan-listed companies. Covers 董監持股 disclosure interpretation, tunnelling risk, and cross-shareholding structures. Primary source for the governance-risk interpretation layer of 董監持股 data.
- 金融監督管理委員會 (FSC) (2024) *公司治理藍圖3.0* (Corporate Governance Blueprint 3.0). https://www.fsc.gov.tw/ch/home.jsp?id=96&parentpath=0,2&mcustomize=news_view.jsp&dataserno=202301110001. FSC's current governance framework. The regulatory anchor for understanding how 董監持股 changes are monitored and what constitutes a governance red flag under current FSC policy.

## Critical Attribution Corrections

### 融資 and 融券 are OPPOSITE in directional signal — do not confuse

The most consequential LLM error in Taiwan equity analysis: **融資 and
融券 are not synonyms, not variants of each other, and not interchangeable**.
They carry opposite directional signals:

- **融資** (margin long) = an investor BORROWS CASH from a securities
  firm to BUY shares. A rising 融資 balance means **retail investors are
  bullish and leveraged long**. It is a measure of leveraged demand.
- **融券** (short-sale borrow) = an investor BORROWS SHARES from a
  securities firm to SELL SHORT. A rising 融券 balance means **bearish
  positioning is increasing**. It is a measure of short interest.

A stock with high 融資 balance and rising 融資 balance is one where retail
investors are crowding in long with borrowed money. A stock with high 融券
balance is one where traders are betting the price will fall. These
**point in opposite directions**. Any analysis that treats them as equivalent
"margin data" or "leveraged position data" without distinguishing direction
is fundamentally wrong. The TWSE primary source (MI_MARGN) reports both
on the same page; read the column headers explicitly.

**Banned conflation**: "margin balance" as a generic term without specifying
whether you mean 融資 (long margin) or 融券 (short borrow) is not acceptable
in any investing-team deliverable.

### 月營收 deadline is the 10th calendar day — not end-of-month, not the 15th

A second systematic LLM error: mis-stating the monthly revenue filing
deadline. The statutory deadline under 證券交易法第36條 and FSC administrative
order is the **10th calendar day of the following month**. If the 10th is a
Saturday, Sunday, or national holiday, the deadline shifts to the next
business day.

Common wrong answers that must not appear in deliverables:
- "companies report revenue by the end of the following month" — wrong
- "revenue is disclosed by the 15th" — wrong
- "revenue is disclosed monthly but the exact deadline varies" — wrong
  without specifying that it varies only due to holiday shifting from the 10th

The 10th-day deadline is meaningful for event-driven analysis: it creates a
predictable monthly announcement window (approximately the 1st–12th of each
month) during which TWSE-listed companies release prior-month revenue figures.
This window concentrates both news risk and price gaps for earnings-sensitive
names.

### 投信 is NOT 外資 — they are separate institutional categories with different signals

The TWSE T86 三大法人 classification separates three distinct entities.
**投信 and 外資 are not the same category** and carry different analytical
implications:

- **外資及陸資** includes all registered foreign institutional investors
  (SITCA-registered foreign funds, QFIIs, foreign proprietary desks) plus
  qualified mainland China investors (QDII, RQDII). This is the largest
  category by volume and is widely followed by market participants as the
  dominant price-setter.
- **投信** (Investment Trust / 投資信託) refers specifically to **domestic
  Taiwan mutual funds and ETF managers** registered under the Securities
  Investment Trust and Consulting Act (SITCA). These are wholly domestic
  entities — retail savings aggregators, pension-linked products, and
  domestic institutional buyers. Their flow dynamics are different from
  foreign capital: 投信 is subject to domestic regulatory mandates, has
  year-end performance pressure, and often acts counter-cyclically to 外資.

Calling 投信 "foreign investors" or treating 投信 flow as equivalent to
外資 flow nullifies the diagnostic value of institutional divergence signals
(see Section 1). The TWSE T86 report explicitly names and separates all
three categories; any claim that 投信 = 外資 or that they are sub-categories
of each other contradicts the primary source.

### 董監持股 pledge ratio above 50% is a governance risk flag — not a neutral data point

A fourth common error: reporting 董監持股 pledge ratios (質押比) as neutral
descriptive statistics without flagging governance risk. Per Yeh (2008)
and FSC Blueprint 3.0, a pledge ratio (shares pledged / total director
shares held) exceeding 50% signals that **a material portion of director
wealth is encumbered as loan collateral**. This creates structured
incentives to:

- Suppress disclosure of negative news to prevent margin-call triggering
  stock price declines
- Maintain artificially high share prices through buyback programs or
  earnings management
- Oppose capital-raising that dilutes the share price base

A pledge ratio is not simply "director pledged X% of shares" — it is a
**governance risk indicator** with interpretive obligations. Deliverables
must flag pledge ratios >50% as governance risk signals and cite Yeh 2008
as the interpretive framework. Reporting the ratio without the risk framing
is incomplete analysis.

## 三大法人 (Three Major Institutional Investors)

### Classification — authoritative taxonomy from TWSE T86

The TWSE T86 report defines exactly three categories. No Taiwan equity
analysis may use a different categorization without explicitly noting the
deviation from the TWSE primary source.

**外資及陸資** (Foreign Investors + Mainland China capital)

All SITCA-registered foreign institutional investors, qualified foreign
institutional investors (QFIIs), foreign proprietary trading desks, plus
qualified Renminbi-denominated mainland China investors (QDII / RQDII).
The category is aggregated under one line in T86 since the inclusion of
陸資 (mainland China capital) following liberalization; individual
foreign-vs-mainland breakdown is not provided in the standard T86 daily
report. Volume characteristics: the largest of the three categories by
average daily net flow. Behavioral characteristics: trend-following at
multi-month horizon; sensitive to USD/TWD and global risk-appetite
regime (see `investment-macro-regime.md` for RAI context).

**投信** (Investment Trust — domestic Taiwan mutual funds)

Domestic Taiwan fund managers registered under SITCA. This category
represents aggregated net flows from all Taiwan-domiciled mutual funds,
ETF managers, and discretionary trust accounts. Volume characteristics:
materially smaller than 外資 in normal conditions; can surge during
domestically-driven thematic cycles (e.g., government-mandate funds,
Taiwan strategic-industry ETFs). Behavioral characteristics: often
exhibits contrarian behavior relative to 外資 — highest diagnostic value
when the two categories diverge (see Integration Signals below). Subject
to domestic regulatory mandates, year-end performance reporting, and
retail subscription / redemption cycles.

**自營商** (Dealers — proprietary trading desks)

Proprietary trading desks of Taiwan securities firms. This category
includes both directional and hedging activity from dealer books.
Volume characteristics: variable; not systematically large relative to
外資. Behavioral characteristics: lower directional signal value because
dealer flows include structured-product delta hedging, index arbitrage,
and options market-making rebalancing — activities that are price-neutral
in aggregate. Use 自營商 data as context, not as a primary signal.

### How to Read the Data

The T86 report provides daily net buy (買超) and net sell (賣超) figures
for each category across all TWSE-listed stocks in aggregate. Company-level
institutional flow requires querying the TWSE individual-stock institutional
page or Bloomberg/Refinitiv terminals.

**Buy/sell terminology**:
- 買超 = net buy (total purchases minus total sales > 0)
- 賣超 = net sell (total purchases minus total sales < 0)
- These are NET figures, not gross volume. A 買超 of NT$500M means the
  institution bought NT$500M more than it sold that day — not that it
  purchased NT$500M in total.

**Preferred aggregation windows**:

| Window | Use case |
|--------|----------|
| **Single day** | Noisy; useful only for same-day event reactions |
| **5-day rolling sum** | Short-term momentum; captures week-level flows |
| **20-day rolling sum** | Primary signal window; smooths intra-week noise; aligns with monthly calendar |
| **60-day rolling sum** | Structural positioning; identifies multi-month accumulation or distribution |

Single-day data is insufficient for thesis formation. Use 20-day rolling
sum as the default when describing institutional positioning.

### Integration Signals — reading concordance and divergence

**Strongest bullish institutional signal**: 外資 and 投信 both in 買超
(net buying) over a 20-day window, with self-reinforcing momentum (each
week's 5-day sum positive). This concordance indicates both global capital
allocators and domestic fund managers are increasing exposure simultaneously
— a high-conviction accumulation pattern.

**Monitoring signal — institutional divergence**: 外資 in 賣超 (selling)
while 投信 in 買超 (buying). This is not inherently bullish or bearish; it
requires context:
- If 外資 is selling due to global risk-off (rising DXY, EM outflows),
  投信 buying may reflect domestic value perception — a potential stabilizing
  floor, but not a reversal signal until 外資 reverses.
- If 外資 is selling on company-specific negative catalysts, 投信 buying
  may indicate domestic funds "catching a falling knife" — a risk signal.
  Check 月營收 trend and 董監持股 for corroboration.

**De-risking signal**: All three categories simultaneously in 賣超 over
a 5–10-day window is a high-confidence de-risking signal. Three-way
selling indicates no institutional category is providing demand support.

**自營商 anomaly check**: A day where 自營商 net flow is outsized and
directionally opposite to 外資 and 投信 usually reflects structured-product
rebalancing, not a directional call. Do not over-interpret single-day
dealer flows.

### Anti-drift

When citing 三大法人 data:
- Use the exact TWSE T86 category names: 外資及陸資 / 投信 / 自營商
- Never substitute "institutional investors" without specifying which category
- Never treat 投信 as a foreign investor category
- Always specify the aggregation window (1-day / 5-day / 20-day) when
  stating a net flow figure
- Cite TWSE T86 as the primary source for all institutional flow claims

## 月營收 (Monthly Revenue)

### Disclosure Rules — statutory basis

**Governing law**: 證券交易法第36條 (Securities and Exchange Act Article 36)
plus FSC administrative order (台財證字令). All TWSE- and TPEX-listed
companies are required to file monthly revenue by the **10th calendar day
of the month following the reporting month**. If the 10th falls on a
Saturday, Sunday, or public holiday, the deadline extends to the next
business day.

**Filing unit**: NT$ thousands (新台幣仟元), unaudited, as filed by the
reporting entity. Whether the filing represents consolidated (合併) or
standalone (個體) revenue depends on the company's reporting election;
verify against the MOPS filing metadata. For companies with overseas
subsidiaries or manufacturing affiliates, consolidated revenue is the
relevant figure for revenue-trend analysis. Standalone revenue can
significantly under-represent total operations.

**Filing platform**: 公開資訊觀測站 (MOPS) at mops.twse.com.tw. The
月營收資訊系統 is the canonical access point for both raw filings and
the MOPS-provided year-over-year comparison tools.

**Announcement concentration**: The practical release window is the
1st–12th calendar day of each month, with the heaviest disclosure
concentration on the 8th–10th. Event-driven analysis must account for
this concentration: surprise beats or misses tend to produce intra-day
price gaps on announcement day; post-announcement drift is common for
names with thin institutional coverage.

### Analytical Framework

**MoM (月增率)**: Month-over-month percentage change. Seasonality-sensitive:
January is typically depressed due to Chinese New Year production shutdowns;
February is often elevated as the post-CNY catch-up month; Q3 months tend
to be strong for export-oriented electronics and semiconductor names ahead
of holiday inventory build. MoM is useful for detecting plant shutdowns,
order pull-forwards, and short-term demand shocks, but requires seasonal
adjustment before drawing trend conclusions.

**YoY (年增率)**: Year-over-year percentage change. Removes seasonality
by comparing the same calendar month across years. The **primary revenue
signal** for trend analysis. A sustained positive YoY growth rate is the
baseline for revenue-inflection identification.

**3-month YoY rolling average**: Smooths one-off effects (typhoon shutdowns,
customer inventory adjustments, plant fires, Chinese New Year timing
differences between years). The preferred indicator for determining whether
a revenue acceleration is structural or transient:
- Three consecutive months of accelerating YoY growth (+X%, +Y%, +Z%
  where Z > Y > X) = **revenue inflection point** — the pattern most
  likely to attract 外資 attention and trigger price re-rating
- Two consecutive misses following a period of beats = early warning of
  demand deceleration, warranting downside thesis review

**Consensus vs actuals**: For names covered by institutional research
(Bloomberg consensus available), the beat/miss relative to consensus is
more information-relevant than the absolute YoY figure — the market
has already priced the consensus estimate. For small/mid cap names with
no coverage, absolute YoY and sequential trend are the primary signals.

### Revenue as Leading Indicator — bounded applicability

月營收 is a **leading indicator for earnings trends, not a substitute for
earnings analysis**. Revenue growth is necessary but not sufficient for
earnings improvement. Gross margin and operating leverage determine whether
revenue growth translates to profit growth:

- High-fixed-cost businesses (fab-lite or fabless semiconductor names,
  OSAT packaging) exhibit strong operating leverage: revenue acceleration
  above the breakeven point generates disproportionate profit growth
- Low-gross-margin businesses (EMS/ODM assemblers, component distributors)
  require sustained volume growth to move the earnings needle materially
- Gross margin compression (visible in quarterly earnings, not monthly
  revenue) can cause a revenue beat to coincide with an earnings miss

Never present a 月營收 beat as equivalent to an earnings beat. They are
different data points with different analytical weight.

### Anti-drift

When citing 月營收 data:
- State the statutory deadline as "10th calendar day of the following month"
  — never "end of month", never "15th", never "mid-month"
- Always specify whether the cited figure is consolidated or standalone
- Cite MOPS as the primary filing platform
- Cite 證券交易法第36條 as the statutory basis if the deadline or
  disclosure obligation is at issue
- Distinguish MoM from YoY explicitly; do not mix them in the same sentence
  without labeling both

## 董監持股 (Director and Supervisor Shareholdings)

### Disclosure Rules — statutory basis

**Monthly disclosure (證交法第25條)**: Directors and supervisors of
TWSE/TPEX-listed companies must report their total shareholding monthly.
The TWSE aggregates these filings and publishes the data via the
董監事持股及質押資料查詢 portal. The data includes total shares held and
total shares pledged (質押) for each named director/supervisor.

**Pre-trade announcement (證交法第22條之2)**: Directors and supervisors
intending to trade shares in a volume that exceeds 10% of their personal
holdings must publicly announce the intention at least 3 days before
executing the trade. This requirement creates a visible signal: a
pre-announced director sale above the 10% threshold is a factual, publicly
disclosed insider distribution event.

**Pledging disclosure**: Shares pledged as loan collateral (質押) are
disclosed separately from total shareholding. The pledge ratio is
calculated as: (total pledged shares / total shares held) × 100%. The
TWSE portal provides both figures per director/supervisor.

### Pledge Ratio — governance risk interpretation

The pledge ratio is the primary governance risk variable in 董監持股 data.
Per Yeh (2008) *實踐公司治理* — the canonical academic framework for
Taiwan-listed company governance risk:

**Pledge ratio thresholds** (Yeh 2008 framework, FSC Blueprint 3.0 context):

| Pledge ratio | Interpretation |
|---|---|
| <30% | Normal; some collateralized financing, not alarming |
| 30–50% | Elevated; warrants monitoring; director wealth significantly exposed |
| >50% | **Governance risk flag**: majority of director holdings encumbered; forced-sale trigger risk |
| >80% | Severe; any meaningful stock price decline risks forced liquidation by creditors |

When a director's shares are pledged and the stock price falls to the
creditor's margin-call level, the creditor can force-sell the pledged shares
to recover the loan — creating a self-reinforcing downward price spiral.
Directors in this position have strong incentives to:

1. **Delay disclosure of negative news** that would trigger a price decline
2. **Advocate for aggressive share buybacks** to support the price floor
3. **Oppose operational decisions** (new capital raises, debt restructuring)
   that reduce share price in the short term, even if value-accretive long-term

This creates a structural conflict between maximizing shareholder value and
protecting personal collateral positions. FSC Blueprint 3.0 identifies
high pledge ratios as a monitoring priority for governance examinations.

### Cross-shareholding and tunnelling risk (Yeh 2008)

Beyond pledge ratios, Yeh (2008) identifies two structural governance risks
specific to Taiwan's corporate ownership landscape:

**Low director shareholding + high cross-shareholding**: When board members
hold small personal equity stakes while control is maintained through
cross-shareholding structures (pyramid shareholding, circular ownership via
affiliated companies), the director's personal downside from poor decisions
is limited while extraction opportunities exist. This is Yeh's
"tunnelling risk" framework: resources can be shifted from listed entities
to unlisted affiliated entities in ways that benefit controlling shareholders
at the expense of minority shareholders.

**Sustained monthly shareholding decline by majority of board members**:
When multiple directors simultaneously and consistently reduce their
individual shareholdings across multiple reporting months, this is an
insider distribution pattern. It is distinct from a single director's
pre-announced trade (which is also a signal but more limited in scope).
Multi-director sustained decline across 3+ months = high-confidence
distribution thesis.

**Sudden large increase in director shareholding**: Requires source
verification — could be secondary offering, ESOP exercise, directed issue
to board members, or genuine open-market insider buying. These have
different governance implications. An ESOP exercise does not signal the
same bullish conviction as a board member making large open-market
purchases at prevailing prices.

### Anti-drift

When citing 董監持股 data:
- Always state the pledge ratio numerically; never omit the denominator
  (pledged shares / total shares held)
- Flag any pledge ratio >50% as a governance risk signal; cite Yeh 2008
- Cite 證交法第25條 for the monthly disclosure obligation
- Cite 證交法第22條之2 for pre-trade announcement obligations
- Distinguish individual director data from company-level aggregate data

## 融資融券 (Margin Long / Short-Sale Balances)

### Critical Distinction — LLM hallucination hotspot

**融資 (margin long)**: An investor opens a margin account with a securities
firm, deposits margin collateral, and borrows the remaining purchase amount
in cash from the firm to buy shares. The outstanding loan balance is the
融資餘額 (margin loan balance). High and rising 融資 balance indicates
**leveraged retail bullish positioning**. It is directionally LONG.

**融券 (short-sale borrow)**: An investor borrows shares from a securities
firm and immediately sells them, expecting to buy them back at a lower price
later. The outstanding borrowed-shares balance is the 融券餘額 (short borrow
balance). High and rising 融券 balance indicates **increasing bearish
positioning / short interest**. It is directionally SHORT.

These two instruments are opposite sides of market positioning. A stock
with high 融資 and low 融券 is one where retail bulls are heavily
leveraged. A stock with high 融券 and low 融資 is one where short sellers
are betting on a decline. Aggregate 融資 + 融券 is not a "total leverage"
figure — it is two opposite signals added together, which produces
analytically meaningless output.

**TWSE primary source**: 融資融券餘額查詢 (MI_MARGN) at TWSE, providing
daily 融資餘額, 融資限額, 融券餘額, and 融券限額 by stock.

### Key Metrics

**融資使用率** (Margin utilization rate):

```
融資使用率 = (融資餘額 / 融資限額) × 100%
```

The TWSE sets 融資限額 (margin loan capacity limit) per stock based on
market cap and other criteria. The utilization rate measures how much of
the permitted margin capacity is currently in use.

| 融資使用率 | Interpretation |
|---|---|
| <30% | Low retail leverage; margin not a significant market factor |
| 30–50% | Moderate; retail participation but not crowded |
| 50–70% | **Elevated**; monitoring warranted; distribution pressure risk if price falls |
| >70% | **Overheated retail leverage**; high forced-selling risk on any price decline |
| >80% | Extreme; historically associated with distribution phase tops |

**融券占股本比率** (Short interest as % of issued shares):

```
融券占股本比率 = (融券餘額 [shares] / 公司已發行股數) × 100%
```

| Short interest % | Interpretation |
|---|---|
| <2% | Negligible short interest |
| 2–5% | Normal range for liquid TWSE stocks |
| 5–10% | **Meaningful short interest**; potential short-squeeze fuel if catalyst emerges |
| >10% | **High short interest**; significant bearish conviction AND significant short-squeeze potential |

**融資融券比** (Long margin / short borrow ratio):

```
融資融券比 = 融資餘額 (shares) ÷ 融券餘額 (shares)
```

A high ratio (many margin longs relative to short borrows) indicates the
market structure is crowded long with retail leverage. This is not bullish
— it indicates that selling pressure from forced margin calls will be
proportionally large relative to short-covering demand. A low ratio indicates
short sellers dominate the leverage structure; a price rally could trigger
disproportionate short covering.

### Signal Interpretation

**Rising 融資 + falling price = forced-selling risk**

When 融資 balance rises (or stays elevated) while price declines, leveraged
retail investors are holding losing positions with declining collateral
value. As collateral value falls, securities firms issue margin calls;
investors who cannot meet the calls are force-sold. This creates a
feedback loop: forced selling → lower price → more margin calls → more
forced selling. A stock in this pattern is a distribution pressure / forced-
selling risk situation, not a buying opportunity, until 融資 balance
cleanses (declines substantially) or price stabilizes above key collateral
levels.

**Rising 融資 + rising price = crowded retail long with growing leverage risk**

The price is rising but so is the leverage. This can continue during strong
momentum phases but creates increasing fragility: any negative catalyst
triggers the margin-call loop described above. High 融資 utilization during
a price uptrend is a risk management flag, not confirmation of a clean trend.

**Rising 融券 + rising price = short-squeeze potential**

Short sellers are increasing positions against rising price. If the price
continues to rise, short sellers face mounting mark-to-market losses and
may need to cover (buy back shares), accelerating the price rise. A stock
with >5% short interest and an emerging positive catalyst (strong 月營收,
concordant 外資 + 投信 buying) has elevated short-squeeze potential.

**Sharp 融資 decline = de-leveraging complete, potential base**

A rapid, large decline in 融資 balance (typically over 5–15 trading days)
means margin accounts are being closed: either by forced sales after margin
calls or by voluntary liquidation by retail investors cutting losses. When
the 融資 balance stabilizes at a lower level after a steep decline, the
forced-selling overhang is reduced. This pattern — steep 融資 decline
followed by balance stabilization — is one indicator of a potential price
base, to be confirmed by 三大法人 and 月營收 signals.

**Low 融資 utilization = no retail overhanging supply**

When 融資 utilization is below 30%, retail margin is not a significant
market factor. In this context institutional flow (三大法人) and
fundamental catalysts (月營收 trend) carry more weight in thesis formation
because there is no retail leverage overhang to complicate the price action.

### Anti-drift

When citing 融資融券 data:
- Always specify whether you mean 融資 (long margin) or 融券 (short borrow)
  — never use "margin balance" generically
- State the direction of each: 融資 = bullish retail leverage; 融券 = bearish
  short positioning
- Cite TWSE MI_MARGN as the primary data source
- When reporting 融資使用率, always include both 融資餘額 and 融資限額
- Never add 融資 and 融券 balances to produce a "total leveraged position" —
  they are opposite signals

## Integration Pattern — Taiwan Equity Diagnosis

Standard four-step diagnostic sequence for Taiwan equity analysis. Cross-
reference `protocols/taiwan-market-diagnosis.md` for the full workflow;
this section defines the logic ordering rationale.

### Step 1: 月營收 trend (3-month YoY)

**Question**: Is revenue accelerating, decelerating, or flat?

Revenue trend is the **first filter** because it establishes whether the
fundamental business is improving. A revenue inflection point (three
consecutive months of accelerating YoY growth) is the most common
catalyst for institutional re-rating. If the revenue trend is negative or
decelerating, the remaining signals operate in a headwind environment;
re-rating theses require either a revenue recovery thesis or a valuation /
restructuring angle independent of revenue trend.

Priority data points:
- 3-month YoY rolling average and its direction (accelerating / decelerating)
- Consolidated vs standalone (verify against MOPS filing metadata)
- Latest month vs consensus estimate (beat/miss magnitude)
- Seasonality context (CNY impact, Q3 electronics build)

### Step 2: 三大法人 cumulative 20-day flow

**Question**: Are institutions accumulating or distributing?

Institutional flow follows revenue inflection with a lag: 外資 typically
begins accumulating 1–3 months after a consistent revenue beat pattern
emerges. Checking 三大法人 20-day cumulative flow reveals whether the
market is in the early accumulation phase, mid-trend, or late-stage
distribution.

Priority data points:
- 外資 20-day cumulative (+ = accumulation; - = distribution)
- 投信 20-day cumulative (concordant or divergent with 外資?)
- 自營商 direction (contextual check only)
- Concordance assessment: both 外資 and 投信 positive = strongest signal

### Step 3: 融資使用率 (retail leverage check)

**Question**: Is retail margin a risk factor (overhanging supply or forced-
selling potential)?

High 融資 utilization (>60%) in an uptrend signals late-stage retail
participation and growing fragility. The question is not "is retail buying
good?" but "does the current retail leverage level create near-term
forced-selling risk that could interrupt the thesis?"

Priority data points:
- 融資使用率 current level and direction (rising or declining)
- 融資融券比 for crowding assessment
- 融券占股本比率 for short-squeeze potential (if relevant)

### Step 4: 董監持股 trend and pledge ratio

**Question**: Are there governance risks that could impair the thesis?

Governance risk is checked last not because it is least important but
because it is the slowest-moving signal. Monthly disclosure frequency
means this data lags real-time conditions. However, if a high pledge ratio
or sustained director selling pattern exists, it functions as a thesis
modifier regardless of how strong Steps 1–3 look.

Priority data points:
- Overall director pledge ratio (governance risk if >50%)
- Month-over-month change in director shareholding aggregate (distribution
  pattern if declining over 3+ months)
- Any pre-announced large director trades (証交法第22條之2 disclosures)

### Integration output

A complete Taiwan equity diagnostic statement should cover all four
signals with a directional assessment and a confidence level:

```
Revenue (Step 1): [accelerating / decelerating / flat] — [YoY range, window]
Institutional (Step 2): [accumulating / distributing / mixed] — [20-day, 外資/投信 direction]
Retail leverage (Step 3): [low / moderate / elevated / overheated] — [融資使用率 %]
Governance (Step 4): [clean / monitor / risk flag] — [pledge ratio, director trend]

Integrated signal: [bullish / bearish / mixed / insufficient data]
Primary risk to thesis: [name the signal that contradicts or qualifies the primary call]
```

A thesis supported by accelerating revenue + concordant institutional
accumulation + low retail leverage + clean governance is the highest-
conviction combination. Any single signal in the opposite direction is a
qualifier; two or more opposing signals require thesis revision.

## Relationship to Other Standards

| Standard | Relationship |
|---|---|
| `investment-macro-regime.md` | L1 macro regime (Investment Clock, GIP Quad) provides the global context in which Taiwan equity analysis sits. A Taiwan stock in a revenue acceleration trend performs differently in IC Recovery vs IC Stagflation. |
| `investment-sector-industry.md` | Sector / industry classification determines which monthly revenue seasonality pattern applies and which institutional flow dynamics are normal vs anomalous for that sector. |
| `investment-security-valuation.md` | Valuation multiples and earnings models are the downstream consumer of 月營收 trend analysis. Revenue trend sets the earnings revision direction; valuation determines whether the re-rating has room to run. |
| `investment-portfolio-construction.md` | Position sizing and risk management decisions use 融資使用率 and 董監持股 pledge ratios as tail-risk modifiers. High retail leverage or high pledge ratio = increased event-risk = reduced position size per risk budget. |

These standards are **complementary layers**. A complete Taiwan equity
investment thesis integrates all four layers: global regime context (L1
macro) + sector placement (L2 sector/industry) + security-level
fundamentals and valuation (L3 security) + Taiwan-specific structured
disclosure signals (this standard).

See also: `protocols/taiwan-market-diagnosis.md` for the operational
step-by-step workflow that sequences these signals into a single
diagnostic session.

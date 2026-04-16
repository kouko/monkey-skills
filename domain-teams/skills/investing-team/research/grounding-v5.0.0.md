# investing-team Grounding Audit — v5.0.0

**Version context**: domain-teams v5.0.0. This release introduces `investing-team` as a new domain team, simultaneously retiring `research-team`'s Investment Analysis workflow. The 4 foundational investment standards are migrated from research-team (where they were grounded at v4.9.0 and extended at v4.11.0); 7 new standards cover the decision/verdict/sizing/Taiwan/data layer that was absent.

---

## Standards Audit

### Migrated from research-team (v4.11.0 grounding inherited)

These four files are copied verbatim from `research-team/standards/`. Their primary-source grounding was established in `research-team/research/grounding-v4.9.0.md` and extended in `research-team/research/grounding-v4.11.0.md`. This note records the migration; the detailed attribution corrections remain in those files.

| File | Tier | Primary Sources Count | Grounding Origin | Notes |
|---|---|---|---|---|
| `investment-macro-regime.md` | 3 | 10 | research-team v4.9.0 + v4.11.0 | IC / Dalio / Koo / Hedgeye GIP / MMT (Mosler+Wray+Kelton) / GRAI (Kumar&Persaud 2002) |
| `investment-sector-industry.md` | 3 | 7+ | research-team v4.9.0 + v4.11.0 | Fama-French 1993/2015 / Carhart 1997 / sector rotation / JP exception (Kubota-Takehara) |
| `investment-security-valuation.md` | 3 | 6+ | research-team v4.9.0 + v4.11.0 | Damodaran 2012 / Graham&Dodd / Campbell&Shiller 1998 CAPE / Penman / Koller et al. |
| `investment-portfolio-construction.md` | 2 | 5+ | research-team v4.9.0 + v4.11.0 | Taleb 2012 Barbell / Bridgewater All-Weather / 60/40 / Sharpe 1964 CAPM critique |

**Migration rationale**: These standards were authored for an investor-perspective analytical workflow but lived inside `research-team`, which is oriented toward business/academic research. The separation at v5.0.0 reflects a clarity principle: frameworks designed for "should I buy this asset?" belong in `investing-team`, not `research-team`. The file bodies are unchanged; only the host directory changes.

---

### New Standards (authored at v5.0.0)

#### `investment-thesis-structure.md` — Tier 2

**Primary sources grounded on:**
- Bevelin 2007 *Seeking Wisdom* — inversion / mental models checklist
- Fisher 1958 *Common Stocks and Uncommon Profits* Ch.3 — 15-point qualitative checklist / scuttlebutt
- Drobny 2006 *Inside the House of Money* — variant perception as the load-bearing thesis question
- Marks 2011 *The Most Important Thing* — second-level thinking prerequisite
- Mauboussin 2012 *The Success Equation* — calibration, pre-mortem technique

**Tier 2 justification**: LLMs know the broad concepts (variant perception, inversion, pre-mortem) but routinely (a) conflate variant perception with contrarianism, (b) treat pre-mortem as retrospective, (c) misidentify Fisher's scuttlebutt as social media sentiment. Tier 2 because these distinctions are known to the model but require explicit spelling out for precision — not the same severity as Tier 3 hallucination hotspots like the IC 4-phase naming.

**Attribution corrections established**:
1. Variant perception ≠ contrarianism. Variant perception is a specific claim: "I believe X and consensus believes ¬X, and here is why I am right." Pure contrarianism is betting against consensus without a positive reason.
2. Pre-mortem is prospective, not retrospective. Mauboussin's pre-mortem imagines failure before it occurs; a post-mortem analyzes failure after it occurred. Do not conflate.
3. Fisher's scuttlebutt = structured qualitative fieldwork (interviewing suppliers, customers, competitors, ex-employees). NOT social media sentiment or web scraping.

---

#### `decision-framework-and-verdict.md` — Tier 2

**Primary sources grounded on:**
- Graham & Dodd 1934/2008 *Security Analysis* Ch.20 — margin of safety (buy only when intrinsic value substantially exceeds price)
- Klarman 1991 *Margin of Safety* Ch.4 + Ch.6 — intrinsic value as range; discount calibrated to estimation error
- Damodaran 2012 *Investment Valuation* Ch.35 — bias catalog: anchoring, confirmation, narrative, recency, overconfidence, endowment effect
- Kahneman 2011 *Thinking Fast and Slow* Ch.12 + Ch.24 — overconfidence; inside vs outside view; reference class forecasting
- Mauboussin & Callahan 2014 "A Checklist for Superforecasters" (Credit Suisse) — base rates, evidence updating, skill vs luck

**Tier 2 justification**: LLMs know Graham's margin of safety concept at a surface level but routinely (a) conflate MoS with stop-loss, (b) use "BUY" to mean "I like this company" rather than a specific valuation condition, (c) present Damodaran's bias catalog as normative (biases are always present) rather than descriptive (biases occur, here is how to detect and correct).

**Attribution corrections established**:
1. Margin of safety ≠ stop-loss. MoS is the gap between intrinsic value and market price at the time of purchase. A stop-loss is a post-purchase exit rule. They operate at different stages and serve different purposes.
2. BUY verdict requires a specific valuation condition (price ≤ intrinsic_value × MoS factor), not a qualitative assessment of business quality.
3. Damodaran's bias catalog is descriptive: it lists biases that commonly distort valuations, with detection and de-biasing actions. It does NOT assert valuations are always distorted.
4. Conviction grade (A/B/C) is orthogonal to verdict direction (BUY/HOLD/SELL). A Grade C BUY is possible: a speculative undervalued situation with high uncertainty. Size reflects the grade, not the verdict.

---

#### `position-sizing-and-risk.md` — Tier 2

**Primary sources grounded on:**
- Kelly 1956 *Bell System Technical Journal* 35(4) — exact formula: f* = (bp − q) / b
- Thorp 2006 in *Handbook of Asset and Liability Management* — fractional Kelly (f*/2, f*/4) as practical compromise
- CFA Institute 2024 Curriculum Vol. 6 — risk budgeting: allocate VaR, not capital
- Taleb 2007 *The Black Swan* Ch.15 — VaR failure in fat-tailed distributions
- Taleb et al. 2012 IMF WP/12/216 — fragility heuristic: asymmetric harm from negative deviations
- Vince 1992 *The Mathematics of Money Management* — optimal-f, terminal ruin probability

**Tier 2 justification**: LLMs know Kelly and VaR but routinely (a) mis-state the Kelly formula as f* = p − q (forgetting to divide by b), (b) describe fractional Kelly as a risk-aversion parameter when it is actually a correction for probability estimation error, (c) describe VaR as measuring the worst-case loss when it measures only the confidence-threshold loss, not the tail.

**Attribution corrections established**:
1. Kelly formula: f* = (bp − q) / b, NOT f* = p − q. The p − q form is only correct when b = 1 (even-odds bet), which is never true in equity investing.
2. Fractional Kelly is NOT a risk-aversion parameter. It is a practical correction for the fact that investors mis-estimate p (the win probability). Thorp's argument: if your p is wrong by ε, full Kelly will over-bet catastrophically; f*/2 or f*/4 provides a safety margin against estimation error.
3. VaR does NOT measure worst-case loss. It measures the loss at the Xth percentile confidence level. The tail beyond that percentile is explicitly excluded — and that excluded tail is exactly where ruin lives (Taleb).

---

#### `taiwan-equity-frameworks.md` — Tier 3

**Primary sources grounded on:**
- TWSE T86 三大法人買賣超日報 (https://www.twse.com.tw/zh/trading/fund/T86.html)
- MOPS 月營收資訊系統 (https://mops.twse.com.tw/mops/web/t05st10_ifrs); statutory: 證交法第36條
- TWSE 董監事持股及質押查詢 (https://www.twse.com.tw/zh/company/insiderHoldings.html); statutory: 證交法第25條 + 第22條之2
- TWSE 融資融券餘額查詢 (https://www.twse.com.tw/zh/trading/margin/MI_MARGN.html)
- 葉銀華 2008 《實踐公司治理》元照出版 — governance risk interpretation for 董監持股
- FSC 公司治理藍圖3.0 (2024) — regulatory anchor for 董監持股 monitoring

**Tier 3 justification**: LLMs frequently (a) reverse 融資 and 融券 directional signals, (b) mis-state the 月營收 deadline (10th calendar day, not end of month or 15th), (c) conflate 投信 (domestic mutual funds) with 外資 (foreign investors) as single "institutional" category, (d) mis-interpret high pledge ratio as neutral when it is a governance risk signal. These are cold-query hallucination hotspots with high investment-decision impact.

**Attribution corrections established** (4 high-severity):
1. 融資 (margin long) and 融券 (short-sale borrow) are OPPOSITE in directional signal. Rising 融資 = retail bullish/leveraged. Rising 融券 = bearish positioning. LLMs routinely merge them as "margin trading" with a single directional interpretation.
2. 月營收 deadline is the **10th calendar day** of the following month, per 證交法第36條 + FSC administrative order. Not end of month. Not the 15th. This affects timeliness assessment of analyst models.
3. 三大法人 = 外資及陸資 + 投信 + 自營商. These three categories have different characteristics: 外資 is large/trend-following; 投信 is smaller/often contrarian to 外資; 自營商 is often hedging. Do not treat them as interchangeable "institutions."
4. High 董監持股 pledge ratio (>50%) is a governance RED FLAG, not a neutral data point. High pledging creates incentive to suppress bad news to maintain stock price and avoid margin calls (葉銀華 2008).

**Taiwan-specific sourcing note**: There is no Taiwan-equivalent of the global academic canon (no "Taiwan Investment Clock," no peer-reviewed Taiwan-specific valuation framework parallel to Damodaran). The frameworks in this file are: (a) regulatory primary sources (TWSE/MOPS/FSC/法條) for disclosure rules and data taxonomy, and (b) 葉銀華 2008 for governance interpretation. The valuation and macro frameworks for Taiwan equities use the global standards in the migrated files (Damodaran, Investment Clock, Fama-French) applied to Taiwan context.

---

#### `strategic-frameworks-investor-lens.md` — Tier 2

**Primary sources grounded on:**
- Porter 1980 *Competitive Strategy* — Five Forces (source framework; investor interpretation is derived)
- Greenwald & Kahn 2005 *Competition Demystified* — barriers to entry as ROIC sustainability test; replication cost question
- Dorsey 2008 *The Little Book That Builds Wealth* — 4 moat sources: intangible assets, switching costs, network effects, cost advantages
- Henderson 1970 BCG Perspective No. 66 — canonical BCG Matrix origin
- Mauboussin & Rappaport 2016 *Expectations Investing* — price-implied growth rate; backward-reading stock prices to extract consensus expectations

**Tier 2 justification**: LLMs know Porter and BCG but routinely (a) use Porter as a company-level checklist rather than an industry-structure framework, (b) conflate "competitive advantage" with "economic moat" (Greenwald: moat specifically requires barriers high enough to sustain above-WACC returns), (c) present BCG as an investment signal when Henderson 1970 designed it as a resource-allocation tool.

**Dual-home note**: `research-team/standards/strategic-frameworks.md` covers these same frameworks from an operator perspective (market entry, competitive positioning for business strategy). This file covers the investor perspective. Both files should note the other's existence to guide team routing.

**Attribution corrections established**:
1. Porter's Five Forces is an INDUSTRY-structure analysis tool. It answers "how structurally profitable is this industry?" not "is this company good?" The unit of analysis is the industry, not the firm.
2. Economic moat (Greenwald) ≠ competitive advantage. A moat specifically means barriers high enough to sustain returns ABOVE the cost of capital over a long time horizon. A competitive advantage that doesn't translate to above-WACC returns is not a moat.
3. BCG Matrix was designed for capital allocation across business units in a diversified corporation. The investor interpretation (using it to assess management capital discipline) is a derived application, not what Henderson 1970 describes.

---

#### `data-sources-and-fixtures.md` — Tier 2

**Primary sources grounded on:**
- 12factor.net Factor III (Config) + Factor X (Dev/prod parity) — credentials in env vars; data provenance discipline
- TWSE/MOPS (canonical Taiwan filings portal)
- SEC EDGAR (canonical US company filings)
- FRED (canonical US macro series)
- yfinance (ranaroussi/yfinance) — documented as unofficial, price-only, NOT for financials

**Tier 2 justification**: LLMs routinely (a) confuse MOPS as a third-party aggregator when it IS the statutory filing portal, (b) use yfinance for financial statement data when it is price-only / unofficial, (c) claim FRED is current-day when series have publication lags. These are data-quality errors with direct impact on investment analysis correctness.

---

#### `backtesting-and-robustness-discipline.md` — Tier 2

**Primary sources grounded on:**
- López de Prado 2018 *Advances in Financial Machine Learning* Ch.7 — CPCV, deflated Sharpe, overfitting
- Harvey, Liu & Zhu 2016 *Review of Financial Studies* 29(1) — multiple testing; t ≥ 3.0 threshold
- Lo 2002 *Financial Analysts Journal* 58(4) — annualized Sharpe; non-i.i.d. correction
- Bailey, Borwein, López de Prado & Zhu 2014 *Notices AMS* 61(5) — PBO definition; BBLZ metric
- Arnott, Harvey & Markowitz 2019 *JFDS* 1(1) — 5-step backtesting protocol

**Tier 2 justification**: LLMs know the concept of backtest overfitting but routinely (a) apply HLZ's t ≥ 3.0 threshold to all quantitative signals rather than specifically to novel cross-sectional factor discovery, (b) describe the deflated Sharpe ratio without the correct co-authorship (Bailey & López de Prado 2014, NOT López de Prado alone), (c) conflate in-sample and out-of-sample without the purging requirement for time-series leakage.

---

## Extraction Decision Record

**Why v5.0.0 is a MAJOR bump (not MINOR)**: The retirement of `research-team`'s Investment Analysis workflow is a breaking change. Users who invoked research-team for investment analysis will now be routed to investing-team via the updated `using-domain-teams` router. The 4 migrated standards are removed from `research-team/standards/` in Commit 3/3. Any session relying on `research-team`'s investment-* file paths will break.

**Why clean extraction over dual-home**: A dual-home approach (keep in research-team, also add to investing-team) would:
- Create two SSOT for the same content → drift risk
- Perpetuate the conceptual confusion between "research-team = academic research / business analysis" and "investing-team = personal investment decisions"
- Require a disambiguation layer that adds cognitive overhead without adding value

The clean extraction reflects the principle: "research-team = researcher/analyst/operator perspective; investing-team = investor perspective." This is the user-role separation principle established at v5.0.0.

**strategic-frameworks dual-home exception**: `research-team/standards/strategic-frameworks.md` (Porter/BCG/PESTEL from operator perspective) is intentionally kept in research-team AND `investing-team/standards/strategic-frameworks-investor-lens.md` is added. This is NOT drift — the two files have different interpretive lenses, cite partially overlapping but distinct primary sources (Greenwald & Kahn 2005 is investor-specific), and serve different analytical purposes. Each file notes the existence of the other.

# XBRL verification universe — SEC operational-KPI pipeline

A curated, **live-verified** set of real SEC filers used as the ground-truth
sampling pool for `data-markets` / `analysis-kpi` XBRL work — live probes, live
shape-anchor tests, and regression checks. Every row was verified against real
SEC EDGAR XBRL (edgartools 5.42.0) on the date in §Provenance; nothing here is
guessed. Each company earns its slot by exercising a **distinct data shape** —
this is a diversity set, not a popularity list.

**How to use:** need a filer that exercises condition X (a non-December fiscal
year, a 52/53-week calendar, a bank revenue concept, an ADR 20-F regime, a
CostOfRevenue false-positive)? Pick from the §Special-condition index, then draw
the row's details from §The universe. When adding a company, verify it live and
record what NEW shape it adds — if it duplicates an existing row's shape, it does
not earn a slot.

**Status legend:** ✅ VERIFIED (all listed facts confirmed live); ⚠️ PARTIAL
(regime/aggregate confirmed, dimensional detail not deep-checked); the ADR group
is regime-verified but mostly out-of-scope (see §ADR / foreign).

---

## Special-condition index (pick by the edge you need to exercise)

| Condition | Tickers | What it stresses |
|---|---|---|
| **Non-December fiscal year** | AAPL(Sep), COST(Aug/Sep), MSFT(Jun), PG(Jun), ORCL(May), NKE(May), CRM(Jan), WMT(Jan), HD(Jan), NVDA(Jan), MDT(**Apr**), TM/BABA/SONY(Mar), **INTU/CSCO(Jul)**, **ACN(Aug-fixed)**, **HPQ/AMAT/ADI(Oct/Nov)**, **LRCX(Jun-floating)** | fiscal-calendar classification; quarter boundaries ≠ calendar quarters |
| **July fiscal year** | INTU(Jul-31 fixed), CSCO(Jul floating 52/53wk) | the only July anchors — a FYE quarter unseen elsewhere |
| **Short XBRL history (post-2021 IPO)** | SNOW, PLTR | ~6 10-Ks only — a truncated multi-filing history (fewer years to stitch) |
| **Fintech / payments** | PYPL | plain `us-gaap:Revenues`, clean P,S,G — distinct from bank/insurer/asset-mgr concepts |
| **All 5 breakdown axes at once (P,S,G,Sub,Con)** | HPQ | the richest signature — stresses full dimensional + consolidation qualifier together |
| **Pure-SaaS revenue** | NOW, SNOW, WDAY | subscription revenue; NOW/WDAY leak CostOfRevenue/RPO false positives, SNOW is clean |
| **52/53-week (floating) calendar** | COST, HD, NVDA, AVGO, QCOM, ADBE, SBUX, PEP, DIS | odd quarter day-counts (13 vs 14 weeks), 53rd-week years, `fiscal_period` col sometimes absent |
| **Fixed-calendar retailer (NOT floating)** | WMT | looks like a 52/53-wk retailer but has fixed Jan-31 calendar quarters (irregular day counts) |
| **Bank revenue concept** | JPM, BAC, WFC, C | `RevenuesNetOfInterestExpense`; WFC tags BOTH `Revenues` + `RevenuesNetOfInterestExpense` (summation-collision risk) |
| **Insurer revenue concept** | PGR, MET, TRV | extension `*PremiumsEarned*` concepts, NOT a stable `us-gaap:PremiumsEarned` |
| **REIT / lease revenue** | PLD, AMT, O | `RentalRevenue`, ASC-842 straight-line components; ladder-schedule & pro-forma false positives |
| **Utility (non-ASC-606 + fuel-type)** | NEE, DUK, SO | `RevenueFromContractWithCustomer**Including**AssessedTax` (not Excluding!); DUK splits by fuel-type CONCEPTS not axes; SO `RevenueNotFromContractWithCustomer` |
| **ADR / foreign 20-F + 6-K (no 10-Q)** | TSM, ASML, SAP, NVO, AZN, SHEL, TM, BABA, UL, NU, SONY | out-of-scope regime; IFRS/US-GAAP basis; 6-K semi-annual or zero-XBRL (see §ADR) |
| **Multi-concept `us-gaap:Revenues`** | NFLX, KO, NVDA, T, VZ, DIS, PG, PEP, MCD, SBUX, ADBE, ORCL, XOM, COP | dimensional revenue under plain `Revenues`, not `RevenueFromContractWithCustomer` |
| **CostOfRevenue false-positive (dimensioned)** | **CAT**, AVGO, ADBE, TSLA, WMT, HD, CL, T, QCOM, NOW, IBM, DELL, HPQ | `us-gaap:CostOfRevenue`/COGS extensions tagged with breakdown axes → emitted as fake revenue by the current filter |
| **Percentage-value false-positive** | BA, HON, IBM, ADI, AMAT | `*RevenuePercentage`/`*RevenueChangePercent` extension concepts (value is a %, not $) pass the filter, dimensioned |
| **Deferred-revenue false-positive (dimensioned)** | SBUX, BLK | `DeferredRevenue*` liability concepts tagged dimensionally |
| **Geographic axis 10-K-only** | AAPL, JPM | a dimension present annually but absent from the 10-Qs → "no quarterly coverage" case |
| **ConsolidationItems intermittent** | KO | axis present in Q1 10-Q + 10-K, absent in Q3 10-Q — varies quarter-to-quarter |
| **Single-axis / minimal shape** | ISRG(Product only), CRM(P,G no S), LLY(no ConsolItems), TRV(no Product), MCD(S only) | axis-cardinality lower bound |
| **Subsegments axis** | NKE, T, NEM, MDT, ABT | the `srt:SubsegmentsAxis` path |
| **Real restatement (fixture)** | INTC | ClientComputingGroup FY2020 recast 40057M→40535M across FY21/FY22 10-Ks (scope-A xbrl_restatement_factpack.json) |
| **dei fiscal-year-end drifts per filing** | NVDA (--01-31 vs --01-25) | don't cache/hardcode FYE per ticker |

---

## The universe (by sector; all ✅ VERIFIED live unless noted)

Columns: Regime · FYE · top-line dimensional revenue concept(s) · dim axes
(P=ProductOrService, S=BusinessSegments, G=Geographical, Sub=Subsegments,
Con=ConsolidationItems) · false-positive `*Revenue*` concepts the current filter
would wrongly emit · Q4-directly-tagged (N everywhere observed).

### Technology — semiconductors
- **NVDA** · 10-K/10-Q · Jan(52/53wk, FYE drifts) · `us-gaap:Revenues` · P,S,G,Con · none · Q4:N
- **AVGO** · 10-K/10-Q · ~Nov-2(52wk) · RFCC-Excl · P,S,G · **CostOfRevenue + Semiconductor/InfrastructureSoftwareCostOfRevenue (dim COGS)** · Q4:N
- **QCOM** · 10-K/10-Q · ~Sep-28(52wk) · `Revenues`+RFCC · P,S,G · CostOfRevenue · Q4:N
- **AMD** · 10-K/10-Q · ~Dec-27(52wk) · RFCC-Excl · P,S,G · RPO-timing (minor) · Q4:N

### Technology — software / cloud
- **MSFT** · 10-K/10-Q · Jun-30 · RFCC-Excl · P,S · none · Q4:N
- **ORCL** · 10-K/10-Q · May-31 · `Revenues`+RFCC (+Cloud/Sw/HwRevenues ext) · P,S,G · RPO% · Q4:N
- **ADBE** · 10-K/10-Q · ~Nov-28(52wk) · `Revenues` · P,S,G · **CostOfRevenue + CostOfRevenueSignificantSegmentExpense** · Q4:N
- **CRM** · 10-K/10-Q · Jan-31 · RFCC-Excl · P,G (**no S**) · DeferredRev(BizComb), RPO · Q4:N

### Technology — internet / platform
- **AMZN** · 10-K/10-Q · Dec-31 · RFCC-Excl · P,S,G (**dimensional: AWS/NA/Intl**) · RPO (minor) · Q4:N
- **GOOGL** · 10-K/10-Q · Dec-31 · RFCC (Revenues top non-dim) · P,S,G · RPO% (minor) · Q4:N
- **META** · 10-K/10-Q · Dec-31 · RFCC-Excl · P,S,G · none · Q4:N
- **NFLX** · 10-K/10-Q · Dec-31 · **`us-gaap:Revenues`** · Streaming×G (US&Canada/EMEA/LatAm/APAC) · — · Q4:N

### Consumer discretionary
- **AAPL** · 10-K/10-Q · ~Sep-26 · RFCC-Excl · P,S; **G is 10-K-only** · — · Q4:N
- **TSLA** · 10-K/10-Q · Dec-31 · RFCC-Excl+`Revenues` · P,S,G (**no Con**) · **CostOfRevenue(dim) + RPO** · Q4:N
- **MCD** · 10-K/10-Q · Dec-31 · `Revenues` · S only · RPO-timing (minor) · Q4:N
- **SBUX** · 10-K/10-Q · ~Sep-28(52wk) · `Revenues` · P,S,G · **DeferredRevenue*(dim, large surface)** · Q4:N
- **NKE** · 10-K/10-Q · May-31 · RFCC-Excl · **P,S,G,Sub** · none · Q4:N
- **HD** · 10-K/10-Q · Jan-31(floating 52/53wk) · RFCC-Excl · P,S,G · **CostOfRevenue** · Q4:N
- **WMT** · 10-K/10-Q · Jan-31(**fixed calendar**) · RFCC-Excl+`Revenues` · P,S,G · **CostOfRevenue** · Q4:N
- **COST** · 10-K/10-Q · ~Aug-30(floating 52/53wk, 53rd-wk yrs) · RFCC-Excl(+`Revenues` 10-K) · P,S (**no G**; 10-Q lacks `fiscal_period` col) · — · Q4:N

### Consumer staples
- **PG** · 10-K/10-Q · Jun-30 · `Revenues` · S,G · none · Q4:N
- **KO** · 10-K/10-Q · Dec-31(52/53wk) · `Revenues`(+ko:RevenueForReportableSegments/IntersegmentRevenue ext) · P,S,G; **Con intermittent per quarter** · — · Q4:N
- **PEP** · 10-K/10-Q · ~Dec-27(52wk) · `Revenues`(+DisaggregationOfNetRevenue* ext) · S,G · none · Q4:N
- **CL** · 10-K/10-Q · Dec-31 · RFCC-Excl · S,G · CostOfRevenue · Q4:N
- **MO** · 10-K/10-Q · Dec-31 · RFCC-Excl · P,S(10-K) · none · Q4:N

### Financials — banks
- **JPM** · 10-K/10-Q · Dec-31 · `RevenuesNetOfInterestExpense`(+`Revenues` 10-K + 8 jpm:* ext) · S; **G 10-K-only** · Con present · Q4:N
- **BAC** · 10-K/10-Q · Dec-31 · `Revenues`+bac:RevenuesNetOfInterestExpenseFullTaxEquivalentBasis (ext) · P,S,G,Con · none · Q4:N
- **WFC** · 10-K/10-Q · Dec-31 · `Revenues` + `RevenuesNetOfInterestExpense` (**both tagged**) · P,S,Con · **OtherCostOfOperatingRevenue** (naive "CostOfRevenue" substring misses it) · Q4:N
- **C** · 10-K/10-Q · Dec-31 · `Revenues`, PrincipalTransactionsRevenue · P,S,G,Con · ContractWithCustomerLiabilityRevenueRecognized (correctly pre-excluded) · Q4:N

### Financials — insurers / asset managers
- **PGR** · 10-K/10-Q · Dec-31 · `Revenues`; **no us-gaap:PremiumsEarned** → ext pgr:PremiumsEarnedFeesAndOtherRevenue · P,S,Con · none · Q4:N
- **MET** · 10-K/10-Q · Dec-31 · `Revenues`, RFCC-Excl, ClosedBlockOperationsRevenue · P,S,G,Con · — · Q4:N
- **TRV** · 10-K/10-Q · Dec-31 · `Revenues`, trv:RevenuesExcludingRealizedGainLoss · S,G,Con (**no Product**) · none · Q4:N
- **BLK** · 10-K/10-Q · Dec-31 · RFCC-Excl · P,G (**no S**) · **8/16 concepts FP: blk:*DeferredRevenue*, RPO*** · Q4:N
- **BX** · 10-K/10-Q · Dec-31 · `Revenues`+ext (FeeRelated/PerformanceRevenues…) · P,S,G,Con · bx:*Percentage* (ratio, unit gap) · Q4:N

### Real estate (REITs)
- **PLD** · 10-K/10-Q · Dec-31 · `Revenues`, pld:RentalRevenue, PropertyManagementFeeRevenue · S,G,Con (no P) · DeferredRevenue; pld:NetIncreaseDecreaseToRentalRevenue*(ladder); **Q4-direct heuristic hit = likely spurious** · Q4:~
- **AMT** · 10-K/10-Q · Dec-31 · `Revenues`, RFCC…, amt:StraightLineRevenue · P,S,G,Con · **CostOfRevenue** · Q4:N
- **O** · 10-K/10-Q · Dec-31 · `Revenues`, RevenueRecognitionLeases · P,G (single-segment) · BusinessAcquisitionsProFormaRevenue (pro-forma) · Q4:N

### Utilities
- **NEE** · 10-K/10-Q · Dec-31 · RFCC-**Including**AssessedTax · P,S,Con · RPO, nee:RegulatoryLiabilityDeferredRevenue* · Q4:N
- **DUK** · 10-K/10-Q · Dec-31 · RFCC-Including + **fuel-type concepts** (RegulatedOperatingRevenueElectric*/Gas) · P,S,Con · 3×RPO* · Q4:N
- **SO** · 10-K/10-Q · Dec-31 · `Revenues`, RFCC-Including, **RevenueNotFromContractWithCustomer** · P,S,Con · so:UnbilledRevenues*, 4×RPO* · Q4:N

### Healthcare
- **PFE** · 10-K/10-Q · Dec-31 · `Revenues`(+RCC) · P,S,G,Sub · CollaborativeRev(dim, non-operating) · Q4:N
- **MRK** · 10-K/10-Q · Dec-31 · `Revenues` · P,S,G · CollaborativeRev(dim) · Q4:N
- **LLY** · 10-K/10-Q · Dec-31 · `Revenues` · P,S,G (**no Con**) · none · Q4:N
- **MDT** · 10-K/10-Q · **Apr-24** · RFCC-Excl · S,G,Sub · none · Q4:N
- **ABT** · 10-K/10-Q · Dec-31 · RFCC · P,S,G,Sub · none · Q4:N
- **ISRG** · 10-K/10-Q · Dec-31 · RFCC · **Product only** · DeferredRev(not-dim) · Q4:N
- **UNH** · 10-K/10-Q · Dec-31 · RFCC + `Revenues` · P,S · none · Q4:N
- **CVS** · 10-K/10-Q · Dec-31 · cvs:PremiumsEarnedNetAndRCC (ext) · P,S (no G) · none · Q4:N
- **CI** · 10-K/10-Q · Dec-31 · RFCC + ci:NonInvestmentRevenue (ext) · P,S · none · Q4:N

### Energy
- **XOM** · 10-K/10-Q · Dec-31 · `Revenues` + **RevenueNotFromContract** (commodity/derivative, dim, LEGIT) · P,S,G · RevNotFromContract(dim, keep) · Q4:N
- **CVX** · 10-K/10-Q · Dec-31 · RFCC + `Revenues` · S,G (no P) · CostOfRevenue (not-dim, ok) · Q4:N
- **COP** · 10-K/10-Q · Dec-31 · `Revenues` + RevenueNotFromContract · P,S,G · RevNotFromContract(dim, keep) · Q4:N
- **SLB** · 10-K/10-Q · Dec-31 · RFCC · P,S,G(,Sub) · DeferredRev(not-dim) · Q4:N

### Materials
- **LIN** · 10-K/10-Q · Dec-31 · RFCC · S(,G in 10-K) · none · Q4:N
- **DOW** · 10-K/10-Q · Dec-31 · `Revenues` + **RFCC-Including** · S,G,Sub/P · RCCincl(dim, ok) · Q4:N
- **NEM** · 10-K/10-Q · Dec-31 · RFCC · P,S,Sub(,G) · none · Q4:N (high Product/Subsegment fact density)

### Industrials — **CostOfRevenue-false-positive-heavy sector**
- **CAT** · 10-K/10-Q · Dec-31 · `Revenues` · P,S,G · **`us-gaap:CostOfRevenue` DIMENSIONED (20 Q / 15 FY facts)** → the CostOfRevenue-bug REPRODUCER (mandatory slot) · Q4:N
- **BA** · 10-K/10-Q · Dec-31 · `Revenues`+RFCC · P,S,G · **ba:Revenue*Percentage (dim, value=%)** · Q4:N
- **HON** · 10-K/10-Q · Dec-31 · RFCC · P,S(,G) · **hon:RevenueFromContractWithCustomerPercentage (dim, value=%)** · Q4:~1 borderline (a %-concept, not real Q4)
- **UPS** · 10-K/10-Q · Dec-31 · RFCC · P,S,G · none · Q4:N
- **GE** · 10-K/10-Q · Dec-31 · `Revenues`+RFCC · P,S(,G) · ContractAsset*(not-dim) · Q4:N

### Technology — big-tech cohort extension (SaaS / fintech / IT / semi-equipment)
Added to complete the big-tech cohort; each earns a slot by a NEW shape (record-only duplicates below).
- **CSCO** (networking) · 10-K/10-Q · **Jul(floating 52/53wk: 07-29→07-27→07-26)** · RFCC-Excl · P,S,G,Con · RPO · Q4:N
- **TXN** (analog semis) · 10-K/10-Q · Dec-31 · RFCC-Excl · **S,G only (no P, no Con)** · **none (zero-FP surface)** · Q4:N
- **LRCX** (semi equipment) · 10-K/10-Q · **Jun(floating: 06-25→06-30→06-29)** · RFCC-Excl · P,S,G,Con · none · Q4:N
- **NOW** (ServiceNow, SaaS) · 10-K/10-Q · Dec-31 · RFCC-Excl · P,G (no S) · **CostOfRevenue(dim)** · Q4:N
- **INTU** (Intuit) · 10-K/10-Q · **Jul-31 (fixed)** · `Revenues`+RFCC-Excl · P,S; Con qualifier · none · Q4:N
- **SNOW** (Snowflake) · 10-K/10-Q · Jan-31 · RFCC-Excl · P,S,G · **none (clean)** · Q4:N · **~6 10-Ks (2021 IPO)**
- **PLTR** (Palantir) · 10-K/10-Q · Dec-31 · RFCC-Excl · **S,G (no P); Con qualifier** · none · Q4:N · **~6 10-Ks (2021 IPO)**
- **ACN** (Accenture, services) · 10-K/10-Q · **Aug-31 (fixed, not floating)** · `Revenues` · P,S (no G) · none · Q4:N
- **PYPL** (PayPal, fintech) · 10-K/10-Q · Dec-31 · `us-gaap:Revenues` · P,S,G · none · Q4:N
- **HPQ** (HP Inc) · 10-K/10-Q · **~Oct(floating)** · `Revenues` · **P,S,G,Sub + Con (all 5 at once)** · CostOfRevenue · Q4:N

### Record-only — verified but shape-duplicates (checked, do NOT occupy a slot)
Kept so a future prober knows these were verified and why they add nothing new:
- **IBM** — Dec-fixed + dual RFCC/`Revenues` (≈ORCL); CostOfRevenue + `*RevenueChangePercent`(%) FP (≈existing groups); P,S,G,Con (≈NVDA).
- **MU** — Aug/Sep floating (≈COST); G 10-K-only (≈AAPL/JPM).
- **ADI** — Nov floating (≈AVGO cluster); S,G (≈TXN); `*PercentageOfRevenue`(%) (≈BA/HON).
- **AMAT** — S,G,Con-no-P (≈TRV); `*ChangeInRevenuePercentage`(%) (≈BA/HON); Oct (≈AVGO/ADI cluster).
- **DELL** — Jan-30 floating (≈HD); CostOfRevenue-dim (≈CAT group); G 10-K-only (≈AAPL).
- **WDAY** — Jan-31 + RFCC-Excl + P,G-no-S + RPO-dim FP (≈CRM, near-exact duplicate).

---

## ADR / foreign private issuers — OUT OF SCOPE (regime edge cases)

All 11 file **20-F (annual) + 6-K (interim)**, **zero 10-K/10-Q** → categorically
out of scope for a quarterly-10-Q pipeline. Kept because each teaches a
regime-detection lesson. FYE Dec-31 unless noted; TM/BABA/SONY = Mar-31.

| Ticker | Country | Basis | Interim XBRL cadence | Dimensional rev | Lesson |
|---|---|---|---|---|---|
| TSM | Taiwan | IFRS | 6-K `fp=None` → annual-only | ✅ Y (geo, via Filing.xbrl() only) | dimensional data exists but **companyfacts API strips it** |
| BABA | China | US-GAAP | 6-K mixed FY/Q2 (irregular) | ✅ Y (segment, via Filing.xbrl()) | US-GAAP despite China domicile; Mar FYE |
| ASML | Netherlands | **US-GAAP** | 6-K **zero XBRL** | ⚠️ | filing exists ≠ XBRL exists |
| SAP | Germany | IFRS | 6-K **zero XBRL** | ⚠️ | zero-XBRL guard needed |
| NU | Brazil | IFRS | 6-K **zero XBRL** | ⚠️ | zero-XBRL guard needed |
| AZN | UK | IFRS | 6-K `fp=Q2` → **semi-annual** | ⚠️ | quarterly SLA sees 6-mo-stale data |
| UL | UK | IFRS | 6-K all `Q2` → **semi-annual** | ⚠️ | EU dropped mandatory quarterly reporting |
| SHEL | UK/NL | IFRS | 6-K Q2 dominant + some Q3 | ⚠️ | closest-to-quarterly of the foreign set |
| NVO | Denmark | IFRS | 6-K `fp=FY` | ⚠️ | no real quarterly signal |
| TM | Japan | IFRS (was US-GAAP pre-2021) | 6-K/A `fp=None` | ⚠️ | mid-history GAAP→IFRS, dual-tagged; Mar FYE |
| SONY | Japan | IFRS (was US-GAAP ~FY2022) | 6-K `fp=FY` | ⚠️ | mid-history basis switch; Mar FYE |

**Design implication:** a foreign-ADR ticker must be detected (20-F regime) and
returned as an explicit N/A with reason, never silently produce an empty series;
concept resolution must be basis-aware (IFRS `ifrs-full:Revenue` vs US-GAAP);
dimensional data for these needs per-filing `Filing.xbrl()`, not `companyfacts`.

---

## Filter-bug findings surfaced by this sweep (feeds a data-layer fix)

The shipped `_is_revenue_concept` (`"Revenue" in local_name` minus deferred-revenue
prefixes) is **too permissive across sectors**. Real dimensioned false positives
found:

1. **CostOfRevenue / COGS** — dimensioned at CAT (reproducer), AVGO, ADBE, TSLA,
   WMT, HD, CL, T, AMT, QCOM; plus WFC's `OtherCostOfOperatingRevenue` (the
   "Operating" infix defeats a literal "CostOfRevenue" check).
2. **Percentage/ratio concepts** — BA/HON `*RevenuePercentage`, BX `*Percentage`:
   value is a **percent, not dollars** → needs a unit-type ($) guard.
3. **RemainingPerformanceObligation (RPO)** — backlog disclosure, widespread.
4. **DeferredRevenue* dimensioned** — SBUX (large), BLK; only the
   `ContractWithCustomerLiability*` prefix is currently excluded.
5. **Non-operating revenue** — PFE/MRK CollaborativeRevenue (dimensioned).
6. **REIT artifacts** — PLD ladder-schedule, O pro-forma-M&A revenue.

Concepts the filter must **KEEP** (legit non-RFCC revenue): `us-gaap:Revenues`,
`RevenuesNetOfInterestExpense` (banks), `RevenueNotFromContractWithCustomer`
(energy/utilities), `RevenueFromContractWithCustomer**Including**AssessedTax`
(utilities), and many company-extension revenue concepts (insurers, asset mgrs).

→ A robust fix is a **$-unit guard + a cost/percentage/RPO/deferred deny-list +
an allow of known legit non-RFCC concepts**, not a substring. This is a scope-A
(2.21.0) correctness defect independent of quarterly work.

---

## Fiscal-calendar findings (live-verified 2026-07-17, 6 filers × 5 FYs)

Probed: NVDA, AAPL, MSFT, COST, WMT, JNJ — chosen to span 52/53-week (NVDA/AAPL/
COST), fixed non-Dec (MSFT Jun), Jan (WMT), and calendar (JNJ) fiscal years.

**The filing DECLARES its own fiscal year and quarter on its cover page.** Every
10-Q/10-K carries these dei cover-page facts (read via `filing.xbrl()`, absent
from bulk companyfacts):

- `dei:DocumentFiscalYearFocus` — the fiscal year the filing reports.
  **Present 90/90, correct 90/90.** Decisive cases: AAPL FY2025-Q1 has
  `period_of_report = 2024-12-28` (a CALENDAR-2024 date) and declares
  `DocumentFiscalYearFocus = 2025`; NVDA (Jan FYE) has every quarter in the prior
  calendar year and declares correctly on all 15.
- `dei:DocumentFiscalPeriodFocus` — Q1/Q2/Q3 on a 10-Q, FY on a 10-K.
  **Correct 90/90**, and identical across the three 10-Qs of one fiscal year.
- `dei:CurrentFiscalYearEndDate` — the year-end month-day. **Exact 90/90 (0-day
  error).** It is NOT nominal: for 52/53-week filers it drifts year-to-year in
  lockstep with the audited year-end (NVDA `--01-30 → --01-29 → --01-28 → --01-26
  → --01-25`).

**Projecting a fiscal year forward by +12 months is inferior but safe.** Against
the same 30 filer-years: dei = 0-day error on all; a `+12mo`-from-last-known-FYE
projection = 1-6 day error (dist: 10×0d, 14×1d, 4×2d, 2×6d). The two 6-day
misses are AAPL and COST FY2023 — both **53-week years**, which only the filer
knows about and no projection can predict. Neither source ever exceeds a 20-day
window-match tolerance, so projection is a safe FALLBACK; the declared tag is the
authority.

**Sample caveat:** all six are large, mature filers. Small-cap / recently-IPO'd /
immature-XBRL filers were NOT probed — `DocumentFiscalYearFocus` presence is not
guaranteed there, so a consumer must fail loud (never guess the calendar year)
when the tag is absent, not assume 90/90 holds universally.

## Root-cause defect this surfaced (scope-A artifact, inherited by scope B)

`_filing_period_year` returns `int(period_of_report[:4])` — the **calendar** year —
while its docstring claims "the fiscal year a filing REPORTS". True for a 10-K by
SEC convention (year-end's calendar year == FY label); **false for a 10-Q at every
non-December-FYE filer.** Scope A only ever fetched 10-Ks, so it shipped harmlessly
in 2.21.0. Live-verified failure on the 10-Q path: `extract_dimensional_revenue(
"NVDA", form="10-Q", since_year=2026, until_year=2026)` selects **0 of the 3 real
FY2026 quarters** (all end in calendar 2025) and **1 FY2027 quarter** instead, and
every emitted fact is labelled `fiscal_year: 2025`. Three call sites inherit the
calendar-year lie: pre-fetch selection (`_filing_in_year_range`), the per-fact
`fiscal_year` label (`_build_dimensional_revenue_fact`), and the coverage report.
The `fiscal_year` field itself is currently unread downstream — `kpi_xbrl.py`'s
`period` key derives from `period_end[:4]` and its docstring says "NEVER from the
`fiscal_year` column". Correct label source = each fact's own `period_end` measured
against the filing's dei fiscal calendar (what T5 is specced to do), NOT the
filing's single focus stamped onto every fact (which mislabels prior-year
comparatives — verified on AAPL FY2019 10-K: its FY2017/2018/2019 facts all
collapse to 2019 under a filing-level stamp).

## Filing-deadline mechanics (published SEC regulation — exact, not estimated)

Whether a missing quarter is "not yet due" vs "overdue" is DERIVABLE, not guessable:

- **10-Q**: period-end + 40 days (large-accelerated & accelerated) / 45 days
  (non-accelerated). **10-K**: FYE + 60 / 75 / 90 days by the same tiers. Rules
  13a-13 / 13a-1 (17 CFR 240); filer tier defined by Rule 12b-2. Source: SEC
  form instructions + Release 33-8644.
- Filer tier is machine-readable: `dei:EntityFilerCategory` per filing, and the
  top-level `category` field on `data.sec.gov/submissions/CIK########.json`
  (AAPL → "Large accelerated filer").
- A late filer must file **Form 12b-25 (NT 10-Q / NT 10-K)** by the next business
  day; these appear as distinct form types in the EDGAR submissions histogram, so
  "this quarter is late, and here is the filer's own stated reason" is directly
  detectable, not inferred. (Corroborating late signals, unverified for
  completeness: SEC Delinquent-Filings program; NYSE ".LF" ticker suffix.)
- 52/53-week forward projection has **no published standard** — DQC_0006 gives a
  period-LENGTH validation tolerance (Q1 65-115d, FY 340-390d), not a projection
  rule. The authoritative next-FYE source is the filer's own
  `dei:CurrentFiscalYearEndDate`.

## Calculation-linkbase coverage (for the parked "read the filer's own rollup" option)

22-filer stratified probe (2026-07-17): every filer exposes a non-empty
`xbrl.calculation_linkbase()` (22/22) with an identifiable income-statement
revenue rollup (22/22). Dimensional-fact concept coverage: **18/21 at 100%**, 3
partial (MET 33%, BA 50%, JPM 89% — concepts living only in a footnote schedule,
never in the calc tree; fact-weighted, BA/MET miss ~60% of their volume). REIT
pro-forma (`BusinessAcquisitionsProFormaRevenue`) and PLD ladder concepts are
**structurally absent** from the linkbase → cannot leak. Insurance verdict
(PGR/TRV 100%, MET partial) is real BUT its unique value is now small: the three
insurers' DIMENSIONAL revenue concepts (`pgr:PremiumsEarnedFeesAndOtherRevenue`,
`trv:RevenuesExcludingRealizedGainLoss`, `us-gaap:Revenues`) all already contain
"Revenue" and pass the name path; `us-gaap:PremiumsEarnedNet` appears only in the
income-statement total, which we do not extract dimensionally. So the linkbase
layer is a defense-in-depth option, not a prerequisite. (Raw per-filer data:
scratchpad `coverage_results.json`, this session.)

## Industry practice for data-absence reporting (2 research passes, cited)

No published industry standard exists for a filer-period "coverage / why-is-this-
absent" report — confirmed after a hard second look; hand-rolling is the norm.
Closest public art: **Compustat** documents missing-data codes (`.C` combined /
`.I` insignificant / `.S` reports only Q2+Q4 / `.A` reports only Q4 / `.` NA);
**point-in-time** databases (Compustat PIT, `RDQ` = report-date-of-quarterly
separate from `DATADATE`) solve the closest analog — "was this known as of date
X" vs "does it exist at all". Most transferable idea: treat absence as
**time-relative**, splitting (a) not-yet-due (SEC deadline) / (b) due-but-unfiled
(Form NT signal) / (c) filed-but-facts-absent (XBRL). XBRL is sparse by design
(no forced zero-fill), so "never zero-fill a discontinued segment" follows the
data model, not a house rule.

---

## Provenance

- All rows verified live 2026-07-16 via edgartools 5.42.0 against real 10-K + a
  recent 10-Q per filer, classified through the repo's own `_is_revenue_concept`
  / `_dimension_signature`. ADR group verified via submissions form-histograms +
  companyfacts + per-filing `Filing.xbrl()` (TSM/BABA deep-checked).
- ⚠️ PARTIAL rows: dimensional detail not deep-checked (aggregate + regime
  confirmed) — ASML/SAP/NVO/AZN/SHEL/TM/UL/NU/SONY.
- Sweep run as 4 parallel verification agents + 3 earlier probe passes (AAPL/NFLX
  deep; WMT/COST/MSFT/HD; JPM/TSLA/KO/NVDA). INTC carried from the scope-A
  restatement fixture.
- Big-tech cohort extension (2026-07-16, 2 parallel agents, 16 filers verified):
  10 earned new slots (CSCO, TXN, LRCX, NOW, INTU, SNOW, PLTR, ACN, PYPL, HPQ);
  6 verified as shape-duplicates → record-only (IBM, MU, ADI, AMAT, DELL, WDAY).
  The Magnificent Seven (AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA) + NFLX are all
  in-set. **Total: ~87 slotted filers + 6 record-only, all live-verified 2026-07-16.**
- Fiscal-calendar + filing-deadline + calc-linkbase + industry-practice sections
  added 2026-07-17 (edgartools 5.42.0): dei-tag reliability from a 6-filer × 5-FY
  probe (90/90); the `_filing_period_year` calendar-vs-fiscal root cause; the
  22-filer calc-linkbase coverage probe; SEC deadline mechanics + 2 industry
  research passes. These fed the scope-B rebuild decision, not the 07-16 sweep.
- Selection principle: a filer earns a slot ONLY by adding a data shape not already
  covered (a new FYE anchor, axis combo, revenue-concept class, filter-bug class, or
  history length) — this is a diversity set, not a market-cap or cohort-completeness list.

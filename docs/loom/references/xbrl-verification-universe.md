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
| **Non-December fiscal year** | AAPL(Sep), COST(Aug/Sep), MSFT(Jun), PG(Jun), ORCL(May), NKE(May), CRM(Jan), WMT(Jan), HD(Jan), NVDA(Jan), MDT(**Apr**), TM/BABA/SONY(Mar) | fiscal-calendar classification; quarter boundaries ≠ calendar quarters |
| **52/53-week (floating) calendar** | COST, HD, NVDA, AVGO, QCOM, ADBE, SBUX, PEP, DIS | odd quarter day-counts (13 vs 14 weeks), 53rd-week years, `fiscal_period` col sometimes absent |
| **Fixed-calendar retailer (NOT floating)** | WMT | looks like a 52/53-wk retailer but has fixed Jan-31 calendar quarters (irregular day counts) |
| **Bank revenue concept** | JPM, BAC, WFC, C | `RevenuesNetOfInterestExpense`; WFC tags BOTH `Revenues` + `RevenuesNetOfInterestExpense` (summation-collision risk) |
| **Insurer revenue concept** | PGR, MET, TRV | extension `*PremiumsEarned*` concepts, NOT a stable `us-gaap:PremiumsEarned` |
| **REIT / lease revenue** | PLD, AMT, O | `RentalRevenue`, ASC-842 straight-line components; ladder-schedule & pro-forma false positives |
| **Utility (non-ASC-606 + fuel-type)** | NEE, DUK, SO | `RevenueFromContractWithCustomer**Including**AssessedTax` (not Excluding!); DUK splits by fuel-type CONCEPTS not axes; SO `RevenueNotFromContractWithCustomer` |
| **ADR / foreign 20-F + 6-K (no 10-Q)** | TSM, ASML, SAP, NVO, AZN, SHEL, TM, BABA, UL, NU, SONY | out-of-scope regime; IFRS/US-GAAP basis; 6-K semi-annual or zero-XBRL (see §ADR) |
| **Multi-concept `us-gaap:Revenues`** | NFLX, KO, NVDA, T, VZ, DIS, PG, PEP, MCD, SBUX, ADBE, ORCL, XOM, COP | dimensional revenue under plain `Revenues`, not `RevenueFromContractWithCustomer` |
| **CostOfRevenue false-positive (dimensioned)** | **CAT**, AVGO, ADBE, TSLA, WMT, HD, CL, T, QCOM | `us-gaap:CostOfRevenue`/COGS extensions tagged with breakdown axes → emitted as fake revenue by the current filter |
| **Percentage-value false-positive** | BA, HON | `*RevenuePercentage` extension concepts (value is a %, not $) pass the filter, dimensioned |
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

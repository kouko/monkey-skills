# Brief — 52/53-week filer 支援：week-based duration lane

Date: 2026-07-18 · Stage: brainstorming output (loom-code Stage 1) · Consumer: `writing-plans`

## Design-side on-ramp

Axis 0 negative guard: test-covered increment on the shipped quarterly-KPI lane
(no new user-facing surface, no new product shape) — silently skipped per the
family reception table. PRINCIPLES.md remains absent (declined-for-now stands;
not re-raised).

## Recon verdict (the arc's entry fork)

**(b) — fixable.** COST's 10-Q XBRL DOES tag week-based-duration dimensional
revenue; our pipeline drops it at two independent gates. Evidence (accession
`0000909832-26-000051`, FY2026 Q3, period end 2026-05-10, live-fetched
2026-07-18): `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax` at
~12-week (83d) AND ~36-week (251d) windows, each with full dimensional
breakdown (`srt:ProductOrServiceAxis` ×6 members + `srt:ConsolidationItemsAxis`
OperatingSegments; 18 dimensional facts per window incl. prior-year
comparatives). Dimensional tagging is symmetric with totals — no totals-only
nuance. `dei:CurrentFiscalYearEndDate` present (`--08-30`).

## Problem

The shipped quarterly Operating-KPI lane (PR #586, 2.23.0/5.9.0) produces
**zero quarterly evidence for 52/53-week filers**: COST's live memo feed
honestly refused with `q4_source_missing` ×54 and carried no usable quarterly
series, even though the source filings are richly tagged. The job: when kouko
runs `/report-equity-memo COST` (or any week-based US filer), the memo should
present the same quarterly KPI trends + derived Q4 as month-based filers get —
with the unequal quarter lengths (12wk Q1–Q3 vs 16–17wk Q4) honestly labeled,
because a 16-week Q4 presented as comparable to 12-week quarters misleads.

## Users

- **kouko**, running `/report-equity-memo <ticker>` on week-based US filers
  (COST today; other 4-week-period / 4-4-5-family retailers later); reads the
  memo with investor eyes — a mislabeled or silently-spliced unequal-length
  quarter is worse than absence.
- **Weak-model protocol consumers** (haiku/sonnet memo writers) executing the
  investing-team protocol literally — the disclosure rule's wording must be
  transcribed from the shipped feed schema
  (docs/loom/memory/prose-contract-mechanism-transcribes-from-code.md).

## Smallest End State

1. **One shared week/month period-classification primitive** — both today's
   Gate P (fiscal-boundary labeling) and Gate C (duration-class mapping) decide
   through it. Single-function constraint is load-bearing: edgartools shipped
   the same class of fix split across two code paths and had to re-fix it
   (issue #816). No parallel patched copies.
2. **Positive allowlist of week-based duration bands** (per
   docs/loom/memory/shared-classifier-over-open-dialects-needs-allowlist.md):
   ~12/13wk (83–91d) → quarter-length; ~24/26wk (167–182d) → H1-YTD;
   ~36/39wk (251–273d) → 9mo-YTD-equivalent; ~16/17wk (111–119d) →
   week-based Q4-length; ~52/53wk (363–371d) → FY. Everything else stays
   unclassifiable (fail-closed unchanged).
3. **Gate P rework**: week-based filers' quarter ends can sit ~20d from the
   month-subtracted boundary (COST Q3: 2026-05-10 vs nominal 2026-05-30) —
   boundary matching must become week-aware for the week lane instead of
   widening the ±10d month tolerance (widening would let month-lane errors in).
   `dei:CurrentFiscalYearEndDate` drifts annually for these filers — read
   per-filing, never cached
   (docs/loom/memory/fiscal-year-derive-per-fact-against-filing-calendar.md).
4. **Q4 derivation works on the week lane**: FY − 36wk-YTD, same fail-closed
   `q4_source_missing` refusal when the YTD anchor is absent; derived-Q4
   tagging rules from 2.23.0 unchanged.
5. **Per-point week-count labeling** in the feed (e.g. `duration_weeks`), so
   downstream rendering can state 16–17wk Q4 vs 12wk quarters.
6. **Protocol disclosure rule** (domain-teams investing-team memo protocol):
   unequal-quarter-length disclosure whenever the feed carries week-based
   points — wording transcribed from the shipped schema fields, not from
   accounting literature.
7. **Supplementary week-normalized YoY column** (user-ratified 2026-07-18,
   second research round): when two compared periods' week counts differ, the
   feed/render layer additionally carries a per-week-normalized YoY growth
   figure (value ÷ weeks, then YoY) — as-reported stays the primary number,
   1:1 traceable to the filing; the adjusted figure is supplementary, never a
   replacement. Grounding: Johnston "14-Week Quarters" shows analysts do NOT
   self-adjust for the mechanical ~1/13 boost; filers (Costco/Walmart) headline
   as-reported with week labels.
8. **Acceptance**: live COST feed produces the quarterly series + derived Q4,
   independently recomputed against public figures; AAPL/NVDA month-lane output
   byte-stable (regression); suite green.

Version bumps: investing-toolkit → 2.24.0; domain-teams → 5.10.0.

## Current State Evidence

- **Forward**: `pack_us.py` `pack_kpi_quarterly`
  (investing-toolkit/skills/data-markets/scripts/pack_us.py:982+) → per-filing
  fetch + fiscal labeling in
  investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py →
  `kpi_xbrl.py` quarterly-series
  (investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py:1306+)
  `classify_fact_period` → `kpi_memo_feed.py` 1.1 quarterly arm
  (`build_quarterly_memo_feed`). `pack_us.py` adds no extra duration filter on
  the kpi path (its ≥350d gate at pack_us.py:298-318 is the annual lane).
- **Reverse (SSOT)**: domain-teams is canonical for analysis-layer standards;
  the memo protocol lives at
  domain-teams/skills/investing-team/protocols/deep-equity-research-memo.md
  (Operating-KPI block :135-196). Cross-plugin delegation contract (repo
  CLAUDE.md): data layer stays in investing-toolkit, analysis/protocol in
  domain-teams; no gate logic copied across.
- **Error**: Gate P — boundaries dict + `UnclassifiablePeriodError` raise at
  sec_edgar_client.py:2336-2347, per-fact quarantine :2855-2859 (kills BOTH
  83d and 251d facts of a Q3 filing; week-based Q1 ends ~7d off happen to pass
  — why the live pack still showed "3mo" facts). Gate C — kpi_xbrl.py:286-292
  raises on any duration_months ∉ {3,6,9,12} (251d→8mo, 111d→4mo, 167d→5mo all
  die). Downstream refusal: `q4_source_missing` (fail-closed, observed ×54).
- **Data**: COST census (accession 0000909832-26-000051): ~12wk DIM=18
  TOTAL=2; ~36wk DIM=18 TOTAL=3; 41 revenue duration facts total. Artifacts
  (machine-local scratchpad, volatile): `cost_duration_census.{md,json}`,
  `cost_10q_duration_census.py` — regenerate via the recon script if gone.
- **Boundary**: `FISCAL_BOUNDARY_TOLERANCE_DAYS = 10`
  (sec_edgar_client.py:2166); `_AVG_DAYS_PER_MONTH = 30.44` month rounding
  (sec_edgar_client.py:2114); `_DURATION_CLASS_BY_MONTHS = {3,6,9,12}`
  (kpi_xbrl.py:155). All three spot-checked verbatim this session.

## Alternatives Considered (Axis 4 — research-grounded)

1. **DQC-style wide day-slop windows** (XBRL US DQC_0006; [EN]
   https://xbrl.us/data-rule/dqc_0006/ ,
   https://github.com/DataQualityCommittee/dqc_us_rules) — validation-layer
   tolerance only; no week awareness at all; widening our windows to match
   would admit month-lane misclassifications and gives no Q4-derivation
   signal. Rejected.
2. **edgartools date-drift fix** ([EN]
   https://github.com/dgunning/edgartools/issues/816 , fixed v5.31.5) —
   treats period ends in the first ~7 days of a month as previous-month;
   solves 13-week-quarter boundary drift (JNJ/PFE style), NOT our 12/36-week
   duration-window failure. Rejected as the mechanism; adopted as the
   cautionary lesson (two-path desync → single shared primitive).
3. **Filer-declared week structure as ground truth** (COST 8-K/10-K prose:
   13 four-week periods; Q1–Q3 = 12wk each, Q4 = 16wk, 17wk in 53-week years;
   [EN] https://www.sec.gov/Archives/edgar/data/909832/000090983223000038/costex9918-k92623.htm)
   — confirms the week-band table direction; not an importable library.
   **Chosen direction** (bands as positive allowlist).
- JA searches corroborated only domain mechanics (retail 52/53-week YoY
  handled at analysis layer by excluding the extra week) — no JA source on
  classifier internals; no EN/JA disagreement. Vendor internals (Calcbench
  etc.): insufficient data. SEC Financial Statement Data Sets spec (`aqfs.pdf`)
  403'd — `qtrs` field derivation unverified this session.

Second round — investment-practice layer (user-requested, 2026-07-18):

4. **Filer practice = as-reported + week-count labels** (chosen as primary
   presentation): Costco headlines "16-week fourth quarter ... compared to ...
   17-week fourth quarter" with no normalization ([EN]
   https://investor.costco.com/news/news-details/2024/Costco-Wholesale-Corporation-Reports-Fourth-Quarter-and-Fiscal-Year-2024-Operating-Results/default.aspx );
   Walmart isolates the extra week to comp-sales via week-53→week-1 lookback
   and states "the additional week only affects 4-5-4 comparable sales" ([EN]
   stock.walmart.com 8-K FY25 Q4 earnings release).
5. **Readers do not self-adjust** (why disclosure-only is insufficient):
   Johnston, "14-Week Quarters" (658 52/53-week filers, 1994–2006) — analysts
   on average fail to adjust for the predictable ~7.7% (1/13) 14-week-quarter
   boost; the market misprices the mechanical surprise ([EN]
   https://care-mendoza.nd.edu/assets/152197/leonepaper.pdf ). A JA retail
   commentator manually computes the per-week-adjusted growth Costco's own
   release omits ([JA] https://note.com/amekabu/n/n23ec880fbc42 ) — downstream
   readers are forced to self-compute; the memo should do it for them.
6. **Vendor calendarization ≠ this problem**: Bloomberg/FactSet
   calendarization docs cover fiscal-year-end alignment across companies, not
   intra-year week-count variance ([EN]
   https://doc.exabel.com/dsl/data_signals/factset_estimates.html ,
   https://corporatefinanceinstitute.com/resources/accounting/calendarization/ );
   week-count-specific vendor handling: insufficient data. Sell-side style
   guides (CFA/WSP/BIWS) on 16–17wk quarters: insufficient data. NRF 4-5-4
   calendar restates 53-week years the following year ([EN]
   https://nrf.com/resources/4-5-4-calendar ).

## What Becomes Obsolete (Axis 5)

- BACKLOG §"52/53-week filer support" — consumed by this arc; delete the
  section when the arc ships.
- The implicit "month lane is the only lane" contract in
  `_derive_fiscal_label` / `_duration_months` docstrings and any protocol
  wording implying COST-class refusal is the terminal state — update in the
  same change (refusal stays the correct fallback, no longer the expected
  COST outcome).
- No code deletion expected: the month lane remains authoritative for
  month-based filers.

## Decision

Build the week-based duration lane: one shared classification primitive with a
positive week-band allowlist, week-aware fiscal-boundary matching (per-filing
FYE, never cached), Q4 = FY − 36wk-YTD on the existing fail-closed derivation,
per-point week counts in the 1.1 feed, an unequal-quarter-length disclosure
rule in the investing-team protocol (wording transcribed from the shipped
schema), and — user-ratified — a supplementary per-week-normalized YoY growth
figure whenever compared periods' week counts differ (as-reported stays the
primary, filing-traceable number). We will NOT: widen the month lane's ±10d
tolerance, build a static registry of week-based filers (detection is
per-filing from observed durations + dei calendar), replace as-reported
figures with normalized ones, or touch non-US markets.

## Out of Scope

- calc-linkbase arc, Form-NT arc (parked, unchanged).
- pack.py PEP 723 root hardening + other §memo-wiring 2.23.0 post-ship debt
  (fires on next touch per BACKLOG; not this arc's rider).
- tier-① store lane, WITHHELD states (Do-Not-Touch stands).
- Replacing as-reported figures with normalized ones anywhere (the
  supplementary adjusted-YoY column is the only adjustment math in scope);
  no Walmart-style week-53→week-1 comp-sales lookback remapping.
- Non-US filers; exhaustive 4-4-5/4-5-4/5-4-4 taxonomy beyond the observed
  positive bands.

## Open Questions

1. Week-lane detection trigger: recommend per-filing inference (week-band
   duration hits + dei FYE drift), no registry — plan-time design detail.
2. 53-week specifics: 17wk Q4 (119d) is COST's declared absorption; verify
   per-filer from facts rather than hard-coding the COST pattern — the
   allowlist bands already cover it; labeling carries the observed week count.

# Brief: reconstruct the three statements as the filer declared them

Date: 2026-07-26
Branch: `feat-spine-chain-coverage`
Supersedes: `docs/loom/BACKLOG.md` — "spine chain misses 33 filer-years of
reported history (OPEN, Start: READY)". That entry proposed widening the concept
chain with measured synonyms; §Alternatives records why that is the wrong shape.
An earlier, narrower brief in this same session (revenue-only) was withdrawn
after the user asked for the whole statement — §Decision records the measurement
that made the wider scope the cheaper one.

## Design-side on-ramp

Axis 0 negative guard fired — an increment plus a correctness fix on a shipped
lane, not product-shaped new work. Skipped silently.

## Problem

The user wants **10+ continuous years of the three financial statements for ONE
company, to read that company's trend**. Cross-company comparison is explicitly
not the current priority (stated 2026-07-26).

Today the pipeline forces every filer's statements through a fixed 14-field
spine, resolved by fixed concept chains. That is lossy in both directions:

**It drops what does not fit.** Measured across 65 domestic operating filers
from `docs/loom/references/xbrl-verification-universe.md`, one 2016-2018 10-K
each, the chain finds NOTHING for:

| field | blank | notes |
|---|---|---|
| `gross_profit` | 57% | mostly genuine — utilities/REITs/banks present no gross profit |
| `total_liabilities` | 32% | filer tags `LiabilitiesAndStockholdersEquity` instead — **21/21 derivable** |
| `operating_income` | 23% | mixed; oil majors present no operating-income line at all |
| `revenue` | 15% | **all recoverable** — whole sectors use concepts the chain never listed |
| `capex` / `eps_basic` | 12% / 9% | |
| `total_assets`, `total_equity` | **0%** | universal — needs no work |
| cash-flow trio, `cash`, `net_income`, `pretax_income` | 2-3% | near-universal |

The `revenue` blanks are sector-shaped, not an era artifact — utilities
(`RegulatedAndUnregulatedOperatingRevenue`: DUK, NEE), REITs
(`RealEstateRevenueNet`: O, PLD), mining (`RevenueMineralSales`: NEM), software
(`SalesRevenueServicesNet`: CRM), pharma/beverage (`SalesRevenueGoodsNet`: MRK,
PFE, KO). Because filers converged on
`RevenueFromContractWithCustomerExcludingAssessedTax` after ASC 606 took effect
in 2018, the chain covers the modern era and covers the pre-2018 era only for
filers who happened to use `Revenues` or `SalesRevenueNet`. **For whole sectors
the series therefore begins in 2018** — the requested 10-year trend, truncated
to five.

**It cannot say WHY a cell is empty.** Three different facts render identically
today: the chain missed a concept the filer did use; the filer presents no such
line (an oil major genuinely has no operating-income line); the value is
derivable from the filer's own arithmetic but not separately tagged. A reader
cannot tell a pipeline defect from a real accounting fact.

**And it silently understates two filers.** PSX resolves to a component
(−2.2% vs the filing's own total) and XOM likewise (−2.9%), because each names
its total with a concept absent from the chain.

## Users

kouko, analysing one company at a time. **When** reading one company's 10-year
statements, **I want** the statements as that company actually filed them, **so
I can** tell a real decline from a hole in my own pipeline.

Two consequences of single-company-at-a-time:

- Per-filing parsing is affordable. **Ten years is 8 filings, not ~4** —
  CORRECTED 2026-07-26 from a live run, refuting this brief's own arithmetic.
  Each 10-K does carry three comparative years, but consecutive 10-Ks OVERLAP by
  two of them: filing N covers Y, Y-1, Y-2 and filing N+1 covers Y+1, Y, Y-1. So
  the first filing yields 3 years and every subsequent one adds exactly ONE —
  **N filings yield N+2 distinct years**, not 3N. Measured: 4 filings → 6 years;
  8 → 10 years (2016-2025). Cost follows: ~86s cold for a decade, not the ~42s
  the recompute-vs-persist decision was argued on. That decision does not change
  (a derived cache would still buy back only the warm-path seconds), but the
  number it was argued on was wrong and is corrected here rather than left for a
  reader to inherit.
- A silently-low year is the expensive failure: on a trend chart it reads as a
  downturn and nothing distinguishes it from a real one.

## Current State Evidence

- **Forward** — `kpi_spine_view.SPINE_FIELD_CHAINS` (`kpi_spine_view.py:201`)
  declares the 14 fields; `_resolve_field` (`:353`) keeps the first-present
  entry per period identity in chain order. That is the only revenue-selection
  site on the read path.
- **Reverse** — the store is written by two producers and BOTH already carry the
  accession per fact, which is the join key this design needs:
  `sec_edgar_client.build_statement_backfill` (`:3711`) emits one fact per
  (concept, annual period, **accession**) and its docstring already warns "A
  CONSUMER MUST THEREFORE KEY ON `accession` TOO"; `kpi_us_statements.py` maps a
  single parsed filing. `companyfacts` rows carry `accn`, already propagated
  (`sec_edgar_client.py:338`).
- **Error** — `_period_identity` (`kpi_spine_view.py:338`) already encodes this
  brief's posture for a different unknown: a null `period_axis_key` means "I have
  NOT proven this is the same period as anything else", and two nulls never
  resolve against each other, so both filer figures survive. Refusing to guess
  and keeping the refusal visible is an established convention here.
- **Data** — the store is bitemporal and append-only; its dedup key includes
  `source_accession`, so one period legitimately holds several vintages.
  `_identity_vintage` (per the module header at `:123`) pins ONE
  `(as_of, source_accession)` across fields for the balance identity — the same
  discipline governs anything read per-filing.
- **Boundary** — `sec_edgar_client._acquire_raw_filing(accession)` (`:928`) is
  the shared accession→`Filing` acquirer with typed failure categories already
  defined (`:987`). No new network primitive is needed.

Evidence paths appendix:
`investing-toolkit/skills/analysis-kpi/scripts/kpi_spine_view.py`,
`investing-toolkit/skills/analysis-kpi/scripts/kpi_us_statements.py`,
`investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py`,
`investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`,
`docs/loom/references/xbrl-verification-universe.md`,
`docs/loom/BACKLOG.md`.

## Decision

**Reconstruct each of the three statements from the filing's own declared
structure, verify the filer's declared arithmetic against the filer's own
numbers, and make the 14-field spine a derived view over that — not the storage
format.**

An XBRL filing ships two structures, and the reconstruction needs both, each in
its own job:

| structure | its actual job | used here for |
|---|---|---|
| presentation linkbase | layout | which lines exist, their order, indent, and the filer's own label |
| calculation linkbase | arithmetic | which children sum into which parent, and with what sign |

This division matters because the presentation structure was measured to be
**unreliable for INFERRING semantics** — asked which concept is the total
revenue, it named a 193M professional-services line as ServiceNow's total
against an actual 1,933M. That is a misuse, not a defect: layout tells you where
a line sits, never what it means. Using it for order and labels — what it is
for — is sound. Nothing in this design may infer meaning from presentation
position.

Measured evidence, on the committed verification universe:

- **The declared arithmetic is true.** Across 56 filers, every declared subtotal
  was checked as Σ(child × weight) against the filer's own reported figure:
  **501 of 509 reconcile (98.4%)**, and the **income statement is 212 of 212 —
  100.0%**. That the income statement is perfect is the load-bearing part: it is
  the only statement that is actually broken today (balance sheet and cash flow
  blank rates are 0-3%).
  The oracle is independent of the structure being tested — weights and
  hierarchy come from the linkbase, values from the fact table, and nothing
  forces them to agree — so this is not a
  `construction-guaranteed-invariant-proves-nothing` check.
- **The 8 residual failures are understood, not waved away.** Five were a probe
  artifact (a non-numeric child). Three are genuine filer-declaration quirks,
  all in the cash-flow statement; NEE's was diagnosed to the line — it declares
  both `ProfitLoss` and `NetIncomeLoss` as children of operating cash flow, and
  the 5,378M discrepancy is exactly its net income counted twice. Real, rare
  (3 in 509), and it must surface as a flagged line rather than a silent number.
- **The reconstruction is faithful and complete enough to read.** KO's FY2017
  income statement resolves to 26 real lines carrying the company's OWN labels
  ("NET OPERATING REVENUES", "GROSS PROFIT"), its own custom concept
  (`ko_UnusualOrInfrequentItemOperating` — which no fixed concept list could ever
  contain, and which costs this design nothing because it reads structure, not
  names), signs, calculation parents, and three comparative years per filing.

**Separating statement lines from dimensional noise is the single largest
implementation risk, and it is NOT solved.** KO's FY2017 income-statement
presentation role returns **80 rows** of which only 26 are statement lines; the
rest are segment breakdowns ("Asia Pacific", "Latin America") interleaved in the
same role and marked by a dimension label. Filtering on that dimension label was
validated on that ONE filing, from ONE era, and **measurably fails on modern
filings**: from ~2019 filers disaggregate revenue via `srt:ProductOrServiceAxis`,
whose DOMAIN MEMBERS appear as presentation rows whose concept ends in `Member`
and carry no dimension label. A probe using the dimension-label filter alone
read `TechnologyServiceMember` as IBM's first statement line and
`NaturalGasReservesMember` as Duke Energy's, across 2019-2026 — that is, for the
entire recent half of the very decade this arc exists to reconstruct.

So the filter is a first-class task with its own acceptance evidence, not a
line of glue: it must be **structural** (the concept is a
Member/Axis/Domain/Table/LineItems placeholder, or the row is dimensioned) and
**positive** — keep rows proven to be undimensioned statement lines — never a
denylist of observed member names, per
`docs/loom/memory/shared-classifier-over-open-dialects-needs-allowlist.md`
("the set of dialects is OPEN; a denylist fails toward the dangerous direction
the moment an unsampled producer adds a key you did not list"). It must be
verified across BOTH eras and across sectors before any render is trusted,
because a leaked member row corrupts the statement silently — it renders as a
plausible line with a plausible label.

**Every empty cell must say which kind of empty it is.** Three kinds, three
distinct renderings — never one blank:

| kind | meaning | how it is decided |
|---|---|---|
| not presented | the filer's statement has no such line | the line is absent from the reconstructed statement |
| not tagged | the line exists, that period has no undimensioned value | line present, value absent for that period |
| derived | not separately tagged but computable from the filer's own arithmetic | e.g. total liabilities = `LiabilitiesAndStockholdersEquity` − whole equity − mezzanine (21/21 filers) |

A derived value must be labelled as derived, and the whole-equity subtlety is
NOT optional: subtracting parent-only `StockholdersEquity` would push minority
interest into "liabilities". The existing `_equity_kind` / mezzanine machinery
already resolves whole equity and must be reused rather than re-derived
(`kpi_spine_view.py` header, "THE EQUITY TERM IS WHOLE EQUITY").

**The mezzanine is a SEPARATE term and this brief first omitted it** (corrected
2026-07-26, caught by Task 5's implementer). Temporary equity sits BETWEEN
liabilities and equity, so it is not part of whole equity and leaving it in the
remainder relabels it as debt — the same defect as the minority interest, a
different term. The formula is `_annotate_balance_identity`'s own identity
(`A = L + mezzanine + E`) solved for L, not a new claim. Measured on the
committed capture: KO FY2017 tags `LiabilitiesAndStockholdersEquity` (87,896M)
with NO `Liabilities` line, parent-only `StockholdersEquity` 17,072M and a
non-zero `MinorityInterest` 1,905M — so the parent-only mistake is worth exactly
that 1,905M, mislabelled as debt.

**Arithmetic in `Decimal`, never binary float.** Cross-layer arithmetic on money
in this module family has already manufactured a false restatement signal once
(`docs/loom/memory/construction-guaranteed-invariant-proves-nothing.md`, the
`1.005 × 1e9` case), and a verification test value must be chosen to be
float-hostile or a green suite proves nothing.

### Three layers, previously conflated

The loss this arc removes came from binding three separable things into one
storage format. They separate as:

| layer | job | status |
|---|---|---|
| as-filed statements | fidelity — what the filer actually reported | what this arc builds |
| named quantities | "this filer's line X IS `revenue`" | **necessary and unavoidable** — every derived metric (margin, growth, return) needs a named quantity to bind to; a faithful statement alone cannot supply one |
| the specific 14 field names | which names exist | a preference, and once the layer above is a view, a freely reversible one |

**The 14-field list is NOT redesigned in this arc.** Only its POSITION changes —
from storage format to derived view. Two reasons, both load-bearing:

1. Redesigning it now would be deciding at the moment of maximum cost and
   minimum information. The whole point of demoting it is that afterwards the
   list changes without a data migration; deciding before the reconstruction
   exists means deciding blind.
2. Which fields belong is substantially a **taste call**, not a measurable one —
   it depends on what the user intends to compute, which is not yet stated.
   Per `judgment-rubrics.md` §6 the honest move is to say so and pick the
   reversible option, not to dress a preference as analysis.

An earlier draft of this brief argued that `gross_profit` and `operating_income`
are bad fields because 57% / 23% of filers have no such line. **That criticism
is withdrawn**: it is an argument against them as a STORAGE format, and it
evaporates once they are a view — "this filer presents no such line" is then a
faithful report, not a lost value.

The one behavioural change the view does need: it must be able to render **"not
presented"** distinctly from empty. Otherwise the three-kind taxonomy resolved in
the reconstruction layer is flattened back into one undifferentiated blank at the
point the user actually reads it, and the arc's central benefit is discarded one
layer before delivery.

### Series identity across a decade — concept, never label

Measured over 14 filings each for three filers chosen to span the failure modes
(KO changed concept at ASC 606; DUK's whole sector uses a concept no chain
lists; IBM never moved):

| filer | concept changes, 2013-2026 | label changes |
|---|---|---|
| KO | **1** (2019, ASC 606) | 2 |
| DUK | **0** | 0 |
| IBM | **0** | **5** |

Two consequences:

- **A filer's own concept is a near-stable series key** — zero or one transition
  per decade. Within-company continuity is therefore a SMALL problem, and its
  transitions are enumerable EVENTS, not a per-period inference. A decade of one
  company yields a handful of transitions, each reviewable side by side with both
  concepts and both values. (If a model is ever used anywhere in this pipeline,
  that is the only place it fits — proposing a handful of auditable transitions,
  never adjudicating every period.)
- **The filer's own LABEL is not a key.** IBM kept one concept for 14 years while
  its label moved `Total revenue` → `Total revenue (Note T)` → `Revenue (Note O)`
  → `Revenue (Note C)` → `Revenue (Note D)` → `Revenue`, because it embeds a note
  cross-reference that renumbers. Labels are for display only; nothing may key on
  them.

This also sharpens what the 14-field view is FOR: cross-company canonicalization
is the hard problem (whole sectors disagree), within-company continuity is the
easy one — and the user has deprioritised cross-company. The view stays because
derived metrics need named quantities, not because trends require it.

### A limit this brief must not overclaim

The 63-of-65 resolution rate was measured on filings **filed 2016-2018 only**.
Resolution is era-dependent: DUK's calculation tree yields 2-3 candidate totals
(unresolvable) for every filing FILED 2013 through 2017, and resolves cleanly
from the one FILED in 2018 onward — 5 of its 14 years.

**"CANDIDATE TOTALS" IS REVENUE-SCOPED, NOT CALC-TREE ROOTS** — stated because
this brief left it open and Task 8's implementer reasonably read it the other
way, then measured that reading and refuted it. The count comes from the
structural rule this arc is founded on: among the income calculation tree's
REVENUE-ish concepts, those whose calculation parent is NOT itself a revenue
concept. One survivor is the filing's total; two or three is the ambiguity.
Applied to ALL calc-tree roots the phrase is meaningless — measured on the
committed capture, KO income has 2 roots, KO balance sheet 2, IBM income 4, IBM
cash flow 1, because `Assets` / `LiabilitiesAndStockholdersEquity` and the EPS
rows are legitimately separate roots. A root-count rule would report almost
every real statement unresolved.

**FILED, not fiscal — the distinction was ambiguous here for one round and it
matters.** Task 7's implementer read this sentence as fiscal-year-scoped and
found an apparent contradiction: the committed DUK capture has period-of-report
2017-12-31, so under a fiscal reading it would be unresolvable, while Task 7's
RED demanded it yield a value. Under the correct FILED reading there is no
contradiction — that filing was filed in 2018 and resolves to
`RegulatedAndUnregulatedOperatingRevenue` with its three parts summing to 0.00%.
A year in this brief always means the FILING year unless it says fiscal. A 10-year reconstruction spans exactly the era
that was not measured. The per-era resolution rate is therefore something this
arc must MEASURE, not assume, and the honest expectation is that early years
resolve worse than the sampled window.

## Smallest End State

For ONE US company: the three statements as filed, for 10+ years, each line
carrying the filer's own **XBRL** label, with every declared sum verified and
every empty cell typed.

**"XBRL" is load-bearing in that sentence and this brief first omitted it.** A
filer files its income statement twice and the two disagree — for KO FY2017, 15
of 26 labels and 3 line positions differ between the printed page and the XBRL
exhibit, with zero figures differing. The full measurement and what it does and
does not bound are under §"THE FILER'S OWN LABEL MEANS ITS XBRL LABEL" below;
this line names the qualifier so a reader who stops here does not leave with the
unqualified promise.

1. From one accession: the three statements as ordered lines — label, concept,
   level, weight, calculation parent, per-period values — segment slices
   excluded.
2. Verification pass: every declared sum checked in `Decimal`; failures surfaced
   as flagged lines, and groups whose children are not fully tagged reported
   separately from groups that genuinely disagree (a missing child is not a
   wrong sum).
3. The three-kind empty taxonomy above, including derived total liabilities.
4. Multi-filing assembly: 10+ years from N filings, restatement vintages kept
   per the store's existing newest-filed policy rather than a new one. Series
   identity keys on the FILER'S OWN concept (near-stable: 0-1 transitions per
   decade), never on its label; a transition is recorded as an explicit,
   reviewable event rather than silently resolved.
5. The 14-field spine re-expressed as a view over the reconstruction, so the
   existing tearsheet keeps working. **The field list is unchanged** — only its
   position moves. The single behavioural addition: the view renders "not
   presented" distinctly from empty, so the three-kind taxonomy survives to the
   point the user reads it.
6. Per-era resolution rate reported, not assumed — the structural rule's 63/65
   was measured on 2016-2018 filings only, and this arc reconstructs years
   outside that window.

**"THE FILER'S OWN LABEL" MEANS ITS XBRL LABEL, AND FOR MOST LINES THAT IS NOT
THE LABEL IT PRINTED.** Measured 2026-07-26 by transcribing KO's FY2017 primary
document (`a2017123110-k.htm`) by hand and comparing it to the reconstruction:
**a filer files its income statement TWICE and the two disagree.** Of 26 lines,
15 labels differ between the printed page and the XBRL exhibit (an em dash for a
word; a US-GAAP standard label where the page uses KO's own; `(in shares)` /
`(in dollars per share)` suffixes; `AVERAGE SHARES OUTSTANDING — BASIC`
collapsing to `AVERAGE SHARES OUTSTANDING`), 3 lines are transposed — the
exhibit puts the `CONSOLIDATED NET INCOME` subtotal BEFORE two components the
page puts above it — and 6 cells print an em dash where the exhibit tags `0`.
**Zero figures differ**: every number the filer printed survives unchanged.

The reconstruction is faithful to the exhibit, and that is checkable rather than
asserted: it matches SEC's OWN renderer over the same accession (`R2.htm`, an
independent implementation) byte for byte on all 26 labels and their order. So
this is a fact about filing practice, not a defect — but it bounds what this arc
can promise. A reader comparing the output to a printed 10-K will see different
words against identical numbers, and must be told which document they are
reading. Whether the arc should instead FAIL on that divergence is a product
call this brief does not settle; it cannot be resolved in code, because both
strings are the filer's own.

**Acceptance is line-by-line against the real filing**, not sum reconciliation
alone. Sum checks prove the declared arithmetic holds; they do not prove the
reconstructed statement matches what a human reads in the 10-K — lines outside
every sum (EPS rows carry `weight=None` / no calculation parent), order, and
labels are all unproven by them. One company, two filings, every line compared
to the filed document.

## Alternatives Considered

Industry research was run earlier this session and is summarised, not repeated.

1. **Widen the concept chains with measured synonyms** — the BACKLOG's proposal.
   *Rejected*: it cannot see a concept nobody thought to test, which is exactly
   how the utility / REIT / mining sectors were missed; it leaves PSX and XOM
   understated; and it keeps one global ordering imposed on filers who disagree
   with each other.
2. **Keep the 14-field spine as the storage format, fix only revenue.** This was
   this session's own earlier proposal, withdrawn. *Rejected*: the measurement
   showed the loss is not revenue-specific (`operating_income` blanks 23% >
   `revenue` 15%), and a per-field fix would have to be repeated per field while
   still discarding the hierarchy and the filer's labels. The structure
   extraction is the same work either way — only what is kept differs.
3. **Curated per-filer mapping tables + human review** — what the commercial
   vendors ship (Calcbench maintains 1000+ standardized metrics; Compustat uses
   human analysts; S&P Capital IQ presents as-reported alongside standardized).
   *Rejected for now*: correct at vendor scale, wrong shape for one user reading
   one company — it trades compute for unbounded human curation, and the
   curation is the part that goes stale.
4. **LLM judgement on concept continuity** — the user asked this be researched.
   *Rejected as the primary mechanism*: the FinAuditing benchmark measured 13
   SOTA models dropping **60-90%** in accuracy on hierarchical multi-document
   financial structures — this task's exact shape — while the deterministic
   structure answers 98.4% of declared sums outright. The production pattern
   that does work is LLM-proposes + deterministic-verification + escalation, so
   it stays available for the residual cases, never for the resolution step.

## What Becomes Obsolete

- `SPINE_FIELD_CHAINS` stops being the resolution rule for US filings. It must
  not be left in place as dead-but-live config: either it is deleted, or its
  remaining role is written down explicitly, in the same change.
- The BACKLOG entry "spine chain misses 33 filer-years" is superseded by this
  brief and must be closed with a pointer, not left implying the synonym fix is
  still the plan.
- Any read-path logic that treats an empty cell as one undifferentiated blank.

## Open Questions

- **Financial-sector filers.** A bank's income statement has no single revenue
  origin by construction, and 9 of the 79 universe filers are financials. The
  reconstruction should still render their statements faithfully — the open
  question is only what the DERIVED 14-field view shows for them, and it must
  not be guessed at implementation time.
- **The 3 cash-flow declaration quirks** (GE, NEE, SBUX) surface as flagged
  lines in this cut. Whether any of them should be auto-corrected is deliberately
  not decided here.
- **Cost per company** at 10 years is expected to be minutes, not hours, but has
  not been measured end-to-end; measure it in the live dogfood rather than
  asserting it.
- **Pre-XBRL years.** XBRL is mandatory only from ~2009-2011 depending on filer
  size, so "10+ years" is reachable today but "20 years" is not, without the HTML
  path the user parked.

## Out of Scope

- The TW lane (`kpi_tw`) — different filing format, no calculation linkbase in
  this shape.
- Quarterly periods; annual only, matching the measurement.
- HTML table parsing for pre-XBRL years (user parked 2026-07-26: "可以 我們先
  處理好 XBRL 格式 之後再考慮要不要解析 HTML 表格").
- Statements beyond the three (equity-changes statement, comprehensive income).
- Any change to how the store writes existing KPI points; existing series keep
  their identity.

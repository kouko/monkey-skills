# US revenue coverage and the missing hierarchy — measurement audit

- **Date**: 2026-07-28
- **Scope**: the US statement lanes of `investing-toolkit` — why one filer's stored
  revenue series is nine years shorter than its siblings, whether the obvious fix
  is safe, and where the filing's own line-item hierarchy stops travelling. Lens:
  **what is measurable from source and from the local cache**, not what the
  planning documents assert.
- **Method**: four read-only source traces plus two offline sweeps over the local
  companyfacts cache (`~/.cache/investing-toolkit/sec_edgar/facts_<CIK>.json`).
  No network call, no CLI run, nothing written to the repo by the sweeps. Roster:
  `docs/loom/references/xbrl-verification-universe.md`.
- **Status**: observation only. The decisions this audit fed are recorded in
  `docs/loom/BACKLOG.md` — but they ship on a SEPARATE branch
  (`docs-backlog-resequence-around-hierarchy`) that is not merged as of this
  file landing, so a reader on `main` will not find them yet. This audit is
  deliberately shipped first because its measurements are not re-derivable. Two of this audit's findings were promoted to
  `docs/loom/memory/` as durable lessons (named in §6).
- **Relation to prior audits**: independent of
  `2026-07-27-investing-arc-defect-provenance-audit.md`; that audit asks where
  defects ORIGINATE across arcs, this one measures one defect's data substrate.
  No overlap in evidence.

> **Citation convention.** Source citations below are `symbol` + `path:line` as
> measured on 2026-07-28 against `d24a1067`. Line numbers drift; the symbol name
> is the durable half. Downstream documents should cite THIS file by section
> anchor (§N), never by line — the lesson `2026-07-27-...-provenance-audit.md`
> records in its own errata.

## Verdict (one line)

The store lane cannot tell a filer's revenue TOTAL from one of its COMPONENTS,
because its source is a flat fact table; every proxy tested for that distinction
failed on measurement, and the structure that would settle it is parsed and
shipped by a sibling lane before being discarded unused.

---

## §1 Coverage limit — read this before quoting any number

46 of the 71 roster filers had a cached `companyfacts` payload. The other 25 had
none: ADBE, NFLX, SBUX, CL, MO, MET, TRV, BLK, BX, PLD, LLY, MDT, ABT, ISRG,
CVS, CI, LIN, DOW, NEM, UPS, NOW, INTU, ACN, PYPL, HPQ.

**Every count in §2 and §3 is a FLOOR, not a census.** A filer absent from the
cache is absent from the finding, not evidence of absence.

## §2 Chain-membership audit

**Question**: which revenue-family concepts does each filer actually carry, and
which of those does `_STATEMENT_SPINE_CHAINS["revenue"]`
(`sec_edgar_client.py:3483-3489`) list? That constant is a FETCH LIST — the rule
is stated in `build_statement_backfill`'s own docstring (`:3938`, "NO CONCEPT IS
SELECTED AGAINST ANOTHER. A chain is a FETCH LIST") — so an unlisted concept is
never fetched at any granularity.

**Method**: case-insensitive substring match on `revenue` or `sales` over each
filer's `facts.us-gaap` keys. Deliberately NOT a curated list: curation would
reproduce the omission that caused the gap.

**Result, and its own correction.** The headline reads "42 of 46 filers carry an
unlisted revenue-family concept". That number is true and misleading. The ranked
list is dominated by noise:

| unlisted concept | filers | 10-K rows | what it actually is |
|---|---|---|---|
| `CostOfRevenue` | 18 | 784 | the opposite side of the income statement |
| AFS-securities concepts (many variants) | up to 24 | 315+ | balance-sheet / OCI / cash-flow |
| `DeferredRevenueCurrent` | 17 | 313 | a liability |
| `ContractWithCustomerLiabilityRevenueRecognized` | 19 | 212 | a disclosure |
| `RevenueRemainingPerformanceObligation` | 20 | 145 | a disclosure |
| **`SalesRevenueGoodsNet`** | **14** | **419** | **a genuine revenue line** |

Only **KO (+9 years) and AMD (+2 years)** showed span growth from an unlisted
concept. WFC's and XOM's apparent gains are pattern noise.

> **UNRECONCILED, and recorded rather than resolved.** This +9/+2 came from the
> span-growth sweep; §3's components-only list names FOUR filers (adding MRK 5
> years and PFE 2). Neither MRK nor PFE is in §1's uncached set, so both were
> measured, and the brief groups all three of KO/MRK/PFE under the same concept
> (`docs/loom/specs/2026-07-26-as-filed-statement-reconstruction.md:43-44`). The
> two sweeps therefore disagree about MRK and PFE and the raw output is gone
> (§7), so the honest bound is: **at least 2 filers, at most 4.** Note the
> understatement runs in the direction that favoured abandoning the fix — weigh
> it accordingly before citing the low number.

**The finding that mattered was the sibling.** `SalesRevenueServicesNet`
(11 filers) is also unlisted, and its presence beside `SalesRevenueGoodsNet` is
what exposed the real problem: the same concept is one filer's TOTAL (KO — a
beverage filer with no services line) and another filer's COMPONENT (AMZN, CSCO,
BA, GE, HON, IBM, ORCL, MSFT, TSLA, VZ, UNH). `companyfacts` carries nothing
that distinguishes the two cases, and magnitude does not either — one filer's
component exceeds another's total.

**Chain ORDER cannot rescue it.** The store lane performs no selection
(`sec_edgar_client.py:3821`, "NO SELECTION HAPPENS HERE"); the read side resolves
first-present per period in chain order (`kpi_spine_view._resolve_field`,
`:426-432`) with no row count, no magnitude test and no disagreement refusal.
Appending a component AFTER the total protects only the periods where the total
exists — exactly the periods that needed no help.

## §3 The component-sum rescue — measured and failed

**Hypothesis tested**: where no total is tagged, sum the components; validate the
component set on the periods where a total AND its components both exist.

**Method**: 10-K rows only, span 340-400 days, deduplicated per
`(concept, start, end)` keeping the most recently `filed` row.

**Result**: of 148 (filer, year) overlap pairs — **61 EXACT, 0 CLOSE (within
0.5%), 87 OFF**, most by 30-98%, because filers routinely tag only one of
Goods/Services in a given year.

**The decisive detail is not the ratio.** The same filer flips between EXACT and
OFF across adjacent years (AMD, BA, CRM, KO, TSLA), so no filer can be validated
once and then trusted for the periods that need filling.

Two disqualifying shapes:

1. **CRM FY2013** — components exceed the total by 118%, because
   `SalesRevenueServicesNet` for one period was filed as 181M, then 3,050M (the
   company TOTAL), then 6,667M. The dedupe rule picked the newest, which was the
   corrupt one. Promoted to a durable lesson (§6).
2. **AMD FY2016/2017** — components exceed the total by 1.1-1.4%, because the
   total is an ASC 606 retrospective restatement while the component is the
   as-originally-filed figure. Two accounting vintages, not a bookkeeping error.

**The prize was small regardless.** Components-only years — the years a fill
would actually reach — exist for 4 filers, 18 filer-years: KO 2007-2015 (9),
MRK 2011-2015 (5), PFE 2014-2015 (2), AMD 2008-2009 (2). For each of these the
only concept present is `SalesRevenueGoodsNet` acting as a pseudo-total, so no
summing is involved even where a fill would be attempted.

## §4 Where the hierarchy stops — hop-by-hop

**Question**: the filing declares its own line-item hierarchy (calculation
linkbase). Does it reach a consumer?

| hop | state | evidence |
|---|---|---|
| parse | PRESERVED | `Line` (`kpi_us_statement_shape.py:319-326`) carries `level`, `weight`, `calculation_parent`, `balance`; built in `_line` (`:499-515`) |
| pack | PRESERVED | `_reconstruction_payload` (`pack_us.py:1287-1295`) projects `[asdict(line) for line in lines]` — the whole tree ships in the `reconstruct` JSON |
| view | **USED ONCE, THEN DROPPED** | `_fields_of` (`kpi_spine_view.py:1193-1215`) emits `{field, concept, statement, periods}` plus a conditional `unresolved` (`:1210-1214`) that names candidate CONCEPTS only; hierarchy is consumed at `:1102` (`statement_check.revenue_totals(lines)`) and discarded |
| store lane | **NEVER PRESENT** | source-level absence — this lane reads `companyfacts` (`build_statement_backfill`, `sec_edgar_client.py:3932-3936`), a flat fact table |

**Grounding note on the last row, stated because the obvious citation does not
carry it.** `sec_edgar_client.py:3932-3936` establishes only that the source IS
`companyfacts`; the word `linkbase` appears ZERO times in that module. The
absence claim rests on `analysis-kpi/references/cli-reference.md:597-598` ("a
store dump carries no calculation linkbase" — the sentence wraps, the word is on
598) plus the SEC API's own response shape. Harder grounding would have to come
from SEC's documentation, not from this repo.

**The sharpest finding, and the correction it later needed.** 13 of the 14 spine
fields pick their concept from a hardcoded name chain
(`kpi_spine_view._chain_concept`, `:1108-1124`) **even on the as-filed path where
the tree is present**. Only `revenue` uses the structural rule. The module's own
header (`:244-252`) states this openly as an evidence limit.

> **This is a statement about MECHANISM, not about OUTCOMES, and §8 measures the
> difference.** Read §8 before treating it as a defect: converting those 13
> fields was measured across 14 filings and is NOT justified — the name chain
> produces the correct answer almost everywhere the two methods can be compared,
> and the structural analogue is systematically wrong on one field.

**Dead machinery found in the same trace** (both independently re-verified):

- `level` is captured, packed, rehydrated (`kpi_spine_view.py:1017`) and **read
  by nothing** in production.
- `kpi_us_statement_series.py` has **no importer anywhere in the repo** — only
  its own test loads it; `kpi_spine_view.py:1116,1225` name it in docstrings as
  where a multi-filing join "would" happen. Its `SeriesPoint` (`:137-150`) drops
  hierarchy anyway.

## §5 Feeding the store from the as-filed lane — measured cost

**Why the question arose**: the as-filed lane already has the hierarchy (§4), so
"use it as the store's source" looks like a re-sequence. It is not.

- **The two payloads do not join.** The reconstruct lane emits statement-shaped
  nests (lines × period-keyed value maps); ingest consumes a FLAT fact list
  (`kpi_us_statements.us_statement_pack_to_points`, `:241-317`). No flattener
  exists.
- **`Line` has no `unit` field** (`kpi_us_statement_shape.py:319-326`) while a
  store point requires one — the frozen dataclass must widen, touching every
  construction site.
- **Concept spelling differs**: reconstruct emits `us-gaap_X`, the store lane
  holds `us-gaap:X`. Unnormalized, one series fragments into two. *Inferred from
  two code paths; NOT measured on disk.*
- Period fields exist only as composite key strings
  (`duration_2017-01-01_2017-12-31`); `filed` exists only per filing and must be
  pushed down per fact.
- **The real blocker is trust vocabulary.** The lane deliberately declares no
  `source_kind` (`pack_us.py:1465-1472`), and `kpi_gate.TRUSTED_SOURCE_KINDS`
  (`kpi_gate.py:106-108`) admits exactly three kinds. Adding one is a durable
  decision about what the store is willing to believe.
- **Depth arithmetic**: consecutive 10-Ks overlap by two comparative years, so
  N filings yield N+2 distinct years (`pack_us.py:1202-1212`, verbatim). KO's
  ~19 years needs ~17 filings, ~3 min cold per filer at the measured ~10.7 s per
  filing. `list_filings` can now return them — the only cap is the caller's own
  `limit` (`sec_edgar_client.py:694`), the upstream truncation having been fixed
  by the submissions-pagination work (`:593`, `:642-651`). **A "balance sheet is
  N+1" variant was asserted during this investigation and is WITHDRAWN**: it was
  attributed to the brief's §Users, but that section says "Each 10-K does carry
  three comparative years" (`:71`) and ":164 three comparative years per filing",
  with no statement-type distinction — so the ATTRIBUTION was wrong.
  **The claim itself does have an in-repo source, and this audit originally denied
  that on the strength of a grep it ran but did not read**: a repo-wide search for
  `comparative` returns well over two hundred hits (the exact count drifts with every commit and is not worth pinning), one of which states it verbatim —
  `kpi_us_statement_series.py:6-7`, "A 10-K carries three comparative years for
  income and cash flow and two for the balance sheet". That module is the DEAD
  machinery flagged in §4 (no importer anywhere), so its docstring is unverified
  rather than authoritative. The instruction is unchanged — measure it before
  sizing any backfill on it — but the ground is "the only source is a dead
  module's docstring", not "there is no source".
- **The parser is form-agnostic**; the annual assumptions live around it — the
  inline `["10-K"]` (`pack_us.py:1539-1541`), `RECONSTRUCT_ANNUAL_FILINGS`
  (`:1218`), and `kpi_us_statement_check._era` (`:803-823`) which buckets by
  filing-date YEAR and would collapse four quarterly filings into one bucket.
- **Unverified and load-bearing**: there is **no 10-Q role URI anywhere in this
  repo**, so "the classifier handles 10-Q" is inference, not measurement.

**Recorded decisions any such change must engage with, not ignore**:
`pack_us.py:1465-1472` and
`docs/loom/plans/2026-07-26-as-filed-statement-reconstruction.md:470-479` — the
reconstruction is recomputed, never persisted, because "the correct
cache-invalidation trigger is OUR OWN CODE CHANGING". *Honest scope note*: that
argument is about a DERIVED CACHE sized on seconds saved, and is NOT a claim that
the reconstruction is untrustworthy — it is narrower than "never feed the store".
Separately, the `reconstruct` verb carries an unresolved layer inversion
(`pack_us.py:1229-1252`, "the honest fix is probably that this verb belongs in
analysis-kpi"); making it a store producer would harden that before it is
resolved.

## §6 Claims this audit made and then refuted

Recorded so they are not re-derived, and because each cost real effort to
disprove.

1. **"42 of 46 filers have a coverage gap."** True as a count, misleading as a
   conclusion — see §2. The number answers "how many filers carry an unlisted
   revenue-SHAPED concept", not "how many are missing revenue history".
2. **"HON FY2007-2009 is a components-only case that would understate revenue by
   ~20%."** FALSE. The cache does carry a `Revenues` total for those years (from
   later filings' comparatives) and `Revenues` is already in the chain. HON was
   never at risk. The error was reading "no `SalesRevenueNet`" as "no total".
3. **"Ordering the chain so the total precedes the component makes the widening
   safe."** FALSE — see §2's last paragraph. Ordering protects only the periods
   that already have a total.

Two findings were promoted to durable lessons rather than left here:
`docs/loom/memory/latest-filed-row-is-not-a-safe-tiebreak.md` (from §3's CRM
case) and
`docs/loom/memory/concept-name-matching-cannot-separate-a-line-from-its-namesakes.md`
(from §2).

## §7 What could not be measured

- The raw sweep output was session-scoped and no longer exists. The numbers in
  §2 and §3 are reproducible only by re-running the sweeps against a cache in the
  same state; they are recorded here precisely because they are not re-derivable
  from the repo.
- 25 roster filers were uncached (§1), so every population count is a floor.
- Whether every filer's components sum to its total in the years NOT sampled.
- Whether a 10-Q's presentation roles classify (§5) — no sample exists in-repo.
- Concept-spelling parity between the two lanes (§5) — inferred, not measured.

## §8 Converting the other 13 fields to structure-driven selection — measured and rejected

**Question**: §4 records that 13 of 14 spine fields select their concept by a
hardcoded name chain rather than by the filing's declared structure. Does that
mechanism difference produce WRONG ANSWERS?

**Method**: for each spine field, on each filing, compare the name chain's pick
(first-present in chain order) against a structural filter analogous to
`kpi_us_statement_check.revenue_totals` — drop any candidate whose
`calculation_parent` is itself another candidate for the same field. Classify
per (filing, field): AGREE / DIVERGE / NO-CANDIDATE / STRUCTURE-UNDECIDABLE.

**Evidence**: measured twice. First at **n=2** (the only filings this repo held
row-level `calculation_parent` for: KO FY2017, IBM FY2025). Then, after a live
capture authorised for this purpose, at **n=14** — adding JPM, WFC, GE, UNH,
MSFT, AMZN, MRK, PFE, WMT, VZ, TSLA, BRK-B, each on its most recent 10-K. The
12 filers were chosen to MAXIMISE multi-candidate cases (banks tagging two
revenue concepts, filers with non-controlling interests, goods+services
splits) — a filing with one candidate per field cannot discriminate between the
two methods at all.

**Result: converting is NOT justified.**

1. **The n=2 reasoning was wrong and the larger sample refuted it.** At n=2, 11
   of 14 fields had only ONE candidate in every filing, which suggested the two
   methods were equivalent by construction. At n=14 that set collapses to **6 of
   14** — multi-candidate cases are common, not rare. The "equivalent by
   construction" argument does not hold.
2. **But the two methods still AGREE wherever both resolve** — except on one
   field, where the structural rule is wrong.
3. **`total_equity`: the structural rule is systematically wrong, 8 of 8.**
   Whenever a filer tags both `StockholdersEquity` and
   `StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest`, the
   former's `calculation_parent` is ALWAYS the latter — a structural certainty,
   not filer-specific ambiguity. So the structural filter always promotes the
   including-NCI figure. The name chain's parent-only-first order is the correct
   and deliberate choice (`kpi_equity_terms.py` records 17 of 32 filers resolving
   to parent-only), and this measurement reconfirms it at higher n.
4. **Three new STRUCTURE-UNDECIDABLE cases** — fields the name chain answers
   correctly today and a structural rule would leave unresolved: WFC `revenue`
   (both candidates unparented; the ASC 606 sub-concept has no calculation arc),
   WMT `net_income` (`ProfitLoss` vs `NetIncomeLoss`, both unparented), KO
   `eps_basic` (headline EPS vs continuing-operations-only). Converting turns an
   answered cell into an unanswered one in each.
5. **The inverse opportunity did not grow.** "Name chain finds nothing, structure
   could" is still only KO's `revenue` — the case that motivated the existing
   `revenue_totals`. **Measurement gap, stated because it is the one thing that
   could still justify structural work**: production has an unrestricted
   structural finder for `revenue` ONLY, so for the other 13 fields this check
   could not run. Absence of new opportunities there is unmeasured, not proven.

**Consequence for planning**: the rung that proposed this conversion was
withdrawn on this evidence. Do not re-propose it from §4's mechanism observation
alone — §4 says the tree is unused, §8 says using it would make the answers
worse.

**Where the raw output lives**: the per-(filing, field) detail was session-scoped
and is gone, as was the enlarged capture (12 filings, ~5.9 MB of verbatim rows).
Re-deriving requires re-running the capture. The classifications above are
recorded observations.

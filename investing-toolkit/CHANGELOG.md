# Changelog

All notable changes to investing-toolkit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v2.39.2] — 2026-07-30

### Changed — `data-markets` description diet

- Frontmatter `description` reworded and hard-wrapped at ≤76 chars/line
  (no trigger hook dropped; trimmed wording survives in each SKILL body)
  — part of a cross-plugin pass trimming four outlier skill
  descriptions.

## [v2.39.1] — 2026-07-27

### Fixed — a filer's history stopped where SEC's `recent` block did

`sec_edgar_client.fetch_submissions` read only the main submissions document's
`filings.recent` block, which SEC caps at one year or the 1,000 most recent
filings (whichever is more). Older filings live in the archive documents named
by `filings.files[]`, and those were never requested — so a company's returned
filing history was bounded by its TOTAL filing volume, not by how much history
it has. The pipeline returned the LEAST history for the most actively-filing
companies, and returned it as an ordinary success with no truncation signal.

Measured live 2026-07-27 across the 71-filer roster in
`docs/loom/references/xbrl-verification-universe.md`, asking each for 8 annual
filings:

| | returned | actually held |
|---|---|---|
| JPM | 1 | 27 |
| BAC | 1 | 32 |
| C | 1 | 27 |
| META | 2 | 14 |
| WMT | 3 | 32 |

29 of 71 filers were truncated; only 37 reached the 10 distinct annual periods
that a decade of trend analysis needs.

- `fetch_submissions` now follows `filings.files[]` and merges every archive
  page into `filings.recent` before returning. The merged payload keeps the
  parallel-array shape every reader already expects, so `list_filings` and
  every pack are unchanged — this is a transport fix, not an interface change.
- **A failed archive page returns an error, never a partial history.** A
  short-but-successful answer is the defect being fixed wearing a different
  hat: the caller cannot tell "this filer has 3 10-Ks" from "page 2 of 5
  failed". Page errors are not cached, so one 503 cannot poison a filer for a
  TTL.
- **The merged payload uses a new cache key** (`submissions_full_{cik}`). The
  payload's shape is unchanged but its semantics are not — an entry written by
  the old code is a truncated history indistinguishable from a complete one,
  and aliasing the old key would have let a warm cache serve truncation out of
  fixed code, per company and unpredictably.
- **Each archive page is cached under its own 7-day key.** The page fan-out is
  very uneven — 28 of the 33 flagged filers have 0-3 pages, but JPM has 68, C
  39, BAC 20 — so re-paying it on every 24 h expiry of the main document would
  roughly double a `reconstruct` run for the sector that needed the fix most.
  Measured: JPM cold 69.3 s, then 31.5 s once only the main document expires.
  The TTL is 7 days rather than permanent because SEC re-partitions the
  newest archive page in place.

- **`--no-cache` clears the submissions caches again.** It unlinked
  `submissions_{cik}` — the key nothing reads any more — leaving both the
  merged entry and the 7-day archive pages warm, so the flag reported a bust
  and then served the cache. The key set now lives in `bust_cik_caches()`,
  which also globs the filer's archive pages (their names embed the CIK, so
  the glob cannot reach another company). Measured on JPM: 70 entries removed.
- **An archive entry with no `name` is an error, not a skip.** SEC states each
  entry's `filingCount`, so dropping one discards a known, counted block —
  a probe with a nameless entry declaring 1,138 filings previously returned a
  clean success over a history missing all of them.
- **A short column in `filings.recent` no longer mislabels filings.** The join
  padded columns that were *missing*, never ones that were *short*; a short
  column let the next page's rows slide forward, so filings after the gap
  carried an earlier filing's accession number. `list_filings`'s bounds checks
  turn that into wrong data rather than an error, which would have reached
  `pack_reconstruct` as the wrong document filed under the wrong year.

- **`--no-cache` reports what it removed**, including zero, on both its
  branches. A ticker the map cannot resolve busts nothing, and a silent no-op
  there is indistinguishable from a successful bust — the failure this flag
  exists to rule out. An unreadable ticker map is reported as its own cause
  rather than as an unknown ticker, so the operator is pointed at SEC and not
  at their own input.

Grounding for the four above: three whole-branch review rounds, each with a
mutation pass. The first found 5 of 9 mutants of the merge surviving the full
suite — including deleting the padding whose own docstring described behaviour
the code did not have. **12 of 12 distinct mutants of this change are now
killed** by `tests/data/test_sec_submissions_pagination.py`, none surviving —
a claim about that file, not about the whole suite, which is what was
measured. Live re-verification after the fixes: JPM cold 8/8 filings, 10
annual periods, and 70 cache entries removed by one `bust_cik_caches` call.

### Known limits

- Two filers on the roster remain short for reasons this change does not
  address, and both are legitimate: DOW (7 10-Ks, 2019 spin-off) and PLTR (6,
  2021 IPO).
- Two more return almost nothing because their ticker resolves to a
  re-registered holding company whose CIK carries no history — XOM (0 10-Ks
  under CIK 2115436; the 7 real ones sit under 34088) and BLK (2, oldest
  2025-02). That is an entity-resolution defect, tracked separately; this
  change does not stitch across a predecessor CIK.

## [v2.39.0] — 2026-07-26

### Added — as-filed three-statement reconstruction, and a typed empty cell

A US filer's three statements are now reconstructed from the filing's OWN
presentation and calculation linkbases, instead of being forced through a fixed
14-field concept chain. The 14-field spine becomes a derived VIEW over that
reconstruction rather than the storage format.

- `pack.py --pack reconstruct` (US only) returns one company's statements per
  accession, carrying the filer's own labels, weights, calculation parents and
  per-period values — plus a `verification` section with per-era resolved counts,
  a reason per unresolved statement, and a sum-check census in which
  `within_rounding` is its own answer rather than a rounded-away `agrees`.
- `kpi_spine_view.py derive-as-filed` reads that payload and emits the 14 fields
  with **every empty cell typed**: `not_presented` (the filer files no such
  line), `not_tagged`, or `derived` with the arithmetic that produced it.

Why: measured across 65 domestic operating filers, the fixed chain found NOTHING
for whole sectors — utilities (`RegulatedAndUnregulatedOperatingRevenue`), REITs
(`RealEstateRevenueNet`), mining (`RevenueMineralSales`), software
(`SalesRevenueServicesNet`), pharma and beverage (`SalesRevenueGoodsNet`) — so
those filers' revenue series began in 2018, when everyone converged on the
ASC 606 concept. Two more (PSX, XOM) were silently understated by 2-3% because
each names its total with a concept absent from the chain.

Grounding: across 56 filers, 501 of 509 declared subtotals reconcile against the
filers' own reported figures, and the income statement is 212 of 212. Acceptance
is line-by-line against the filed document, which surfaced that a filer files
its income statement twice and the two renderings disagree on 15 of 26 labels
with zero figures differing.

### Known limits

- The structural rule's 63-of-65 was measured on filings FILED 2016-2018;
  `resolution_report` therefore breaks its counts down by era rather than
  assuming the sampled window generalises.
- `verify` sees presented lines only, so a calculation child absent from the
  statement face produces a false `disagrees` it cannot distinguish.
- XBRL is mandatory only from ~2009-2011, so 10+ years is reachable and 20 is
  not without HTML parsing, which stays out of scope.

## [v2.38.0] — 2026-07-26

### Added — US as-reported annual statement lane + derived spine view

A US filer's three-statement history now ACCUMULATES in the KPI store instead
of being recomputed and thrown away on every memo run. The lane stores what
the filer actually tagged and derives the market-comparable spine at READ
time, so concept selection stays correctable.

- **`statement-backfill` pack** (`pack.py --pack statement-backfill --ticker
  <T> --market us`) — walks SEC `companyfacts` for the source concepts of the
  14 spine fields and keeps only annual, 10-K-carried rows, classified by each
  row's own start→end span rather than its `fy`/`fp` labels. Every rejected
  row lands in `coverage.skipped_rows` under a named reason. A ticker whose
  resolved CIK carries no statement history is a loud typed error with no
  `facts` key — never an empty-but-successful pack — and a truncated history
  is surfaced in `coverage`, never stitched from a predecessor CIK.
- **`kpi_us_statements`** (pure library) + **`kpi_us_statements_ingest
  ingest --filing`** (store driver) — the `kpi_id` is the filer's OWN qname,
  verbatim and namespace-preserved (`us-gaap:Revenues`). No slug derivation,
  so the id is injective by construction and `us-gaap:Revenues` and
  `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax` are TWO
  series, not one silently-resolved series. Every point is built before the
  first append, so a rejected pack writes nothing; re-ingesting the same pack
  appends no duplicate.
- **`kpi_spine_view derive`** (pure read-side view) — maps a `kpi_store dump
  --company` payload onto the 14 canonical spine fields, resolving PER PERIOD
  which concept represents each field. The render pipeline is one plain pipe
  (`kpi_store dump | kpi_spine_view derive | tearsheet_format`);
  `tearsheet_format.py` is unchanged. A field absent from a period yields no
  entry and a field absent everywhere yields no row — never 0, never a
  derived guess.
- **Balance-sheet identity flag.** Per period the view checks `total_assets −
  (total_liabilities + mezzanine + whole equity)` and attaches a
  `balance_identity` flag above a 1e-5 RELATIVE residual. It never suppresses
  or alters a value. **The flag is attached to the store payload but is NOT
  rendered by `tearsheet_format`** — a flagged period looks identical to a
  clean one on the rendered tearsheet, so read the raw JSON from
  `kpi_spine_view derive` (the flag rides on the `total_assets` series' period
  entry) to see it. Documented in `analysis-kpi/SKILL.md` and its
  `references/cli-reference.md`.

**Capability limit — this lane cannot return 20 years of history.** US XBRL
begins with the SEC's 2009-2011 phase-in, so `companyfacts` holds nothing
earlier. Measured over the committed 47-ticker probe
(`investing-toolkit/tests/data/fixtures/us_statement_shapes_probe_2026-07-26.json`):
**0 of 46 usable filers have ≥20 usable years; the median is 18**, and the
floor moves forward one year per calendar year rather than deepening
backward. Anyone expecting two decades should read this line rather than an
empty table. Pre-2009 history is reachable only via HTML/text extraction
(which this repo forbids) or a vendor-standardized source — a separate
product decision.

The lane keys the store on the TICKER, the same as the existing
dimensional/top-line lanes, so one filer has one store company and a single
`dump --company AAPL` feeds the spine view every lane's series at once.

### Fixed — `build_top_line_backfill` silently truncated 10 of 47 filers

The top-line backfill picked the first allowlist concept that returned ANY
rows and stopped there, so a filer that switched revenue tags mid-history
kept only its pre-switch years. Selection is now resolved **per period**
across every allowlist concept, so both eras emit as one continuous annual
series. When two concepts cover the same period, allowlist order breaks the
tie only if the values AGREE; when they disagree the period is skipped with a
named `top_line_concept_value_conflict` reason rather than guessing which tag
is right.

**Your existing stored `total_revenue` series may be incomplete.** This was a
defect in shipped code, not a new capability: measured on the 47-filer probe,
10 filers were getting a silently short series (AAPL, CRM, F, HD, HON, META,
MS, MSFT, TGT, WFC — HD and MSFT ended at 2010, losing ~15 years each). The
store is append-only, so the missing years do not appear retroactively —
**re-run the `kpi-topline-backfill` pack and re-ingest** to fill them in. The
recovered years append as ordinary points; nothing already stored is
rewritten.

Offline suite: 1175 passed, 2 skipped, 61 deselected (from 1089 at the
branch base). Beyond the suite, the lane was run end to end against six real
filers — MSFT, AAPL, WMT, JPM, TSLA and XOM — chosen for the shapes that
break it rather than for coverage; that run found three defects the suite
could not see, all fixed here.

## [v2.37.0] — 2026-07-25

### Fixed — `derive_kpi_id` made injective, up to case

`derive_kpi_id` minted the durable series identity for every dimensional KPI
point by a lossy transform of the fact's XBRL signature, and the loss cut both
ways — too coarse on one axis, too fine on another. A live 47-filer probe
measured both: 23 of 47 filers lost their entire dimensional lane to a
collision that should never have happened, and 21 series were split across two
identities that should have been one. This release fixes the identity function
so neither case arises.

The guard's all-or-nothing blast radius — one colliding signature refuses the
whole pack, not just that series — is unchanged and remains open; it simply has
far less to fire on now.

- **A non-default `ConsolidationItemsAxis` member now discriminates
  `kpi_id`.** A segment's operating view and its intersegment eliminations —
  previously the same id, because the axis was dropped entirely — now mint
  two distinct series. This axis accounts for 128 of the 149 collisions the
  47-filer probe found (the other 21 are the case drift below); the 23 filers
  that lost their whole dimensional lane did so to one kind or the other, not
  to this one alone. A default or absent member still adds no token, so the
  already-shipped 2.36.0 fold (an absent tag and an explicit
  `OperatingSegmentsMember` are one series) is unchanged.
- **`kpi_id` now carries a 12-hex digest of the case-folded identity
  tuple**, making it injective up to case — mirroring `kpi_store._series_key`'s
  own readable-stem-plus-digest pattern. One filer's 10-Q and 10-K spellings
  of the same segment (e.g. `DataCenterMember` vs `DatacenterMember`) used to
  mint two ids, permanently splitting that series' quarterly history from its
  annual history; they now fold into ONE series carrying both. 21 such series
  were measured on the probe corpus.
- **The collision guard (`_claim_kpi_id`) now accepts a case-insensitively
  equal claimant** — both spellings' points append into the one shared
  series — and still raises on every other, structurally distinct claimant.
- **`kpi_store` now budgets the series FILENAME length.** The readable
  `<company>__<kpi_id>` stem is capped so the atomic-write temp file stays
  within the 255-byte filesystem limit; the collision-proofing digest is still
  computed over the FULL raw `(company, kpi_id)` pair, and any filename that
  already fit is byte-identical. Found by the close-out dogfood, not by the
  suite: the id digest added 14 bytes, which pushed JNJ's 4-axis signatures
  from 243 to 257 bytes and aborted that filer's entire ingest with
  `OSError: [Errno 63] File name too long`. `kpi_id` values are unaffected —
  only the file the series is stored in.

**Breaking: `kpi_id` values change format.** Any series written by an
earlier version will not line up with points written by this one. No
migration is shipped, and none is possible: under the old scheme, a
non-default consolidation member produced an id byte-identical to the
default member's, so no script could tell the two apart after the fact.
Anyone holding an existing `kpi-store` should re-ingest from source. Shipped
as a minor bump because the store is verifiably empty at ship time — no
consumer is broken in fact — not because the change is non-breaking.

Offline suite: 1087 passed, 2 skipped, 61 deselected (`-m "not network"`).
Close-out dogfood: the real `ingest_pack` → `kpi_store.append` path run over
all 47 cached live SEC packs into an isolated store — 47 of 47 ingested, 0
aborted, 51,147 facts → 2,100 series → 35,415 stored points.

## [v2.36.0] — 2026-07-25

### Added — company total (top-line) revenue, two-lane store ingestion

A US company's top-line revenue now reaches the KPI store and renders on the
tearsheet beside the segment breakdown, via two lanes that land under one
canonical series.

- **Lane B — per-filing parse emits the flat top-line fact.** The existing
  per-filing XBRL parse (`extract_dimensional_revenue`) now also identifies and
  emits the filer's winning top-line concept at zero extra fetch cost, via a
  closed, ordered allowlist grounded in XBRL US DQC Revenue Guidance
  (`select_top_line_concept`) — one winner per filing, `dimensions == {}`.
- **Lane A — `kpi-topline-backfill` pack.** A new `build_top_line_backfill`
  reshapes the `companyconcept` REST series into annual-only history predating
  the filings Lane B fetched, reachable through the data layer's one pack
  facade (`--pack kpi-topline-backfill`). Quarterly rows, and rows whose period
  end has *crossed into January*, are skipped with a named coverage reason
  rather than guessed — Lane A has no dei fiscal calendar to disambiguate a
  52/53-week filer's year-end crossing, so Lane B stays the authority there.
  That check is one-sided by design: a December year-end gets the same label
  from both lanes — provided the filer's *nominal* year-end is also in
  December — and is backfilled normally, so the ordinary
  December-fiscal-year-end filer keeps its full history. Known residual: a
  filer whose nominal year-end sits in early January while the year's actual
  end drifted back into late December still diverges, undetectably from this
  lane, and is labelled one year lower than `kpi-quarterly` labels it; treat
  `kpi-quarterly` as the authority wherever both lanes cover a year.
- **Canonical `total_revenue` series, per-lane provenance.** `kpi_xbrl_ingest`
  stops skipping flat facts and routes them to the fixed canonical `kpi_id`
  `total_revenue` (not a concept-derived slug), grouped on one key so a filer
  that switches tagging across years merges into a single series without
  tripping the collision guard. Provenance is assigned per lane within one
  ingest call: Lane A's points carry `xbrl-companyfacts`, Lane B's carry the
  new trusted kind `xbrl-topline` (admitted to `kpi_gate.TRUSTED_SOURCE_KINDS`,
  pinned to the `<trust-class>-<lane>` naming convention), and dimensional
  points keep `xbrl-dimensional`.
- **Store-aware disagreement guard.** Before appending a flat top-line point,
  the ingest driver reads the existing series and raises when a stored point
  shares the same dedup key (company, kpi_id, period, as_of, accession) but
  carries a different value — the two lanes read the same filing under the
  same accession, so a disagreement there means one of them is wrong. A point
  for the same period under a DIFFERENT accession still appends as a legitimate
  restatement, unchanged.
- **e2e seam test — and what it caught.** Both lanes ingested into an isolated
  store, then rendered: a fiscal year both lanes cover resolves to the same
  value and the same period label, backfill-only years join the same series,
  and the tearsheet shows the total row beside the segment rows with the
  restatement marker unchanged. Wiring the real producers together this way,
  instead of each lane's own hand-built envelope, is what surfaced the arc's
  one real shipped defect: the backfill producer emitted no `fiscal_calendars`
  map, and `facts_to_points` refuses to guess a point's source filing form
  without one, so 100% of the backfill lane's facts were silently rejected at
  ingest until `18fc47fd` fixed it. That fix is deliberately narrow about which
  form it will assign: only a literal `10-K` carrier earns a fiscal-period
  focus, and every other carrier — including a `10-K/A` amendment, which is
  exactly where a restated annual figure would land — is skipped with a named
  coverage reason rather than guessed. An amended year therefore still keeps
  its original, pre-restatement number in the backfill lane; closing that gap
  is deferred, not silently accepted.

Offline suite: 1072 passed, 2 skipped, 61 deselected (`-m "not network"`).

## [v2.35.0] — 2026-07-25

### Added — TW-market XBRL → kpi_store producer

The store-backed tearsheet gains a TW-market feed. A new `kpi_tw` producer maps
a TW iXBRL filing's canonical layer into the market-agnostic `kpi_store`, and a
`kpi_tw_ingest` driver appends those points to the UNCHANGED store — so the
existing `report-kpi-tearsheet` renders a TW multi-period series with no store
or tearsheet code change.

- **`kpi_tw` producer.** `as_of` is the authorisation-for-issue date parsed from
  the filing's ROC-era 民國 date fact
  (`tifrs-notes:DateAndProceduresOfAuthorisationForIssueOfFinancialStatements`) —
  a deterministic, non-wall-clock, already-fetched date the store's `as_of` guard
  accepts. `tw_canonical_to_points` maps the `twse_ixbrl` canonical layer into
  market-agnostic `kpi_store` points, deriving `kpi_id` =
  `<canonical-field-slug>[__basis-<C|A>]` (C=合併/A=個體) — since TW carries no
  us-gaap dimensional axes, the consolidation basis is the only discriminator,
  substituting for the US `axis=member` signature. The canonical field-slug (not
  the raw concept) is the durable identity, so a company's revenue stays one
  series across concept/taxonomy variation. Flat totals are kept (inverting the
  US empty-dims skip).
- **`kpi_tw_ingest` driver.** Reads a filing's canonical, calls the producer, and
  appends each point to the UNCHANGED market-agnostic `kpi_store` (reusing
  `kpi_store.append`; no cross into the data-markets cache layer). Idempotent
  append-only — running it over N filings builds the cross-period series.
- **興櫃-ready.** The 興櫃 semiannual cadence fits the store's existing `_qtrs`
  machinery (6-month duration → 2 quarters) with no new `period_kind`.

Note: the ingest consumes a filing envelope (canonical + facts) the caller
assembles — `run_pipeline` emits canonical but not `facts` today. A glue-free
`pack_tw` envelope verb (mirroring `pack_us.pack_kpi_quarterly`, so TW is
"ticker→tearsheet without glue" like US) is a post-ship follow-up.

## [v2.34.0] — 2026-07-24

### Added — US XBRL → kpi_store producer (dimensional revenue)

The tearsheet's store-backed history now has a second data-market feed. A new
`kpi_xbrl_ingest ingest` verb maps each US filing's dimensional signature to a
mechanically-derived `kpi_id` and appends every cross-filing vintage to
`kpi_store.py` — no collapse, mirroring the existing TW iXBRL producer's
append-only doctrine. A US ticker's fact-pack now renders a KPI tearsheet
(with restatement † markers) without hand glue between the fetch layer and
the store.

- **`kpi_xbrl_ingest ingest` verb.** Dimensional revenue facts from a US
  XBRL fact-pack are grouped by dimensional signature, each signature mapped
  to a stable `kpi_id`, and every cross-filing vintage appended to the
  company's store series — restatements surface via the store's existing
  `history`/`disagreement` doctrine rather than being silently overwritten.
- **`period_start` carried onto points.** Dimensional facts now emit
  `period_start` alongside `period_end`; the field is carried through onto
  store points so period-boundary reconstruction no longer needs a separate
  lookup.
- **e2e seam probe.** pack → ingest → tearsheet render exercised end-to-end;
  a restatement renders its dagger (†) through the full pipeline, not just at
  the store layer.

Full suite: **1004 passed, 2 skipped, 61 deselected.**

## [v2.33.0] — 2026-07-24

### Added — TW iXBRL endorsement/guarantee (背書保證) ingestion

A new curated data field surfaces per-counterparty endorsement/guarantee rows
from TW MOPS iXBRL filings. The section carries no leaf `tuple_ref` and only
shared `context_ref`s, so document order is the sole handle for reconstruction.

- **`extract_endorsement_guarantee_notes`.** New extractor in
  `twse_ixbrl_notes.py` reconstructs per-counterparty endorsement rows by
  document-order segmentation on the `CompanyNameOfTheEndorserGuarantor` anchor
  (endorser / counterparty / individual limit / ending balance / actual provided
  / collateral-secured / relationship Y-N flags), plus a curated aggregate: a
  **span-scoped** total actual/ending balance, counterparty count, and a
  subsidiary-vs-external split derived from the Y/N flags. The aggregate is
  span-scoped to the endorsement rows to avoid the 資金貸與 (financing-to-others)
  table-conflation — a doc-wide sum would overcount (e.g. 台泥 1101: 62.8bn
  span-scoped vs 105.9bn doc-wide, where 74 of 113 `ActualAmountProvided` facts
  belong to the separate 資金貸與 note). The 0-anchor case yields a first-class
  "none" result (explicit empty summary + empty rows, never a silent zero).
- **Routed by population through `_extract_notes`.** The curated endorsement
  field surfaces in the pipeline output for every taxonomy where the section is
  present (industrials most commonly); the prior deferral test flipped from a
  must-NOT-surface assertion to an inclusion assertion. No parser change, no
  fetch change — the data is reachable with the current pipeline.

## [v2.32.1] — 2026-07-24

### Fixed — memo consumes the financial-sector DCF `not_applicable` marker

Post-ship follow-ups to the 2.31.0 financial-sector arc. Previously a financial
ticker's memo silently degraded: `dcf_compute` emitted a structured
`{"not_applicable": "financial-sector"}` result that no downstream consumer
recognized, so the memo's `intrinsic_mid` resolved to a silent `null` with no
explanation. The Phase-4 pipeline now renders it explicitly.

- **DCF N/A rendered end-to-end.** Three surfaces gained an explicit marker
  branch: the Phase-4 seed contract (`report-equity-memo/references/phase4-seed-contract.md`,
  incl. an acceptance-check (a) carve-out so a compliant N/A memo is no longer
  self-rejected), the memo orchestrator (`report-equity-memo/SKILL.md` Phase 3/4:
  `intrinsic_mid: null` stated with reason, never a silent default), and the
  investing-team memo protocol (`domain-teams` 5.10.1) — all render
  `DCF: N/A — financial sector` quoting the `reason` string, with the
  rule_verdict/Deviation-Block flow bypassed (no fabricated verdict). Producer
  `dcf_compute.py` output shape unchanged.

### Changed — internal refactors + test coverage (no behavior change)

- **Rule-of-Three extractions.** `twse_ixbrl_canonical.py` gained
  `_ordered_values_meta` (3 call sites) and `twse_ixbrl_notes.py` gained
  `_group_and_select_current` (3 note extractors) — duplicated sorted→values→meta
  and by-concept-grouping blocks collapsed; canonical output byte-identical.
- **Decode-coverage test.** New fact-count-equality test under the production
  `decode_ixbrl_document` (UTF-8-first) path — the legacy big5hkscs test was the
  only fact-count guard before; all 8 stored-count fixtures pass with zero deltas.
- **Dead citation cleanup.** Five stale `scratchpad/fh-measurement*` comment
  references in the canonical/notes modules replaced with the operative measured
  fact inline.

## [v2.32.0] — 2026-07-24

KPI tearsheet — the store's per-company history now renders. A new
`report-kpi-tearsheet` skill turns `kpi_store.py`'s durable observation
history into a one-company Markdown tearsheet, closing the gap the
v2.30.0 entry called out ("a rendered tearsheet is deferred" — **superseded
by this entry**: a format now ships).

- **kpi_store read CLI.** `list-series` prints every `[company, kpi_id]` pair
  as JSON; `dump --company <C>` emits the closure-grouped pinned payload —
  points grouped into periods via `same_period`, `canonical_value` computed
  through `Decimal`, `disagreement` flagged per the `history` doctrine,
  corrupt series files skipped per-file into `warnings` rather than raising.
- **report-kpi-tearsheet skill.** `tearsheet_format.py` renders the dump to
  Markdown: periods as columns, newest-left, one row per `kpi_id`; a
  disagreement cell carries a `†` marker and every vintage (value, as_of,
  source accession) is listed in a `## Revisions` block; empty series render
  a graceful no-records card; a footer states provenance and echoes
  `warnings` verbatim; an optional `--out <path>` writes the file instead of
  stdout. Layout follows US-terminal convention (periods as columns); the JP
  lane's periods-as-rows convention is documented as a conditional reversal,
  not yet built.
- **Hardening (T2b).** `list_series` / `history` no longer crash on a
  shape-corrupt series JSON file (non-dict content, or a dict with
  non-list `points`) — the same never-raise contract `dump` already held,
  root-caused into the shared `_load_series` loader.
- **Docs.** `analysis-kpi/references/cli-reference.md` documents both new
  subcommands (flags, exit codes, one worked example each).

Offline suite: 982 passed, 2 skipped (`-m "not network"`).

## [v2.31.0] — 2026-07-23

### Added — Taiwan financial-sector iXBRL ingestion (-fh / -basi / -bd / -ins)

Taiwan financial-institution filings now ingest into memo-fetch. Before this, a TW
financial-holding / bank / broker / insurer ticker fell through to a yfinance stub;
now the real MOPS iXBRL canonical + bank asset-quality notes flow into the memo.

- **Five taxonomy families behind a classifier.** `classify_taxonomy` routes each
  filing to one of `ci` (industrial, existing) / `fh` (financial holding) / `basi`
  (standalone commercial bank + bills-finance) / `bd` (broker) / `ins` (insurer), via
  a builder registry; four new financial canonical builders share one
  `_build_financial_canonical` helper (deposits kept distinct from interest-bearing
  borrowings; `-ins` resolves the insurance-contract-liability field with a
  first-present `tifrs-bsci-ins:` → `ifrs-full:` fallback for reinsurers).
- **Bank asset-quality notes.** NPL ratio / coverage ratio / NPL amount / gross loans
  for the Total-Loans row, tagged with the banking-subsidiary name — `-fh` via the
  `ix:tuple` hierarchy (per-subsidiary, incl. two-bank post-merger FHCs), `-basi` via
  the `context_ref` suffix pattern.
- **Fetch: report_id C→A fallback.** Individual-only filers (insurers, bills-finance)
  are served only at `report_id=A`; the pipeline now tries C then A.
- **Smart decode.** The financial family is served UTF-8 despite a `charset=big5`
  declaration (industrial `-ci` is genuine Big5); `decode_ixbrl_document` decodes
  UTF-8-first with a Big5 fallback so Chinese names/labels are legible.
- **DCF fail-loud for financials.** Canonicals emit `sector_class="financial"` and omit
  DCF-trigger fields; `pack_tw` forwards `sector_class` into the memo payload and
  `dcf_compute` returns a structured `not_applicable` (rather than a silently-wrong
  bank valuation or a hard crash at the memo's Phase-3 artifact gate).

Offline suite: 963 passed (`-m "not network"`). 24-file arc, whole-branch review PASS.

## [v2.30.1] — 2026-07-23

- **report-equity-memo Phase 4 guard (docs-only).** Phase 4's delegation to
  `domain-teams:investing-team` MUST be driven from the main conversation —
  never wrapped inside a single subagent. Live-probed 2026-07-23: a subagent
  exposes no `Agent`/`Task`/`Workflow` tool, so a skill executed inside one
  silently loses its internal multi-agent orchestration (the writer≠evaluator
  gate panel degrades to self-audit). The SKILL.md now states the correct
  dispatch shape and requires explicit disclosure when a run executed degraded.

## [v2.30.0] — 2026-07-22

KPI observation history (US lane) — the durable store can now answer "what have I
recorded for this company, and has it changed?" A figure you confirmed months ago
can quietly stop being what the company says: J&J's FY2021 revenue was
93,775,000,000 in the FY2021/FY2022 10-Ks and re-presented as 78,740,000,000 in
FY2023. `history` surfaces every vintage of one period across filings so that
change becomes visible instead of a stale number carried forward.

- **Enumerable store.** `list_series` / `list_companies` / `list_kpis` recover
  what's held by reading each series file's content (the filename digest is
  one-way); a corrupt file is skipped per-file, never fatal to the listing.
- **Period identity = the raw `(start, end)` pair.** A stored point carries
  `period_start`/`period_end`/`period_kind`; `same_period` groups two observations
  of one fiscal period across filings by exact date pair with a month-end-snap
  fallback, refusing to merge genuinely different spans. Fiscal labels stay
  analysis coordinates, derived from the filing's own fiscal-year-end — never
  `end[:4]` or the companyfacts `fy` tag (validated across 14 filers / 64k groups:
  the pair is byte-stable 98.99%, the `fy` tag disagrees 98.3%, `end[:4]` mis-keys
  up to 64% for non-December fiscal years).
- **Explicit per-point `scale`; every lane stores a base-comparable value.** The
  prose lane hardcodes scale 1 (its value is already base — Part-2 folds the
  magnitude in); the 8-K table lane sets scale = magnitude(confirmed unit) at
  commit while its value stays the verbatim printed cell; XBRL is base → 1.
  `history` compares `value × scale` through `Decimal` (not binary float — a float
  multiply fabricated a false restatement on 1.4–5.1% of realistic two-decimal
  cells). A same-figure-at-two-scales pair reads as no change; a real revision
  reads as a change. Detection is a value diff, never an event lookup; a
  superseded value is retained, never marked wrong.
- **Write-time integrity stamp.** Each new prose point carries a sha256 of the
  anchored token plus the surface version — recording that can't be added
  retroactively (the read-time re-verifier is deferred).

Scoped to the US lane (the other markets' four copy-pasted producers + a JP stub
are a separate cleanup). Retention was dropped (the "≥10yr norm" was unevidenced);
a rendered tearsheet is deferred (no shipped public format exists, and the prose
lane isn't user-invocable yet). Change-folder: none (brainstorming-brief input);
plan `docs/loom/plans/2026-07-22-kpi-observation-history.md`.

## [v2.29.0] — 2026-07-20

Narrative-evidence arc, Slice A **Part 2** (number robustness): makes the prose
KPI numbers CORRECT and rejects the ones that were never KPIs. Part 1 shipped
the walking skeleton; a live 5-company test then showed META's Family DAP
"3.56 billion" committing as `3.56` — off by 1e9 — which is what this part fixes.

- **Word-scale magnitude parsing.** The locator absorbs a trailing
  thousand/million/billion/trillion into the matched token, so the source anchor
  spans the whole phrase, and the value derivation applies the multiplier through
  `Decimal` rather than binary float.
- **Date / fiscal-period rejection.** A 4-digit year preceded by a period cue
  ("fiscal 2026", "Q1 2026") is a label, not a value. Deliberately narrow — a
  bare year with no cue survives.
- **Bounding qualifiers.** "up to 45,000 deliveries" commits carrying its
  qualifier instead of as a bare 45000 fact, so neither the human confirmer nor a
  downstream memo reads a precision the filing never claimed. `"over"` is guarded
  against common phrasal verbs ("turned over 931 units" states no bound).
- **One consistent normalization.** nbsp/thin-space thousands separators,
  full-width and Arabic-Indic digits, full-width comma/period, and curly quotes
  fold into one canonical surface. Every fold is one char → one char, so all
  char offsets and the `text[start:end] == token` anchor survive untouched.
- **Bounded provenance context.** The committed quote is now the number plus a
  bounded slice of its surrounding text — enough to verify the datum, not enough
  to drag a filing paragraph's executive names and compensation figures into the
  durable store.

Review caught a value-FABRICATION bug mid-branch: the grouping regex had a
trailing digit guard but no leading one, so re-scanning could start inside a
longer digit run and fuse two unrelated numbers — `"Fiscal 2026<nbsp>250,000
units"` produced the token `"2026,250,000"`. The source anchor still HELD on that
token, since it is guaranteed by construction; it offers no protection against
this class. Fixed with the mirror-image guard.

The whole-branch review then found two more of the same class, both living in the
seam BETWEEN tasks where no per-task review could see them: magnitude absorption
had reopened the period-label filter (`"fiscal 2026 billion-dollar cost program"`
committing 2,026,000,000,000), and an nbsp acting as a word separator after a
comma-grouped number fabricated a fused value (`"1,428<nbsp>500-mile trucks"` →
1,428,500). Both closed, each with a regression test written against the
interaction rather than against either layer alone.

Two known limits are declared in the plan's Notes rather than papered over: a
bounding qualifier separated from its figure by an intervening word; and personal
data in the SAME clause as the number, which no fixed-width window can exclude
without entity recognition. Plan:
`docs/loom/plans/2026-07-20-8k-prose-kpi-intake-part-2.md`; change-folder:
`docs/loom/2026-07-19-8k-prose-kpi-intake/`. Part 3 (lifecycle/hardening) and the
SKILL wiring remain deferred.

## [v2.28.0] — 2026-07-20

Narrative-evidence arc, Slice A **Part 1** (walking skeleton): a "Route B for
prose" mechanical producer that isolates a single operational-KPI datum from an
8-K EX-99 earnings-release PROSE sentence (the class Route B's table walker and
the bulk-narrative layer both drop — e.g. AMZN headcount, TSLA deliveries), with
a verbatim quote + character-offset anchor, through the SAME three-layer trust
(mechanical value+coords / LLM semantic / human confirm-all) into the EXISTING
tier-① store. Foundational machinery + tests; not yet wired into a user-facing
SKILL workflow (that + number robustness + lifecycle/hardening are Parts 2–3).
Change-folder: `docs/loom/2026-07-19-8k-prose-kpi-intake/`; plan:
`docs/loom/plans/2026-07-19-8k-prose-kpi-intake-part-1.md`.

### Added

- **Prose text surface** (`data-markets` / `exhibit_prose.py`, NEW):
  `prose_surface(html)` flattens raw EX-99 HTML into the single canonical
  non-table prose text (stdlib `html.parser`, nesting-depth table exclusion with
  a block-break at the table boundary so flanking prose can't merge);
  `locate_numbers(text)` returns plain numeric tokens `{token,start,end}` with
  the exact-substring anchor invariant `text[start:end]==token` by construction;
  a `--locate` CLI emits the located numbers as JSON.
- **Prose KPI candidate producer** (`analysis-kpi` / `kpi_prose_candidates.py`,
  NEW): `propose` → RAW candidates (mechanical value/quote/offset, null semantic
  slots, `needs_semantic`) crossing to `exhibit_prose` by SUBPROCESS (mirrors
  `kpi_8k_candidates` ↔ `exhibit_tables`); `passes_substring_gate` (anti-
  fabrication — verifies the verbatim token/quote, never the normalized value,
  fail-closed on empty/None); `commit` (human confirm-all gate, fail-closed);
  `commit_to_store` (appends a `source_kind="prose"` point with a
  `prose:{start}-{end}` anchor + verbatim_quote + filing attribution via the
  UNMODIFIED `kpi_store.append`); `intake` (honest gaps — explicit empty-success
  vs a loud ≥2-exhibit `multi_exhibit` gap).

### Unchanged (red line)

- `kpi_store.py` / `kpi_validate.py` are BYTE-UNCHANGED; prose points ride the
  existing provenance/as_of guards un-weakened (truthy-token discipline, mirroring
  Route B's `table:0`). The existing quarterly memo feed reads
  `build_quarterly_series`, not the store, so prose points do not surface in the
  memo under Slice A (pinned by a regression test).

## [v2.27.0] — 2026-07-19

Taiwan iXBRL financial-statement ingestion — TW equity memos now source
their canonical three statements + DCF fields + curated notes from the real
inline-XBRL filing (MOPS `t164sb01`, a gate-free Big5 GET), replacing the
deferred yfinance-only canonical stub, and degrade back to the yfinance stub
when a filing isn't available. Plan:
`docs/loom/plans/2026-07-19-tw-ixbrl-ingestion.md`.

### Added

- **TW iXBRL fetch/parse pipeline** (`data-markets`): `twse_ixbrl_fetch.py`
  (t164sb01 fetch — Big5 decode, season fallback for 興櫃 semiannual cadence,
  502 retry; one URL covers 上市/上櫃/興櫃/KY), `twse_ixbrl_parser.py` (generic
  fact extraction via regex/iterparse over `ix:` tags — NOT DOM, which silently
  drops ~85% of nested facts; `scale`-attribute-driven scaling),
  `twse_ixbrl_canonical.py` (canonical three-statement mapping for industrial
  `-ci` filers, incl. the DCF-required `total_debt`/`cash`/`ebit`/`capex`/`fcf`
  fields verified against 2330 + 1301 fixtures; financial `-fh` → unsupported
  marker), `twse_ixbrl_notes.py` (4 curated note categories: financial-instruments
  by measurement category, Mainland-China investment + MOEA ceiling, related-party
  balances + flows, employee-benefit expense), and `twse_ixbrl.py` (the
  `run_client`-invokable CLI assembling the pipeline into JSON).

### Changed

- **`pack_tw.py` memo-fetch** now sources the TW canonical from the iXBRL client
  (provenance-wrapped Tier-A `twse_ixbrl` group), filling the previously-deferred
  `_build_canonical_from_yf_financials_tw` stub; on iXBRL fetch failure it degrades
  to the retained yfinance stub rather than an empty canonical (no regression).

### Notes

- Scope is statements + generic fact layer + curated note fields, NOT a full
  note-table reconstruction engine — annual-filing verification showed TW iXBRL's
  forensic notes (inventory write-downs, tax bridge, aging buckets, PP&E
  rollforward) are absent at any period; value concentrates in the ~4 curated
  concept families. Endorsement/guarantee, parent-only (個體) statements, and
  `-fh` canonical are deferred (see plan Decision Log).

## [v2.26.0] — 2026-07-19

Route B 8-K earnings-release semi-auto KPI intake lane — a mechanical
producer + LLM-semantic + human-confirm three-layer path that turns an
earnings 8-K press-release exhibit into confirmed operational-KPI points
in the EXISTING tier-① store, without the value or its coordinates ever
passing through an LLM. Plan:
`docs/loom/plans/2026-07-19-8k-earnings-kpi-intake.md`.

### Added

- **Exhibit acquisition via attachments** (`data-markets` /
  `sec_edgar_client.py`): `fetch_exhibit_documents(ticker, accession=None)`
  resolves the latest earnings 8-K (Item 2.02) — or the given accession —
  and enumerates ALL EX-99.* attachments off `filing.attachments`,
  returning each document's RAW HTML (`attachment.content`) plus metadata
  (accession / document / exhibit_type / filingDate). This sidesteps
  `_segment_8k`'s ≥2-exhibit-item LOOM-SIMPLIFY ceiling (attachments
  enumerate every EX-99.x directly). Each document is cached under the NEW
  key family `exhibit_raw_{accession}_{document}` — never the legacy
  `narrative_sections_{accession}` slot (incompatible payload shapes share
  the immutable TTL; the distinct prefix makes the two caches un-aliasable
  so a pre-warmed machine can't get a schema-passing HIT of the wrong
  shape). A failed resolution/acquisition is a loud `{"error": ...}` slot,
  surfaced not cached.
- **Generic HTML table walker** (`data-markets` / `exhibit_tables.py`):
  stdlib `html.parser` extractor — raw exhibit HTML → JSON list of tables,
  each cell `{table_index, row, col, text}` after rowspan/colspan
  resolution + empty-separator-cell cleanup, plus a per-row leading-label
  path. No pandas/lxml (coordinate fidelity across the Workiva
  colspan/duplicate-cell artifact needs a custom walker). MECHANICAL only:
  values are the exact printed strings (nbsp/whitespace normalized, never
  parsed to float). CLI: `exhibit_tables.py --html <path> --out <json>`.
- **8-K candidate three-layer intake** (`analysis-kpi` /
  `kpi_8k_candidates.py`): `propose` subprocesses the table walker and
  emits RAW candidate points (verbatim label path + exact-printed value +
  `period_hint` + source coordinates + `confirmed: false`), leaving
  `kpi_id`/`unit`/`period` explicit `null` with a `needs_semantic` list —
  the mechanical layer NEVER invents a slug, a unit, or a normalized
  period. The LLM layer (analysis-kpi SKILL.md prose workflow) proposes
  those semantic slots by reading the verbatim labels; the human
  confirm-all gate ratifies and flips `confirmed: true`. `commit
  --company <T>` then appends ONLY confirmed-and-complete candidates into
  the tier-① store via the EXISTING `kpi_store.append` — unconfirmed
  entries are skipped, and a null semantic slot or missing provenance is
  refused loud (the store's own confirm-all trust gate is un-weakened).

## [v2.25.0] — 2026-07-19

JNJ restatement-axis fix — vintage-axis exclusion accounting and
per-signature refusal granularity join the dimensional-revenue producer
and the quarterly-KPI consumer chain. Plan:
`docs/loom/plans/2026-07-19-jnj-restatement-axis-signature.md`.

### Added

- **Vintage/unknown-axis exclusion accounting** (`data-markets` /
  `sec_edgar_client.py`): `_dimension_signature` now excludes, rather than
  silently collapsing, any fact carrying a `dim_` axis that is neither a
  whitelisted breakdown axis nor the ConsolidationItems qualifier —
  `srt:RestatementAxis` (any member, namespace-agnostic, via
  `_VINTAGE_AXIS_LOCAL_NAME`) is the named `"vintage"` exclusion category,
  every other disallowed axis is `"unknown"` (fail-closed). Each exclusion
  is counted in the pack's `coverage.axis_exclusions` channel
  (`{category, axis, member, concept, accession, period_end}`) via
  `_dimensional_axis_exclusions`; the 3-key signature shape
  (`concept`/`dimensions`/`consolidation`) is unchanged.
  `srt:ConsolidatedEntitiesAxis` — a sibling-axis spelling of the
  consolidation qualifier live-observed on INTC's 2021-2023 filings
  (member `OperatingSegmentsMember`) — is recognized as a second
  consolidation-qualifier axis (`_CONSOLIDATION_AXIS_LOCAL_NAMES`), folded
  into the same `consolidation` slot; a fact carrying both qualifier axes
  with DIFFERING members is excluded under the self-describing
  `"consolidation_conflict"` category.
- **`period_recast` coverage flag** (`analysis-kpi` / `kpi_xbrl.py`):
  `build_quarterly_series` aggregates the pack's `"vintage"`-category
  `axis_exclusions` — read from BOTH the quarterly and annual coverage
  arms — into at most one pack-wide `period_recast` coverage_flag,
  carrying the affected accession(s) and the raw exclusion entries
  verbatim under `exclusions`. Unknown-category exclusions stay
  pack-level accounting only; zero vintage exclusions emit no flag.
- **`signature_refused` per-signature refusal** (`analysis-kpi` /
  `kpi_xbrl.py`): a genuine intra-filing ambiguity
  (`_IntraFilingAmbiguityError`, raised by `resolve_binding`'s per-group
  call) is now caught per signature group instead of aborting the whole
  build — the poisoned group is skipped, a `signature_refused`
  coverage_flag records its accession(s), verbatim exception reason, and
  offending signature, and every other signature group's series still
  emits. Any other exception type still propagates.

## [v2.24.0] — 2026-07-18

Week-based duration lane — 52/53-week fiscal calendars (COST-class filers)
join the month lane across the quarterly-KPI chain, producer primitive
through the memo feed. Plan:
`docs/loom/plans/2026-07-18-52-53-week-filer-support.md`.

### Added

- **Shared week-band primitive** (`data-markets` / `sec_edgar_client.py`):
  a positive-allowlist day-span → week-count/week-lane-band mapping
  (`_WEEK_BANDS`), colocated with the existing month-lane primitive; every
  dimensional-revenue fact now emits `duration_weeks` alongside
  `duration_months`, plus a producer-decided `week_lane_band` — the
  producer classifies once, the consumer transcribes (no second band
  table).
- **Week-aware Gate P boundaries**: `_derive_fiscal_label`'s sub-annual
  path gains week-offset quarter boundaries computed per filer from
  `_WEEK_QUARTER_STRUCTURES`, matched within a tight
  `_WEEK_BOUNDARY_TOLERANCE_DAYS = 2` — the month lane's own ±10d
  tolerance is unchanged.
- **Week-lane Gate C classes** (`analysis-kpi` / `kpi_xbrl.py`):
  `classify_fact_period` transcribes each fact's `week_lane_band` into a
  `duration_class` string (e.g. `16wk`/`17wk`, `36wk-YTD`, `52wk-FY`/
  `53wk-FY`); facts with neither a month- nor week-lane match still
  raise (fail-closed unchanged).
- **Week-lane Q4 derivation**: `derive_q4_points` mints a derived Q4 from
  a week-lane FY point minus its `36wk-YTD` sibling, with
  `duration_weeks = FY_weeks − YTD_weeks` (16 or 17); a group carrying
  BOTH a month-lane 9mo-YTD candidate AND a week-lane `36wk-YTD`
  candidate refuses as `q4_basis_ambiguous` rather than guessing a
  basis; a missing YTD anchor still yields the existing
  `q4_source_missing` refusal.
- **Feed carries week counts + supplementary normalized YoY**: the 1.1
  quarterly feed passes through each point's `duration_weeks`, and a
  point whose same-signature prior-year comparator carries a DIFFERENT
  week count gets a supplementary `week_normalized_yoy` field
  ((value/weeks) vs. (prior value/prior weeks) − 1), skipped on any
  zero-denominator side; the as-reported value/YoY stay primary and
  `MEMO_FEED_QUARTERLY_SCHEMA_VERSION` stays "1.1" (additive fields,
  passthrough — no envelope bump).

## [v2.23.0] — 2026-07-18

Memo quarterly-KPI wiring — the honest fiscal-calendar quarterly chain shipped
in v2.22.0 now reaches the rendered memo. A new `kpi-quarterly` data pack, a
`quarterly-series` CLI, and a quarterly/XBRL memo-feed arm (schema 1.1) join
the fact-pack → series → memo-feed chain end-to-end, and `report-equity-memo`
gains a Phase 3.5 step that runs the chain for US tickers and hands the feed
to `investing-team`'s Operating-KPI block. Plan:
`docs/loom/plans/2026-07-18-memo-quarterly-kpi-wiring.md`.

### Added

- **`data-markets` `kpi-quarterly` pack** (US-only): calls
  `extract_dimensional_revenue` and emits the dimensional-revenue fact-pack
  JSON (facts[] + per-accession fiscal_calendars + `_status` envelope); a
  non-US ticker returns `_status.status == "usage_error"` (no silent skip).
- **`analysis-kpi` `quarterly-series` CLI** on `kpi_xbrl.py`: takes a
  fact-pack JSON path, classifies + builds a break-aware series per
  full-dimensional-signature group (`granularity="quarterly"`), derives Q4
  points, and emits one series JSON with parallel calendar/fiscal labels
  intact on every point.
- **`analysis-kpi` memo-feed quarterly/XBRL arm** (`kpi_memo_feed.py`,
  envelope `_memo_feed_schema_version` 1.0 → 1.1): `build_quarterly_memo_feed`
  + CLI subcommand `build-quarterly`. Fail-closed on per-point XBRL
  provenance completeness (reported points: `source_accession` + `concept`;
  derived points: `derived: True` + non-empty plural `source_accessions`/
  `source_forms`) and `assert_dqc_schema` on every coverage flag; this lane
  does not call the tier-① store gate (`kpi_gate.is_trusted`) — its trust is
  machine-verified provenance, not a store confirmation.
- **`report-equity-memo` Phase 3.5**: for a US ticker, runs
  kpi-quarterly pack → `quarterly-series` → `build-quarterly` and adds the
  resulting memo-feed JSON as an OPTIONAL `### Resource Paths` entry;
  non-US tickers get an explicit skip note in the seed (never silent).
- **Offline end-to-end chain test**: fact-pack fixture → `quarterly-series` →
  `build-quarterly`, asserting derived points keep plural accessions and the
  calendar/fiscal pair, `coverage_flags` survive verbatim, and a poisoned
  payload (derived point stripped of `source_accessions`) exits 1.

## [v2.22.0] — 2026-07-18

Quarterly (10-Q) operational-KPI support, rebuilt on an honest fiscal-calendar
foundation. The root defect — a primitive returning the CALENDAR year under a
"fiscal year" docstring, which mislabeled every non-December-FYE filer's
quarters — is replaced end-to-end: every dimensional fact now carries BOTH a
calendar label and a fiscal label in parallel (mirroring Compustat
DATADATE/DATACQTR/DATAFQTR), never one collapsed into the other. Spec:
`docs/loom/2026-07-16-operational-kpi-quarterly/specs/operational-kpi-quarterly/spec.md`;
plan: `docs/loom/plans/2026-07-16-operational-kpi-quarterly.md`; decision record:
`docs/loom/2026-07-16-operational-kpi-quarterly/rebuild-findings.md`.

### Added

- **Parallel period labels per fact** (`data-markets` / `sec_edgar_client.py`):
  `calendar_year`/`calendar_quarter` (calendar quarter containing period_end) +
  `fiscal_year`/`fiscal_quarter` (per-fact, own period_end vs that filing's dei
  calendar; comparatives from their OWN period, never the filing focus stamped;
  fail-loud on an unreadable calendar — never a calendar fallback) +
  `derivation_basis` (dei-declared | projected).
- **Declared-fiscal-year selection**: a 10-Q range request selects filings by
  their DECLARED fiscal year (index-window guess pre-fetch, reconciled against
  `dei:DocumentFiscalYearFocus` post-fetch — out-of-range declarations excluded
  and surfaced, unreadable declarations flagged, never calendar-bucketed).
- **Coverage honesty rebuilt**: comparison universe = the full filings index;
  absence states not_yet_filed / out_of_requested_range / unclassified +
  observed states attempted-fetch-failed / filed-but-unlabelable (one bad
  filing quarantines, never aborts the run) + index-visible-but-not-selected
  selection gaps. All flags on ONE DQC schema (type/old/new/accessions/reason).
- **Quarterly analysis chain** (`analysis-kpi` / `kpi_xbrl.py`): period
  classification consumes the emitted labels (analysis never re-derives fiscal
  years); series key on the FISCAL basis; duration-qualified identity key
  de-conflates 3mo single-quarter from YTD cumulatives; derived Q4 =
  FY − 9mo-YTD (guarded, segregated `derived: True` lane, dual-accession
  provenance, three label groups); single-granularity series with fiscal-range
  output filtering; structured point provenance (accession + source form +
  duration_class).
- **Live shape-anchor** (network-marked) pinning dual-duration facts + all
  three dei cover tags against real SEC EDGAR.

### Changed

- `_filing_period_year` (calendar-as-fiscal lie) removed; call sites route
  through honest primitives (`_filing_period_end_calendar_year`,
  `_quarterly_fiscal_year_guesses`, `_derive_fiscal_label`).
- Revenue-concept gate: deny list names the real
  `RevenueFromCollaborativeArrangement*` family + REIT pro-forma/ladder class;
  synthetic $-unit backstop regression added.

## [v2.6.0] — 2026-07-12

US SEC primary-source narrative layer — the memo pipeline can now read what
management actually wrote, not just XBRL numbers. Segmentation is pure data
acquisition: every item the filing's primary document enumerates is emitted,
never a curated analysis-selected subset (the downstream consumer decides what
to read). Ships the narrative capability of the US SEC primary-source spec
(`docs/loom/2026-07-12-us-sec-primary-source-layer/specs/narrative/spec.md`);
plans: `docs/loom/plans/2026-07-12-us-sec-narrative.md` +
`docs/loom/plans/2026-07-12-us-sec-narrative-all-items.md`.

### Added

- **`data-markets` / `sec_edgar_client.py` narrative via edgartools**: a 10-K
  or 10-Q is segmented into one section per item in the filing's item list
  (a real AAPL 10-K yields all 23 items — Business, Risk Factors, MD&A,
  Financial Statements + notes, Controls, Governance…); an 8-K is segmented by
  every reported item, with exhibit-bearing items (2.02 / 7.01 / 8.01) followed
  to their **Exhibit 99.x** (where an 8-K's substance lives) and tagged
  `disclosure_status: furnished` — other reported items carry their body text,
  tagged `filed`. No non-99.x attachment is fetched.
- **Section provenance**: every section carries accession, CIK, item id, filing
  date, period of report, and a reconstructable SEC Archives URL pointing at
  *that section's own* source document (an 8-K section's URL points at the
  exhibit, not the body).
- **Paths-not-content**: section text is written to files under the toolkit
  cache and returned as `text_path`, never inlined into the JSON result. Both
  path segments are allowlist-sanitized and the write is containment-checked.
- **Per-section fail-loud** feeding `pack.py`'s `_status`: five distinct error
  classes (`absent_item`, `missing_exhibit`, `extraction_error`, `timeout`
  (retryable), `version_drift`) — a section is never silently empty or
  fabricated. The result wrapper carries `narrative_status` (ok / partial /
  failed) + `failed_items` so the failure state is visible without unwrapping
  `sections`.
- **SEC fair-access**: a non-compliant `<name> <email>` identity is rejected
  *before* any request is sent (edgartools does not fail fast); its built-in
  jittered backoff is preserved; filings are cached per accession under a
  dedicated key.

### Changed

- **`--action narrative` internals**: the legacy regex parser
  (`parse_item_sections` / `_ITEM_HEADER_RE` / `_TextExtractor` / the old
  `fetch_narrative`) is **retired**; segmentation now runs through edgartools'
  typed section API. The CLI contract (action name, `--accession`, result keys,
  exit-1-iff-error) is unchanged.

## [v2.5.0] — 2026-07-12

Verdict-layer defenses — hardening the memo pipeline against weak-model
failure at the judgment layer (a controlled strong-vs-weak comparison on
identical 2330.TW data surfaced rule-deviation, false data-unavailability
claims, dropped disclosures, and UTC date leakage after #539's artifact
gates already closed fake-completion). Plan:
`docs/loom/plans/2026-07-12-verdict-layer-defenses.md`. Pairs with
domain-teams v5.7.0 (the gate-side enforcement).

### Added

- **`analysis-dcf` `rule_verdict`**: `verdict_thresholds` now carries a
  deterministic `rule_verdict` (SELL / HOLD / BUY-string / null when no
  price) + `rule_verdict_basis` (price + thresholds compared) — the
  mechanical verdict-rule application moves into code so the memo LLM
  adopts it or files a gated Deviation Block rather than re-deriving it.
- **`report-equity-memo/scripts/pack_inventory.py`**: pure-stdlib CLI
  turning a data pack into a machine-readable section inventory
  (present/kind/rows|keys + `_status` echo), so a memo's "data unavailable"
  claims are checkable against ground truth.
- **`report-equity-memo/references/phase4-seed-contract.md`**: the four
  verdict-layer defense elements the Phase 4 packet must carry
  (`rule_verdict` binding-or-gated, pack inventory, issuer-timezone date
  anchoring, verbatim-disclosure pass bar) + the orchestrator's acceptance
  greps; SKILL.md Phase 4 gains a pointer (step 2b).

## [v2.4.1] — 2026-07-12

### Added

- **Vault filename & folder convention** (`vault-frontmatter.md` new section,
  referenced from Phase 5b): all-English `YYYY-MM-DD {identifier} Equity Memo.md`
  under `investing/memos/`; equity identifier = Yahoo/RIC ticker as-is (dot
  suffix included, e.g. `2330.TW`); future non-equity descriptors (`FX Memo`,
  `Commodity Memo`) use clean identifiers (ISO 4217 `USDTWD`, `XAUUSD`, house
  energy codes, caret-stripped indices) — raw vendor sigils (`=X`/`=F`/`^`) are
  Obsidian-link-hostile and stay in frontmatter, never filenames. Same-day
  re-analysis updates the existing note. (RESOLVED 2026-07-12 with the user;
  grounded in an Obsidian-constraints + multi-asset-symbology survey.)

## [v2.4.0] — 2026-07-11

Investing analysis memory layer (Obsidian-carried), pilot on
`report-equity-memo`. Brief: `docs/loom/specs/2026-07-11-investing-obsidian-memory-layer.md`.

### Added

- **`skills/report-equity-memo/references/vault-frontmatter.md`** — toolkit-owned
  frontmatter schema SSOT (8 fields: type/ticker/market/date/verdict/confidence/
  price_at_analysis/intrinsic_mid), Obsidian Bases date-typing note, sample
  track-record `.base` snippet.
- **Phase 0 — Recall Prior Verdicts**: before any data fetch, grep prior memos'
  frontmatter for the same ticker; surface last verdict/date/price + delta;
  three-way disclosure (hit / no-hits / no-vault) in the memo's Limitations.
- **Phase 4 always-on frontmatter**: the memo file begins with the schema block
  regardless of destination; artifact gate additionally verifies `head -1` is `---`.

### Changed

- **Phase 5b field ownership**: `obsidian:obsidian-markdown` must respect the
  toolkit frontmatter fields (placement/wikilinks/vault conventions only; never
  re-invent or overwrite); default vault folder `investing/memos/`
  (default-unless-user-says-otherwise).

## [v2.3.1] — 2026-07-11

Dogfood fix package (PR #539) — version bump so the fixes deploy via
`plugin update`; full findings in `docs/skill-dogfood/2026-07-11-data-markets/report.md`.

### Fixed

- **`analysis-dcf`** — per-share intrinsic value was exactly 1,000,000×
  too large on every market (script assumed $M inputs; all data-markets
  packs emit absolute currency). Fixtures reshaped to real producer shape.
- **`analysis-comps`** — multi-ticker batch peer packs now expand to N
  peer entries; unresolvable tickers fail loud via `_provenance.warnings`
  instead of silent all-null.
- **`data-markets`** — TWSE cache hits re-attach the declared
  `_cache_age_seconds`/`_cache_ttl_seconds` pair; description gains
  data-layer vocabulary, source names, and a regime-routing clause;
  cache-metadata docs clarify per-section injection.
- **`analysis-screener` / `analysis-macro-regime`** — stale
  `data-{country}` paths replaced; regime description now leads with the
  classification job.
- **`report-equity-memo`** — every phase requires an ls-verified on-disk
  artifact before it counts as complete (anti fake-completion gates;
  Phase 4 gains a defined artifact).

## [v2.3.0] — 2026-07-11

`data-markets` consolidation: 5 per-country data skills merged into one,
a live-reproduced silent-cache-crash bug closed, and a fail-loud exit
contract added to the data layer. See
[ADR-0009](docs/adr/0009-data-markets-consolidation-and-cache-util.md)
for the full design record.

### Added

- **`skills/data-markets/`** — replaces `skills/data-{us,jp,tw,kr,cn}/`.
  Thin `SKILL.md` (routing + shared contract + worked examples) +
  `references/market-{us,jp,tw,kr,cn}.md` (per-market sources, tiers,
  key requirements, caveats). 18 unique clients (deduplicated from 23:
  yfinance ×5 → 1, fred ×2 → 1) + one per-market `pack_{market}.py`
  module each, behind a single `pack.py` facade with ticker-suffix
  market auto-detection (`--market` required for `regime-pack`).
- **`skills/data-markets/scripts/cache_util.py`** — single cache module
  for all clients: XDG/uv-style path precedence (explicit arg >
  `INVESTING_TOOLKIT_CACHE` > `$XDG_CACHE_HOME/investing-toolkit` >
  `~/.cache/investing-toolkit`), empty-string-safe env parsing,
  post-resolution writability check with loud stderr warning + tempdir
  fallback, cadence-aware `compute_ttl()` (generalizes `dgbas_client.py`'s
  `_compute_ttl` to all 18 clients), schema-versioned roundtrip helpers.
- **Fail-loud `pack.py` exit contract**: `0` = all sections ok, `2` =
  partial (was silently exit `0` in 4 of 5 old `pack.py`s), `1` = all
  failed / unexpected exception, `64` = usage error (bad args/pack name,
  mixed-market ticker list, missing `--market` for `regime-pack`). A
  top-level `_status` block (`status`, `market`, `pack`,
  `failed_sections`, `warnings`) is injected into every response.
- `agents/data-fetcher.md` rewritten against the merged skill (`pack.py`
  invocations, exit-contract table, `cache_util` cache section) —
  replaces v1.x content referencing pre-v2.0.0 per-client scripts and
  flat `1h`/`6h`/`24h` TTLs.

### Fixed

- **Silent cache-directory crash (live-reproduced)**: the old canonical
  invocation set `INVESTING_TOOLKIT_CACHE` from a hook-only variable that
  is empty inside a Bash tool call, collapsing to the literal path
  `/cache`. Every client's unguarded cache-dir `mkdir()` then crashed,
  and 4 of 5 `pack.py` implementations swallowed the crash into an error
  slot while still exiting `0` — reports silently received `None` prices
  with no failure signal. `cache_util.resolve_cache_dir()` now strips +
  empty-checks the override, probes writability, and falls back loudly
  instead of crashing.

### Changed — BREAKING

- **`data-{us,jp,tw,kr,cn}` skill names removed.** All invocations
  (slash commands, agent dispatch, downstream `SKILL.md` references)
  migrate to `data-markets` — see `agents/data-fetcher.md` and
  `skills/data-markets/SKILL.md` for the new invocation form.
- **`INVESTING_TOOLKIT_CACHE` is now fully optional.** Previously
  required by the (silently broken) canonical invocation; omit it
  entirely for the default `~/.cache/investing-toolkit` path, or set it
  deliberately to override.
- **`sync-clients.sh` and its MD5-sync CI discipline removed** — a
  single-copy skill has no cross-copy drift to guard against.

### Removed

- `skills/data-{us,jp,tw,kr,cn}/` (5 skills, ~4-5k net LOC reduction
  including 4 duplicate `yfinance_client.py` copies + 1 duplicate
  `fred_client.py` + ~1,077 LOC of per-client cache boilerplate
  collapsing into one `cache_util.py`).
- `scripts/sync-clients.sh`, `tests/test_sync_clients.py`.

## [v2.1.1] — 2026-07-05

### Fixed — `report-equity-memo` Codex dispatch-portability

Phase 2.5's peer-discovery step named `general-purpose` (a real
Claude-Code built-in agent-type name) directly in `SKILL.md`, with no
literal `Agent(...)` syntax but also no per-host reference file (Codex
dispatch-portability survey finding, `docs/skill-mining/2026-07-05-
codex-dispatch-portability-survey.md` — classed borderline (A)/(B)).
Reworded to "dispatch a general-reasoning subagent" and added
`references/{claude-code-tools.md,codex-tools.md}` mapping
`general-purpose` onto Codex's `default`/`worker`/`explorer` built-ins.

### Fixed — description self-contradiction

Caught by whole-branch review: `plugin.json` + `.codex-plugin/plugin.json`
+ the root marketplace entry all said "Claude Code CLI only" while
shipping a full Codex manifest — same class of bug already fixed for
`briefing-toolkit` on this branch. Dropped the false host-restriction
claim from all three copies.

### Fixed — awkward dispatch sentence (behavioral dogfood follow-up)

A blind cold-reader flagged the peer-discovery dispatch sentence as
splitting subject from verb with a 30-word parenthetical, and naming
only Claude Code's agent-type inline. Restructured into two sentences
naming both hosts' agent-type symmetrically (`general-purpose` /
`default`).

## [v2.1.0] — 2026-05-02

`analysis-macro-regime` Phase 1 per-country classifier refactor. Decomposed the v1.9.0 unified IC + Hedgeye GIP classifier into 5 native per-country modules (`classify_us / jp / tw / kr / cn`). See [ADR-0004](docs/adr/0004-analysis-macro-regime-phase1-per-country-classifiers.md) for design rationale + Phase 2 deferral.

### Added

- **5 per-country classifier modules** (`classify_{us,jp,tw,kr,cn}.py`) — each implements its country's native framework rather than re-labeling legacy IC:
  - **US**: IC + Hedgeye GIP + Fed FIT (post-FAIT 2025) + 4-tier real-rate decomposition (HLW / LM / SEP / NY Fed composite) + yield-curve overlay.
  - **JP**: BOJ stance + Tankan business sentiment DI (大企業/中小企業 × 製造/非製造) + ESRI 景気動向指数 CI + deflation/inflation regime detection + ECB ex-post real-yield 4-tier band.
  - **TW**: NDC 五色景氣燈號 score-led (9-45 composite) + 9 構成項目 dispersion (per 2024 revision) + TIER 製造業營業氣候測驗點 + TSMC TAIEX concentration overlay.
  - **KR**: BOK 단일 2% target alignment + KOSTAT 동행지수순환변동치 cycle phase + 가계부채 GDP overlay + KOSPI 삼성+SK 하이닉스 ~40.96% concentration overlay.
  - **CN**: PBOC reaction (7天逆回购 1.40% post-2024-07) + credit impulse (CICC TSF flow-yoy 2nd-derivative) + 4-component dispersion alarm + 房地产 GDP-share overlay (3 definitions disclosed) + CPI framing enum (`supportive_recovery_below_target` captures PBOC's "wants inflation up" stance).
- **5 calibration YAMLs** (`scripts/calibrations/{us,jp,tw,kr,cn}.yaml`) — machine-readable extracts of `references/thresholds-{country}.md` (2026-Q1/Q2 vintages). All numeric thresholds plumbed into classifier code instead of sitting as un-executed documentation.
- **5 grounding research notes** (`research/grounding-{country}-2026-05.md`) — partial-recalibration delta refreshes per `recalibration-protocol.md` template. JP captured 4 material BOJ events 2026-04-19 → 2026-05-02 (FY2026 核 CPI 1.9%→2.7-2.8% upward revision, 6-3 vote, Ueda 4/30 anchor).
- **Output schema `2.0-phase1`** with `by_country.{cc}` envelope (country / framework_used / native_verdict / indicators_used / data_quality / confidence / provenance). `cross_country` hardcoded `null` (deferred to Phase 2).
- **Per-country fetch additions**:
  - JP: `boj_client.py --tankan-business-di` (4 series codes verified vs BOJ official docs); `pack.py` wires Tankan + ESRI coincident-index / leading-index / 機械受注 e-Stat presets.
  - CN: `pack.py:_compute_credit_impulse()` (CICC TSF flow → trailing-12m-sum YoY → 12-month change); methodology doc at `references/credit-impulse-methodology.md`.

### Changed

- **Output schema migration** for direct `regime_compose.py` consumers: read `out["by_country"][cc]` instead of `out["countries"][cc]`. `out["cross_country"]` is `null` in Phase 1.
- **Per-country threshold reference docs** (`references/thresholds-{country}.md`) — partial-recalibration refresh from v1.11.0 (2026-04-19) to 2026-05-02. JP captures 4 material BOJ policy events.

### Removed

- `_legacy_ic.py` — the v1.9.0 unified `classify_country()` IC + GIP fallback path. Helpers migrated to `_helpers.py`; per-country classifiers import from there.
- `out["countries"]` and `out["cross_country_consensus"]` schema fields (replaced by `out["by_country"]`; consensus deferred to Phase 2).

### Deferred (per fresh-eyes audit + ADR-0004)

- **Cross-country comparable surface** (Phase 2 / ADR-0005). Re-trigger: Phase 1 stable ≥4 weeks, ≥5 multi-country invocations, or memo workflow surfacing concrete need. If none fire within 6 months, evaluate whether comparable surface is needed at all.
- **KR ESI explicit ECOS API integration** — current code uses fdr_client KEYSTAT 'sentiment' group as best-effort fallback; explicit ECOS key-based integration deferred to v2.2.0.
- **TW TIER preset wiring at NDC client level** + live TWSE monthly weight ingestion — deferred to v2.1.x or v2.2.0.
- **CN true stock-yoy credit impulse** — current implementation uses flow-yoy second-derivative with explicit honest methodology label; switch when PBOC publishes stock series via akshare or direct scrape.

## [v2.0.0] — 2026-05-01

Three-Layer Skill Architecture (Data / Analysis / Report). See [ADR-0001](docs/adr/0001-data-analysis-report-layers.md) for the architectural decision and [migration guide](docs/migration-v2.0.0.md) for v1.x → v2.0.0 upgrade instructions.

### Breaking changes

- Plugin version bumped 1.16.5 → 2.0.0 (skill-API breaking changes — see Removed below).
- All 14 v1.x skill **directories** deleted and replaced by 16 new skills under three layers (5 `data-{country}` + 6 `analysis-*` + 4 `report-*` + 1 router).
- Removed `investing-toolkit/scripts/sync-scripts.sh`, `investing-toolkit/scripts/sync-check.sh`, and `investing-toolkit/tests/test_skill_md_sync.py` — the v1.16.1 dual-mode sync mechanism is retired.
- Slash-command **internal routing** now points at the new skills (full mapping in [ADR-0001 §Slash-Command Rename Map](docs/adr/0001-data-analysis-report-layers.md)). User-facing slash command names (`/invest-memo`, `/invest-screen`, `/invest-portfolio`, `/invest-macro`) are preserved.

### Added

- **5 new `data-{country}` skills** (US / JP / TW / KR / CN) — Layer 1 country-bundled fetch with 5 pack types each (`equity` / `regime` / `industry` / `screener-input` / `portfolio-input`).
- **6 new `analysis-*` skills** (Layer 2, pure compute, no I/O):
  - `analysis-dcf` — Damodaran 3-stage DCF (rename of v1.x `dcf-valuation`).
  - `analysis-comps` — peer multiples comparison (5 multiples: P/E trailing + forward, EV/EBITDA, P/S, P/B); statistics + anchor delta + composite ranking. **NEW.**
  - `analysis-screener` — multi-criteria screener engine (rename of v1.x `stock-screener` compute path).
  - `analysis-technical` — RSI / MACD / Bollinger / ATR / SMA (rename of v1.x `technical-snapshot`).
  - `analysis-portfolio` — holdings P&L + regime overlay (rename of v1.x `invest-portfolio`).
  - `analysis-macro-regime` — IC + GIP regime classification across US/JP/TW/KR/CN (rename of v1.x `macro-regime-snapshot`).
- **4 new `report-*` skills** (Layer 3, orchestrators):
  - `report-equity-memo` — full equity memo pipeline (rename of v1.x `investment-memo-writer`).
  - `report-stock-snapshot` — country-aware stock snapshot (consolidates v1.x `us-stock-snapshot` / `japan-stock-snapshot` / `taiwan-stock-snapshot`).
  - `report-portfolio-review` — portfolio review report (orchestrator above `analysis-portfolio`).
  - `report-screener-list` — screener list report. **NEW.**
- **`analysis-comps`** as a first-class skill: peer multiples (P/E trailing + forward, EV/EBITDA, P/S, P/B) with median / mean / IQR statistics, anchor delta vs peer median, and composite ranking.
- **`report-equity-memo` Phase 2.5**: runtime `research-agent` peer-discovery for the Comps section (`--auto` / `--interactive` modes).
- **ADR-0001**: Three-Layer Skill Architecture decision record at `investing-toolkit/docs/adr/0001-data-analysis-report-layers.md`.
- **Migration guide**: user-facing v1.x → v2.0.0 upgrade guide at `investing-toolkit/docs/migration-v2.0.0.md`.
- **CI sync workflow**: `.github/workflows/check-script-sync.yml` enforces MD5 equality between canonical clients (`investing-toolkit/scripts/`) and `data-{country}/scripts/` copies. Advisory in v2.0.0; will become required in v2.0.1+.
- **New helper**: `investing-toolkit/scripts/sync-clients.sh` (canonical → copies sync; `--check` mode for CI).
- **New slash command**: `/invest-snapshot` → routes to `report-stock-snapshot`.
- **Test suite**: 296 non-network + 27 network automated pytest tests covering data packs, analysis compute, and report orchestration.

### Changed

- **Architecture** — three-layer separation (Data / Analysis / Report). Layer 1 is I/O-only, Layer 2 is pure compute, Layer 3 orchestrates. See ADR-0001.
- **Cross-skill data passing** — main agent + temp files (replaces v1.x intra-skill subprocess dispatch). Each layer reads/writes JSON via temp file paths passed by the main agent.
- **`fred_client.py`** — parallel multi-series fetch via `ThreadPoolExecutor` (default 8 workers; configurable via `FRED_MAX_WORKERS` env var); removed custom User-Agent header (FRED bot filter blocked it, causing intermittent fetch failures).
- **Slash commands** — internal routing updated; user-facing names preserved (`/invest-memo`, `/invest-screen`, `/invest-portfolio`, `/invest-macro`). New: `/invest-snapshot`.

### Removed

- 14 v1.x skill directories: `us-macro`, `japan-macro`, `taiwan-macro`, `korea-macro`, `china-macro`, `us-stock-snapshot`, `japan-stock-snapshot`, `taiwan-stock-snapshot`, `technical-snapshot`, `stock-screener`, `dcf-valuation`, `invest-portfolio`, `macro-regime-snapshot`, `investment-memo-writer`.
- `investing-toolkit/scripts/sync-scripts.sh` (replaced by `sync-clients.sh`).
- `investing-toolkit/scripts/sync-check.sh` (replaced by `sync-clients.sh --check`).
- `investing-toolkit/tests/test_skill_md_sync.py` (v1.16.1 dual-mode validation; obsolete in v2.0.0 main-agent + Bash architecture).

### Fixed

- **JP bare 4-digit ticker resolution** (critical): `analysis-portfolio._resolve_price()` now auto-resolves `7203` ↔ `7203.T` mismatches between holdings files and `data-jp` pack output. Pre-fix produced silent missing-price entries; post-fix logs the mapping under `_provenance.ticker_resolutions`.
- **ROC quarter filing-aware logic**: `data-tw/pack.py.latest_roc_quarter()` no longer returns unfiled quarters near the Mar 31 / May 15 / Aug 14 / Nov 14 filing-deadline boundaries.
- **`analysis-dcf`** removed a dangerous unit-normalisation heuristic that mis-scaled BRK.A-style low-share-count stocks by 1e6× (mis-classifying market cap and intrinsic value).
- ~30 Wave 4 quality findings addressed in PR #172 and ~10 in PR #173.

### Pull requests

- **#172** — three-layer refactor (15 → 15 skills; 14 v1.x deleted; 11 + 4 implementer agents across Phase 1 + Phase 2; ADR-0001; 272-test suite baseline).
- **#173** — `analysis-comps` + `report-equity-memo` peer-discovery (15 → 16 skills; 24 new tests; `fred_client` parallel fetch + UA fix).
- **#(this PR)** — documentation polish (CHANGELOG, migration guide, READMEs, design-principles update) and final v2.0.0 plugin-version bump.

### Slash-command routing map (high-level)

User-facing slash commands stay stable. Only the underlying skill they route to changes.

| Slash command | v1.x routes to | v2.0.0 routes to |
|---|---|---|
| `/invest-macro` | `us-macro` / `japan-macro` / `taiwan-macro` / `korea-macro` / `china-macro` | `data-{country}` regime-pack + `analysis-macro-regime` |
| `/invest-memo` | `investment-memo-writer` | `report-equity-memo` |
| `/invest-screen` | `stock-screener` | `report-screener-list` |
| `/invest-portfolio` | `invest-portfolio` | `report-portfolio-review` |
| `/invest-snapshot` *(new)* | (none) | `report-stock-snapshot` |

For the full v1 skill → v2 skill mapping (16 entries including internal renames), see [ADR-0001 §Slash-Command Rename Map](docs/adr/0001-data-analysis-report-layers.md).

[v2.0.0]: https://github.com/kouko/monkey-skills/releases/tag/investing-toolkit-v2.0.0

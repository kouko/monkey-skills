# Plan: company total (top-line) revenue lane

Source brief: docs/loom/specs/2026-07-25-company-total-revenue.md
Total tasks: 11
Critical-path depth: 5 (≤5) — 1→2→5→6→10; levels are {1,7,11} {2,3} {4,5} {6,8,9} {10}
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-25, round 5 — 14/14 applicable checks; checks 12/16 N/A, 5 retired, 15 advisory-no-entry). Rounds 1/3/4 returned NEEDS_REVISION; round 5 additionally adjudicated and CONFIRMED the planner's refusal of round 4's suggested fix.

## Notes

- **Change-folder binding: N/A, stated loudly.** The input is the brainstorming
  brief above (Layer 0 explicit handoff). Two non-archived change-folders exist
  (`docs/loom/2026-07-12-us-sec-primary-source-layer/`,
  `docs/loom/2026-07-19-8k-prose-kpi-intake/`) but both belong to prior shipped
  arcs — neither covers this work, so nothing is bound and
  `check_scenario_coverage.py` does not apply to this plan.
- **Version coordination — RESOLVED 2026-07-25**: PR #612 merged (`fa37de6b`,
  investing-toolkit 2.35.0) before this arc started, so Task 10 targets
  **2.36.0**. The arc branch `feat-total-revenue-lane` was cut at `fa37de6b`
  == `origin/main` (memory `new-arc-branch-bases-on-origin-main-not-merged-tip`).
  If another PR lands a minor bump mid-arc, re-resolve the number and rebase
  onto `origin/main` before whole-branch review (the #610 precedent from arc (d)).
- **Envelope provenance contract (shared literal — declared HERE so Tasks 4 and 5
  need no ordering between them)**: a fact-pack envelope MAY carry a top-level
  `"source_kind"` string that applies to its FLAT facts only. Task 4's
  `kpi-topline-backfill` envelope sets it to the exact literal
  `"xbrl-companyfacts"`; Task 5 makes `ingest_pack` assign provenance per lane —
  dimensional facts keep `"xbrl-dimensional"`, flat facts take the
  envelope-declared kind when present and otherwise `"xbrl-topline"` — and fail
  loud on a kind outside `kpi_gate.TRUSTED_SOURCE_KINDS`. Both tasks read that literal
  from this plan, not from each other's code, so their `Files touched` stay
  disjoint and both remain `Independent: true`. Rationale: without this, every
  Lane A point lands in the append-only store stamped `"xbrl-dimensional"` — a
  factually wrong durable provenance label that nothing fails loud on
  (`kpi_gate.py:95` trusts both kinds).
- **Anti-fixture-fabrication** (memory `hand-authored-fixture-is-a-fabrication-risk`,
  `fixtures-mirror-producer-shape`): every fixture in Tasks 1-6 must be CAPTURED
  from the real extractor / real SEC response shape, never hand-typed. The live
  probe run for the brief is the capture source of record — it currently lives
  only in a session-scoped scratchpad, so **Task 1 copies it into the branch** at
  `investing-toolkit/tests/data/fixtures/topline_probe_2026-07-25.json`; every
  later task reads the in-repo copy, so a fresh SDD session never loses the
  oracle. (8 filers: AAPL/INTC/JPM/SNOW/WMT/NVDA/XOM/COST, 2026-07-25.) Never use a
  December-FYE-only fixture (December is the one FYE where calendar-year logic
  accidentally works, hiding the calendar-vs-fiscal trap).
- **One winner per filing.** Task 2 applies `select_top_line_concept` at the
  FILING level and emits only the winning concept's flat facts. Task 3 applies
  the SAME selector. This is what makes the two lanes agree (Task 6) and keeps
  the ingest side free of concept arbitration.
- **The collision guard must not fire on the top-line lane.** Arc (d)'s
  `claimed_by` guard (`kpi_xbrl_ingest.py:174-184`) raises when two DISTINCT
  signatures derive one `kpi_id`. A filer that switches tagging across years
  (e.g. `Revenues` → `RevenueFromContractWithCustomer...`) legitimately produces
  two flat signatures that MUST land in the one `total_revenue` series. Task 5
  therefore groups the flat lane on a single top-line key rather than
  per-concept signature — and must NOT weaken the guard for the dimensional
  lane. **No EXISTING raise protects the merge** — verified in code, do not
  assume otherwise: `facts_to_points` (`kpi_xbrl.py:490-586`) emits every
  matching fact without comparing values, and `kpi_store.append`
  (`kpi_store.py:317-324`) documents that a same-dedup-key point carrying a
  DIFFERENT value is treated as a no-op with the FIRST record winning;
  `_reduce_window_group`'s >1-distinct-value raise (`kpi_xbrl.py:648`) sits in
  the BINDING pipeline (`:870`), which the ingest path never calls. Task 5
  therefore ADDS the same-period value-disagreement guard inside
  `kpi_xbrl_ingest.py` — that guard is what discharges the brief's Smallest End
  State #3 clause "disagreement is a fabricated `†` and must fail loud, never be
  silently stored". This is not scope creep: `kpi_store.append`'s own docstring
  (`kpi_store.py:323-325`) registers the check as "OUT OF SCOPE for this task
  (a later slice's job if needed)" — this arc is that later slice, and it lands
  the guard at the ingest producer rather than inside the store's read-modify-write.

- **The disagreement guard is keyed on the DEDUP KEY, and must be STORE-AWARE —
  NOT on "a different accession"**. This is the single most dangerous place to
  get the polarity wrong, so it is pinned here with live evidence:
  - **Same period + SAME accession + different value → RAISE.** The two lanes are
    reading the SAME filing, so a disagreement means one of them is wrong. Live
    proof the lanes share an accession: `companyconcept` rows carry
    `accn=0001045810-26-000021 / filed=2026-02-25` — exactly the accession and
    filed date Lane B's per-filing parse of that same 10-K produces. Their dedup
    keys therefore COINCIDE, and `kpi_store.append` would silently keep the first
    (`kpi_store.py:321-325`) — a wrong number stored with no error.
  - **Same period + DIFFERENT accession + different value → APPEND, never raise.**
    That is a LEGITIMATE restatement and is precisely what the store's `†` exists
    to render (arc (d) shipped on INTC's two real CCG recasts). Live proof the
    case is common: NVDA's FY2025 period `2024-01-29..2025-01-26` appears under
    BOTH `0001045810-25-000023` (filed 2025-02-26) and `0001045810-26-000021`
    (filed 2026-02-25) — the prior year re-reported inside the next 10-K.
    A guard that raised on "different accession + different value" would fire on
    every genuine recast and destroy the arc (d) capability.
  - Because Lane A and Lane B arrive in SEPARATE `ingest_pack` calls, an
    intra-pack-only check cannot see the other lane's already-stored point — the
    guard must read the existing series (`kpi_store.query_latest` / `history`,
    READ APIs only; no store read-logic edit, brief §Out of Scope respected).
  - Cross-lane agreement is empirically confirmed, not assumed: Lane A returns
    NVDA `215,938,000,000` and WMT `713,163,000,000` for their latest fiscal
    years — byte-identical to the Lane B probe values in the brief's §Probe
    findings table.

- **Live confirmation of the `fy`/`fp` trap Task 3 must avoid**: in the
  `companyconcept` response every row from NVDA's FY2026 filing is stamped
  `fy=2026, fp=FY` — including the FY2024 comparative ending `2024-01-28` and the
  FY2025 comparative ending `2025-01-26`. Reading `fy` would mislabel two of three
  years. This is memory `fiscal-year-derive-per-fact-against-filing-calendar`
  trap #2, observed live 2026-07-25.
- **kpi_xbrl purity preserved**: `kpi_xbrl.py` stays pure-compute; the store
  write stays in `kpi_xbrl_ingest.py`.
- **Store/tearsheet read logic untouched** (brief §Out of Scope): no edits to
  `kpi_store.py` read paths, `same_period`/`_qtrs`, or `tearsheet_format.py`.
Kickoff decision: durable series identity for the top-line lane → the fixed
  canonical `kpi_id` literal `total_revenue` (describes the economic meaning, not
  whichever concept string a given filer happens to tag; mirrors the TW producer's
  canonical-field-slug decision). User-confirmed one-way-door decision, 2026-07-25.

Kickoff decision: Lane B flat facts' `source_kind` → the NEW value `xbrl-topline`,
  admitted to `kpi_gate.TRUSTED_SOURCE_KINDS` (Task 11). Reusing
  `xbrl-dimensional` would stamp a factually wrong provenance label on a
  non-dimensional fact, and relabelling stored points later is a durable-store
  migration; the gate edit is one frozenset entry. User-confirmed one-way-door
  decision, 2026-07-25. Lane A stays `xbrl-companyfacts` (already trusted).

Kickoff decision: which concept wins when a filer reports several candidates →
  the XBRL US DQC Revenue Guidance ordering, encoded verbatim as Task 1's closed
  allowlist (mixed revenue types → `Revenues` is the total; all-ASC-606 →
  the contract-with-customer concept). Derivation-for-confirmation, not an open
  choice — user-confirmed 2026-07-25; live evidence is WMT (`Revenues` 713,163M,
  which is WMT's own "Total revenues" line, vs RFCC 706,413M).

Kickoff decision: whether self-defined `source_kind` values need a "we defined
  this" prefix → NO. Evaluated 2026-07-25 at user request. Every value in the
  vocabulary is self-defined (`xbrl-dimensional`, `xbrl-companyfacts`,
  `llm-located`, `prose`), so a uniform "ours" marker carries zero discriminating
  information; IETF RFC 6648 / BCP 178 deprecates exactly this construct because
  the prefix must be renamed once a value becomes de facto standard — and here a
  rename is a durable-store migration. The prefix that already does real work is
  the TRUST-CLASS segment (`xbrl-` = machine-structured filing provenance, which
  is what `kpi_gate` keys on), so the shape is `<trust-class>-<lane>` and
  `xbrl-topline` joins it correctly on the same axis as `xbrl-dimensional`.
  Task 11 converts that implicit convention into a mechanical pin.

- **Known naming debt, deliberately NOT fixed in this arc** (Task 7 records it in
  BACKLOG): `xbrl-companyfacts` names a SEC REST endpoint but `kpi_tw_ingest.py:54`
  reuses it for TW MOPS iXBRL, where no such endpoint exists — the second segment
  mixes an endpoint-name axis with the shape axis the other values use; and
  `kpi_prose_candidates.py:433,697` mints a bare `"prose"` with no trust-class
  segment at all. Renaming either is a durable-store migration (the one-way door
  this arc exists to respect), so both ship as documented debt, not silent drift.

Amendment note 1 (post-PASS, schema-safe → re-review skipped): applied the round-2
  reviewer's own three non-blocking notes — added the
  `topline_probe_2026-07-25.json` fixture to Tasks 2-6 `Context paths` (without it
  a fresh implementer never sees the oracle under paths-not-content delegation),
  and corrected two cosmetic line refs (collision guard `:174-184`,
  `SUPPORTED_PACKS` `:1190-1197`). No field added/removed, no `Dependencies` or
  `Independent` change, DAG and depth unchanged → plan-document-reviewer re-run
  skipped per writing-plans §"Amending a PASS plan".

Amendment note 2 (post-PASS, DAG CHANGED → round-3 re-review REQUIRED, verdict
  reset to PENDING): the kickoff briefing resolved Lane B's `source_kind` to the
  NEW value `xbrl-topline`, which must be admitted to
  `kpi_gate.TRUSTED_SOURCE_KINDS` — a DIFFERENT module than any existing task
  owns, so the 10-task plan had no task covering it (a real coverage gap the
  round-2 review could not see, because the brief deliberately left this decision
  open). Added **Task 11** (level 1, `Dependencies: none`) and made Task 5 depend
  on it. Task 5's provenance assignment was also corrected from per-pack to
  PER-LANE after the kickoff surfaced that a Lane B pack carries both fact kinds.
  Task 7 gained the naming-debt BACKLOG entry. Task numbering is a label, not an
  ordering: Task 11 sits at level 1 alongside Tasks 1 and 7.

Amendment note 3 (round-3 NEEDS_REVISION fixes, verdict stays PENDING pending
  round 4): corrected a FALSE claim this plan previously asserted — that
  `facts_to_points` already raises on a same-period value disagreement. It does
  not; independently verified at `kpi_xbrl.py:490-586` (no cross-fact
  comparison), `kpi_xbrl.py:648` + `:870` (the raise belongs to the binding
  pipeline, which ingest never calls — `kpi_xbrl_ingest.py:187` calls only
  `facts_to_points`), and `kpi_store.py:321-325` (same-dedup-key/different-value
  = first record wins, silently). Task 5 now ADDS that guard, which is what
  discharges brief SES #3's fail-loud clause; §Notes, Task 5's RED, and its
  Context paths were all corrected. Task 6's provenance assertion now pins both
  literals per lane instead of paraphrasing Lane B's. Task 7 gained the missing
  RED clause for its second deliverable. Task 11's `Brief item covered` no longer
  quotes a sentence absent from the brief.

Amendment note 4 (round-4 NEEDS_REVISION fix, verdict stays PENDING pending
  round 5): round 4 correctly found brief SES #3's fail-loud clause unowned — an
  intra-pack guard cannot see the other lane's already-stored point, since the
  two lanes arrive in separate `ingest_pack` calls. Its SUGGESTED fix was NOT
  applied as written: it keyed the raise on "same period, DIFFERENT
  `source_accession`", which is the definition of a LEGITIMATE restatement and
  would fire on every genuine recast, destroying arc (d)'s `†` capability.
  Live-verified 2026-07-25 instead: `companyconcept` rows carry the same
  accession/filed as the per-filing parse of that filing (NVDA
  `0001045810-26-000021` / `2026-02-25`), so the two lanes' dedup keys COINCIDE;
  and the same period legitimately recurs under different accessions (NVDA FY2025
  under both `…25-000023` and `…26-000021`). The guard is therefore ONE
  store-aware check keyed on the FULL dedup key — same key + different value
  raises, different accession still appends. Task 5's Description / RED /
  `Brief item covered` and §Notes now encode that polarity with the live evidence.
  Round 5 adjudicated this refusal independently and CONFIRMED it, citing a
  stronger precedent than the planner had: `kpi_xbrl.py:642-654`, the repo's own
  shipped anti-fabrication raise, buckets values BY ACCESSION and fires only
  within a single accession — with a comment (`:640-641`) stating that a
  multi-filing recast of the same value "must NOT abort the whole series".

Amendment note 5 (post-PASS, schema-safe → re-review skipped per writing-plans
  §"Amending a PASS plan"): applied round 5's three non-blocking notes.
  (a) The probe oracle was COPIED INTO THE BRANCH before SDD dispatch
  (`investing-toolkit/tests/data/fixtures/topline_probe_2026-07-25.json`, 8
  filers, untracked pending Task 1's commit) — the plan previously named only a
  session-scoped scratchpad basename no fresh implementer could resolve; Task 1's
  Description and Context paths now point at the in-repo file.
  (b) Task 3 gained the `fiscal_quarter = "FY"` + duration fields that
  `classify_fact_period` hard-requires, plus a **New-Year-boundary fail-loud**:
  Lane A's period-end-year labelling is unsound for a 52/53-week filer whose
  year-end crosses Jan 1 (dei says FY2024, period-end says 2025), and Lane A has
  no dei calendar to check against — a divergent `period` label would give the two
  lanes DIFFERENT dedup keys, making Task 5's guard blind and minting a fabricated
  `†` from one filing. Such rows are now skipped with a named coverage reason;
  Lane B stays the authority for those years.
  (c) Task 6's e2e now also pins that both lanes emit an IDENTICAL `period` label
  for a shared fiscal year, using a near-New-Year-FYE filer.
  No field added/removed, no `Dependencies`/`Independent` change, DAG and depth
  unchanged (still 5).

## Task 1 — data-markets: top-line revenue identification primitives

- Description: Add three pure primitives to `sec_edgar_client.py`: (a) an ORDERED
  closed allowlist `_TOP_LINE_REVENUE_CONCEPTS = ("Revenues",
  "RevenuesNetOfInterestExpense", "RevenueFromContractWithCustomerExcludingAssessedTax",
  "RevenueFromContractWithCustomerIncludingAssessedTax")` — narrower than the
  existing `_REVENUE_ALLOW_CONCEPT_LOCAL_NAMES`, which must NOT be reused;
  (b) `_is_top_line_revenue_fact(fact)` — true only when `is_dimensioned` is
  False AND the existing duration / currency / non-NaN gates pass AND the
  concept local-name is in the allowlist; (c)
  `select_top_line_concept(facts) -> str | None` — first-present in allowlist
  order over the candidate facts' concepts, None when there are no candidates.
  ALSO commit the captured live-probe evidence file
  `investing-toolkit/tests/data/fixtures/topline_probe_2026-07-25.json` — it is
  ALREADY PRESENT in the working tree as an untracked file (copied verbatim from
  the live probe, 8 filers, 9,915 bytes); commit it unmodified, do NOT regenerate
  or hand-edit it, so every later task's fixture oracle survives a fresh session.
- Module: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
- Files touched: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py, investing-toolkit/tests/data/test_sec_edgar_top_line.py, investing-toolkit/tests/data/fixtures/topline_probe_2026-07-25.json
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py  (`_REVENUE_ALLOW_CONCEPT_LOCAL_NAMES` :2034-2040, `_REVENUE_DENY_SUBSTRINGS` :2069-2078, `_dimensional_revenue_candidate_gates` :2313-2331, `_is_dimensional_revenue_fact` :2334-2353, `_dimension_signature` def :2225-2310)
  - docs/loom/specs/2026-07-25-company-total-revenue.md  (§Probe findings — the 8-filer evidence table these assertions encode)
  - investing-toolkit/tests/data/fixtures/topline_probe_2026-07-25.json  (already in the working tree, untracked — the capture this task commits; per-filer `A_flat` / `B_qualifier_only` / `C_dimensional_concepts` buckets)
- Acceptance:
  - RED: `test_sec_edgar_top_line.py::test_top_line_identification` — a parametrized test over the captured probe shapes asserting: JPM's `us-gaap:InvestmentBankingRevenue` / `PrincipalTransactionsRevenue` / `BrokerageCommissionsRevenue` / `jpm:*` component facts are REJECTED; XOM's `us-gaap:Revenues` carrying `ConsolidationItemsAxis=OperatingSegmentsMember` is REJECTED (it is 452,209M against a true total of 332,238M); JPM's and NVDA's flat `us-gaap:Revenues` are ACCEPTED; and `select_top_line_concept` returns `Revenues` for JPM (7 candidates) and for WMT (`Revenues` 713,163M over RFCC 706,413M), returns the RFCC concept for AAPL (its only candidate), and returns None when only component concepts are present.
  - GREEN: the three primitives exist and the parametrized test passes; every pre-existing dimensional-extraction test stays green (the dimensional predicates are untouched).
- External surfaces: SEC XBRL fact shape via edgartools 5.42.0 `facts.to_dataframe()` records — grounding: in-repo evidence (`sec_edgar_client.py:1789-1797` documents the record columns) + live probe capture 2026-07-25.
- Dependencies: none
- Independent: true
- Brief item covered: Decision — "Concept selection is a closed, ordered, first-present allowlist, grounded in XBRL US DQC Revenue Guidance" + "Only `is_dimensioned == False` qualifies".
- Status: done(c301c7be)  # spec-reviewer PASS; code-quality-reviewer PASS_WITH_NOTES — its 🟡 (one 106-line test bundling five behaviors, violating F.I.R.S.T Independent) was routed back and fixed: 1 test → 14 parametrized items. The plan's RED id `test_top_line_identification` was deliberately RENAMED away in that split; the acceptance property is that the behaviours are pinned, not the function name. Two 🟢 docstring corrections also applied. Reviewer independently re-ran the suite and mutation-checked the XOM assertion rather than trusting self-report.

## Task 2 — data-markets: Lane B emits the winning flat top-line facts

- Description: In `extract_dimensional_revenue`'s per-filing loop, additionally
  collect the filing's top-line candidates via Task 1's predicate, resolve ONE
  winner with `select_top_line_concept`, and emit that winner's facts into the
  SAME `facts` list through the existing `_build_dimensional_revenue_fact`
  builder (so each carries `period_start`, `duration_months`, `duration_weeks`,
  `week_lane_band`, `fiscal_year`, `fiscal_quarter` from the filing's dei
  calendar) with `dimensions == {}`. A filing with no candidate contributes
  nothing and is recorded in `coverage` with a named reason — never fabricated,
  never silently dropped. Do not change any dimensional-fact behavior.
- Module: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
- Files touched: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py, investing-toolkit/tests/data/test_sec_edgar_top_line.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py  (`extract_dimensional_revenue` :2991+, per-filing loop; `_build_dimensional_revenue_fact` :2837-2961)
  - investing-toolkit/skills/data-markets/scripts/pack_us.py  (`pack_kpi_quarterly` :957-1030 — the two arms that consume this extractor unchanged)
  - investing-toolkit/tests/data/fixtures/topline_probe_2026-07-25.json  (the captured 8-filer live-probe oracle committed by Task 1 — the fixture source of record)
- Acceptance:
  - RED: `test_sec_edgar_top_line.py::test_extractor_emits_one_flat_top_line_per_filing` — the pack from a captured non-December-FYE filing shape contains exactly ONE flat top-line concept, its facts carry `dimensions == {}` plus a non-None `fiscal_year`, `fiscal_quarter`, and `period_start`; a filing whose only revenue facts are components yields zero top-line facts and one named `coverage` entry.
  - GREEN: the pack carries both dimensional and top-line facts; all pre-existing `extract_dimensional_revenue` tests stay green (dimensional output byte-unchanged for a fixture with no flat candidates).
- External surfaces: SEC XBRL fact shape via edgartools 5.42.0 — grounding: same as Task 1.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: Smallest End State #1 — "the existing per-filing XBRL parse also emits the company's flat top-line revenue fact".
- Status: done(7320a494)  # spec-reviewer PASS; code-quality-reviewer PASS_WITH_NOTES — its 🟡 (the single-candidate fixture could not kill two mutants: dropping the winner match, and dropping the flat-only gate) was routed back and closed with two mutation-VERIFIED cases. Durable finding recorded in the commit: a consolidation-qualifier-only fact also has `dimensions == {}`, so `dimensions == {}` cannot distinguish XOM's segment view (452,209M) from its true total (332,238M) — only the native `is_dimensioned` flag can.

## Task 3 — data-markets: Lane A companyconcept annual-only backfill reshape

- Description: Add `build_top_line_backfill(ticker, ...)` to `sec_edgar_client.py`:
  fetch the companyconcept series for each allowlist concept in order, pick the
  first concept that returns rows (`select_top_line_concept`'s ordering, applied
  to which concepts have data), keep ANNUAL rows only (a `start`→`end` span of
  approximately 12 months, using this module's existing day-span helpers — never
  a hardcoded 365), and reshape each row into the same fact shape Lane B emits
  (`dimensions == {}`, `period_start` from `start`, `period_end` from `end`,
  `accession` from `accn`, `filed` from `filed`, `fiscal_year` from the period-end
  year — the SEC annual-labeling convention — plus the fields
  `classify_fact_period` HARD-REQUIRES or it raises unclassifiable:
  `fiscal_quarter = "FY"` and `duration_months` (and, for a week-lane filer,
  `duration_weeks` + `week_lane_band`), computed from the row's own
  `start`→`end` span via this module's existing day-span helpers). MUST NOT read
  the row's `fy` / `fp` fields at all: they are the FILING's focus, not the fact's
  period — live-confirmed 2026-07-25, every row from NVDA's FY2026 filing is
  stamped `fy=2026` including its FY2024 and FY2025 comparatives (memory
  `fiscal-year-derive-per-fact-against-filing-calendar` trap #2). Quarterly rows
  are skipped with a named coverage reason, never guessed.
  **New-Year-boundary fail-loud**: the period-end-year rule is only sound when the
  fiscal-year LABEL equals the period-end calendar year. For a 52/53-week filer
  whose year-end crosses New Year (a FY2024 ending 2025-01-03), it does not — and
  Lane A has no dei calendar to check against, so it must NOT guess. Skip any
  annual row whose `end` falls within the module's existing fiscal-boundary
  tolerance of Jan 1 and record it under `coverage` with a named reason; Lane B,
  which HAS the dei calendar, remains the authority for those years.
- Module: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
- Files touched: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py, investing-toolkit/tests/data/test_sec_edgar_top_line_backfill.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py  (`summarize_concept` :271-294 — the row shape `{start,end,value,accn,form,fy,fp,filed}`; `fetch_facts` :239; `action_facts` :666-711; `_filing_period_end_calendar_year` :2964-2988 — the annual-label convention and its explicit non-applicability to quarterlies; `_duration_span_days` :2378+)
  - docs/loom/memory/fiscal-year-derive-per-fact-against-filing-calendar.md
  - investing-toolkit/tests/data/fixtures/topline_probe_2026-07-25.json  (the captured 8-filer live-probe oracle committed by Task 1 — the fixture source of record)
- Acceptance:
  - RED: `test_sec_edgar_top_line_backfill.py::test_backfill_is_annual_only_and_ignores_fy_fp` — given a captured companyconcept payload mixing annual and quarterly rows under `fp: FY` for a non-December-FYE filer, the result contains only the annual rows; each carries `fiscal_year` equal to its own `period_end` year plus `fiscal_quarter == "FY"` and a `duration_months` that makes it classifiable by `kpi_xbrl.classify_fact_period`; a row whose `fy` disagrees with that derivation still gets the period-derived value (proving `fy` is unread); and an annual row whose `end` falls within the fiscal-boundary tolerance of Jan 1 is EXCLUDED with a named `coverage` reason rather than labelled by the calendar-year rule.
  - GREEN: annual-only reshape produces Lane-B-shaped facts; a ticker with no allowlist concept returning rows yields a loud error slot, never an empty-but-successful pack.
- External surfaces: HTTP API: `data.sec.gov/api/xbrl/companyconcept/CIK{cik}/us-gaap/{concept}.json` — grounding: in-repo evidence (`sec_edgar_client.py:59` pins the URL template; `summarize_concept` :271-294 documents the row fields) + live probe 2026-07-25.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: Smallest End State #2 — "an annual-only backfill from the `companyconcept` REST series fills fiscal years older than the filings Lane B fetched".
- Status: done(f14ef7cc)  # spec PASS; quality PASS_WITH_NOTES — 🟡 (New-Year test covered only the after-Jan-1 branch; a sign flip would have gone untested) routed back and closed by parametrizing both directions. Also emitted calendar_year/quarter on override: both lanes feed ONE series, so inconsistent field presence inside it degrades silently.

## Task 4 — data-markets: `kpi-topline-backfill` pack entry

- Description: Add a `kpi-topline-backfill` pack to `pack_us.py` that calls
  `build_top_line_backfill` for one ticker and emits the standard pack envelope
  (same `{"pack", "ticker", "facts", "coverage", ...}` shape `pack_kpi_quarterly`
  emits), and register it in the pack-name list so `pack.py --pack
  kpi-topline-backfill --ticker X` resolves. The envelope MUST additionally carry
  the top-level key `"source_kind"` set to the exact literal `"xbrl-companyfacts"`
  (the plan's §Notes envelope provenance contract; brief §Decision names this kind
  as already trusted) — without it every Lane A point would inherit
  `ingest_pack`'s `"xbrl-dimensional"` default and carry a factually wrong durable
  provenance label. No analysis logic in the pack layer.
- Module: investing-toolkit/skills/data-markets/scripts/pack_us.py
- Files touched: investing-toolkit/skills/data-markets/scripts/pack_us.py, investing-toolkit/tests/data/test_pack_us_topline_backfill.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/pack_us.py  (`pack_kpi_quarterly` :957-1030 — envelope shape to mirror; `SUPPORTED_PACKS` registry :1190-1197)
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py  (`build_top_line_backfill` — produced by Task 3)
  - investing-toolkit/tests/data/fixtures/topline_probe_2026-07-25.json  (the captured 8-filer live-probe oracle committed by Task 1 — the fixture source of record)
- Acceptance:
  - RED: `test_pack_us_topline_backfill.py::test_topline_backfill_pack_envelope` — `pack_kpi_topline_backfill("NVDA")` with the fetch stubbed returns an envelope whose `pack == "kpi-topline-backfill"`, whose `source_kind == "xbrl-companyfacts"`, and whose `facts` are the reshaped annual rows; the pack name resolves through the registry.
  - GREEN: the new pack is reachable by name, its envelope matches the existing pack contract plus the declared `source_kind`, and existing pack tests stay green.
- External surfaces: CLI flag: `pack.py --pack kpi-topline-backfill` — grounding: in-repo evidence (`pack_us.py:1190-1197` `SUPPORTED_PACKS` registry, `:24` the documented pack list).
- Dependencies: Task 3 completes first
- Independent: true
- Brief item covered: Smallest End State #2 — the backfill must be runnable, i.e. reachable through the data layer's one pack facade — plus Decision "Lane A is annual-only … `source_kind = \"xbrl-companyfacts\"` (already trusted)" (the producing half).
- Status: done(fc661e7e)  # spec PASS; quality NEEDS_REVISION→PASS on round 2. Two 🟡: a FOURTH pack-name pinning site (`pack.py` US_ONLY_PACKS) was missed — a US-only pack absent from it falls through to the TW module and misnames a market problem as a typo; and a fixture paired one year's real revenue with another year's period/accession under a docstring claiming captured provenance. Fixed by regenerating from the real producer.

## Task 5 — analysis-kpi: ingest flat top-line facts under a canonical `total_revenue` id

- Description: In `kpi_xbrl_ingest.py`, stop skipping flat facts
  (`ingest_pack` :152-153) and route them to a SEPARATE top-line lane: every flat
  fact (`dimensions == {}`) maps to the fixed canonical `kpi_id` constant
  `total_revenue` — NOT `derive_kpi_id`'s bare-concept slug — and is appended via
  the non-collapsing `facts_to_points` so each vintage is its own point. Group the
  flat lane on ONE top-line key so that two different flat concepts (a filer that
  switched tagging across years) merge into the one series WITHOUT tripping the
  `claimed_by` collision guard; the guard's behavior for the dimensional lane must
  be unchanged. ALSO assign provenance PER LANE, not per pack — a Lane B pack
  carries BOTH kinds of fact, so one pack-wide label would be wrong for half of
  it: dimensional facts keep `"xbrl-dimensional"`; flat top-line facts take the
  envelope-declared `"source_kind"` when the pack carries one (Lane A backfill →
  `"xbrl-companyfacts"`) and otherwise default to `"xbrl-topline"` (Lane B, whose
  flat facts come from the per-filing parse). RAISE on any kind outside
  `kpi_gate.TRUSTED_SOURCE_KINDS` before writing anything. ALSO add the
  STORE-AWARE value-disagreement guard (§Notes pins its polarity): before
  appending a flat top-line point, consult the existing series via the store's
  READ APIs (`query_latest` / `history` — no edit to store read logic) and RAISE
  when a stored point shares this point's FULL dedup key
  `(company, kpi_id, period, as_of, source_accession)` but carries a DIFFERENT
  `value`. A stored point for the same period under a DIFFERENT accession is a
  legitimate restatement and MUST still append (that is what `†` renders) — do
  NOT raise on it. Remove the now-obsolete "OUT OF SCOPE this arc" comments in
  `ingest_pack` and in `derive_kpi_id`'s docstring.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl_ingest.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl_ingest.py, investing-toolkit/tests/analysis/test_kpi_xbrl_ingest.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl_ingest.py  (`derive_kpi_id` :85-109, `_signature_key` :112-122, `ingest_pack` :125-194 incl. the flat-skip :152-153 and the collision guard :174-184)
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py  (`facts_to_points` :490-586 — the non-collapsing emitter; note it does NO cross-fact value comparison, so no raise comes from here)
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py  (`append` :317-324 — the documented first-record-wins behavior on a same-dedup-key/different-value collision, i.e. the silent path this task's new guard must pre-empt)
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py  (`append` :303, `_dedup_key` :176, `_require_provenance` :138)
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_gate.py  (`TRUSTED_SOURCE_KINDS` :95 — the allowed provenance labels)
  - docs/loom/memory/derived-durable-id-slug-is-a-lossy-one-way-door.md
  - investing-toolkit/tests/data/fixtures/topline_probe_2026-07-25.json  (the captured 8-filer live-probe oracle committed by Task 1 — the fixture source of record)
- Acceptance:
  - RED: `test_kpi_xbrl_ingest.py::test_flat_facts_ingest_as_canonical_total_revenue` — a pack mixing dimensional and flat facts appends the flat ones under `kpi_id == "total_revenue"`; a pack whose flat facts span TWO different allowlist concepts across years lands them in that ONE series without raising the collision guard; two vintages of one annual period produce two points (no collapse); and `test_cross_lane_value_disagreement_raises` — ingesting a SECOND pack whose flat point shares the FULL dedup key `(company, kpi_id, period, as_of, source_accession)` of an ALREADY-STORED point but carries a DIFFERENT value RAISES before any append (the cross-lane fabrication case: both lanes read the same filing, so they share an accession — see §Notes for the live accession-alignment evidence), WHILE ingesting a point for the same period under a DIFFERENT accession with a different value still APPENDS and produces two vintages (a legitimate restatement — the guard must NOT fire on it). This guard is ADDED by this task: no such check exists today (`facts_to_points`, `kpi_xbrl.py:490-586`, does no cross-fact comparison, and `kpi_store.append`, `kpi_store.py:321-325`, silently keeps the FIRST record on a same-dedup-key/different-value collision). Plus `test_ingest_assigns_provenance_per_lane` — for a Lane B pack (no envelope `source_kind`) the dimensional points carry `"xbrl-dimensional"` while the flat points carry `"xbrl-topline"` in the SAME ingest call; for a Lane A pack declaring `"source_kind": "xbrl-companyfacts"` the flat points carry that kind instead; and a pack declaring a kind outside `TRUSTED_SOURCE_KINDS` RAISES before anything is written.
  - GREEN: `ingest_pack`'s returned `kpi_ids` includes `total_revenue`; each lane's points carry their own correct provenance; all pre-existing dimensional ingest tests — including the collision-guard test — stay green.
- External surfaces: none (pure internal logic over the fact-pack dict).
- Dependencies: Tasks 2, 11 complete first
- Independent: true
- Brief item covered: Decision — "`kpi_id` is a fixed canonical constant (e.g. `total_revenue`), NOT `derive_kpi_id`'s empty-dimensions bare-concept slug" — plus Decision "Lane A is annual-only … `source_kind = \"xbrl-companyfacts\"` (already trusted)" (the consuming half) — plus Smallest End State #3's second clause, "disagreement is a fabricated `†` and must fail loud, never be silently stored" (the store-aware dedup-key guard is what discharges it; Task 6 owns the first clause, the same-value agreement).
- Status: done(23cbdbf9)  # spec PASS (both adjudications upheld); quality NEEDS_REVISION→PASS_WITH_NOTES on round 2. Three 🟡, all of the same family — assertions that prove nothing: raw `!=` resting on an unpinned invariant another module owns (and already violated by the 8-K lane), a fabricated `filed` date compared against itself, and a build-then-write restructure whose justification no test exercised. All closed and mutation-verified.

## Task 6 — two-lane e2e: overlap agreement + tearsheet renders the total

- Description: Add an end-to-end seam test over an ISOLATED store dir
  (`KPI_STORE_DIR`) that ingests a captured Lane B pack and a captured Lane A
  backfill pack for the same ticker, then asserts (a) a fiscal year covered by
  BOTH lanes resolves to the SAME value, (b) the older years only Lane A covers
  are present in the same `total_revenue` series, and (c) the rendered tearsheet
  shows the total row alongside the segment rows, with the restatement `†`
  behavior unchanged.
- Module: investing-toolkit/tests/analysis
- Files touched: investing-toolkit/tests/analysis/test_top_line_two_lane_e2e.py
- Context paths:
  - investing-toolkit/tests/analysis/test_kpi_xbrl_to_tearsheet_e2e.py  (arc (d)'s seam probe — the pattern to mirror, incl. isolated-store handling)
  - investing-toolkit/skills/report-kpi-tearsheet/scripts/tearsheet_format.py  (the pure formatter; read-only in this arc)
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py  (`query_latest` :393, `history` :459)
  - investing-toolkit/tests/data/fixtures/topline_probe_2026-07-25.json  (the captured 8-filer live-probe oracle committed by Task 1 — the fixture source of record)
- Acceptance:
  - RED: `test_top_line_two_lane_e2e.py::test_two_lanes_agree_and_tearsheet_renders_total` — currently fails because no top-line series exists; once green it asserts the overlapping fiscal year's value is identical from both lanes, that each lane's points carry their own provenance (the Lane A pack's flat points carry `source_kind == "xbrl-companyfacts"`; the Lane B pack's flat top-line points carry `"xbrl-topline"` while its dimensional points stay `"xbrl-dimensional"` in the same ingest call), the Lane-A-only years are present, that a fiscal year both lanes cover receives the IDENTICAL `period` label from each (so their dedup keys genuinely coincide and Task 5's guard can see them — pin this with a captured filer whose fiscal year-end sits near New Year, the case where Lane A's period-end-year rule and Lane B's dei-calendar rule could diverge), and the tearsheet output contains the total row next to the segment rows.
  - GREEN: the test passes against captured real-shaped packs, with no edits to `tearsheet_format.py` or `kpi_store.py` read logic.
- External surfaces: none (consumes captured packs; no live fetch in the test).
- Dependencies: Tasks 4, 5 complete first
- Independent: true
- Brief item covered: Smallest End State #3 — "An overlapping fiscal year covered by BOTH lanes yields the same value (pinned by a real-data test)" + #1's "the tearsheet renders it beside the segment series".
- Status: done(dd87ca1c)  # spec PASS (Amendment 5(c) substitution upheld as fully discharging intent); quality NEEDS_REVISION→closed. FOUND THE ARC'S ONE REAL SHIPPED DEFECT (see the seam-fix commit 18fc47fd). Its own 🟡s were all documentation honesty — a stale RED banner over a green suite, an undisclosed Lane B hand-built envelope, and a miscounted counterfactual ledger.

## Task 7 — docs: rewrite the BACKLOG entry and supersede arc (d)'s out-of-scope note

- Description: Rewrite `docs/loom/BACKLOG.md` §"company total (top-line) revenue
  lane" — its stated premise ("`extract_dimensional_revenue` emits ZERO flat
  totals, so top-line company revenue is unfetchable via arc (d)'s dimensional
  path… the only shipped source is `action_facts(ticker,'Revenues')`") is
  disproved by the 2026-07-25 live probe. Replace it with the two-lane decision,
  citing the probe evidence and the brief. Mark the arc (d) brief's §Out of Scope
  top-line entry as superseded by this arc, with a one-line pointer. ALSO add a
  new BACKLOG entry recording the `source_kind` naming debt this arc deliberately
  did NOT fix: `xbrl-companyfacts` names a SEC REST endpoint yet
  `kpi_tw_ingest.py:54` reuses it for TW MOPS iXBRL (no such endpoint exists
  there), and `kpi_prose_candidates.py:433,697` mints a bare `"prose"` with no
  trust-class segment — both are durable stored values, so renaming either is a
  store migration, not an edit (see §Notes for the evaluated decision and its
  RFC 6648 grounding).
- Module: docs/loom
- Files touched: docs/loom/BACKLOG.md, docs/loom/specs/2026-07-24-kpi-xbrl-store-producer.md
- Context paths:
  - docs/loom/BACKLOG.md  (§"investing-toolkit KPI tearsheet — company total (top-line) revenue lane")
  - docs/loom/specs/2026-07-25-company-total-revenue.md  (§What Becomes Obsolete — the exact items to remove)
- Acceptance:
  - RED: `grep -c "The only shipped source is" docs/loom/BACKLOG.md` returns 1 (the disproved premise is still present at `docs/loom/BACKLOG.md:234`; note the capital `T` — a lowercase pattern matches nothing and would make this task look already-done), AND `grep -c "kpi_tw_ingest.py:54" docs/loom/BACKLOG.md` returns 0 (the `source_kind` naming-debt entry does not exist yet).
  - GREEN: that grep returns 0; the section states the two-lane decision and cites the probe; the arc (d) brief carries the superseded pointer; and `grep -c "kpi_tw_ingest.py:54" docs/loom/BACKLOG.md` returns >=1 (the `source_kind` naming-debt entry exists).
- Dependencies: none
- Independent: true
- Brief item covered: What Becomes Obsolete — "`docs/loom/BACKLOG.md` §'company total (top-line) revenue lane' — its premise is probe-disproved; rewrite to the two-lane decision" + the arc (d) brief supersede entry.
- Status: done(2b521ff9)  # spec-reviewer PASS, code-quality-reviewer PASS (one 🟢 phrasing nit, non-blocking)

## Task 8 — docs: analysis-kpi SKILL + cli-reference wiring for the top-line lane

- Description: Document in `analysis-kpi`'s SKILL.md and `references/cli-reference.md`
  that `kpi_xbrl_ingest ingest` now also ingests flat top-line facts under the
  canonical `total_revenue` series, and how the two-lane workflow runs
  (Lane B pack → ingest; Lane A backfill pack → ingest). No behavior change.
- Module: investing-toolkit/skills/analysis-kpi
- Files touched: investing-toolkit/skills/analysis-kpi/SKILL.md, investing-toolkit/skills/analysis-kpi/references/cli-reference.md
- Context paths:
  - investing-toolkit/skills/analysis-kpi/SKILL.md
  - investing-toolkit/skills/analysis-kpi/references/cli-reference.md
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl_ingest.py  (as modified by Task 5)
- Acceptance:
  - RED: `grep -c "total_revenue" investing-toolkit/skills/analysis-kpi/references/cli-reference.md` returns 0.
  - GREEN: both files describe the top-line lane and the two-lane ingest workflow; `test_skill_structure.py` stays green (SKILL.md body stays under the token cap).
- Dependencies: Task 5 completes first
- Independent: true
- Brief item covered: Smallest End State #1/#2 — the shipped lanes must be discoverable from the skill surface that runs them.
- Status: done(f3f69d07)  # spec PASS; quality PASS_WITH_NOTES — 🟡: the doc flattened a hedge the source docstring had just been rewritten IN REVIEW to keep. Turning code into documentation strips qualifiers, and the summary is what the next operator reads instead of the source.

## Task 9 — docs: data-markets SKILL wiring for top-line emission + the backfill pack

- Description: Document in `data-markets`' SKILL.md that the kpi-quarterly pack
  now also carries the company's flat top-line revenue facts, and that
  `--pack kpi-topline-backfill` provides the annual-only companyconcept history
  backfill. No behavior change.
- Module: investing-toolkit/skills/data-markets
- Files touched: investing-toolkit/skills/data-markets/SKILL.md
- Context paths:
  - investing-toolkit/skills/data-markets/SKILL.md
  - investing-toolkit/skills/data-markets/scripts/pack_us.py  (as modified by Task 4)
- Acceptance:
  - RED: `grep -c "kpi-topline-backfill" investing-toolkit/skills/data-markets/SKILL.md` returns 0.
  - GREEN: the SKILL.md pack list includes `kpi-topline-backfill` and notes the top-line facts now riding in the kpi-quarterly pack; `test_skill_structure.py` stays green.
- Dependencies: Tasks 2, 4 complete first
- Independent: true
- Brief item covered: Smallest End State #1/#2 — the data layer's documented pack surface must name the new capability.
- Status: done(670b1041)  # spec PASS; quality PASS_WITH_NOTES — 🟡: frontmatter left stale as 'pre-existing' while the SAME change fixed the identical pre-existing gap in the body, from the same cause at the same cost. Reviewer caught the inconsistency; orchestrator reversed its own earlier agreement with the implementer.

## Task 10 — version bump + CHANGELOG + Codex manifest sync

- Description: Bump `investing-toolkit/.claude-plugin/plugin.json` to the next
  available minor relative to `origin/main` at close-out (see §Notes — PR #612
  holds 2.35.0), add the matching CHANGELOG entry naming the two-lane top-line
  capability, and mirror the bump into the Codex manifest by running
  `python3 scripts/sync_codex_manifests.py investing-toolkit` and committing its
  output unmodified. Stamp the CHANGELOG's test count from an actual
  `pytest --collect-only` at close-out, never mid-branch (memory
  `stamp-changelog-test-counts-at-closeout`).
- Module: investing-toolkit/.claude-plugin/plugin.json
- Files touched: investing-toolkit/.claude-plugin/plugin.json, investing-toolkit/CHANGELOG.md, investing-toolkit/.codex-plugin/plugin.json
- Context paths:
  - investing-toolkit/.claude-plugin/plugin.json
  - investing-toolkit/CHANGELOG.md
  - scripts/sync_codex_manifests.py
- Acceptance:
  - RED: `scripts/check_version_bump.py` (or its paired test) fails — the branch changes skill content without a version bump.
  - GREEN: version bumped, CHANGELOG entry present and naming the capability, Codex manifest in sync (the manifest-drift test passes).
- Dependencies: Tasks 6, 8, 9 complete first
- Independent: false
- Brief item covered: Open Questions #3 — "Version + base freshness: PR #612 is OPEN at 2.35.0, so this arc is **2.36.0**; if #612 merges mid-arc, rebase onto `origin/main` before review" (repo convention: a skill-content change must bump the plugin version — memory `skill_content_pr_requires_plugin_version_bump`).
- Status: done(d7673ce3)  # quality NEEDS_REVISION→closed. Two 🟡: the entry omitted the arc's one real defect (a release note listing only additions hides what a reader most needs — that a lane was unusable until an e2e caught it), and the closing count reported COLLECTED where every prior entry reports PASSED, which is both off-convention and less informative. Version gate verified green post-commit (exit 0), not assumed.

## Task 11 — kpi_gate: admit `xbrl-topline` and pin the source-kind naming convention

- Description: Add `"xbrl-topline"` to `kpi_gate.TRUSTED_SOURCE_KINDS` — the
  provenance label Lane B's flat top-line facts carry (§Notes kickoff decision;
  without it Task 5's fail-loud check would reject the arc's own points). Update
  the constant's comment to state the vocabulary shape explicitly:
  `<trust-class>-<lane>`, where the FIRST segment is the trust class the gate
  keys on (`xbrl-` = machine-structured filing provenance, needing no sampled
  ground-truth labels) and the second names the lane. Then PIN that convention
  mechanically — a test asserting every member of `TRUSTED_SOURCE_KINDS` begins
  with `xbrl-`, so a future trusted kind cannot be minted outside the trust
  class by prose discipline alone. Do NOT rename any existing value (all four are
  durable stored values; renaming is a store migration — Task 7 records the debt).
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_gate.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_gate.py, investing-toolkit/tests/analysis/test_kpi_gate_source_kinds.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_gate.py  (`TRUSTED_SOURCE_KINDS` :95 and its trusted-by-source comment :89-94; the attestation check :310-352 that consumes it)
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_tw_ingest.py  (:50-54 — the TW producer reusing `xbrl-companyfacts`; read-only evidence for the comment, do NOT change it)
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_prose_candidates.py  (:433,697 — the bare `"prose"` kind; read-only evidence, do NOT change it)
- Acceptance:
  - RED: `test_kpi_gate_source_kinds.py::test_topline_kind_is_trusted_and_convention_pinned` — asserts `"xbrl-topline" in kpi_gate.TRUSTED_SOURCE_KINDS` (fails today) and that every member of the set starts with `"xbrl-"`.
  - GREEN: both assertions pass; `"llm-located"` and `"prose"` remain OUTSIDE the trusted set (the untrusted lanes are unaffected); all pre-existing `kpi_gate` tests stay green.
- External surfaces: none (pure internal constant + its guard).
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State #1 — "the existing per-filing XBRL parse also emits the company's flat top-line revenue fact… ingests it into `kpi_store`" — the ENABLING half: without `xbrl-topline` in the trust set, Task 5's fail-loud check rejects Lane B's own points and nothing can be stored at all. The brief is silent on Lane B's provenance label (it settles only Lane A at §Decision); the value was fixed by this plan's §Notes kickoff decision, user-confirmed 2026-07-25.
- Status: done(9f8f084a)  # spec-reviewer PASS; code-quality-reviewer PASS_WITH_NOTES — its 🟡 (a stale enumeration in `attest_source`'s docstring that THIS change made wrong) was routed back to the implementer and fixed before commit, not carried as debt.

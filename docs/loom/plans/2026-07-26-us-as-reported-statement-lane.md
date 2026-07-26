# Plan: US as-reported statement lane + derived spine view

**Source brief**: docs/loom/specs/2026-07-26-us-as-reported-statement-lane.md
**Total tasks**: 10
**Critical-path depth**: 4 (≤5 ✓)
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-07-26 03:44)

Input path: brainstorming brief. No loom-spec change-folder bound — the repo
carries two non-archived change-folders (`2026-07-12-us-sec-primary-source-layer`,
`2026-07-19-8k-prose-kpi-intake`) and neither matches this branch slug; the
caller handed a brief path, so layers (i)/(ii) do not run. Stated, not skipped.

## Task 1 — Commit the 47-filer discovery probe as a capture script + dated fixture

- **Description**: Port the session's discovery probe into a committed capture
  script plus a dated JSON fixture, mirroring the shipped precedent
  (`capture_kpi_id_identity_probe.py` + `kpi_id_identity_probe_2026-07-25.json`).
  The script re-derives, over the same 47-ticker corpus, exactly the measurements
  the brief cites: per-field concept coverage, naive-vs-per-period staleness,
  shipped-lane truncation, the balance identity with the mezzanine term, and
  usable-history depth. The fixture is the committed record of the 2026-07-26 run.
- **Module**: `investing-toolkit/tests/data/fixtures/capture_us_statement_shapes_probe.py`
- **Files touched**: `investing-toolkit/tests/data/fixtures/capture_us_statement_shapes_probe.py`, `investing-toolkit/tests/data/fixtures/us_statement_shapes_probe_2026-07-26.json`, `investing-toolkit/tests/data/test_us_statement_probe_fixture.py`, `investing-toolkit/tests/data/test_capture_us_statement_shapes_legacy_selector.py` (added in the review round that froze the pre-fix selector — see §Post-PASS amendment note)
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/tests/data/fixtures/capture_kpi_id_identity_probe.py`
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/tests/data/fixtures/capture_companyconcept_form_domain.py`
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/docs/loom/specs/2026-07-26-us-as-reported-statement-lane.md`
- **Acceptance**:
  - **RED**: `test_us_statement_probe_fixture.py::test_fixture_pins_the_brief_cited_measurements` fails (no fixture)
  - **GREEN**: the offline test loads the fixture and asserts the brief's cited numbers hold — 47 tickers probed, exactly 1 filer with 0 us-gaap concepts, 13 filers never tagging a total `Liabilities`, 10 filers whose shipped-lane series ends ≥1 year early, 0 filers with ≥20 usable years. Test is offline (fixture-only, no network mark)
- **External surfaces**:
  - HTTP API: `data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json` — grounding: live capture 2026-07-26 (this fixture) + existing in-repo use at `sec_edgar_client.py:56`
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: §Current State Evidence — "Probe scripts and raw JSON currently live in the session scratchpad; ... they MUST be committed as a capture script plus a dated fixture in the plan's first task, or the numbers below have no auditable source"
- **Status**: done(accd4126)

## Task 2 — Resolve the top-line concept PER PERIOD, fixing the shipped truncation

- **Description**: `build_top_line_backfill` currently picks the first allowlist
  concept that returns ANY rows and `break`s (`sec_edgar_client.py:2863-2872`), so
  a filer that switched revenue tags keeps only its pre-switch years. Replace that
  with: fetch every `_TOP_LINE_REVENUE_CONCEPTS` entry, then resolve per PERIOD.
  When one period has rows from two concepts, break the tie by allowlist order
  **only if the values agree**; when they disagree, skip that period with a named
  `coverage.skipped_rows` reason (`top_line_concept_value_conflict`) — never guess
  which tag is right. Extract the per-period merge as a module-local helper so
  Task 5 reuses it rather than re-implementing it.
- **Module**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Files touched**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`, `investing-toolkit/tests/data/test_sec_edgar_top_line_backfill.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/tests/data/test_sec_edgar_top_line_backfill.py`
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/pack_us.py`
- **Acceptance**:
  - **RED**: `test_sec_edgar_top_line_backfill.py::test_backfill_spans_a_mid_history_concept_switch` fails — a filer whose early years are tagged `Revenues` and later years `RevenueFromContractWithCustomerExcludingAssessedTax` currently yields only the early years
  - **GREEN**: the backfill emits BOTH eras as one continuous annual series; a same-period value conflict is skipped with the named reason and never emitted
- **External surfaces**:
  - HTTP API: `data.sec.gov/api/xbrl/companyconcept/CIK{cik}/us-gaap/{concept}.json` — grounding: in-repo pinned use at `sec_edgar_client.py:57` + committed fixture `companyconcept_form_domain_2026-07-25.json`
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: §Resolved at kickoff #1 — "Fix `build_top_line_backfill`'s truncation IN THIS BRANCH ... the correct rule is the same per-period resolution this arc introduces"
- **Status**: done(a4ea4f64)

## Task 3 — Map an as-reported statement pack to store points (pure)

- **Description**: New pure-compute mapper `us_statement_pack_to_points(pack)`:
  one store point per (concept, period), `kpi_id` = the filer's own qname
  **verbatim, namespace preserved** (`us-gaap:Revenues`) — no slug derivation, so
  the id is injective by construction. `as_of` = the row's `filed` date;
  `source_accession` = the row's `accn`; `source_cell_ref` = the qname;
  `source_kind` = `"xbrl-companyfacts"`; `unit` copied from the pack. Consumes the
  pack shape PINNED in ## Notes, so it does not wait on Task 5. Imports no
  data-markets module (the analysis↔data-markets boundary).
- **Module**: `investing-toolkit/skills/analysis-kpi/scripts/kpi_us_statements.py`
- **Files touched**: `investing-toolkit/skills/analysis-kpi/scripts/kpi_us_statements.py`, `investing-toolkit/tests/analysis/test_kpi_us_statements.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-kpi/scripts/kpi_tw.py`
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py`
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/docs/loom/plans/2026-07-26-us-as-reported-statement-lane.md`
- **Acceptance**:
  - **RED**: `test_kpi_us_statements.py::test_two_revenue_concepts_become_two_series` fails
  - **GREEN**: a pack carrying both `us-gaap:Revenues` and `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax` yields points under TWO distinct `kpi_id`s, each carrying complete provenance that `kpi_store.append`'s guards accept
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: §Smallest End State #1 — "`us-gaap:Revenues` and `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax` are **two series**, not one resolved series"
- **Status**: done(ac4a2556)

## Task 4 — Derive the spine from stored as-reported series, resolving per period (pure)

- **Description**: New pure module taking a `kpi_store.py dump --company` payload
  and emitting a payload of the SAME pinned schema whose `series` are the canonical
  spine fields. For each spine field and each period, pick the first concept in
  that field's ordered chain that has an observation **for that period** — the
  resolution the store deliberately does not do at write time. A field with no
  concept present in a period yields NO entry for that period (never 0, never a
  derived guess). `tearsheet_format.py` is not touched.
- **Module**: `investing-toolkit/skills/analysis-kpi/scripts/kpi_spine_view.py`
- **Files touched**: `investing-toolkit/skills/analysis-kpi/scripts/kpi_spine_view.py`, `investing-toolkit/tests/analysis/test_kpi_spine_view.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py`
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/report-kpi-tearsheet/scripts/tearsheet_format.py`
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-kpi/scripts/kpi_tw.py`
- **Acceptance**:
  - **RED**: `test_kpi_spine_view.py::test_resolves_a_different_concept_per_period` fails
  - **GREEN**: given a dump whose `us-gaap:Revenues` series covers only the early periods and whose contract-revenue series covers only the later ones, the derived `revenue` series spans BOTH; a field absent from every stored series produces no row at all
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: §Smallest End State #2 — "A new pure view module maps the store's `dump --company` payload into a spine-shaped payload, resolving **which concept represents a field in that period** at read time"; and §Decision "Absence is data: a field the filer never tagged renders absent. Never 0, never derived-by-guess"
- **Status**: done(b372f793)

## Task 5 — Fetch the as-reported annual statement pack

- **Description**: New `build_statement_backfill(ticker)` emitting the ## Notes-pinned
  pack: for every source concept of the 14 spine fields, keep `companyfacts` rows
  whose carrier form is an allowlisted annual carrier (`_TOP_LINE_ANNUAL_CARRIER_FORMS`
  — 10-K only; a 20-F's annual history must not be stamped as a 10-K) and whose own
  start→end span classifies annual via `_duration_months`, never the row's `fy`/`fp`.
  Reuses Task 2's per-period merge helper. Every rejected row lands in
  `coverage.skipped_rows` with a named reason. A loud error slot on total failure —
  never an empty-but-successful pack.
- **Module**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Files touched**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`, `investing-toolkit/tests/data/test_sec_edgar_statements.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/pack_us.py`
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/docs/loom/plans/2026-07-26-us-as-reported-statement-lane.md`
- **Acceptance**:
  - **RED**: `test_sec_edgar_statements.py::test_emits_one_fact_per_concept_per_annual_period` fails
  - **GREEN**: the pack carries the pinned envelope + one fact per (concept,
    annual period, **accession**) with `accn`/`filed`/`form`/`unit`; a non-10-K
    carrier and a non-annual span are each skipped with their own named reason.
    **CORRECTED 2026-07-26 after the Task 5 review** — this line originally said
    one fact per (concept, annual period), which was too narrow and was the
    orchestrator's error, not the implementation's. Two rows for one window from
    DIFFERENT accessions are a restatement, and the brief's own job story asks for
    "every vintage preserved"; the shared resolver passes them through by design and
    collapse is `kpi_xbrl._reduce_window_group`'s job downstream. The multiplicity
    is the load-bearing property of this lane, so it must be pinned by a test in
    both directions, not left implied.
- **External surfaces**:
  - HTTP API: `data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json` — grounding: in-repo pinned use at `sec_edgar_client.py:56` + Task 1's committed fixture
- **Dependencies**: Task 2 completes first
- **Independent**: false
- **Brief item covered**: §Decision — "Scope of stored concepts: the spine's source concepts only"; "Granularity: annual (10-K-carried) only"
- **Status**: done(1840695e)

## Task 6 — Refuse a CIK that carries no statement history

- **Description**: Before any row work, verify the resolved CIK actually carries
  statement facts; a CIK whose `companyfacts` holds zero us-gaap concepts (measured:
  XOM resolves to an entity with 0) returns a loud, typed error slot naming the
  ticker, the resolved CIK, and the resolved entity name. Additionally record the
  observed first/last statement period in `coverage` so a TRUNCATED history
  is visible to the caller. Never stitch a predecessor CIK.
  **CORRECTED 2026-07-26 after the Task 6 review**: an earlier draft of this line
  cited "GOOGL from 2014, DIS from 2018". Those are each filer's BALANCE-SHEET
  start — a different measurement from the one the committed probe records. The
  fixture's `earliest_fact_end`, taken as the minimum across all 14 spine fields'
  10-K rows, is GOOGL **2012-12-31** and DIS **2016-10-01**, and those are the
  numbers the implementation cites. The implementer grounded in the fixture over
  the plan text, which was the right call.
- **Module**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Files touched**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`, `investing-toolkit/tests/data/test_sec_edgar_statements.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/docs/loom/memory/ticker-to-cik-can-resolve-to-a-decoy-entity.md`
- **Acceptance**:
  - **RED**: `test_sec_edgar_statements.py::test_cik_without_statement_history_is_a_loud_error` fails — a zero-concept companyfacts payload currently yields an empty-but-successful pack
  - **GREEN**: that payload returns the typed error slot (no `facts` key); a normal filer is unaffected and its `coverage` carries the observed history span
- **Dependencies**: Task 5 completes first
- **Independent**: false
- **Brief item covered**: §Decision — "CIK continuity: refuse loudly when the resolved CIK carries no statement history; surface (not silently stitch) a truncated one"
- **Status**: done(8074a177)

## Task 7 — Flag a balance-sheet identity residual in the view

- **Description**: For each period the derived spine covers, compute
  `total_assets − (total_liabilities + mezzanine + total_equity [+ minority_interest])`
  and attach a flag when `|residual| / total_assets` exceeds **1e-5**.
  **CORRECTED 2026-07-26 after the Task 7 review** — this line originally read as a
  flat three-term identity, which was WRONG, and the error originated here rather
  than in the implementation. The equity term must be whole equity. Whether it
  already is depends on which concept that period's `total_equity` chain resolved
  to: `StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest`
  already contains the non-controlling interest, so nothing is added; plain
  `StockholdersEquity` is parent-only, so `MinorityInterest` MUST be added for that
  period or the residual is exactly the NCI and the period is falsely flagged.
  The chain in the PIN below puts parent-only FIRST, so this is the majority case,
  not an edge case: cross-tabbed against the committed probe fixture, 17 of 32
  checkable filers resolve parent-only (CVX, PSX, WFC, C, MS, IBM, QCOM, COST, PEP,
  JNJ, PFE, UNH, BA, GE, F, GM, TSLA), and the effect is material for GE, F, GM,
  UNH, C and MS. The "30 of 32 balance exactly" measurement was produced by the
  probe's own four-term, incl-NCI-preferring formula
  (`capture_us_statement_shapes_probe.py`, `_balance_identity`) — it is evidence for
  the CONDITIONAL form above, and must not be cited as evidence for a flat
  three-term one. The mezzanine term
  (`TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterests`,
  falling back to `RedeemableNoncontrollingInterestEquityCarryingAmount`) is
  REQUIRED, not optional — measured, TSLA's entire residual was exactly its
  redeemable NCI. A period missing any component is NOT flagged (uncheckable ≠
  wrong; 13 filers never tag a total `Liabilities`). The flag never suppresses or
  refuses a value.
  **AMENDED 2026-07-26 after the live dogfood — ONE VINTAGE, NEVER ACROSS.** The
  first implementation read each component's own `latest`, which mixes filings: at
  MSFT's 2016-06-30 the equity carried a 2018-filed vintage that assets and
  liabilities did not, so the check compared 2017-filed assets against 2018-filed
  equity and reported a 5.7% residual for a period whose 2017 vintage balances to
  the dollar. Four of six dogfooded filers flagged, every one this shape. The check
  now selects ONE vintage — the newest `(as_of, source_accession)` pair carried by
  all of assets, liabilities and the resolved equity — and reads every component,
  mezzanine and minority interest included, out of that filing alone. A period no
  single filing covers is uncheckable, not flagged. The flag names the vintage it
  checked, so the residual is reproducible from the flag; its `components` are that
  filing's figures, which for a restated period differ from the `latest` the
  tearsheet renders — reconcilable only because the vintage is named, so naming it
  is load-bearing rather than cosmetic. Absent-reads-as-0 now means absent from the
  PERIOD, not from the checked filing: if another filing tagged a mezzanine at that
  instant, the instant demonstrably had one and this filing merely omitting the
  amount is a MISSING amount, so the period goes uncheckable. Cross-vintage evidence
  may only ever widen uncheckability — no number entering the arithmetic ever comes
  from outside the checked filing.
- **Module**: `investing-toolkit/skills/analysis-kpi/scripts/kpi_spine_view.py`
- **Files touched**: `investing-toolkit/skills/analysis-kpi/scripts/kpi_spine_view.py`, `investing-toolkit/tests/analysis/test_kpi_spine_view.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-kpi/scripts/kpi_spine_view.py`
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py`
- **Acceptance**:
  - **RED**: `test_kpi_spine_view.py::test_mezzanine_is_required_for_the_identity` fails
  - **GREEN**: a period whose assets exceed liabilities+equity by exactly its temporary-equity amount is NOT flagged; a period off by more than 1e-5 relative IS flagged; a period missing total liabilities is neither flagged nor dropped
- **Dependencies**: Task 4 completes first
- **Independent**: false
- **Brief item covered**: §Decision — "the view computes `A − (L + mezzanine + E)` per period and emits a flag when it exceeds a relative tolerance; it does not refuse data"; §Resolved at kickoff #2 (1e-5)
- **Status**: done(dada7641)

## Task 8 — Wrap the statement pack in the pack_us envelope

- **Description**: Add `pack_statement_backfill(ticker)` — pure I/O orchestration
  mirroring `pack_kpi_topline_backfill` (`pack_us.py:1043`): call the producer, shape
  its return into the standard envelope, and carry the mandatory top-level
  `"source_kind": "xbrl-companyfacts"` literal. A producer error slot rides through
  verbatim with NO `facts` key. No analysis, no filtering, no relabelling here.
- **Module**: `investing-toolkit/skills/data-markets/scripts/pack_us.py`
- **Files touched**: `investing-toolkit/skills/data-markets/scripts/pack_us.py`, `investing-toolkit/tests/data/test_data_markets_us.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/pack_us.py`
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/tests/data/test_data_markets_us.py`
- **Acceptance**:
  - **RED**: `test_data_markets_us.py::test_statement_backfill_envelope_declares_companyfacts_source_kind` fails
  - **GREEN**: the envelope carries `pack`/`ticker`/`fetched_at`/`source_kind`/`company`/`facts`/`coverage`; an error slot passes through with no `facts` key
- **Dependencies**: Task 5 completes first
- **Independent**: true
- **Brief item covered**: §Smallest End State #1 — "A new producer stores, per period, the filer's own us-gaap concepts"
- **Status**: done(e54073a2)

## Task 9 — Drive the pack into the store

- **Description**: Thin driver mirroring `kpi_tw_ingest` (`kpi_tw_ingest.py:74`):
  read a statement-pack envelope, map it via Task 3's pure mapper, and
  `kpi_store.append` every point. Build all points BEFORE the first append so a
  rejected pack writes nothing and leaves no partial state. Fail loud (non-zero
  exit) on a malformed envelope, an untrusted `source_kind`, or a missing `as_of`
  — never a silent swallow. Returns `{company, kpi_ids, appended}`.
- **Module**: `investing-toolkit/skills/analysis-kpi/scripts/kpi_us_statements_ingest.py`
- **Files touched**: `investing-toolkit/skills/analysis-kpi/scripts/kpi_us_statements_ingest.py`, `investing-toolkit/tests/analysis/test_kpi_us_statements_ingest.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-kpi/scripts/kpi_tw_ingest.py`
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-kpi/scripts/kpi_us_statements.py`
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-kpi/scripts/kpi_gate.py`
- **Acceptance**:
  - **RED**: `test_kpi_us_statements_ingest.py::test_rejected_pack_writes_nothing` fails
  - **GREEN**: a valid envelope appends every point and re-ingesting the same envelope is a no-op (dedup key stable); an envelope with an untrusted `source_kind` writes zero points and exits non-zero
- **Dependencies**: Task 3 completes first
- **Independent**: true
- **Brief item covered**: §Smallest End State #1 — "A new producer stores, per period, the filer's own us-gaap concepts for the spine's source concepts"
- **Status**: done(a68df126)

## Task 10 — Document the lane and bump the plugin version

- **Description**: Document the new producer + view in `analysis-kpi/SKILL.md` and
  its CLI reference, state the measured history floor (XBRL begins with the SEC's
  2009-2011 phase-in; median 18 usable years, 0/46 filers ≥20) as an explicit
  capability limit, add the CHANGELOG entry, and bump both plugin manifests in
  lockstep. Test counts in the CHANGELOG are stamped at close-out, not here.
- **Module**: `investing-toolkit/skills/analysis-kpi/SKILL.md`
- **Files touched**: `investing-toolkit/skills/analysis-kpi/SKILL.md`, `investing-toolkit/skills/analysis-kpi/references/cli-reference.md`, `investing-toolkit/CHANGELOG.md`, `investing-toolkit/.claude-plugin/plugin.json`, `investing-toolkit/.codex-plugin/plugin.json`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-kpi/SKILL.md`
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-kpi/references/cli-reference.md`
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/CHANGELOG.md`
- **Acceptance**:
  - **RED**: `python3 scripts/sync_codex_manifests.py --check investing-toolkit`
    exits 1 after only `.claude-plugin/plugin.json` is bumped (and the
    `check-codex-manifest-drift.sh` PostToolUse hook blocks with
    `❌ Codex manifest drift detected`).
    **CORRECTED 2026-07-26 during Task 10** — this line originally pinned
    `.claude/hooks/test_check_codex_manifest_drift.py::test_real_batch_a_plugin_in_sync`,
    which was the orchestrator's error: that test hardcodes `research-toolkit`, so it
    stays green no matter what happens to investing-toolkit's manifests. The
    implementer verified this by bumping one manifest and watching it pass, then
    found the two mechanisms that DO detect the drift. A pinned RED node that cannot
    go red is worse than none — it certifies the check ran.
  - **GREEN**: both manifests carry the same new version, the drift test passes, and SKILL.md documents the two new scripts plus the stated history floor
- **Dependencies**: Tasks 7, 8, 9 complete first
- **Independent**: false
- **Brief item covered**: §Current State Evidence Boundary — "XBRL history begins with the SEC's 2009-2011 phase-in: 0/46 filers have ≥20 usable years; median 18"
- **Status**: done(051be100)

## Notes

### PIN — statement pack envelope (Task 5 produces, Tasks 3 + 9 consume)

Transcribe verbatim; do not paraphrase. This pin is what lets Task 3 run in
parallel with Task 5 instead of waiting on it (the decoupling that worked on the
tearsheet arc).

```
{
  "pack": "statement-backfill",
  "ticker": "<UPPER>",
  "fetched_at": "<iso8601>",
  "source_kind": "xbrl-companyfacts",
  "company": "<entityName>",
  "facts": [
    {
      "concept": "us-gaap:Revenues",       # qname, namespace preserved
      "period_start": "2024-01-01",         # null for an instant
      "period_end": "2024-12-31",
      "period_kind": "duration",            # "duration" | "instant"
      "value": 1234000000.0,
      "unit": "USD",
      "accession": "0000320193-25-000079",
      "filed": "2025-10-31",
      "form": "10-K"
    }
  ],
  "coverage": {"skipped_rows": [ {"type": "...", "old": null, "new": null,
                                  "accessions": ["..."], "reason": "..."} ]}
}
```

Derived point fields (Task 3): `kpi_id` = `concept` verbatim; `as_of` = `filed`;
`source_accession` = `accession`; `source_form` = `form`; `source_cell_ref` =
`concept`; `source_table_id` = `"xbrl:companyfacts-statement"`; `scale` = 1;
`period` = the instant date, or `"<start>/<end>"` for a duration (the store's
dedup discriminator — `kpi_tw._period_fields` precedent).

### PIN — spine field chains (Task 4 consumes; Task 5 fetches their union)

Ordered first-present chains, transcribed from the probe. Order is the
same-period tiebreak, never a per-company winner.

```
revenue              Revenues | RevenuesNetOfInterestExpense |
                     RevenueFromContractWithCustomerExcludingAssessedTax |
                     RevenueFromContractWithCustomerIncludingAssessedTax | SalesRevenueNet
gross_profit         GrossProfit
operating_income     OperatingIncomeLoss
pretax_income        IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest |
                     IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments |
                     IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic
net_income           NetIncomeLoss | ProfitLoss
eps_basic            EarningsPerShareBasic | IncomeLossFromContinuingOperationsPerBasicShare
total_assets         Assets
total_liabilities    Liabilities
total_equity         StockholdersEquity |
                     StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest
cash                 CashAndCashEquivalentsAtCarryingValue |
                     CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | Cash
operating_cash_flow  NetCashProvidedByUsedInOperatingActivities |
                     NetCashProvidedByUsedInOperatingActivitiesContinuingOperations
investing_cash_flow  NetCashProvidedByUsedInInvestingActivities |
                     NetCashProvidedByUsedInInvestingActivitiesContinuingOperations
financing_cash_flow  NetCashProvidedByUsedInFinancingActivities |
                     NetCashProvidedByUsedInFinancingActivitiesContinuingOperations
capex                PaymentsToAcquirePropertyPlantAndEquipment |
                     PaymentsToAcquireProductiveAssets |
                     PaymentsToAcquirePropertyPlantAndEquipmentAndIntangibleAssets
```

Identity components used only by Task 7 (fetched by Task 5, not spine fields):
`TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterests`,
`RedeemableNoncontrollingInterestEquityCarryingAmount`, `MinorityInterest`.

### Kickoff decisions (2026-07-26, pinned before SDD dispatch)

Two implementation forks the sweep found unpinned. Both are two-way doors (read
paths / CLI surface, changeable without touching stored history), so neither was
briefed; they are pinned here so an implementer does not decide them ad hoc.

```
Kickoff decision: kpi_us_statements_ingest CLI shape → `ingest --filing <path>` reading a pack-envelope JSON, one-line JSON summary on stdout, non-zero exit on rejection — verbatim mirror of kpi_tw_ingest.py:146-188
Kickoff decision: how the spine view is invoked → `kpi_spine_view.py derive --dump <path>` (stdin when omitted), so the render pipeline composes as `kpi_store dump | kpi_spine_view derive | tearsheet_format` and tearsheet_format.py stays untouched
```

The plan's one-way-door decisions (qname-as-`kpi_id`, as-reported-not-canonical
storage, annual-only, the 1e-5 tolerance) were all decided and signed off by the
user at the brief stage — recorded in the brief's §Decision and §Resolved at
kickoff. Per `judgment-rubrics.md` §3(c) a documented decision beats re-asking,
so they were NOT re-briefed. The appetite read found no `docs/loom/PRINCIPLES.md`
in this repo; the default (brief every one-way-door hit) was therefore applied to
a set that turned out to be empty of NEW hits — not suppressed.

### Dispatch order

- Wave 1 (all `Independent: true`, disjoint files): Tasks 1, 2, 3, 4.
- Wave 2: Task 5 (after 2), Task 7 (after 4), Task 9 (after 3). Task 9 is
  `Independent: true`; Tasks 5 and 7 are not, because their `Files touched`
  overlap Task 2's and Task 4's respectively.
- Wave 3: Task 6 (after 5) and Task 8 (after 5). Task 8 is `Independent: true`;
  Task 6 stays `false` because it edits `sec_edgar_client.py`, which Task 2 (a
  declared-independent task) also edits.
- Wave 4: Task 10.
- Critical path: 2 → 5 → 8 → 10 = depth 4.

## Decision Log

1. chose to have the orchestrator commit each task in a parallel wave, rather than each worker committing its own — cost-of-change: the day a wave runs in isolated worktrees instead of one shared checkout, this choice costs rewriting the wave's commit step, but it is what stops four concurrent workers racing on one git index and sweeping each other's half-written files into a commit
2. chose to let the two revenue lanes resolve a double-tagged period differently — the per-filing lane picks the company's own total, the backfill lane skips — because only the per-filing lane can see the two tags in their reported context, so only it has grounds to pick — cost-of-change: the day someone wants one stated policy across both lanes, this choice costs a coordinated edit to both plus a re-run of the backfill, and until then the asymmetry is written into both docstrings so it reads as designed rather than accidental

### Post-PASS amendment note (re-review skipped, per SKILL.md §Self-review)

After `plan-document-reviewer` returned PASS (14/14, 2026-07-26 03:44) the plan
was amended in four additive, schema-safe ways: the verdict was stamped; Task
10's RED was pinned to the exact existing node
`.claude/hooks/test_check_codex_manifest_drift.py::test_real_batch_a_plugin_in_sync`
(reviewer note 2); the two Kickoff decisions above were appended; and Tasks 8 and
9 were flipped to `Independent: true` (reviewer note 1, Check-15 advisory).

Check 14 re-verified BY HAND for the flip, since that is the check the flip could
break — every pair of `Independent: true` tasks {1, 2, 3, 4, 8, 9} has a disjoint
`Files touched` set: T1 {capture script, probe fixture, probe test} / T2
{sec_edgar_client.py, test_sec_edgar_top_line.py} / T3 {kpi_us_statements.py,
its test} / T4 {kpi_spine_view.py, its test} / T8 {pack_us.py,
test_data_markets_us.py} / T9 {kpi_us_statements_ingest.py, its test}. Tasks 6
and 7 were deliberately NOT flipped despite the reviewer's advisory: T6 edits
`sec_edgar_client.py` (shared with T2) and T7 edits `kpi_spine_view.py` (shared
with T4), so flipping either would violate Check 14. No task's Dependencies,
Module, RED/GREEN semantics, or DAG structure changed.

### Deferred to close-out, not to a follow-up

A live end-to-end dogfood — real producers into the real store, per filer, reading
what actually LANDS rather than the driver's printed summary — is **not** a plan
task because it is `finishing-a-development-branch`'s verification step, and this
repo has measured that it finds what the suite cannot
(`docs/loom/memory/a-data-probe-is-not-a-pipeline-dogfood.md`). It must run before
the PR, over ≥5 filers spanning a concept switch (MSFT/AAPL), a never-tags-total
filer (WMT), a financial (JPM), and the mezzanine case (TSLA).

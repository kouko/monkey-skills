# Plan: TW-market kpi_store producer

Source brief: docs/loom/specs/2026-07-25-tw-kpi-store-producer.md
Total tasks: 5
Critical-path depth: 4 (≤5)
Execution order: parallel-where-possible (T1→T2→T3 chain, then T4+T5 parallel)
Plan-document-reviewer verdict: PASS (2026-07-25, round 1 — 14/14 checks)

## Kickoff

Kickoff sweep (2026-07-25): NO one-way-door decisions — producer-only arc
mirroring the shipped US producer; all design calls resolved and reversible
(kpi_id=concept+basis pinned, as_of from the authorisation-for-issue fact
resolved by probe, store/tearsheet unchanged). No researchable fork open.
Nothing to brief. Execution: T1→T2→T3 sequential (T1/T2 share kpi_tw.py),
then T4 (dogfood) + T5 (version) as one parallel wave.

## Decision Log

- **T2 corrected the PIN point schema (2026-07-25, checkable-fact, not a user
  decision):** the plan PIN omitted `period`, but `kpi_store.py:173`'s dedup
  5-tuple keys on it — without a distinct `period` per comparative, all of a
  filing's prior-period vintages collapse to one dedup key and are silently
  dropped. The implementer added `period` (instant date, or start/end) and tested
  dedup-key distinctness; the US `kpi_xbrl.py:532` sets it too. Settled by reading
  the store code, PIN corrected.
- **T2 kpi_id keys on the CANONICAL field-slug, not the raw concept (2026-07-25,
  design correction — impl's choice is better than the original PIN):** the PIN
  said `concept-slug`; the impl uses the canonical field name (`revenue`, not
  `ifrs-full:Revenue`). This is MORE correct and load-bearing for TW: financial
  families book the same economic item under DIFFERENT concepts (the
  first-present-fallback lesson), so keying the durable kpi_id on the raw concept
  would split one company's revenue into different series across concept/taxonomy
  variation and block cross-company comparison. The canonical field name is the
  normalized identity the canonical layer exists to provide. PIN corrected to
  `<canonical-field-slug>`.
- **T2 scope calls (agent-decided, two-way door):** mirrored the injective
  collision guard rather than importing it (the US guard is inline in `ingest_pack`,
  not an importable callable; plan permits mirroring, stdlib-only kept). Allowlist
  emits the task's named KPI set, excludes `ebit` (alias of operating_income) and
  `total_debt` (derived, not in the list) — both tested absent.
- **T3 finding — the ingest consumes an ENVELOPE the pipeline doesn't yet emit
  (2026-07-25, two-way door, scope kept as producer-only):** `run_pipeline` emits
  `canonical + notes + _meta` but NOT `facts` (twse_ixbrl.py:156), and the `as_of`
  authorisation date lives in a fact. So the ingest input is a filing envelope
  (canonical + facts + coords) the caller assembles. This arc keeps producer-only
  scope: T4's dogfood assembles the envelope (parse facts + canonical) to prove the
  producer works end-to-end. The **glue-free production path** — a `pack_tw` verb
  emitting the envelope, mirroring `pack_us.pack_kpi_quarterly` — is a BACKLOG
  follow-up (this arc ships the producer + a proven dogfood, not yet the US's
  "ticker→tearsheet without glue"). Late-vetoable: if glue-free-now is wanted, add
  a data-markets envelope task.

## Notes

- **Producer-only arc**: `kpi_store.py` + `report-kpi-tearsheet` are fully
  market-agnostic (recon-verified) — NO store/tearsheet code change. A TW point
  with the same schema renders in the existing tearsheet untouched.
- **as_of source RESOLVED (probe 2026-07-25)**: the TW iXBRL itself carries
  `tifrs-notes:DateAndProceduresOfAuthorisationForIssueOfFinancialStatements`
  (財報經授權發布日 = board authorisation-for-issue date) — a nonNumeric fact
  present in the 1101 fixture. Extract + parse the date out of its value (the
  value may carry procedure text after the date). Deterministic, non-wall-clock,
  already-fetched — no new fetch. This satisfies the store's accession-derived
  `as_of` guard. (Do NOT use a wall-clock date; the store rejects it.)
- **PIN — TW kpi_id**: `<canonical-field-slug>` optionally suffixed `__basis-<C|A>` where
  C=合併(consolidated)/A=個體(parent-only), report_id per `twse_ixbrl.py:118`.
  TW has NO us-gaap dimensional axes → basis is the only discriminator; it
  substitutes for the US `axis=member` signature. REUSE the US injective
  fail-loud collision guard ([[derived-durable-id-slug-is-a-lossy-one-way-door]]:
  key the guard on the consumer's normalized id, fail loud on real collision).
- **PIN — point schema (from `kpi_xbrl.py:526-564`, market-agnostic fields)**:
  `company, kpi_id, period, period_start, period_end, period_kind(instant|duration),
  scale=1, value, as_of, source_accession, source_form, source_table_id="tw:ixbrl",
  source_cell_ref(=concept), source_kind`. TW `raw_value` is already base-scaled
  (`twse_ixbrl_parser.py:161`) → `scale=1`, value=raw_value.
  **`period` is REQUIRED (corrected 2026-07-25, T2)**: kpi_store's write-side dedup
  5-tuple (`kpi_store.py:173`) keys on `point["period"]` — a filing carries 2–3
  comparative periods per field sharing one accession+as_of, so omitting a distinct
  `period` collapses them to one dedup key and silently drops every prior-period
  vintage (the exact loss the store exists to prevent). Derive `period` = the
  instant date, or `start/end`, so each comparative has a distinct dedup key.
- **US-coupled pieces NOT reused** (invert/replace for TW): empty-dims skip
  (`kpi_xbrl_ingest.py:151-153` — US drops flat totals; TW keeps them),
  `source_form` from dei focus (US-only; TW form = a TW value e.g. "TIFRS-Q"),
  `classify_fact_period` edgartools label group (TW maps period from the parser's
  `period{instant|duration}` directly).
- **Store reuse discipline**: reuse `kpi_store.append` as-is; do NOT reuse
  data-markets `cache_util` and do NOT cross the analysis↔data-markets import
  boundary ([[durable-store-mirrors-cache-util-not-imports-it]]).
- **Cadence**: `_qtrs=round(days/91.3125)` (`kpi_store.py:222-246`) already fits
  TW quarterly (1..4) AND 興櫃 semiannual (6-mo→2); no new period_kind. Producer
  stays 興櫃-ready by emitting the honest duration; 興櫃 FETCH stays out of scope.
- Test command: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest investing-toolkit/tests/`
  (1005 offline-passing at branch base 560ad435; 18 live-network failures pre-existing).
- New module lives beside the US producer: `investing-toolkit/skills/analysis-kpi/scripts/`.

## Task 1 — TW authorisation-for-issue date extractor (as_of source)

- Description: Add `extract_tw_authorisation_date(facts)` to a new
  `analysis-kpi/scripts/kpi_tw.py` — find the
  `tifrs-notes:DateAndProceduresOfAuthorisationForIssueOfFinancialStatements`
  fact and parse an ISO date out of its (possibly procedure-text-carrying) value;
  return None if absent. This date is the `as_of` for TW points (non-wall-clock,
  accession-adjacent).
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_tw.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_tw.py, investing-toolkit/tests/analysis/test_kpi_tw.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/twse_ixbrl_parser.py (fact shape: concept/raw_value/period)
  - investing-toolkit/tests/data/fixtures/twse_ixbrl_1101_2026Q1_C.html (carries the auth-date fact)
- Acceptance:
  - RED: `test_extract_tw_authorisation_date` does not exist (collection = 0)
  - GREEN: it passes — 1101 fixture facts → the parsed authorisation date (an ISO date string); a fact-set without the concept → None; full offline suite green
- External surfaces: none (parses already-decoded facts; stdlib date parsing)
- Dependencies: none
- Independent: false
- Brief item covered: "Captures a MOPS disclosure date for `as_of` … the load-bearing prerequisite" (Smallest End State)

## Task 2 — TW canonical → points (kpi_id + point mapping)

- Description: Add `tw_canonical_to_points(canonical, basis, as_of, provenance)`
  to `kpi_tw.py` — for each KPI-worthy canonical concept, derive a TW kpi_id
  = `concept-slug[__basis-<C|A>]` (reusing the US injective collision guard,
  imported or mirrored per the layer-boundary rule) and build a point dict per
  the PIN schema (period_start/end/kind from the fact's period, value=raw_value,
  scale=1, source_* provenance, as_of from Task 1). Keep flat totals (invert the
  US empty-dims skip).
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_tw.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_tw.py, investing-toolkit/tests/analysis/test_kpi_tw.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl_ingest.py (derive_kpi_id + injective guard :85-185, to reuse/mirror)
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py (point schema :526-564)
  - investing-toolkit/skills/data-markets/scripts/twse_ixbrl_canonical.py (canonical KPI fields :56-81)
- Acceptance:
  - RED: `test_tw_canonical_to_points` does not exist (collection = 0)
  - GREEN: it passes — a real 1101 canonical + basis "C" + as_of → points with correct `concept__basis-C` kpi_ids, period_start/end/kind, value, scale=1, source_table_id="tw:ixbrl"; a C-and-A pair yields DISTINCT kpi_ids (no collision/merge); full offline suite green
- External surfaces: none (pure in-memory transform, stdlib only)
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "Derives a TW kpi_id … Maps each fact's period directly to the point schema … synthesizes TW provenance" (Smallest End State)

## Task 3 — TW ingest entry → kpi_store.append

- Description: Add `analysis-kpi/scripts/kpi_tw_ingest.py` with an `ingest`
  entry that reads a TW canonical (twse_ixbrl / pack_tw memo-fetch shape) for one
  filing, calls `tw_canonical_to_points`, and appends each point to the UNCHANGED
  `kpi_store` (reuse `kpi_store.append`; do NOT reuse data-markets cache_util /
  cross the layer boundary). Idempotent append-only; running it over N filings
  builds the cross-period series. Declare the new verb in the command surface.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_tw_ingest.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_tw_ingest.py, investing-toolkit/tests/analysis/test_kpi_tw_ingest.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl_ingest.py (the US ingest entry to mirror :203)
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py (append :135-170 — reuse unchanged)
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_tw.py (Task 1+2 helpers)
- Acceptance:
  - RED: `test_kpi_tw_ingest_appends_points` does not exist (collection = 0)
  - GREEN: it passes — ingesting a 1101 canonical into a temp store writes the expected TW points (readable via `kpi_store.dump_company`); a second ingest of the same filing is idempotent (no duplicate points, dedup on the 5-tuple); the `ingest` verb is declared in the command surface and runs; full offline suite green
- External surfaces: filesystem (durable store under XDG_DATA_HOME via kpi_store — reused, not new); no network in the unit test (fixture canonical)
- Dependencies: Task 2 completes first
- Independent: false
- Brief item covered: "a TW analog of `kpi_xbrl_ingest ingest` that … appends to the unchanged `kpi_store`" (Smallest End State)

## Task 4 — live e2e dogfood + tearsheet render + doc line

- Description: Live dogfood — fetch 2–3 periods of one real TW ticker (2330 台積電)
  via the existing pipeline, ingest each through `kpi_tw_ingest`, and verify the
  UNCHANGED `report-kpi-tearsheet` renders the multi-period TW series (periods as
  columns, TWD unit, values correct). Add ONE "See also" / applicability line to
  `report-kpi-tearsheet/SKILL.md` naming TW as a supported producer. Any render
  failure or wrong value is a surfaced finding routed back to Tasks 1–3.
- Module: investing-toolkit/skills/report-kpi-tearsheet
- Files touched: investing-toolkit/skills/report-kpi-tearsheet/SKILL.md (one doc line; dogfood artifacts land in scratchpad, not the repo)
- Context paths:
  - investing-toolkit/skills/report-kpi-tearsheet/scripts/tearsheet_format.py (render path, read-only)
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_tw_ingest.py (Task 3)
- Acceptance:
  - RED: baseline — no TW ticker renders in report-kpi-tearsheet (the store has no TW series)
  - GREEN: after ingesting ≥2 periods of 2330, `report-kpi-tearsheet` renders a multi-period TWD tearsheet with correct values; SKILL.md names TW
- External surfaces: live TWSE MOPS fetch (network; verification run, no repo writes beyond the doc line)
- Dependencies: Task 3 completes first
- Independent: true
- Brief item covered: "the existing `report-kpi-tearsheet` renders TW KPIs with no store/tearsheet code change … One See also line" (Smallest End State / Decision)

## Task 5 — version bump + manifest sync + BACKLOG + CHANGELOG

- Description: Bump investing-toolkit 2.34.0 → 2.35.0 (new capability = minor) in
  `.claude-plugin/plugin.json`; mirror codex via
  `python3 scripts/sync_codex_manifests.py investing-toolkit`; CHANGELOG entry
  (TW KPI store producer — ticker→XBRL→durable store→tearsheet, producer-only,
  as_of from authorisation-for-issue date, 興櫃-ready via existing `_qtrs`); note
  in BACKLOG that the TW KPI producer shipped and the 興櫃 multi-period arc now
  only needs 興櫃 fetch.
- Module: investing-toolkit/.claude-plugin/plugin.json (coordination anchor)
- Files touched: investing-toolkit/.claude-plugin/plugin.json, investing-toolkit/.codex-plugin/plugin.json (via sync script only), investing-toolkit/CHANGELOG.md, docs/loom/BACKLOG.md
- Context paths:
  - scripts/sync_codex_manifests.py
  - investing-toolkit/CHANGELOG.md, docs/loom/BACKLOG.md
- Acceptance:
  - RED: `grep -m1 version investing-toolkit/.claude-plugin/plugin.json` → 2.34.0 today
  - GREEN: version reads 2.35.0; sync `--check` clean (no diff on re-run); CHANGELOG entry present; BACKLOG updated
- External surfaces: none (repo metadata; codex via committed sync script)
- Dependencies: Task 3 completes first
- Independent: true
- Brief item covered: ship step for the Decision (surface the TW KPI producer)

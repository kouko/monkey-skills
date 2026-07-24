# Plan: US XBRL → kpi_store producer (dimensional revenue)

Source brief: docs/loom/specs/2026-07-24-kpi-xbrl-store-producer.md
Total tasks: 7
Critical-path depth: 5 (≤5) — 1→2→3→{4,5a,5b}→6 (all three mid-tasks are one level)
Execution order: parallel-where-possible (Tasks 4, 5a, 5b are one level)
Plan-document-reviewer verdict: PASS (2026-07-24, round 2 — 12/14 checks, 2 N/A)

## Notes

- **Version coordination**: another session's PR #610 targets 2.33.0 (per repo
  memory). This arc's version bump (Task 6) must pick the NEXT available minor
  relative to whatever is on `origin/main` AT CLOSE-OUT — do not hardcode 2.33.0
  here; finishing-a-development-branch resolves the exact number.
- **Anti-fixture-fabrication** (memory `hand-authored-fixture-is-a-fabrication-risk`,
  `fixtures-mirror-producer-shape`): Task 1 and Task 4 fixtures must be CAPTURED
  from the real extractor's output shape (or a real small fetch), never hand-typed;
  never use a December-FYE-only fixture (December is the one FYE where calendar-year
  logic accidentally works, hiding the calendar-vs-fiscal trap).
- **kpi_xbrl purity preserved**: the store-feed (Task 3) is a NEW thin driver that
  imports `kpi_xbrl` (pure) + `kpi_store`; `kpi_xbrl.py` itself stays pure-compute
  (no durable dir, no network) — do not add a store-writing subcommand inside it.
- **No collapse** (brief Axis-4 decision): the store-feed uses the non-collapsing
  `facts_to_points`, NOT `resolve_binding`/`_restatement_survivor` — each vintage
  is appended so the store's `†` has ≥2 vintages to disagree on.

Kickoff decision: XBRL-ingest KPI naming → mechanical, fully automatic. `kpi_id`
  is derived deterministically AND injectively from the full dimensional signature
  (concept + sorted axis:member local-names, `Member`/`Axis` suffixes stripped,
  lowercased) — readable yet signature-faithful (memory `match-kpi-on-full-
  dimensional-signature-not-one-axis`). No human/LLM slug step. A display-alias
  layer is OUT of scope (a future two-way-door that never touches the durable key).
  (User-confirmed one-way-door decision, 2026-07-24; no PRINCIPLES.md → default-brief.)

Amendment note (post-PASS): Task 3 acceptance tightened to encode the mechanical
  `kpi_id` derivation above. Additive + schema-safe (no field/DAG/dependency change;
  all required fields intact) → plan-document-reviewer re-run skipped per
  writing-plans §"Amending a PASS plan".

## Decision Log

Two-way-door decisions (reversible; recorded, not briefed — kickoff §e):

- **Store-feed lives in a NEW driver script, not a `kpi_xbrl` subcommand** — preserves
  `kpi_xbrl.py`'s documented pure-compute contract (no durable dir, no network). The
  driver imports `kpi_xbrl` (pure) + `kpi_store`, mirroring the prose lane's
  `commit_to_store`. Reversible: could later fold into a subcommand if purity is relaxed.
- **`ingest` consumes a PRE-FETCHED pack (`--pack PATH`), not a `--ticker`** — the
  network fetch stays in data-markets (`pack.py --pack kpi-quarterly`). Reversible: a
  `--ticker` convenience wrapper can be added later without changing the store contract.
- **Version number resolved at close-out** (see Notes; #610 also targets 2.33.0).

Kickoff (one-way-door) decisions land here once resolved, in the pinned
`Kickoff decision: <fork> → <resolution>` format (grep key SDD reads).

## Task 1 — data-markets: emit `period_start` on the dimensional fact
- Description: In `_build_dimensional_revenue_fact`, add `period_start` to the
  emitted fact dict, re-sourced from the raw XBRL duration context already read
  at extract time (the start date `_duration_span_days` consumes) — currently
  dropped. Instant facts carry `period_start = None`; duration facts carry the
  real start. Additive only; do not alter existing emitted fields.
- Module: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
- Files touched: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py, investing-toolkit/tests/data/test_sec_edgar_dimensional.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py  (`_build_dimensional_revenue_fact` :2837-2958, dict :2931-2939; `_duration_span_days` :2391)
- Acceptance:
  - RED: `test_dimensional_fact_carries_period_start` — a duration revenue fact emits `period_start` equal to its raw context start date; an instant fact emits `period_start = None`. Fixture mirrors the real extractor shape (NOT hand-typed, NOT December-FYE-only).
  - GREEN: emitted fact dict contains `period_start`; existing dimensional-extraction tests stay green.
- External surfaces: SEC XBRL fact shape (edgartools) — reads an existing raw field, emits it; no new external dependency.
- Dependencies: none
- Independent: false
- Brief item covered: Smallest End State #1 "Emit `period_start` on the extracted fact — re-source from the raw XBRL duration context".

## Task 2 — kpi_xbrl: emit store period-identity fields on the point
- Description: In `facts_to_points`, add three fields to each emitted point so it
  is store-shaped: `period_start` (pass through from the fact, default None),
  `period_kind` (synthesize `"duration"` / `"instant"` from the existing
  `duration_class`/`period_type` already on the point), and `scale` (hardcoded
  `1` — XBRL values are base, matching the prose lane's rationale). Additive to
  the point dict; do not remove `period_type`/`duration_class`/`calendar_*`.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py, investing-toolkit/tests/analysis/test_kpi_xbrl.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py  (`facts_to_points` :490-568, point dict :526-548)
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_prose_candidates.py  (:695,705-707 — the shape to mirror)
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py  (`_qtrs` :222-247, `same_period` :249-291 — the consumer that reads these fields)
- Acceptance:
  - RED: `test_facts_to_points_emits_store_period_identity` — given a fact carrying `period_start`, the produced point carries `period_start` (passthrough), `period_kind` correct (`duration` for a duration fact, `instant` for an instant), and `scale == 1`.
  - GREEN: two vintages of one annual period (same `period_end`, differing values, differing accession) each produce a point on which `kpi_store.same_period` returns True (they group) — proving the fields unblock grouping.
- External surfaces: none (pure internal logic over the fact dict).
- Dependencies: Task 1 completes first  (needs `fact["period_start"]` to pass through)
- Independent: false
- Brief item covered: Smallest End State #2 "synthesize `period_kind`" + #3 "`scale=1`" + the #1 passthrough into the point.

## Task 3 — store-feed driver: append each vintage (no collapse)
- Description: Add a NEW thin driver script that, given a fetched dimensional
  fact-pack (the `pack_us.pack_kpi_quarterly` shape), maps each dimensional
  signature to a `kpi_id` and appends EVERY fact's vintage as a store point via
  `kpi_store.append`, using the non-collapsing `facts_to_points` (NOT
  `resolve_binding`). Imports `kpi_xbrl` (pure) + `kpi_store`; keeps `kpi_xbrl.py`
  itself pure. Exposes an `ingest` CLI verb (`--pack PATH`, honoring
  `KPI_STORE_DIR`). The verb must be runnable (`--help` works, verb listed).
  **`kpi_id` derivation (Kickoff decision — see Notes):** derive it deterministically
  AND injectively from the full dimensional signature (concept + sorted axis:member
  local-names, `Member`/`Axis` suffixes stripped, lowercased) — never a human slug,
  never a single-axis key (memory `match-kpi-on-full-dimensional-signature-not-one-axis`:
  an empty signature = the top-level total, out of scope this arc; each distinct
  signature = a distinct KPI). No display-alias layer in this arc.
- Module: investing-toolkit/skills/analysis-kpi/scripts/ (new driver script, e.g. `kpi_xbrl_ingest.py`)
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl_ingest.py, investing-toolkit/tests/analysis/test_kpi_xbrl_ingest.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py  (`facts_to_points` — the non-collapsing mapper)
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py  (`append` :303-361; provenance guard :138-147)
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_prose_candidates.py  (`commit_to_store` :749-753 — the intra-skill append pattern to mirror)
  - investing-toolkit/skills/data-markets/scripts/pack_us.py  (`pack_kpi_quarterly` :957-1036 — input pack shape)
- Acceptance:
  - RED: `test_ingest_appends_each_vintage` — given a 2-vintage pack (one dimensional signature, same period_end, two accessions, differing values), `ingest` appends 2 store points under one `kpi_id`; a `kpi_store dump --company` shows both vintages (no collapse). Store isolated via `KPI_STORE_DIR` tmp.
  - RED: `test_ingest_kpi_id_derivation` — two DISTINCT dimensional signatures produce DISTINCT `kpi_id`s (injective); the SAME signature across two vintages produces the SAME `kpi_id` (so they group); the derived id is a readable slug from the stripped member local-name(s), not a human-authored string.
  - GREEN: the `ingest` verb runs end-to-end and is declared in the command surface (listed in `--help`; documented in Task 5); the durable store is untouched (writes only under `KPI_STORE_DIR`).
- External surfaces: filesystem (durable store dir via `KPI_STORE_DIR`) — reuses `kpi_store`'s own atomic-write + locking; no new external dependency.
- Dependencies: Task 2 completes first  (points must carry the store period-identity fields)
- Independent: false
- Brief item covered: Smallest End State #4 "A store-feed path ... appends each vintage via `kpi_store.append` ... non-collapsing `facts_to_points`, NOT the collapsing `resolve_binding`".

## Task 4 — e2e seam probe: pack → ingest → tearsheet renders `†`
- Description: Add an integration test that drives REAL data across the whole
  seam — a captured dimensional pack for a known restatement filer (INTC-shaped,
  ≥2 vintages of one segment) → `ingest` → `kpi_store dump` →
  `tearsheet_format.py` → assert the restated cell carries `†` and a `## Revisions`
  block lists both vintages. This is the cross-module behavioral probe (memory
  `cross-module-field-contracts-execute-probes`): it asserts on values that cross
  every module boundary, not on any single module. Read-only on the formatter.
- Module: investing-toolkit/tests/analysis/ (new integration test)
- Files touched: investing-toolkit/tests/analysis/test_kpi_xbrl_to_tearsheet_e2e.py, investing-toolkit/tests/analysis/fixtures/ (captured pack fixture)
- Context paths:
  - investing-toolkit/skills/report-kpi-tearsheet/scripts/tearsheet_format.py  (`--in`/`--as-of`/`--store-dir`/`--out`; `†` + Revisions)
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py  (`dump` subcommand)
- Acceptance:
  - RED: `test_xbrl_to_tearsheet_e2e_restatement` — the full chain renders a tearsheet whose restated period cell ends with `†` and whose `## Revisions` section lists ≥2 vintages (value + as_of + accession). Fixture captured from real extractor shape, restatement filer (NOT December-FYE-only, NOT hand-typed).
  - GREEN: the assertion passes end-to-end; no change to `tearsheet_format.py` or store read-logic.
- External surfaces: none (test-only; consumes shipped scripts via subprocess/import).
- Dependencies: Task 3 completes first
- Independent: true   # disjoint files from Task 5 (tests vs SKILL docs), no semantic dependency
- Brief item covered: Smallest End State — "The EXISTING tearsheet then renders" + Decision "restatements ... never collapsed — the store's bitemporal `†` needs ≥2 differing vintages".

## Task 5a — analysis-kpi SKILL + cli-reference wiring (ingest verb + workflow)
- Description: Document the runnable workflow so it is not tribal: in
  `analysis-kpi/SKILL.md` + `analysis-kpi/references/cli-reference.md`, add the
  `ingest` verb (flags, exit codes, worked example) and a "US XBRL → tearsheet"
  workflow section (pack fetch via data-markets `--pack kpi-quarterly` → `ingest`
  → `report-kpi-tearsheet`). Doc-mirrors-code, one skill (analysis-kpi).
- Module: investing-toolkit/skills/analysis-kpi
- Files touched: investing-toolkit/skills/analysis-kpi/SKILL.md, investing-toolkit/skills/analysis-kpi/references/cli-reference.md
- Context paths:
  - investing-toolkit/skills/analysis-kpi/references/cli-reference.md  (existing per-subcommand format to match)
- Acceptance:
  - RED: `test_ingest_cli_documented` (or a grep-based doc-consistency check) — the `ingest` verb's documented flags in `cli-reference.md` match the script's actual `--help` flag set; the "US XBRL → tearsheet" workflow section exists and names the three steps in order.
  - GREEN: docs and CLI agree; skill-folder structure hook stays green; no nested subfolder introduced.
- External surfaces: none (documentation).
- Dependencies: Task 3 completes first  (doc-mirrors-code: the verb must exist)
- Independent: true   # disjoint files from Task 4 (tests) and Task 5b (a different skill), no semantic dependency
- Brief item covered: Smallest End State #5 "SKILL wiring — document the ticker→tearsheet workflow ... runnable, not tribal".

## Task 5b — report-kpi-tearsheet SKILL pointer (XBRL as a supported feed)
- Description: Add a one-line pointer in `report-kpi-tearsheet/SKILL.md` naming
  XBRL (via analysis-kpi `ingest`) as a supported store feed alongside the
  prose/8-K lanes. Doc-mirrors-code, one skill (report-kpi-tearsheet).
- Module: investing-toolkit/skills/report-kpi-tearsheet
- Files touched: investing-toolkit/skills/report-kpi-tearsheet/SKILL.md
- Context paths:
  - investing-toolkit/skills/report-kpi-tearsheet/SKILL.md  (existing read-workflow)
- Acceptance:
  - RED: `test_tearsheet_skill_names_xbrl_feed` (or a grep-based check) — `report-kpi-tearsheet/SKILL.md` names the XBRL `ingest` feed.
  - GREEN: the pointer is present; skill-folder structure hook stays green.
- External surfaces: none (documentation).
- Dependencies: Task 3 completes first  (doc-mirrors-code: the verb must exist)
- Independent: true   # disjoint file from Task 4 (tests) and Task 5a (a different skill), no semantic dependency
- Brief item covered: Smallest End State #5 "SKILL wiring — document the ticker→tearsheet workflow ... runnable, not tribal".

## Task 6 — version bump + CHANGELOG
- Description: Bump `investing-toolkit/.claude-plugin/plugin.json` to the next
  available minor (see Notes — resolve at close-out relative to origin/main; a
  new producer feature = minor) and add a CHANGELOG entry naming the XBRL→store
  producer + the ticker→tearsheet workflow. Stamp the final suite test count at
  close-out (memory `stamp-changelog-test-counts-at-closeout`).
- Module: investing-toolkit/.claude-plugin/plugin.json  (version + its atomic CHANGELOG co-edit)
- Files touched: investing-toolkit/.claude-plugin/plugin.json, investing-toolkit/CHANGELOG.md
- Context paths:
  - investing-toolkit/CHANGELOG.md  (existing entry format)
  - investing-toolkit/.claude-plugin/plugin.json  (version field)
- Acceptance:
  - RED: `test_plugin_version_matches_changelog` (or the repo's existing version/CHANGELOG sync check) — plugin.json version equals the newest CHANGELOG heading and is strictly greater than the previous.
  - GREEN: version bumped, CHANGELOG entry present with the final test count; marketplace/version sync check green.
- External surfaces: none (config + docs).
- Dependencies: Tasks 4, 5a, 5b complete first
- Independent: false
- Brief item covered: shipping requirement (repo convention: a skill-content PR bumps the plugin version; feature → minor).

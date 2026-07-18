# Plan: memo 接線 — quarterly KPI series → report-equity-memo → investing-team

Source brief: docs/loom/specs/2026-07-18-memo-quarterly-kpi-wiring.md
Total tasks: 8
Critical-path depth: 4 (≤5) — T2 → T3 → T7 → T6
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-18, 14/14)

Change-folder binding: none — explicit brief handoff (Layer 0; detection not run).
The one non-archived change-folder `docs/loom/2026-07-12-us-sec-primary-source-layer/`
belongs to the already-shipped US SEC arc (housekeeping note surfaced to user).

## Design rulings baked into this plan (from brief + code recon)

- **memo-feed contract gap (verified in code)**: `kpi_memo_feed.py` v1.0 is
  tier-①-shaped — per-point provenance triple `source_accession`/`source_table_id`/
  `source_cell_ref` (kpi_memo_feed.py:77-79) and a store-based trust gate
  `kpi_gate.is_trusted` (kpi_memo_feed.py:112). Quarterly XBRL points (accession(s)
  + concept; derived points carry PLURAL `source_accessions`/`source_forms`,
  kpi_xbrl.py:928-957) cannot ride v1.0: they'd be refused or blanket-WITHHELD.
  → T3 adds a **quarterly/XBRL arm** with its own fail-closed provenance rule;
  envelope `_memo_feed_schema_version` bumps 1.0→1.1 (no existing consumers —
  the module is unconsumed today).
- **XBRL lane trust ≠ store gate**: the quarterly arm does NOT call
  `kpi_gate.is_trusted` (that gate covers the tier-① append-only store lane).
  Its fail-closed guarantees are: per-point XBRL provenance completeness,
  `assert_dqc_schema` on every flag, and verbatim passthrough of
  `coverage_flags` + derived-lane markers. Documented in the module docstring (T3).
- **Derived-Q4 policy (user-ratified, brief §Decision)**: include-and-tag per cell;
  <4 reported quarters → appendix-only; US-only slice.
- **Binding scope for first run (brief Open Q2, planner ruling)**: the quarterly
  CLI builds series for the full-dimensional-signature groups present in the
  fact-pack (per `docs/loom/memory/match-kpi-on-full-dimensional-signature-not-one-axis.md`);
  no per-ticker binding config this slice.

## Task 1 — data-markets: new `kpi-quarterly` pack type

- Description: Add `--pack kpi-quarterly` to the pack facade: US market only,
  calls `extract_dimensional_revenue` (sec_edgar_client.py:2568) for `--ticker`,
  emits the fact-pack JSON (facts[] + per-accession fiscal_calendars + `_status`
  envelope) and a matching schema file; non-US ticker → `_status.status =
  "usage_error"` refusal (no silent skip).
- Module: investing-toolkit data-markets (pack layer)
- Files touched: investing-toolkit/skills/data-markets/scripts/pack.py,
  investing-toolkit/skills/data-markets/scripts/pack_us.py,
  investing-toolkit/skills/data-markets/schemas/us-schema-kpi-quarterly.json,
  investing-toolkit/tests/data/test_pack_facade.py,
  investing-toolkit/tests/data/test_pack_schemas.py,
  investing-toolkit/tests/data/test_data_markets_us.py,  # entailed: SUPPORTED_PACKS migration-contract pin
  investing-toolkit/tests/data/fixtures/data-us-kpi-quarterly-sample.json
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py (extractor + its test fixtures' shape)
  - investing-toolkit/skills/data-markets/schemas/us-schema-memo-fetch.json (schema convention)
  - investing-toolkit/tests/data/fixtures/xbrl_quarterly_msft.json (fact shape)
- Acceptance:
  - RED: new test in test_pack_facade.py — `kpi-quarterly` pack for a US ticker
    (offline, extractor stubbed/fixture-fed) returns the fact-pack keys and
    `_status.status == "ok"`; a `.TW` ticker returns `usage_error`. Fails now:
    pack.py rejects the unknown pack type.
  - GREEN: both assertions pass; test_pack_schemas.py validates the new schema file.
- External surfaces: SEC EDGAR via the existing `extract_dimensional_revenue`
  client path only — no new HTTP surface; offline tests stub it (repo convention:
  requests/edgar stubbed in sys.modules pre-import).
- Dependencies: none
- Independent: true
- Brief item covered: "Fetch step … a callable path that produces the
  dimensional-revenue fact-pack JSON for one ticker" (Smallest End State 1).

## Task 2 — analysis-kpi: `quarterly-series` CLI on kpi_xbrl

- Description: Add a `quarterly-series` subcommand to kpi_xbrl.py's CLI (today
  `build` only, kpi_xbrl.py:1327-1340): input = fact-pack JSON path; per
  full-dimensional-signature group it runs classification → `build_series_with_break`
  (granularity="quarterly", facts passed for coverage flags) → `derive_q4_points`;
  output = one series JSON: `{series: [{signature, points, derived_points, gaps}],
  coverage_flags}` with parallel calendar/fiscal labels intact on every point.
- Module: investing-toolkit analysis-kpi (kpi_xbrl CLI)
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py,
  investing-toolkit/tests/analysis/test_kpi_xbrl.py
- Context paths:
  - investing-toolkit/tests/analysis/fixtures/xbrl_quarterly_nvda_factpack.json
  - investing-toolkit/tests/analysis/fixtures/xbrl_q4_derive.json
  - investing-toolkit/tests/analysis/test_kpi_xbrl_quarterly_e2e.py (existing seam conventions)
- Acceptance:
  - RED: new CLI test in test_kpi_xbrl.py — run `quarterly-series` on an existing
    quarterly fixture; assert output carries a derived point with `derived: True`
    + plural `source_accessions`, and every point has the calendar pair. Fails now:
    subcommand does not exist (argparse exits 2).
  - GREEN: assertions pass; no change to any library function's behavior
    (existing suite stays green).
- Dependencies: none
- Independent: true
- Brief item covered: "CLI-expose the quarterly series build" (Smallest End
  State 2 — the series-production half).

## Task 3 — analysis-kpi: kpi_memo_feed quarterly/XBRL arm (schema 1.1)

- Description: Add `build_quarterly_memo_feed(company, series_payload, generated_at)`
  + CLI subcommand `build-quarterly` to kpi_memo_feed.py. Envelope fields mirror
  v1.0; `_memo_feed_schema_version` → "1.1"; `status` is "TRUSTED" only when every
  reported point carries `source_accession`+`concept` (non-blank) and every derived
  point carries `derived: True` + non-empty PLURAL `source_accessions`/`source_forms`
  — any violation raises ValueError naming field+signature (fail-closed, mirrors
  v1.0 refusal); `coverage_flags` pass through verbatim after `assert_dqc_schema`
  on each; no `kpi_gate` call on this arm (ruling above, in docstring). Tier-①
  `build_memo_feed` behavior unchanged.
- Module: investing-toolkit analysis-kpi (kpi_memo_feed)
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_memo_feed.py,
  investing-toolkit/tests/analysis/test_kpi_memo_feed.py,
  investing-toolkit/skills/analysis-kpi/SKILL.md  # one-line: retire the memo-feed "unconsumed" note
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py (assert_dqc_schema import; series JSON shape from T2)
- Acceptance:
  - RED: new tests in test_kpi_memo_feed.py — (a) a well-formed quarterly series
    payload yields status TRUSTED, schema_version "1.1", coverage_flags verbatim;
    (b) a derived point missing plural `source_accessions` raises ValueError.
    Fails now: function/subcommand absent.
  - GREEN: both pass; existing tier-① tests untouched and green.
- Dependencies: Task 2 completes first (consumes its series JSON shape)
- Independent: false
- Brief item covered: "emits one memo-feed JSON (series + derived-Q4 lane +
  coverage flags, DQC schema intact)" (Smallest End State 2 — the assembly half).

## Task 4 — report-equity-memo: Phase 3.5 + Resource Paths + input-bundle schema

- Description: Insert Phase 3.5 (after Phase 3 DCF, before Phase 4 delegation)
  into report-equity-memo/SKILL.md: US ticker → run kpi-quarterly pack →
  `quarterly-series` → `build-quarterly`, producing one memo-feed JSON; non-US →
  explicit skip note recorded in the seed (never silent). Add the memo-feed path
  as an OPTIONAL entry to `### Resource Paths` (SKILL.md:356-380),
  references/phase4-seed-contract.md (incl. its acceptance greps :129-138), and
  references/schema-phase4-input-bundle.json.
- Module: investing-toolkit report-equity-memo (orchestration prose + schema)
- Files touched: investing-toolkit/skills/report-equity-memo/SKILL.md,
  investing-toolkit/skills/report-equity-memo/references/phase4-seed-contract.md,
  investing-toolkit/skills/report-equity-memo/references/schema-phase4-input-bundle.json,
  investing-toolkit/tests/report/test_phase4_input_bundle.py (new)
- Context paths:
  - investing-toolkit/tests/report/test_pack_inventory.py (report-test conventions)
- Acceptance:
  - RED: new test_phase4_input_bundle.py — asserts schema-phase4-input-bundle.json
    declares the optional kpi memo-feed property and SKILL.md contains a Phase 3.5
    block referencing `build-quarterly` (structural grep-level assertions; prose
    policies are not pytest-able beyond structure — repo memory). Fails now: neither exists.
  - GREEN: assertions pass; test_skill_structure.py stays green.
- Dependencies: Task 3 completes first (doc mirrors the CLI names + feed schema — semantic dep)
- Independent: true  # vs Task 7: disjoint files, no shared symbol (reviewer Check-15 note adopted)
- Brief item covered: "one new phase between Phase 3 and Phase 4; memo-feed JSON
  path joins the Resource Paths; US-only with explicit skip" (Smallest End State 3).

## Task 5 — investing-team protocol: Operating-KPI block

- Description: Add an Operating-KPI block to
  domain-teams/skills/investing-team/protocols/deep-equity-research-memo.md
  (thesis-support position near P3, buy-side convention) + the output template
  (:286-370): consumes ONLY the kpi memo-feed JSON (never recompute, never read
  raw facts); trend table = last 8 quarters, fiscal label + calendar pair shown;
  derived-Q4 cells tagged per-cell with footnote naming FY−ΣQ1-3 + source
  accessions; coverage gaps truncate + footnote (reason verbatim from
  coverage_flags); <4 reported quarters → appendix-only; WITHHELD/absent feed →
  section states the reason verbatim (no fabricated series). TW 月營收 block
  (:136-143) untouched.
- Module: domain-teams investing-team (protocol prose)
- Files touched: domain-teams/skills/investing-team/protocols/deep-equity-research-memo.md
- Context paths:
  - domain-teams/skills/investing-team/checklists/primary-source-citation-compliance.md (gate language the block must be compatible with)
- Acceptance:
  - RED: grep diagnostic — `grep -c 'Operating KPI' protocols/deep-equity-research-memo.md`
    returns 0 today; target-state grep set (block heading present + "derived"
    tagging rule + "WITHHELD" handling + appendix rule each ≥1 hit) fails now.
  - GREEN: all greps hit; no diff outside the new block + template insertion
    (surgical-edit check via `git diff --stat`).
- Dependencies: Task 3 completes first (block mirrors feed schema fields — semantic dep)
- Independent: true  # vs Task 4: disjoint files, no shared symbol; shared upstream declared via Task 3
- Brief item covered: "a new Operating-KPI block in the memo protocol + output
  template … Gate contract unchanged" (Smallest End State 4).

## Task 6 — investing-toolkit version bump + CHANGELOG

- Description: investing-toolkit 2.22.0→2.23.0: bump `.claude-plugin/plugin.json`
  + `.codex-plugin/plugin.json`, add a CHANGELOG v2.23.0 entry named for this
  slice (memo quarterly-KPI wiring: kpi-quarterly pack, quarterly-series CLI,
  memo-feed 1.1 quarterly arm, Phase 3.5). Repo memory: content PRs without a
  bump are silent no-ops on device; bump packets must name the CHANGELOG entry.
- Module: investing-toolkit plugin metadata
- Files touched: investing-toolkit/.claude-plugin/plugin.json,
  investing-toolkit/.codex-plugin/plugin.json, investing-toolkit/CHANGELOG.md
- Context paths:
  - investing-toolkit/tests/test_plugin_metadata.py (version-consistency assertions)
- Acceptance:
  - RED: diagnostic — both manifests read 2.22.0 today (`python3 -c` version
    assert == "2.23.0" fails); CHANGELOG has no v2.23.0 heading (`grep -c '2.23.0'` = 0).
  - GREEN: both manifests read 2.23.0; CHANGELOG v2.23.0 entry present;
    test_plugin_metadata.py green.
- Dependencies: Tasks 4, 7 complete first
- Independent: true  # vs Task 8: disjoint files, separate plugin
- Brief item covered: "Both plugin versions bumped" (Smallest End State 5 —
  investing-toolkit half).

## Task 8 — domain-teams version bump + CHANGELOG

- Description: domain-teams 5.8.1→5.9.0: bump `.claude-plugin/plugin.json` +
  `.codex-plugin/plugin.json`, add a CHANGELOG v5.9.0 entry named for this slice
  (Operating-KPI block in deep-equity-research-memo protocol).
- Module: domain-teams plugin metadata
- Files touched: domain-teams/.claude-plugin/plugin.json,
  domain-teams/.codex-plugin/plugin.json, domain-teams/CHANGELOG.md
- Context paths:
  - domain-teams/CHANGELOG.md (entry format convention)
- Acceptance:
  - RED: diagnostic — both manifests read 5.8.1 today (version assert == "5.9.0"
    fails); CHANGELOG has no v5.9.0 heading.
  - GREEN: both manifests read 5.9.0; CHANGELOG v5.9.0 entry present.
- Dependencies: Task 5 completes first
- Independent: true  # vs Task 6: disjoint files, separate plugin
- Brief item covered: "Both plugin versions bumped" (Smallest End State 5 —
  domain-teams half).

## Task 7 — offline end-to-end seam test (toolkit chain)

- Description: Integration test walking the full toolkit chain offline:
  fact-pack fixture (machine-captured, `_provenance`-stamped — never hand-typed) →
  `quarterly-series` CLI → `build-quarterly` CLI → assert on the final feed:
  derived point still tagged with plural accessions, calendar/fiscal pair intact,
  coverage_flags survived verbatim, and a poisoned payload (derived point stripped
  of `source_accessions`) exits 1.
- Module: investing-toolkit tests (integration)
- Files touched: investing-toolkit/tests/integration/test_memo_feed_chain.py (new)
- Context paths:
  - investing-toolkit/tests/integration/test_cross_layer_chains.py (chain-test conventions)
  - investing-toolkit/tests/analysis/fixtures/xbrl_quarterly_nvda_factpack.json
- Acceptance:
  - RED: the new test file fails now (CLIs absent).
  - GREEN: chain test passes; full suite `pytest investing-toolkit/tests/ -m "not network"`
    ≥ current 731 passed, 0 new failures.
- Dependencies: Tasks 1, 2, 3 complete first
- Independent: true  # vs Task 4: disjoint files (reviewer Check-15 note adopted)
- Brief item covered: brief §Decision "the 2.22.0 anti-fabrication guarantees …
  surviving end-to-end into the rendered tables" — the machine-checkable half
  (toolkit chain); the prose half is T4/T5.

## Notes

- Post-PASS amendments (re-review skipped — additive and schema-safe): (1) added
  analysis-kpi/SKILL.md to Task 3's Files touched (reviewer note: write-set
  completeness); (2) marked Tasks 4 and 7 `Independent: true` per reviewer
  Check-15 advisory — file sets disjoint, no shared symbol, DAG unchanged;
  no field removed, no dependency edge changed; (3) during execution, added
  test_data_markets_us.py + the sample fixture to Task 1's Files touched —
  T1 spec-reviewer ruled the migration-contract edit entailed (write-set gap
  in the plan, not scope creep); Task 1's dual 10-Q+10-K fetch ruled entailed
  by the task graph (derive_q4_points needs FY basis) — plan text under-specified.

- Real-ticker quarterly dogfood rides verification-before-completion / finishing,
  not a plan task (brief §Out of Scope).
- analysis-kpi SKILL.md full backfill is BACKLOG debt; T3 updates only the
  memo-feed "unconsumed" note it directly invalidates (analysis-kpi SKILL.md:392-426)
  — that one-line touch rides T3's Files if needed (same-module doc line).
- No live/network test added this slice: the only external surface reuses the
  already-live-anchored `extract_dimensional_revenue`.
- Stale change-folder `docs/loom/2026-07-12-us-sec-primary-source-layer/` surfaced
  to user for archiving decision — not touched by this plan.
- Kickoff decision: new pack schema filename → `us-schema-kpi-quarterly.json`,
  follows the existing `us-schema-<pack>.json` convention (arm-1 lookup, unbriefed).
- Kickoff decision: quarterly-series output keys series by the full dimensional
  signature → per `docs/loom/memory/match-kpi-on-full-dimensional-signature-not-one-axis.md`
  (arm-1 lookup, unbriefed).
- Kickoff decision: body trend-table span → 8 quarters (Axis-4 research range
  8-12; smallest honest span; appendix carries the full series) — cite brief
  §Alternatives Considered.

## Decision Log

- (planning) Version numbers 2.23.0 / 5.9.0: minor bumps, feature-additive —
  two-way door, agent-decided.
- (planning) Operating-KPI block position = thesis-support near P3 (buy-side
  convention, brief §Alternatives) — two-way door (prose move), late-vetoable.
- (kickoff briefing, user-ratified 2026-07-18) memo-feed 1.1 XBRL-lane trust
  ruling = option 1: the quarterly/XBRL arm does NOT call the store-based
  kpi_gate; admission is machine-verified provenance completeness (accession +
  concept per point; derived points additionally plural source_accessions /
  source_forms) + assert_dqc_schema + verbatim coverage_flags — fail-closed,
  zero user confirmation steps. Clarified during briefing: no per-number and no
  per-company confirmation exists on this lane. Rejected: (2) extending the
  store confirmation gate to XBRL series (new machinery, YAGNI); (3) no gate.
  Reversal trigger: if quarterly series ever ingest manually-corrected values
  via the store, merge the gates then — schema_version 1.1 makes the migration
  detectable.

# Plan: 8-K earnings-release semi-auto KPI intake (Route B)

**Source brief**: docs/loom/specs/2026-07-19-8k-earnings-kpi-intake.md
**Total tasks**: 8
**Critical-path depth**: 5 (≤5 ✓) — T2→T3→T4→T5→T8
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-07-19 re-review, 14/14 checks — LLM-layer split confirmed coverage-clean, no orphan)

## Task 1 — Exhibit acquisition via attachments + new cache key

- **Description**: Add `fetch_exhibit_documents(ticker, accession=None)` to sec_edgar_client.py: resolve the latest earnings 8-K (Item 2.02) or the given accession via edgartools, enumerate ALL EX-99.* attachments via `filing.attachments` (NOT `_segment_8k` / `fetch_narrative_sections`), return per-document raw HTML + metadata (accession, document name, exhibit type, filing date), cached under NEW key family `exhibit_raw_{accession}_{document}` — never the legacy `narrative_sections_{accession}` slot.
- **Module**: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
- **Files touched**: investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py, NEW: investing-toolkit/tests/test_exhibit_fetch.py
- **Context paths**:
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/docs/loom/memory/cache-key-collision-across-migration.md
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/docs/loom/memory/importing-a-module-runs-its-module-level-imports.md
- **Acceptance**:
  - **RED**: `test_exhibit_fetch.py::test_new_cache_key_never_aliases_legacy_narrative_key` — pre-seed `narrative_sections_{accession}` with the legacy dict-shaped payload, assert `fetch_exhibit_documents` does NOT read it (cache miss on its own key → fetch path invoked); plus `test_exhibit_fetch.py::test_multi_exhibit_8k_returns_all_ex99_documents` (stubbed edgartools, 2-exhibit fixture — both EX-99.1 and EX-99.2 returned, no loud-gap behavior).
  - **GREEN**: both tests pass offline (edgar stubbed in sys.modules before import); cache writes land under `exhibit_raw_*` keys only.
- **External surfaces**:
  - SDK package: edgartools `filing.attachments` / `obj.press_releases` — grounding: live spike verification 2026-07-19 (scratchpad route-b-inventory-spike.md, NFLX acc 0001065280-25-000033) + in-repo usage patterns in sec_edgar_client.py
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "any Route B cache mints a NEW key … never reuse narrative_sections_{accession}" + "acquisition goes via attachments" (brief §Current State Evidence Forward/Boundary)

## Task 2 — Generic HTML table walker with cell coordinates

- **Description**: New script `exhibit_tables.py` (data-markets): stdlib `html.parser`-based table extractor — input raw exhibit HTML, output JSON list of tables, each cell with `{table_index, row, col, text}` after rowspan/colspan resolution and duplicate-cell cleanup, plus per-row label path (leading label cells). CLI: `exhibit_tables.py --html <path> --out <json>`. No pandas/lxml dependency (coordinates fidelity requires a custom walker anyway).
- **Module**: investing-toolkit/skills/data-markets/scripts/exhibit_tables.py (new file)
- **Files touched**: NEW: investing-toolkit/skills/data-markets/scripts/exhibit_tables.py, NEW: investing-toolkit/tests/test_exhibit_tables.py, NEW: investing-toolkit/tests/fixtures/nflx_q4_2024_ex991.html
- **Context paths**:
  - /private/tmp/claude-501/-Users-kouko--supacode-repos-monkey-skills-finacial-analytics-r2/1892665d-3d1b-476b-840a-fd38f3512f79/scratchpad/nflx_q4_2024_ex99_raw.html (real fetched exhibit — source for the committed fixture)
  - /private/tmp/claude-501/-Users-kouko--supacode-repos-monkey-skills-finacial-analytics-r2/1892665d-3d1b-476b-840a-fd38f3512f79/scratchpad/route-b-inventory-spike.md (spike evidence: expected values + coordinates)
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/docs/loom/memory/hand-authored-fixture-is-a-fabrication-risk.md
- **Acceptance**:
  - **RED**: `test_exhibit_tables.py::test_nflx_q4_2024_membership_cell_located` — real-bytes fixture (provenance line: accession 0001065280-25-000033, verified live 2026-07-19), assert the walker locates cell text `301.63` with a stable `{table_index,row,col}` coordinate and its row-label path contains "Paid Memberships".
  - **GREEN**: test passes; fixture is committed real bytes (NOT hand-authored), values cross-checked against the spike's live extraction.
- **Dependencies**: none
- **Independent**: false  # all Files touched are NEW paths — disjointness oracle untrusted per plan-format sentinel
- **Brief item covered**: "generic HTML-table extraction (pandas-style walking + colspan/duplicate-cell cleanup …)" (brief §Decision)

## Task 3 — Raw candidate extractor (mechanical layer, values + coordinates only)

- **Description**: New script `kpi_8k_candidates.py` (analysis-kpi) subcommand `propose`: consume exhibit-table JSON (produced by exhibit_tables.py via subprocess, repo layer pattern) + filing metadata → RAW candidate points `{label (verbatim row-label path), value (exact as printed, no normalization), period_hint (verbatim column header text), source_accession, source_table_id, source_cell_ref, confirmed: false}` written to a candidates JSON file. This is the MECHANICAL layer — it emits values + source coordinates + verbatim labels ONLY; it does NOT invent `kpi_id`, `unit`, or a normalized `period`. Those SEMANTIC fields are emitted as explicit `null` with a `needs_semantic: [kpi_id, unit, period]` list, to be filled by the LLM layer (T8's SKILL.md workflow) then ratified by the human. Values + coordinates never pass through an LLM — mechanical producer straight to file (anti-fabrication of the number itself).
- **Module**: investing-toolkit/skills/analysis-kpi/scripts/kpi_8k_candidates.py (new file)
- **Files touched**: NEW: investing-toolkit/skills/analysis-kpi/scripts/kpi_8k_candidates.py, NEW: investing-toolkit/tests/test_kpi_8k_candidates_propose.py
- **Context paths**:
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-kpi/scripts/kpi_schema.py
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/docs/loom/memory/durable-store-mirrors-cache-util-not-imports-it.md (subprocess-not-import layer rule)
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/docs/loom/memory/prose-only-enforcement-dies-on-weak-executors.md (why the LLM layer lives in SKILL.md text + is dogfood-verified, not pytest-verified)
- **Acceptance**:
  - **RED**: `test_kpi_8k_candidates_propose.py::test_nflx_membership_raw_candidate_emitted` — from the T2 fixture's table JSON, candidates include label path "Global Streaming Paid Memberships", value string exactly `301.63`, correct source coordinates, `confirmed: false`, and `kpi_id`/`unit`/`period` all `null` with `needs_semantic` listing them (the mechanical layer NEVER guesses "millions" or a slug).
  - **GREEN**: test passes; candidate shape maps onto kpi_schema.propose()'s `{kpi_id, label, unit, locate_hint}` contract (kpi_id/unit as the LLM-fillable slots, label/locate_hint as the mechanical outputs), mapping documented in the script docstring transcribed from kpi_schema.py BEHAVIOR (not comments).
- **External surfaces**:
  - Internal sibling-team contract: analysis-kpi `kpi_schema.propose()` field shape (LLM-produced-upstream contract) — grounding: in-repo evidence (kpi_schema.py, read at implementation time)
- **Dependencies**: Task 2 completes first
- **Independent**: false
- **Brief item covered**: "machine-parse the press-release exhibit's HTML tables → candidate KPI points {kpi_id, label, value, unit, period, source_accession, source_table_id, source_cell_ref}" (brief §Smallest End State) — split into mechanical (this task) + semantic-LLM (T8 workflow) layers

## Task 4 — Confirm-gate commit into tier-① store

- **Description**: `kpi_8k_candidates.py` subcommand `commit --candidates <file>`: append ONLY entries the human has flipped to `confirmed: true` (with the semantic fields kpi_id/unit/period now filled — by the LLM layer, human-ratified) into the tier-① store via existing `kpi_store.append(point)`; entries lacking provenance OR still carrying a null semantic field (kpi_id/unit/period never filled) are REFUSED loudly by the existing store validation (do not weaken it); unconfirmed entries are never written; summary report (N committed / N skipped-unconfirmed / N refused-incomplete).
- **Module**: investing-toolkit/skills/analysis-kpi/scripts/kpi_8k_candidates.py
- **Files touched**: investing-toolkit/skills/analysis-kpi/scripts/kpi_8k_candidates.py, NEW: investing-toolkit/tests/test_kpi_8k_candidates_commit.py
- **Context paths**:
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-kpi/scripts/kpi_validate.py
- **Acceptance**:
  - **RED**: `test_kpi_8k_candidates_commit.py::test_unconfirmed_candidates_never_land` — a candidates file with one confirmed + one unconfirmed entry commits exactly the confirmed one (store contains 1 point, with full provenance + accession-derived as_of); plus `::test_missing_unit_refused` — a confirmed entry with null unit is refused by store validation, exit non-zero, loud message.
  - **GREEN**: both tests pass against a temp-dir store (env-overridden root per existing kpi_store test pattern).
- **External surfaces**:
  - Internal sibling-team contract: `kpi_store.append(point)` required fields + 5-tuple dedup — grounding: in-repo evidence (kpi_store.py)
- **Dependencies**: Task 3 completes first
- **Independent**: false
- **Brief item covered**: "confirmed points append via the EXISTING kpi_store.append() (schema untouched, confirm-all gate untouched)" (brief §Smallest End State / §Decision)

## Task 5 — NFLX end-to-end exercise

- **Description**: End-to-end offline test chaining the full lane: fixture exhibit HTML → exhibit_tables.py (subprocess) → propose (raw candidate, null semantic fields) → simulated LLM+human step (the test fills kpi_id/unit="millions"/period and flips `confirmed: true`, standing in for the SKILL.md LLM layer + human ratification) → commit → assert the stored point's value is exactly `301.63`, unit/period as confirmed, and all three provenance fields point at accession 0001065280-25-000033 + the fixture's table/cell coordinates.
- **Module**: investing-toolkit/tests/test_8k_intake_e2e.py (new file)
- **Files touched**: NEW: investing-toolkit/tests/test_8k_intake_e2e.py
- **Context paths**:
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/tests/ (existing e2e patterns, e.g. the JNJ synthetic e2e fixture test)
- **Acceptance**:
  - **RED**: `test_8k_intake_e2e.py::test_fixture_exhibit_to_store_roundtrip` fails before wiring is complete.
  - **GREEN**: full suite (`pytest investing-toolkit/tests/ -m "not network"`) passes including the new e2e; no same-operand assertions (each assert compares producer output to an independent expected literal).
- **Dependencies**: Tasks 1, 4 complete first
- **Independent**: false
- **Brief item covered**: "v1 ships the generic table walker + one filer exercised end-to-end (NFLX)" (brief §Smallest End State)

## Task 6 — Persist recon findings into docs/loom/references/

- **Description**: New reference doc `docs/loom/references/nonmonetary-kpi-carrier-map.md` distilling the volatile scratchpad recon into repo-permanent knowledge: (a) 71-filer XBRL non-monetary census verdict + the physical-footprint/capacity cluster table (exact concepts, filers, example values w/ accessions); (b) the 1995–2025 carrier-map era table + regulatory timeline (cited); (c) the traps registry (decoy CIKs XOM/BLK/BA/GOOGL/ORCL with real-vs-decoy CIK numbers, SBUX sub-brand, MET corruption, hedge-notional, TSLA vesting, 2004-pre item undecidability); (d) a header line stating the canonical test-filer list is docs/loom/references/xbrl-verification-universe.md (closing the "12-ticker list was never committed" gap); (e) a "durable store path — host research verdict" subsection recording the 2026-07-19 finding: neither Claude Code nor Codex documents a skill-reachable durable-data dir (CLAUDE_PLUGIN_DATA is textual-substitution-only for skill bodies + hook-only for env + {plugin}-{marketplace} splits on reinstall; Codex PLUGIN_DATA is hook-only, path-undocumented, open interpolation bug #19582; Codex ignores XDG #1980) → host-neutral `KPI_STORE_DIR` / `$XDG_DATA_HOME` / `~/.local/share/investing-toolkit/kpi-store` ladder is the cross-host-safe choice (matches uv precedent), with the explicit reversal condition (revisit iff PLUGIN_DATA extends to skill script invocations on both hosts AND #19582 closes).
- **Module**: docs/loom/references/nonmonetary-kpi-carrier-map.md (new file)
- **Files touched**: NEW: docs/loom/references/nonmonetary-kpi-carrier-map.md
- **Context paths**:
  - /private/tmp/claude-501/-Users-kouko--supacode-repos-monkey-skills-finacial-analytics-r2/1892665d-3d1b-476b-840a-fd38f3512f79/scratchpad/kpi-carrier-map-1995-2025.md
  - /private/tmp/claude-501/-Users-kouko--supacode-repos-monkey-skills-finacial-analytics-r2/1892665d-3d1b-476b-840a-fd38f3512f79/scratchpad/route-a-census.md (+ ext slices, same dir)
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/docs/loom/references/xbrl-verification-universe.md
- **Acceptance**:
  - **RED**: file absent (diagnostic: `test -f docs/loom/references/nonmonetary-kpi-carrier-map.md` fails).
  - **GREEN**: file exists with sections (a)–(d); all example values carry accession cites copied exactly from the recon artifacts; no value invented beyond what a recon artifact records.
- **Dependencies**: none
- **Independent**: false  # NEW path — sentinel; also large-content doc task, keep sequential floor
- **Brief item covered**: "worth persisting the merged findings into docs/loom/references/ during the arc" (brief §Open Questions 1, user-ratified checkpoint point ③)

## Task 7 — BACKLOG re-scope for the double-arc

- **Description**: Edit docs/loom/BACKLOG.md §「investing-toolkit 非金錢營運 KPI 自動化 — 雙路線」: Route B → IN-FLIGHT (this arc, brief/plan paths); Route A → re-scoped per full-universe census (footprint/capacity allowlist: NumberOfStores/NumberOfRestaurants/NumberOfRealEstateProperties + utility MW capacity; three mandatory defenses: per-filer semantic verification, value-sanity gate, QName-keyed classification; carries the per-point `currency` ISO passthrough rider — Route B does not touch XBRL feed emission); add explicit far-parked line: pre-2003 10-K-prose KPI extraction is a separate problem, out of scope for both routes.
- **Module**: docs/loom/BACKLOG.md
- **Files touched**: docs/loom/BACKLOG.md
- **Context paths**:
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/docs/loom/BACKLOG.md
- **Acceptance**:
  - **RED**: diagnostic — current §雙路線 says "Start: RECON FIRST" with no census outcome recorded (grep finds no "footprint" scoping).
  - **GREEN**: section reflects the three user-ratified points; USER-COMMITTED marker retained; entry format follows the BACKLOG header's own spec.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "Route A XBRL non-monetary allowlist (own arc; full-universe census scopes it …)" (brief §Out of Scope) + checkpoint point ② (user-ratified)

## Task 8 — SKILL.md wiring + CHANGELOG + version bump 2.26.0

- **Description**: Document the new intake lane: data-markets SKILL.md (exhibit fetch + table-walker verbs, cache key family), analysis-kpi SKILL.md (8-K candidate 3-layer workflow — MECHANICAL propose emits values+coordinates+null-semantic; the LLM/agent step fills kpi_id/unit/period as candidate proposals reading the verbatim labels; the HUMAN confirm-all step ratifies + flips confirmed:true before commit; state that values/coordinates never pass through the LLM, and that the LLM layer is prose-instruction in SKILL.md verified by dogfood not pytest); add investing-toolkit CHANGELOG 2.26.0 entry; bump investing-toolkit plugin.json to 2.26.0 and run the codex-manifest mirror sync script.
- **Module**: investing-toolkit (plugin docs + manifests)
- **Files touched**: investing-toolkit/skills/data-markets/SKILL.md, investing-toolkit/skills/analysis-kpi/SKILL.md, investing-toolkit/CHANGELOG.md, investing-toolkit/.claude-plugin/plugin.json, investing-toolkit/.codex-plugin/plugin.json
- **Context paths**:
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/CHANGELOG.md
  - /Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/scripts/ (codex manifest sync script location)
- **Acceptance**:
  - **RED**: codex-manifest drift test fails after plugin.json bump until the mirror sync runs (existing drift-detection test); CHANGELOG has no 2.26.0 entry.
  - **GREEN**: drift test passes at 2.26.0; both SKILL.md sections describe the shipped behavior (transcribed from code BEHAVIOR, not from comments); full suite green.
- **Dependencies**: Task 5 completes first
- **Independent**: false
- **Brief item covered**: "Build Route B … feeding tier-①'s EXISTING confirm-all human gate" (brief §Decision — documentation of the shipped surface; version-bump rule per repo convention "改 skill 內容的 PR 必須 bump plugin 版本")

## Notes

- **Change-folder binding: N/A (loudly).** The sole non-archived change-folder `docs/loom/2026-07-12-us-sec-primary-source-layer/` is a recorded wrong-bind hazard (unrelated stale folder, manually N/A'd twice in prior sessions; archiving still unruled — BACKLOG P2). Input is the brainstorming brief only.
- **≥2-exhibit LOOM-SIMPLIFY ceiling NOT lifted in this plan**: acquisition (T1) goes via `filing.attachments`, so `_segment_8k`'s ceiling is not on the execution path. Reversal trigger stands: if any implementer ends up reusing `fetch_narrative_sections`, execute the marker's recorded upgrade on the spot (docs/loom/memory/execute-cheap-loom-simplify-upgrades-at-review.md) — surface it in that task's report.
- **Currency ISO rider does NOT ride this arc**: Route B never touches the XBRL feed emission path; the rider is pinned to Route A's producer touch (recorded in T7's BACKLOG re-scope).
- **Decoy-CIK guard**: v1 intake resolves ticker→current filer via edgartools (correct for CURRENT 8-Ks); the decoy risk is historical backfill, which is out of scope — registry lands in T6's traps section.
- **Parallelism**: T1 ∥ T7 (both Independent: true, disjoint files). T2/T6 have all-NEW Files touched → sentinel keeps them Independent: false (sequential floor) even though semantically parallel-safe.
- **Branch**: cut from origin/main (detached HEAD currently AT 2bd1f805 = origin/main tip) per docs/loom/memory/new-arc-branch-bases-on-origin-main-not-merged-tip.md.

### Kickoff decisions (user-ratified 2026-07-19)

- Kickoff decision: KPI naming = mechanical-values / LLM-semantic-proposal / human-ratify → three-layer split (T3 mechanical raw candidate + null semantic; T8 SKILL.md LLM layer proposes kpi_id/unit/period; human confirm-all freezes kpi_id at first commit). Values + source coordinates NEVER pass through the LLM.
- Kickoff decision: NFLX test fixture = commit TRIMMED real bytes (the membership `<table>` block, header provenance line accession 0001065280-25-000033 + "trimmed, verified live 2026-07-19"; trim only outside the table, zero bytes altered inside) → reversal: if trimmed parse diverges from full-file parse, commit the full exhibit instead (correctness over size).
- Kickoff decision: durable store path = KEEP host-neutral XDG ladder (no CLAUDE_PLUGIN_DATA) → full research verdict + reversal condition persisted in T6(e).

### Plan-amendment skip-note (post-PASS, re-review pending)

Amendments after the PASS verdict split the single "candidate proposer" concern into a mechanical layer (T3) + an LLM-semantic layer documented in T8's SKILL.md, tightened T4/T5 wording accordingly, and added T6 sub-section (e). These change task DESCRIPTIONS and add a doc sub-section; they do not change the DAG, dependencies, Files touched, or task count. Re-running plan-document-reviewer once to confirm (descriptive change but touches acceptance wording — cheap re-review chosen over a skip-note).

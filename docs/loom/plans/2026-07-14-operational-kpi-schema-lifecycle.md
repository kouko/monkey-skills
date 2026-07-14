# Plan: operational-kpi slice 3 — kpi-schema lifecycle + fs extract

Source brief: docs/loom/specs/2026-07-14-operational-kpi-schema-lifecycle.md
Total tasks: 6
Critical-path depth: 5 (≤5)   ← T1 → T2 → T3 → T4 → T6 (at the ceiling)
Execution order: sequential (T1 refactors shared fs; T2-T6 build kpi_schema.py on it)
Plan-document-reviewer verdict: PASS (2026-07-14; 10 applied checks + 4 N/A, no defects)

Change-folder binding: realizes a SUBSET of operational-kpi/spec.md (Requirements: "KPI
schema propose-then-confirm lifecycle", "Schema-scoped extraction boundary", "Superseded
schema without a confirmed successor blocks"). Not archived (capability multi-slice).

Notes:
- T1 is the Rule-of-Three fs extract per docs/loom/memory/durable-store-mirrors-cache-util-not-imports-it.md
  (3rd durable store): move the shared primitives to `_store_fs.py`, repoint kpi_store +
  review_queue. Refactor UNDER coverage — slice-1 + slice-2 tests must stay green unchanged.
- T2-T6 build `kpi_schema.py` (one module) → those five are Independent:false among
  themselves (shared file + test file); T1 touches different files (kpi_store/review_queue/
  _store_fs) but T2 depends on T1's `_store_fs`, so still sequential.
- `propose` stores caller-supplied kpi_defs (the LLM produces them upstream — NOT here).
- Schema confirm routes through slice-2 review_queue's human-confirm seam (no pipeline
  self-confirm — reuse that authorization boundary, do not reimplement).

## Task 1 — extract shared durable-store fs primitives into _store_fs.py (repoint kpi_store + review_queue)
- Description: Create `scripts/_store_fs.py` holding `resolve_store_dir`, the
  `_UNSAFE_KEY_CHARS` sanitize helper, `_atomic_write`, and `_acquire_series_lock` /
  `_release_series_lock` (moved verbatim from kpi_store). Repoint `kpi_store.py` and
  `review_queue.py` to import these from `_store_fs` (same-dir import shim) instead of
  defining/importing-from-kpi_store. Pure refactor under coverage.
- Module: investing-toolkit/skills/analysis-kpi/scripts/_store_fs.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/_store_fs.py,
  investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py,
  investing-toolkit/skills/analysis-kpi/scripts/review_queue.py,
  investing-toolkit/tests/analysis/conftest.py,
  investing-toolkit/tests/analysis/test_store_fs.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py
  - investing-toolkit/skills/analysis-kpi/scripts/review_queue.py
  - docs/loom/memory/durable-store-mirrors-cache-util-not-imports-it.md
- Acceptance:
  - RED: investing-toolkit/tests/analysis/test_store_fs.py::test_store_fs_exposes_shared_primitives fails (module absent)
  - GREEN: `_store_fs` exposes resolve_store_dir + sanitize + _atomic_write + the lock
    pair; kpi_store.py and review_queue.py import them from `_store_fs` (grep: neither
    re-defines `_atomic_write`/`_acquire_series_lock` locally); ALL slice-1 (test_kpi_store)
    + slice-2 (test_review_queue) tests pass UNCHANGED.
- External surfaces: stdlib only (json/os/re/tempfile/pathlib/fcntl).
- Dependencies: none
- Independent: false
- Brief item covered: Smallest End State Part A "fs extract (Rule-of-Three)". Change-folder
  join: operational-kpi / Requirement "KPI schema propose-then-confirm lifecycle" (enabling
  refactor — the shared substrate the schema store also uses).

## Task 2 — kpi_schema scaffold + propose (store PROPOSED schema + enqueue confirm review-item)
- Description: Create `scripts/kpi_schema.py`. `propose(company, kpi_defs, review_item_id)`
  stores a per-company schema file (`version=1`, `status="PROPOSED"`, `kpi_defs` = the
  caller-supplied list) via `_store_fs` primitives (durable, locked, atomic), AND enqueues
  a `subject_type="kpi-schema"` review-item (via review_queue.enqueue) referencing the
  schema. No extraction/confirm here.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_schema.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_schema.py,
  investing-toolkit/tests/analysis/test_kpi_schema.py,
  investing-toolkit/tests/analysis/conftest.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/_store_fs.py
  - investing-toolkit/skills/analysis-kpi/scripts/review_queue.py
- Acceptance:
  - RED: investing-toolkit/tests/analysis/test_kpi_schema.py::test_propose_stores_proposed_schema_and_enqueues fails
  - GREEN: propose writes a PROPOSED schema for the company (version 1, kpi_defs stored)
    AND a kpi-schema review-item appears OPEN in the review queue; register
    KPI_SCHEMA_SCRIPT in conftest.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: Smallest End State Part B #1 "propose". Change-folder join:
  operational-kpi / Requirement "KPI schema propose-then-confirm lifecycle" / Scenario
  "First-time company gets a proposed schema".

## Task 3 — confirm: PROPOSED → CONFIRMED through the human-confirm seam (confirm-once)
- Description: `confirm(company, adjudicated_by)` adjudicates the schema's review-item
  through review_queue's human-confirm seam (reusing its authorization boundary — empty/
  whitespace/pipeline identity rejected) and transitions the company's PROPOSED schema to
  CONFIRMED (records confirmed_by/at). A second confirm on an already-CONFIRMED schema, or
  confirm with no PROPOSED schema, is rejected loud.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_schema.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_schema.py,
  investing-toolkit/tests/analysis/test_kpi_schema.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_schema.py
  - investing-toolkit/skills/analysis-kpi/scripts/review_queue.py
- Acceptance:
  - RED: ...::test_confirm_transitions_to_confirmed_via_human_seam fails
  - GREEN: propose→confirm(company, adjudicated_by="alice") sets status CONFIRMED +
    confirmed_by/at; the review-item is resolved; a self-confirm (adjudicated_by="" or
    pipeline) is rejected; a second confirm raises loud.
- Dependencies: Task 2 completes first
- Independent: false
- Brief item covered: Smallest End State Part B #2 "confirm-once". Change-folder join:
  operational-kpi / Requirement "KPI schema propose-then-confirm lifecycle" / Scenario
  "Confirmed schema unlocks extraction".

## Task 4 — schema-scoped extraction boundary (confirmed_kpi_ids; PROPOSED blocks)
- Description: `confirmed_kpi_ids(company)` returns the kpi_ids of the company's CONFIRMED
  schema (empty/None if no CONFIRMED schema); `is_kpi_in_confirmed_schema(company, kpi_id)`
  → True only for a listed kpi_id under a CONFIRMED schema. A PROPOSED (unconfirmed) schema
  yields no confirmed kpi_ids (extraction blocked).
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_schema.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_schema.py,
  investing-toolkit/tests/analysis/test_kpi_schema.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_schema.py
- Acceptance:
  - RED: ...::test_confirmed_schema_scopes_kpi_ids fails
  - GREEN: after confirm, confirmed_kpi_ids lists the defined ids and
    is_kpi_in_confirmed_schema is True for a listed id, False for an unlisted one; a
    still-PROPOSED schema returns no confirmed kpi_ids.
- Dependencies: Task 3 completes first
- Independent: false
- Brief item covered: Smallest End State Part B #3/#4 "schema-scoped boundary + status
  gating". Change-folder join: operational-kpi / Requirement "Schema-scoped extraction
  boundary" / Scenario "Unlisted metric in a table is ignored".

## Task 5 — amend proposes a new version; superseded-without-confirmed-successor blocks
- Description: `amend(company, new_kpi_defs, review_item_id)` proposes a NEW version
  (increment version, status PROPOSED) through the propose→confirm path; on its confirm the
  prior CONFIRMED version becomes SUPERSEDED. A company whose only schema is SUPERSEDED with
  no CONFIRMED successor yields no confirmed kpi_ids (blocked) and signals re-propose.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_schema.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_schema.py,
  investing-toolkit/tests/analysis/test_kpi_schema.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_schema.py
- Acceptance:
  - RED: ...::test_amend_new_version_and_superseded_blocks fails
  - GREEN: amend creates version 2 PROPOSED; confirming it supersedes version 1
    (status SUPERSEDED) and confirmed_kpi_ids now reflects version 2; a SUPERSEDED-only
    company (no confirmed successor) returns no confirmed kpi_ids.
- Dependencies: Task 3 completes first
- Independent: false
- Brief item covered: Smallest End State Part B #5 "amend / supersede". Change-folder join:
  operational-kpi / Requirement "Superseded schema without a confirmed successor blocks" /
  Scenario "Orphaned superseded schema holds and re-proposes".

## Task 6 — kpi_schema CLI: propose / confirm / status, declared at the command surface
- Description: argparse CLI with `propose` (company + kpi_defs JSON stdin/--file +
  --review-item-id), `confirm` (--company --by), `status` (--company → print the company's
  schema versions + statuses + confirmed_kpi_ids as JSON) subcommands; document in
  analysis-kpi/SKILL.md `## CLI`. Fail-loud exit codes mirroring the sibling CLIs (0/1/2).
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_schema.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_schema.py,
  investing-toolkit/skills/analysis-kpi/SKILL.md,
  investing-toolkit/tests/analysis/test_kpi_schema.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_schema.py
  - investing-toolkit/skills/analysis-kpi/scripts/review_queue.py
  - investing-toolkit/skills/analysis-kpi/SKILL.md
- Acceptance:
  - RED: ...::test_cli_propose_confirm_status_roundtrip fails
  - GREEN: `propose` a schema (stdin defs, KPI_STORE_DIR env) → `status` shows it PROPOSED
    → `confirm --company X --by alice` → `status` shows CONFIRMED + confirmed_kpi_ids;
    subcommands listed by `--help` AND documented in SKILL.md `## CLI`.
- Command surface: propose/confirm/status verbs declared in analysis-kpi/SKILL.md `## CLI`.
- Dependencies: Tasks 2, 3, 4, 5 complete first
- Independent: false
- Brief item covered: Smallest End State Part B #6 "a thin CLI".

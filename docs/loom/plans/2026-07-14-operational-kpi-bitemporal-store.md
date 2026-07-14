# Plan: operational-kpi slice 1 — append-only bitemporal KPI store

Source brief: docs/loom/specs/2026-07-14-operational-kpi-bitemporal-store.md
Total tasks: 8
Critical-path depth: 4 (≤5)   ← longest chain T1 → T4 → T7 → T8 (T7 depends on T4;
  T2/T3/T5/T6 sit at level 2 depending on T1 only)
Execution order: sequential (all tasks touch one module `kpi_store.py` + one test
  file → Independent:false throughout; no parallel wave)
Plan-document-reviewer verdict: PASS (2026-07-14; 14/14 checks). Header depth
  corrected 3→4 post-PASS per reviewer accuracy note — additive factual fix, DAG/fields
  unchanged, re-review skipped per writing-plans "Amending a PASS plan".

Change-folder binding: this slice realizes a SUBSET of
`docs/loom/2026-07-12-us-sec-primary-source-layer/specs/operational-kpi/spec.md`.
Join keys per task below reference that change-id's Requirement/Scenario names. The
change-folder is NOT archived on this branch (capability is multi-slice; archive only
when the final slice ships).

Notes:
- Post-PASS amendment (2026-07-14, re-review skipped per "Amending a PASS plan" —
  additive/schema-safe, DAG + coverage unchanged): (a) test paths corrected
  `tests/` → `investing-toolkit/tests/` to match the real test tree; (b) T1 grounded
  against the codebase — the store resolves its own DURABLE data dir (not the evictable
  `cache_util.resolve_cache_dir()`) and uses self-contained sanitize/atomic-write
  helpers instead of a cross-skill `import cache_util` (which is not this repo's pattern
  and would breach the analysis↔data-markets layer boundary); T1 Files touched adds the
  analysis `conftest.py` (to register `KPI_STORE_SCRIPT`).
- All tasks share `investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py` and
  `investing-toolkit/tests/analysis/test_kpi_store.py`, so none is `Independent: true` — SDD dispatches
  them one at a time, each building on the committed prior. Depth is measured on the
  Dependencies DAG (T2..T7 depend only on T1, not each other → one level), NOT on
  execution serialization.
- Store substrate reuses `data-markets/scripts/cache_util.py` primitives
  (`resolve_cache_dir`, `_UNSAFE_KEY_CHARS` sanitization, atomic tmp+rename) but NOT
  its TTL envelope (`load_cache`/`compute_ttl`) — a bitemporal series is immutable
  append-only, no expiry.

## Task 1 — analysis-kpi skill scaffold + valid append writes a versioned series file
- Description: Create the `analysis-kpi` skill (SKILL.md stating the capability is
  built incrementally; this slice = the store) and `scripts/kpi_store.py` with
  `append(point)` that persists a fully-provenanced point to a file-per-series JSON
  (one file per company+kpi_id, holding a list of point records) under a versioned
  `_kpi_store_meta` envelope. The store resolves its own **durable DATA dir**
  (XDG_DATA_HOME ladder → `~/.local/share/investing-toolkit/kpi-store`, with an
  env override `KPI_STORE_DIR` for tests) — NOT `cache_util.resolve_cache_dir()` (that
  is the evictable cache dir) — and uses **self-contained helpers mirroring**
  cache_util's `_UNSAFE_KEY_CHARS` sanitization + atomic tmp+rename write; it does NOT
  `import cache_util` (cross-skill import breaches the layer boundary — see brief
  Reverse evidence). Register `KPI_STORE_SCRIPT = SKILLS / "analysis-kpi" / "scripts"
  / "kpi_store.py"` in the analysis conftest. A point is a dict with keys
  `company, kpi_id, period, as_of, value, source_accession, source_table_id,
  source_cell_ref` (+ optional `lineage`, `restates` persisted verbatim, not
  interpreted this slice).
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py
- Files touched: investing-toolkit/skills/analysis-kpi/SKILL.md,
  investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py,
  investing-toolkit/tests/analysis/test_kpi_store.py,
  investing-toolkit/tests/analysis/conftest.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/cache_util.py  (PATTERN reference only — do not import)
  - investing-toolkit/tests/analysis/conftest.py
  - investing-toolkit/skills/analysis-xval/SKILL.md
  - docs/loom/2026-07-12-us-sec-primary-source-layer/specs/operational-kpi/spec.md
- Acceptance:
  - RED: investing-toolkit/tests/analysis/test_kpi_store.py::test_append_creates_versioned_series_file_with_point
    fails (kpi_store / append undefined)
  - GREEN: appending one valid point (tmp store dir via the `KPI_STORE_DIR` env
    override) creates exactly one series file under the durable-data root whose JSON
    carries `_kpi_store_meta.version` and a `points` list containing that point; the
    point round-trips unchanged.
- External surfaces: stdlib only (`json`, `os`, `pathlib`, `tempfile`, `re`); NO
  third-party import and NO cross-skill `import cache_util`.
- Dependencies: none
- Independent: false
- Brief item covered: Smallest End State #1 "Append-only bitemporal store … file-per-
  series JSON … reusing cache_util". Change-folder join: operational-kpi / Requirement
  "Bitemporal append-only store" / Scenario "Store substrate is file/JSON, not a database".

## Task 2 — append rejects a point missing provenance (fail loud)
- Description: Add a provenance precondition to `append`: a point missing any of
  `source_accession`, `source_table_id`, `source_cell_ref` (absent, None, or empty)
  raises a loud error and writes nothing — never an unattributed record.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py,
  investing-toolkit/tests/analysis/test_kpi_store.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py
- Acceptance:
  - RED: investing-toolkit/tests/analysis/test_kpi_store.py::test_append_rejects_missing_provenance fails
  - GREEN: appending a point with a missing/empty `source_cell_ref` raises (fail loud)
    and no series file is written / no record added.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: Smallest End State #4 "Provenance completeness or reject".
  Change-folder join: operational-kpi / Requirement "Provenance completeness for every
  series-point" / Scenario "A series-point without a cell reference is rejected".

## Task 3 — append rejects a wall-clock / absent as_of (accession-derived required)
- Description: Add an `as_of` precondition to `append`: the point MUST carry an
  explicit `as_of` marked as accession/disclosure-derived (e.g. an `as_of` field plus
  the point's `source_accession`); a point with no `as_of`, or one flagged
  wall-clock-derived, is rejected loud. (This slice validates the invariant; the
  accession→as_of derivation itself is an upstream slice's job.)
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py,
  investing-toolkit/tests/analysis/test_kpi_store.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py
- Acceptance:
  - RED: investing-toolkit/tests/analysis/test_kpi_store.py::test_append_rejects_wallclock_or_absent_as_of fails
  - GREEN: appending a point with `as_of` absent (or explicitly wall-clock-flagged)
    raises loud and stores nothing; a point with a valid accession-derived `as_of`
    still appends.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: Smallest End State #3 "as_of is accession/disclosure-derived, not
  wall-clock". Change-folder join: operational-kpi / Requirement "Idempotent append with
  an explicit dedup key" / Scenario "as_of is accession-derived, not wall-clock".

## Task 4 — idempotent append dedups on (key + source_accession)
- Description: Make re-appending the identical point a no-op: dedup on
  `(company, kpi_id, period, as_of, source_accession)`. Re-appending the same accession
  with no change does not add a second record; a corrected value carrying a NEW `as_of`
  appends a new record (both retained).
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py,
  investing-toolkit/tests/analysis/test_kpi_store.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py
- Acceptance:
  - RED: investing-toolkit/tests/analysis/test_kpi_store.py::test_reappend_same_accession_is_noop fails
  - GREEN: two appends of the identical (key+source_accession) point leave exactly one
    record; a third append of the same (company,kpi_id,period) with a new as_of +
    accession leaves two records total.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: Smallest End State #2 "Idempotent append with an explicit dedup
  key". Change-folder join: operational-kpi / Requirement "Idempotent append with an
  explicit dedup key" / Scenario "Re-running the same accession does not double-append".

## Task 5 — query_point_in_time returns the greatest as_of ≤ a given date
- Description: Add `query_point_in_time(company, kpi_id, period, as_of_date)` returning
  only records with `as_of <= as_of_date`, selecting the one with the greatest such
  `as_of` (or None if none qualify) — so a later recast never retroactively changes an
  earlier-dated query.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py,
  investing-toolkit/tests/analysis/test_kpi_store.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py
- Acceptance:
  - RED: investing-toolkit/tests/analysis/test_kpi_store.py::test_point_in_time_excludes_later_recast fails
  - GREEN: with an early point (as_of A) and a later recast (as_of B>A) for the same
    (company,kpi_id,period), a query at a date between A and B returns the early point,
    not the recast.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: Smallest End State #5 "Point-in-time … queries". Change-folder
  join: operational-kpi / Requirement "Point-in-time query" / Scenario "Historical memo
  re-run sees only what was known then".

## Task 6 — query_latest returns the greatest as_of overall
- Description: Add `query_latest(company, kpi_id, period)` returning the record with the
  greatest `as_of` across all records for that series (or None if empty).
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py,
  investing-toolkit/tests/analysis/test_kpi_store.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py
- Acceptance:
  - RED: investing-toolkit/tests/analysis/test_kpi_store.py::test_latest_returns_greatest_asof fails
  - GREEN: with multiple as_of records for one (company,kpi_id,period), query_latest
    returns the greatest-as_of record.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: Smallest End State #5 "… + latest queries". Change-folder join:
  operational-kpi / Requirement "Point-in-time query" / Scenario "Latest query returns
  the most recent as_of".

## Task 7 — concurrency-safe append serializes concurrent writes
- Description: Guard `append` with a per-series-file lock (`fcntl.flock` on the POSIX
  dev/CI host; if `fcntl` is unavailable, degrade LOUD — a stated warning, not a silent
  skip) so two concurrent appends to the same series both persist without a lost write
  or a corrupt file.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py,
  investing-toolkit/tests/analysis/test_kpi_store.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py
- Acceptance:
  - RED: investing-toolkit/tests/analysis/test_kpi_store.py::test_concurrent_appends_both_persist fails
  - GREEN: two appends of distinct points to the same series, run from concurrent
    processes/threads, leave BOTH records in the file (no lost update, valid JSON).
- External surfaces: `fcntl` (stdlib, POSIX-only) — locking. Loud degradation if absent.
- Dependencies: Task 4 completes first (lock wraps the dedup-aware append body)
- Independent: false
- Brief item covered: Smallest End State #6 "Concurrency-safe append". Change-folder
  join: operational-kpi / Requirement "Concurrency-safe stores" / Scenario "Two runs on
  the same company do not corrupt the series".

## Task 8 — kpi_store CLI: append + query subcommands declared and runnable
- Description: Add an argparse CLI to `kpi_store.py` with `append` (reads a point JSON
  from stdin/file, calls append) and `query` (point-in-time / latest) subcommands, and
  document them in analysis-kpi/SKILL.md `## CLI`. New verbs must be visible at the
  command surface.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py,
  investing-toolkit/skills/analysis-kpi/SKILL.md,
  investing-toolkit/tests/analysis/test_kpi_store.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py
  - investing-toolkit/skills/analysis-xval/SKILL.md
- Acceptance:
  - RED: investing-toolkit/tests/analysis/test_kpi_store.py::test_cli_append_then_query_roundtrip fails
  - GREEN: `uv run kpi_store.py append` a valid point then `uv run kpi_store.py query
    --latest …` returns that point (subprocess round-trip); the subcommands are listed
    in `uv run kpi_store.py --help` AND documented under analysis-kpi/SKILL.md `## CLI`.
- Command surface: the append/query verbs are declared in analysis-kpi/SKILL.md `## CLI`
  (the toolkit's per-skill command-surface convention, mirroring analysis-xval).
- Dependencies: Tasks 1, 2, 3, 4, 5, 6, 7 complete first
- Independent: false
- Brief item covered: Smallest End State "A thin kpi_store.py CLI surface (append /
  query subcommands) declared in the skill".

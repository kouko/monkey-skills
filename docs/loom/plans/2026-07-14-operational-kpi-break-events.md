# Plan: operational-kpi slice 6 — break-event detection + adjudication lifecycle

Source brief: docs/loom/specs/2026-07-14-operational-kpi-break-events.md
Total tasks: 4
Critical-path depth: 4 (≤5)   ← T1 → T2 → T3 → T4
Execution order: sequential (all tasks touch one module kpi_break.py + one test file)
Plan-document-reviewer verdict: PASS (2026-07-14, round 2; round 1 flagged Check 8 —
  SES #4 Query uncited — fixed by adding #4 to Task 2's Brief item covered; 14/14)

Change-folder binding: realizes a SUBSET of operational-kpi/spec.md (Requirements
"Definition-drift detection triggers a break-event", "Break-event human adjudication and
mapping"). Not archived (multi-slice). Applying breaks / dual series = slice 7.

Notes:
- kpi_break.py reuses `_store_fs` (dir/lock/atomic-write) + `review_queue` (enqueue +
  the human-confirm `adjudicate` seam) by same-skill import, like kpi_schema. detection
  is pure compute; flag/confirm/dismiss are durable + lock-guarded.
- confirm/dismiss route through review_queue.adjudicate → REUSE its auth boundary
  (empty/whitespace/pipeline identity rejected THERE, not reimplemented). No pipeline
  self-confirm. Timestamps caller-supplied (NO wall-clock).
- Nested schema→queue lock order stays consistent (memory nested-cross-file-locks-need-one-global-order).

## Task 1 — kpi_break scaffold + detect_breaks (pure-compute drift detection)
- Description: Create `scripts/kpi_break.py` (PEP-723, same-dir import shim → `import
  _store_fs`, `import review_queue`). `detect_breaks(prev_summary, curr_summary)` (PURE
  COMPUTE, no persistence): compares two consecutive-period summaries — each a dict with
  `segments` (list/set of segment names), `kpi_labels` (kpi_id→label), optional
  `reconciliation` (kpi_id → {parts:[...], total}) — and returns `[{trigger, detail}]`:
  `resegmentation` if the segment set changed; `relabel` if any kpi_id's label changed;
  `arithmetic-mismatch` if a reconciliation's parts don't sum to total (rel tol). No
  drift → []. A summary lacking `reconciliation` simply can't raise arithmetic-mismatch
  (N/A). Register KPI_BREAK_SCRIPT in conftest.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_break.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_break.py,
  investing-toolkit/tests/analysis/test_kpi_break.py,
  investing-toolkit/tests/analysis/conftest.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/_store_fs.py
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_schema.py
  - docs/loom/2026-07-12-us-sec-primary-source-layer/specs/operational-kpi/spec.md
- Acceptance:
  - RED: investing-toolkit/tests/analysis/test_kpi_break.py::test_detect_breaks_flags_each_trigger fails
  - GREEN: a segment-count change → a resegmentation candidate; a changed label → a
    relabel candidate; parts not summing to total → arithmetic-mismatch; identical
    summaries → []; a summary with no reconciliation raises no arithmetic-mismatch.
- External surfaces: stdlib only (json/sys/math) + same-skill imports; no third-party.
- Dependencies: none
- Independent: false
- Brief item covered: Smallest End State #1 "Detection". Change-folder join: operational-
  kpi / Requirement "Definition-drift detection triggers a break-event" / Scenario
  "Segment count changes between quarters".

## Task 2 — flag_break: persist FLAGGED break-event + enqueue review-item
- Description: `flag_break(company, schema_version, candidate, review_item_id)`: persist a
  break-event record `{break_id, company, schema_version, trigger, detail, status:
  "FLAGGED", mapping: None}` in a per-company durable store (lock-guarded RMW via
  _store_fs, distinct filename suffix) AND enqueue a `subject_type="break-event"` review-
  item (via review_queue) referencing the break_id. `get_break`/`list_breaks` read-only.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_break.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_break.py,
  investing-toolkit/tests/analysis/test_kpi_break.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_break.py
  - investing-toolkit/skills/analysis-kpi/scripts/review_queue.py
- Acceptance:
  - RED: ...::test_flag_break_persists_and_enqueues fails
  - GREEN: flag_break stores a FLAGGED record (retrievable via get_break) AND a
    break-event review-item is OPEN in the review queue.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: Smallest End State #2 "Flag + enqueue" + #4 "Query"
  (get_break/list_breaks land here). Change-folder join: operational-kpi / Requirement
  "Break-event human adjudication and mapping" / Scenario "Operator confirms a
  resegmentation mapping" (the flag that precedes it).

## Task 3 — confirm_break (mapping required, human seam) / dismiss_break + states
- Description: `confirm_break(company, break_id, adjudicated_by, mapping, adjudicated_at=None)`:
  adjudicate the break's review-item through `review_queue.adjudicate` (REUSING the auth
  boundary — empty/whitespace/pipeline identity rejected there) BEFORE flipping, then
  transition FLAGGED → CONFIRMED recording the old→new `mapping` (a confirm with a
  missing/empty mapping is rejected loud). `dismiss_break(company, break_id,
  adjudicated_by, adjudicated_at=None)`: FLAGGED → DISMISSED. Reject loud: unknown
  break_id; adjudicating an already-resolved (CONFIRMED/DISMISSED) break. Lock-guarded
  RMW; adjudicate-before-flip so a rejected identity leaves the break FLAGGED.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_break.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_break.py,
  investing-toolkit/tests/analysis/test_kpi_break.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_break.py
  - investing-toolkit/skills/analysis-kpi/scripts/review_queue.py
- Acceptance:
  - RED: ...::test_confirm_and_dismiss_break_via_human_seam fails
  - GREEN: flag → confirm(mapping, by="alice") → status CONFIRMED + mapping stored + the
    review-item resolved; confirm with empty mapping → raises; confirm with adjudicated_by
    "" → raises + break stays FLAGGED; a second confirm/dismiss on a resolved break →
    raises; dismiss → status DISMISSED.
- Dependencies: Task 2 completes first
- Independent: false
- Brief item covered: Smallest End State #3 "Adjudicate". Change-folder join: operational-
  kpi / Requirement "Break-event human adjudication and mapping" / Scenarios "Operator
  confirms a resegmentation mapping", "A false-positive flag is dismissed".

## Task 4 — kpi_break CLI: detect / flag / confirm / dismiss / list
- Description: argparse CLI (mirror kpi_schema/kpi_gate CLIs + exit codes 0/1/2):
  `detect` (two summaries JSON → candidates), `flag` (--company --schema-version
  --review-item-id + candidate JSON → break record), `confirm` (--company --break-id
  --by [--at] + mapping JSON), `dismiss` (--company --break-id --by [--at]), `list`
  (--company → break records JSON). Document in analysis-kpi/SKILL.md `## CLI (kpi_break)`.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_break.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_break.py,
  investing-toolkit/skills/analysis-kpi/SKILL.md,
  investing-toolkit/tests/analysis/test_kpi_break.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_break.py
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_schema.py
  - investing-toolkit/skills/analysis-kpi/SKILL.md
- Acceptance:
  - RED: ...::test_cli_detect_flag_confirm_roundtrip fails
  - GREEN: `flag` a candidate → `list` shows it FLAGGED → `confirm --by alice` (mapping
    stdin) → `list` shows CONFIRMED; malformed JSON → exit 2; subcommands listed by
    `--help` AND documented in SKILL.md `## CLI (kpi_break)`.
- Command surface: detect/flag/confirm/dismiss/list verbs declared in analysis-kpi/SKILL.md `## CLI (kpi_break)`.
- Dependencies: Tasks 1, 2, 3 complete first
- Independent: false
- Brief item covered: Smallest End State #5 "a thin CLI".

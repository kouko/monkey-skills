# Plan: operational-kpi slice 2 — review-item queue + human-confirm seam

Source brief: docs/loom/specs/2026-07-14-operational-kpi-review-queue.md
Total tasks: 7
Critical-path depth: 4 (≤5)   ← longest chain T1 → T3 → T4 → T7
Execution order: sequential (all tasks touch one module `review_queue.py` + one test
  file → Independent:false throughout; no parallel wave)
Plan-document-reviewer verdict: PASS (2026-07-14; 14/14 applicable checks, no defects)

Change-folder binding: realizes a SUBSET of
`docs/loom/2026-07-12-us-sec-primary-source-layer/specs/operational-kpi/spec.md`
(Requirements: "Review-item queue lifecycle and human-confirm seam", "Adjudication
carries immutable identity", "Confirm-seam authorization boundary is stated"). NOT
archived on this branch (capability multi-slice).

Notes:
- All tasks share `investing-toolkit/skills/analysis-kpi/scripts/review_queue.py` and
  `investing-toolkit/tests/analysis/test_review_queue.py` → none Independent:true;
  sequential dispatch. Depth is on the Dependencies DAG (T2/T3 depend on T1; T4/T5/T6
  depend on T3), not execution serialization.
- `review_queue.py` REUSES slice-1 `kpi_store.py`'s durable-dir + sanitize + atomic-
  write + lock primitives by SAME-SKILL import (both in analysis-kpi/scripts/). Per
  docs/loom/memory/durable-store-mirrors-cache-util-not-imports-it.md, the shared-module
  extract is deferred to the THIRD durable store — import, do not copy, do not extract.
- A review-item's `created_at` is a runtime event (caller-supplied), NOT held to
  slice-1's accession-derived `as_of` rule — do not import that guard here.

## Task 1 — review_queue scaffold + enqueue appends an OPEN item to a durable queue file
- Description: Create `scripts/review_queue.py` with `enqueue(item)` appending a
  review-item (dict: `review_item_id, subject_type, subject_id, reason`, defaulting
  `status="OPEN"` + a caller-supplied `created_at`) to a durable append-only queue file
  under a versioned envelope, reusing `kpi_store`'s `resolve_store_dir` + atomic write
  (same-skill import). Add the module + register `REVIEW_QUEUE_SCRIPT` in the analysis
  conftest.
- Module: investing-toolkit/skills/analysis-kpi/scripts/review_queue.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/review_queue.py,
  investing-toolkit/tests/analysis/test_review_queue.py,
  investing-toolkit/tests/analysis/conftest.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py
  - investing-toolkit/tests/analysis/conftest.py
  - docs/loom/2026-07-12-us-sec-primary-source-layer/specs/operational-kpi/spec.md
- Acceptance:
  - RED: investing-toolkit/tests/analysis/test_review_queue.py::test_enqueue_creates_queue_file_with_open_item fails (review_queue/enqueue undefined)
  - GREEN: enqueuing one item (queue dir redirected via KPI_STORE_DIR) creates a queue
    file whose JSON holds the item with `status=="OPEN"`, round-tripped.
- External surfaces: stdlib only + same-skill import of `kpi_store`; no third-party, no
  cross-skill import.
- Dependencies: none
- Independent: false
- Brief item covered: Smallest End State #1 "Enqueue". Change-folder join: operational-
  kpi / Requirement "Review-item queue lifecycle and human-confirm seam" / Scenario
  "Queue file is the single source of pending work".

## Task 2 — list_open returns the OPEN items
- Description: Add `list_open()` returning all items whose `status=="OPEN"` (empty list
  if the queue file is absent — no raise).
- Module: investing-toolkit/skills/analysis-kpi/scripts/review_queue.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/review_queue.py,
  investing-toolkit/tests/analysis/test_review_queue.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/review_queue.py
- Acceptance:
  - RED: ...::test_list_open_returns_only_open_items fails
  - GREEN: with one OPEN and one resolved item, list_open returns exactly the OPEN one;
    missing queue file → [].
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: Smallest End State #2 "List open". Change-folder join: operational-
  kpi / Requirement "Review-item queue lifecycle and human-confirm seam" / Scenario
  "Operator lists and adjudicates open review items".

## Task 3 — adjudicate moves an OPEN item to a resolved state (legal transition)
- Description: Add `adjudicate(review_item_id, decision, adjudicated_by, resolution=None)`
  moving an OPEN item to `APPROVED`/`REJECTED`/`EDITED` (per `decision`), writing the
  resolution. Reject an unknown `review_item_id` or an illegal transition (adjudicating
  an already-resolved item without reopen) loud.
- Module: investing-toolkit/skills/analysis-kpi/scripts/review_queue.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/review_queue.py,
  investing-toolkit/tests/analysis/test_review_queue.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/review_queue.py
- Acceptance:
  - RED: ...::test_adjudicate_resolves_open_item fails
  - GREEN: adjudicating an OPEN item with decision="approve" sets its status APPROVED +
    stores the resolution; adjudicating an unknown id raises loud.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: Smallest End State #3 "Adjudicate". Change-folder join:
  operational-kpi / Requirement "Review-item queue lifecycle and human-confirm seam" /
  Scenario "Adjudication resolves the subject".

## Task 4 — immutable append-only adjudicator identity
- Description: Every adjudication appends an adjudication record carrying
  `adjudicated_by` + `adjudicated_at` to the item's append-only `adjudications` list; a
  later re-adjudication (after reopen) appends a NEW record, never overwrites the first.
- Module: investing-toolkit/skills/analysis-kpi/scripts/review_queue.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/review_queue.py,
  investing-toolkit/tests/analysis/test_review_queue.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/review_queue.py
- Acceptance:
  - RED: ...::test_readjudication_appends_never_overwrites fails
  - GREEN: adjudicating, reopening, then re-adjudicating leaves TWO adjudication records
    (the first retained verbatim), with distinct adjudicated_by preserved.
- Dependencies: Task 3 completes first
- Independent: false
- Brief item covered: Smallest End State #4 "Immutable adjudicator identity". Change-
  folder join: operational-kpi / Requirement "Adjudication carries immutable identity" /
  Scenario "Adjudicator identity is stamped and not overwritten".

## Task 5 — confirm-seam authorization boundary (no pipeline self-confirm)
- Description: `adjudicate` REQUIRES a non-empty human `adjudicated_by`; a call with an
  empty/None `adjudicated_by` OR an explicit `actor_is_pipeline=True` is rejected loud
  and changes nothing. Document the boundary in the docstring.
- Module: investing-toolkit/skills/analysis-kpi/scripts/review_queue.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/review_queue.py,
  investing-toolkit/tests/analysis/test_review_queue.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/review_queue.py
- Acceptance:
  - RED: ...::test_adjudicate_rejects_pipeline_self_confirm fails
  - GREEN: adjudicating with `adjudicated_by=""` (or `actor_is_pipeline=True`) raises
    loud and the item stays OPEN (nothing written); a human identity still adjudicates.
- Dependencies: Task 3 completes first
- Independent: false
- Brief item covered: Smallest End State #5 "Confirm-seam authorization boundary".
  Change-folder join: operational-kpi / Requirement "Confirm-seam authorization boundary
  is stated" / Scenario "Self-confirmation by the pipeline is rejected or delegated".

## Task 6 — reopen moves a resolved item back to OPEN
- Description: Add `reopen(review_item_id)` moving a resolved item back to OPEN (legal
  transition), so it can be re-adjudicated; reject reopening an already-OPEN or unknown
  item loud.
- Module: investing-toolkit/skills/analysis-kpi/scripts/review_queue.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/review_queue.py,
  investing-toolkit/tests/analysis/test_review_queue.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/review_queue.py
- Acceptance:
  - RED: ...::test_reopen_moves_resolved_to_open fails
  - GREEN: a resolved item after reopen has status OPEN and appears again in list_open;
    reopening an OPEN/unknown item raises loud.
- Dependencies: Task 3 completes first
- Independent: false
- Brief item covered: Smallest End State #3 (the `→(reopen)→ open` transition). Change-
  folder join: operational-kpi / Requirement "Review-item queue lifecycle and human-
  confirm seam" / Scenario "Operator lists and adjudicates open review items".

## Task 7 — review_queue CLI: enqueue / list / adjudicate, declared at the command surface
- Description: Add an argparse CLI with `enqueue` (item JSON from stdin/--file), `list`
  (print OPEN items JSON), and `adjudicate` (--id --decision --by [--resolution])
  subcommands; document them in analysis-kpi/SKILL.md `## CLI`. Fail-loud exit codes
  mirroring slice-1's CLI (0 ok, 1 rejected, 2 malformed/non-object).
- Module: investing-toolkit/skills/analysis-kpi/scripts/review_queue.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/review_queue.py,
  investing-toolkit/skills/analysis-kpi/SKILL.md,
  investing-toolkit/tests/analysis/test_review_queue.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/review_queue.py
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py
  - investing-toolkit/skills/analysis-kpi/SKILL.md
- Acceptance:
  - RED: ...::test_cli_enqueue_list_adjudicate_roundtrip fails
  - GREEN: `enqueue` a valid item (stdin, KPI_STORE_DIR env) → `list` shows it OPEN →
    `adjudicate --id ... --decision approve --by alice` → `list` no longer shows it;
    subcommands listed by `--help` AND documented in SKILL.md `## CLI`.
- Command surface: the enqueue/list/adjudicate verbs declared in analysis-kpi/SKILL.md
  `## CLI`.
- Dependencies: Tasks 1, 2, 3, 4, 5, 6 complete first
- Independent: false
- Brief item covered: Smallest End State #6 "A thin review_queue.py CLI".

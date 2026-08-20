---
name: 2026-08-07-phase2-loop-and-l2-harness-review-residue
description: deferred whole-branch review findings from the Phase 2 loop + L2 e2e harness branch
status: open
origin: whole-branch review of `feat/u1-nightly-phase2-loop` (2026-08-07, loom-code 0.64.0 panel — 2 code-reviewer + 2 docs-reviewer arms). The branch fixed the 2 fatal findings and the highest-value should-fix cluster; the items below were deliberately left, each with its reason.
start: next substantive touch of `scripts/phase2-loop/` or `dbt-wiki/tests/`
---

Each item below is a real finding with a `where:` cite, deferred rather
than dismissed. None is a correctness defect in shipped behavior; they are
consistency, portability, and test-hygiene debts.

## Phase 2 loop (`scripts/phase2-loop/`)

- **`is_nightly_paused` keeps the retired "nightly" name.**
  `safety_gates.py:6,46`, its module docstring, and the
  `NIGHTLY_PAUSED` fixture name in `test_safety_gates.py:21,27,33` (plus
  "nightly" in its module docstring, `:1`, and a comment at `:56`) all
  survived the 2026-07-29 rename of the directory and the sentinel
  (`docs/loom/PHASE2_LOOP_PAUSED`). The name is actively disinforming:
  the redesign deliberately registers no schedule, so "nightly" asserts a
  cadence that was decided against. Rename to `is_loop_paused` and update
  the three call sites plus `ROUTINE.md:30`.
- **The freeze-gate regex is mirrored, not imported, with no drift guard.**
  `queue_entry.py:36-39`'s `_PLAN_REVIEWER_PASS_PATTERN` is byte-identical
  to `batch_queue.py:46-49`'s. The docstring documents the mirroring, but
  nothing fails if the two diverge — and the integration test uses a plan
  both patterns accept, so a tightened upstream pattern would let
  `propose_queue_entry` keep emitting entries `check_frozen` rejects,
  silently. `test_queue_entry_batch_integration.py:19-28` already proves
  the cross-plugin file-path import works; either import the pattern or
  assert the two `.pattern` strings are equal.
- **`test_journal_writer.py` reads the live campaign doc.**
  `test_journal_writer.py:7-8,26,39` asserts `updated.startswith(original)`
  against the real `docs/dbt-wiki-quality-campaign.md`, which holds only
  while `## Journal` is the last section — a property of a file this
  campaign keeps appending to. Two later modules on the same branch
  (`test_queue_entry.py`, `test_queue_entry_batch_integration.py`) already
  inline a representative fixture literal; adopt the same shape.
- **Authoring-time scope guard (new, not a review finding).**
  `propose_queue_entry` could refuse to draft an entry whose backlog
  description trips `requires_real_agent_surface`, moving the refusal to
  the planning stage where a human IS present. The execution-stage guard
  would stay as defense in depth. Considered during the 2026-08-07 fix
  round and left out to keep that round scoped to the review findings.

## L2 e2e harness (`dbt-wiki/tests/`)

- **The production text I/O in this directory does not declare `encoding=`.**
  `build_sparse_variant.py:41`, `grader.py:135`,
  `test_e2e_validation.py:343`, `test_e2e_sparse_comment_validation.py:247`,
  `test_gold_questions.py:33,95`. (Two sites DO declare it —
  `test_e2e_validation.py:89,102` — but those are inside the cleanup-guard
  regression test added 2026-08-07, not the I/O paths at issue.) The
  load-bearing site is the report write, which passes
  `ensure_ascii=False` — on a non-UTF-8 default locale it raises
  `UnicodeEncodeError` and destroys the only artifact of a
  quota-spending run, after the quota is spent. The sibling
  `scripts/phase2-loop/` arm is consistently explicit, so this is an
  intra-repo inconsistency as well as a portability risk.
- **Four in-code statements still describe the Task-1 "0 models" fixture.**
  `conftest.py:58-60` justifies the writable `connect()` with reasoning
  that stopped being true once models landed (the code is still correct;
  its stated reason is not); `fixtures/l2-harness/dbt_project.yml:5-6`
  (deeper than this section's other cites, which are relative to
  `dbt-wiki/tests/`) and
  `test_fixture_project.py:14-15` say "0 custom models";
  `test_filler_models.py:87` asserts `>= 6` because "sibling trap tasks
  may still be landing" — a window that closed, and which
  now contradicts `test_build_sparse_variant.py:109` asserting exactly 10
  on the same fixture.
- **`strip_sql_comments.py` is literal-aware for single quotes only.**
  `strip_sql_comments.py:24-41`. A double-quoted SQL identifier
  containing `--` or `/*` (legal in DuckDB/dbt) would be silently
  corrupted. Not exercised by today's fixture. Either handle `"` the same
  way, or state the single-quote-only scope in the docstring.
- **`duckdb` and `PyYAML` are imported directly but declared only
  transitively** through `dbt-duckdb==1.10.1`
  (`requirements.txt:8-9` vs `conftest.py:18`, `grader.py:54`,
  `test_build_sparse_variant.py:17`). Add explicit direct pins.
- **`conftest.py` imports `duckdb` at module scope**, so the pure-Python
  grader tests cannot run without the full dbt install. Deferring the
  import would let `test_grader.py` run on a bare pytest.
- **The `dbt … --project-dir X --profiles-dir X` invocation is hand-rolled
  at three sites** (`conftest.py:44`, `test_fixture_project.py:20`,
  `test_build_sparse_variant.py:88`). Parameterizing
  `run_dbt(project_dir=…)` would collapse all three; each site currently
  has a documented reason, which is why this is a nit.

## Still the real fix, still deferred

Authoritative per-question invariant enforcement needs
`claude -p --output-format stream-json` plus a semantic check. Until then
the grader's prohibition check is advisory by construction (corrected
2026-08-07 — see the campaign doc journal), and 3 of the 5 gold questions
have no substring-checkable prohibition at all.

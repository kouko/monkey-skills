# dbt-wiki Quality Campaign — work queue & state

> Goal: for ANY dbt project, `dbt-wiki` produces (via `pack`) a skill that
> effectively answers business questions with executable SQL.
> Operationalized: the packed skill, driven by a blind agent, answers a
> gold question set with KNOWN answers, end-to-end, across a project
> matrix (dialect × language × comment-density × scale).
>
> Rhythm: agent iterates (session or nightly), human merges weekly batches.
> Every item ships via TDD + red-line scan + 2-round blind branch review + PR.
> All fixture content synthetic. This file is the cross-session handoff anchor.

## Phase 1 — loop enablers (build the objective function first)

- [x] **W1: L2 end-to-end harness (DuckDB fixture)** — synthetic dbt project
  (`tests/fixtures/` at plugin root, dbt-duckdb, ~10 models, seeded data)
  with planted guardrail traps: pre-aggregated ratio column (AVG trap),
  compound-key join (grain fan-out), categorical `value_domain` w/
  accepted_values, forward-dated amortization table (MAX(date) trap),
  prefixed regional twins (scope-undercount trap), mixed comment density.
  Plus `gold-questions.yml`: question → expected answer (exact number from
  seed data) + required invariants. Runner: blind headless agent executes
  init → pack → answer-the-questions against the .duckdb file; grader
  compares numbers. **This makes "effective SQL skill" a measurable claim.**
- [ ] **W2: cross-doc consistency lint** — extract invariant statements
  duplicated across pack SKILL.md / bundle-format / template /
  generation-guidance and mechanically diff the copies. Rationale: 100% of
  R1 blind-review catches in the last two PRs were this defect class
  (stale copy in an untouched file). Promote from review-catch to build-gate.

## Phase 2 — backlog burn-down (from the 2026-07-07 three-agent design review)

High:
- [ ] B1: rescan ~450 lines inline pseudocode → shipped TDD'd scripts
  (includes real `list | set` TypeError at old :203/:540)
- [ ] B2: materiality map lifecycle — cosmetic-stale pages outlive the map
  that classified them; second-and-later sync silently re-treats as material
- [ ] B3: init Phase B resume — no checkpoint; mid-run death re-distills everything
- [ ] B4: init re-run merge contract contradiction (preserve-User-Notes vs
  generator has no merge mode) — add `--merge` or rule re-run semantics
Medium:
- [ ] B5: distill-spec §0 triplication → shared-page-rules.md reference
- [ ] B6: init SKILL.md ~110 lines pseudocode duplicating build_evidence_pages.py internals
- [ ] B7: log.md template dual-spec (SKILL.md vs SCHEMA.md) + missing dialect line
- [ ] B8: stale in-file version headers (rescan "v2.0" etc.)
- [ ] B9: redistill-vs-review stale-clearing convention mismatch
- [ ] B10: sync couples to sibling skills by step number
- [ ] B11: shell-var continuity assumptions across Bash calls in init (state.json)
- [ ] B12: query/SKILL.md scope boundary vs packed bundle (routing line)
- [ ] B13: review skill missing description in installed listing (packaging?)
- [ ] B14: pack Step 2 freeze is manual copy → freeze_knowledge script (count-parity
  now gates it, but script removes the manual step entirely)
Low (next-touch, from PR reviews): flatten_links anchored-link backstop;
`./sibling.md` over-delink; `evid` counter naming; cap_summary 81-char CJK edge.

## Phase 3 — generalization sweep (needs W1)

- [ ] G1: fixture matrix expansion — en-language project; ~~sparse-comment
  project (comments-as-truth assumption stress)~~ **done 2026-07-10, see
  Journal — scored 5/5, no degradation**; snowflake/bigquery dialect
  compile targets (lineage + guidance dialect handling); 100+ model scale
- [ ] G2: probe each matrix cell with the blind runner; triage failures into
  Phase-2-style items (distillation quality on comment-poor projects is the
  predicted weak spot — dbt-wiki treats comments as source of truth)
- [ ] G3: gold-question difficulty ladder (single-table → compound-grain join →
  twin-scope → temporal trap → ambiguous-question-should-ask)

## Phase 4 — unattended operation

- [ ] U1: nightly loop instruction file (queue-driven, budget breaker,
  kill-switch sentinel, journal, serial one-item-per-night, no version pre-bump)
- [ ] U2: local cron + weekly digest; human merge batch stays

## Journal

- 2026-07-08: campaign opened. Prior context: 3.2.0 (consumer-efficiency
  batch) + 3.2.1 (grep-first index) shipped; ~14 design-review findings
  seeded as Phase 2. Real-project dogfood (private, 11 rounds) converged —
  its generic defects are all promoted here already.
- 2026-07-10: W1 shipped — 11-task SDD plan
  (`docs/loom/plans/2026-07-08-w1-l2-e2e-harness.md`), all tasks
  spec-reviewer + code-quality-reviewer PASS/PASS_WITH_NOTES, committed on
  `feat/dbt-wiki-w1-l2-e2e-harness`. The Task 11 real end-to-end run (real,
  non-mocked headless `claude -p`, `--dangerously-skip-permissions`
  opt-in) scored **5/5 (100%)** on the gold question set — the harness's
  first live measurement of "effective SQL skill" and it passed cleanly:
  correct weighted-ratio/fan-out/categorical/as-of/regional-twins answers,
  zero invariant failures, zero pack-bundle or `.dbt-wiki/` leak into
  version control (report: `dbt-wiki/tests/reports/w1-e2e-run.json`,
  gitignored). Two known limitations carried forward, not blocking: (1)
  the grader's invariant check against this real run is advisory-only —
  `--output-format json` exposes only the final assistant message, not a
  full SQL transcript, so a future increment wanting authoritative
  per-question invariant enforcement needs `--output-format stream-json`;
  (2) only 2 of 5 gold questions' prohibitive invariants name an uppercase
  SQL aggregate the grader can mechanically ban (avg_ratio's `AVG(`,
  amortization's `MAX(`) — the other 3 (fanout, categorical,
  regional_twins) have no substring-checkable prohibition and silently
  pass grader-side (also deferred to a future stream-json-based semantic
  check). Next candidate: W2 (cross-doc consistency lint) per the stated
  rhythm, or Phase 3 (G1-G3, gated on W1 — now unblocked).
- 2026-07-10: G1's comment-density slice shipped — a 3-task SDD plan
  (`docs/loom/plans/2026-07-10-g1-sparse-comment-fixture.md`) added a
  dependency-free SQL comment stripper, a fixture-variant builder that
  derives (never hand-duplicates) a sparse-comment copy of the W1
  fixture, and a second real end-to-end run against that sparse variant.
  **Result: 5/5 (100%), an exact match to W1's full-comment baseline —
  delta 0.0pp.** Stripping every inline SQL comment from all 10 models
  did NOT degrade dbt-wiki's answer accuracy on this gold-question set.
  This is a genuine negative result, not a non-finding: the
  "comments-as-source-of-truth" weak spot the campaign predicted did not
  manifest here, at least at this fixture's scale (10 models) and
  question difficulty (5 traps, single-project). It does NOT rule out
  degradation on a larger or more ambiguous project — G1's remaining two
  dimensions (dialect, 100+ model scale) and G2 (probing failures across
  the full matrix) are exactly where a real degradation might still turn
  up. G1 checklist item stays unchecked — only the sparse-comment slice
  is done; dialect + scale remain.
- 2026-08-07: U1's execution-stage slice shipped — a 4-task SDD plan
  (`docs/loom/plans/2026-07-28-phase2-loop-execution-only.md`) that
  **replaced** U1's original "build our own nightly loop" framing. The
  redesign composes `loom-design/scripts/pipeline/batch_queue.py` (queue, state,
  circuit breaker, worktree isolation — all already built and hardened
  twice since) instead of duplicating it, and splits the work by review
  status rather than by clock time: a **planning stage** (interactive,
  unchanged — brainstorm → plan → `Plan-document-reviewer verdict: PASS`)
  and an **execution stage** (`scripts/phase2-loop/ROUTINE.md`) that only
  ever dispatches segment 3 against an already-frozen plan. Delivered: the
  kill switch + scope guard (`safety_gates.py`), the campaign-journal
  writer, `queue_entry.py` (entry authoring + the backlog-description
  lookup the scope guard reads), and an integration proof that the drafted
  TOML round-trips through `batch_queue.py`'s `load_queue` + `check_frozen`.
  Deliberately NOT done: no real `docs/loom/QUEUE.toml` is created and no
  schedule is registered — both wait for the first Phase 2 item to actually
  be planned, and the schedule needs a separate explicit go-ahead. U1's
  checklist box stays unchecked for that reason (same precedent as G1
  above): the machinery exists, the loop has never run. No Phase 2 backlog
  item (B1-B14) has been burned down yet.
- 2026-08-07: **Correction to the 2026-07-10 W1 entry's invariant caveat
  above.** That entry called the grader's invariant check "advisory-only"
  for the real runs, but the code hard-gated on it: `QuestionResult.passed`
  required an empty `invariant_failures`, so the documented posture and the
  implemented one disagreed. Whole-branch review found the consequence — a
  *correct* as-of answer expressed as `WHERE as_of_date = (SELECT
  MAX(as_of_date) … WHERE as_of_date <= '<date>')` was mechanically failed
  by the `MAX(`-ban, and the fixture's own reference model
  `fct_amortization_trap.sql` would have been graded as violating its own
  invariant. The check is now advisory in code as well: `passed` is decided
  by value correctness, flags are recorded and counted
  (`GradeReport.invariant_flag_count`) for a human to read. **The reported
  W1 5/5 and G1 5/5 / 0.0pp figures are unaffected** — both runs had zero
  invariant failures, so no result changes under either rule. The
  stream-json-based semantic check named in the W1 entry remains the real
  fix and remains deferred.

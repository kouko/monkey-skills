# Plan: goal-loop harness v1 — target-agnostic iterate-until-met skeleton

> SUPERSEDED (2026-07-23): scope re-cut to obsidian wiki-update — see
> `2026-07-23-wiki-update-loop.md`. Kept for the task-shape record;
> never dispatched.

Source brief: docs/loom/specs/2026-07-23-goal-loop-harness.md
Total tasks: 8
Critical-path depth: 5 (≤5) — T1→T2→T3→T5→T8; T6 parallel at level 1
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-23, round 2, 14/14 checks)

Notes:
- Change-folder binding: N/A, loudly — the two non-archived
  `docs/loom/<change-id>/` folders (2026-07-12-us-sec-primary-source-layer,
  2026-07-19-8k-prose-kpi-intake) belong to shipped investing arcs
  awaiting archive, not this work; input is the brainstorming brief only.
- Correction vs ratified fork (disclosed at kickoff): wiki-lint's 15
  checks are LLM-executed prose today (no scripts/); adapter #2 therefore
  includes T6, a mechanical validator for the deterministic error-severity
  subset. `references/lint-checks.md` stays SSOT for check semantics; the
  validator implements its mechanical subset and carries a lockstep note
  (drift lesson: lint-checks.md is a known second drift surface).
- Repo memory honored: never `git add -A`; obsidian/ working-tree edits
  out of scope; plugin version bumps ride their owning task.
- Decision 3 disclosure: the courier transport gap's sandbox-external
  re-exec half is deliberately DEFERRED (brief: "do NOT block v1 on it,
  disclose instead") — v1 ships exit-code-only verdict logic + persisted
  grade transcripts (T1/T3); re-exec rides the existing CI-side arc in
  BACKLOG.
- Amendment (2026-07-23, post-PASS): supplementary research round 2
  added brief §Design constraints 1-5; T3/T6/T7 Descriptions amended
  additively (structural scorecard + size circuit-breaker in T3;
  conservation counters in T6; safe/unsafe action tiering + ratchet
  pass-rule in T7). No field/DAG/depth/Acceptance-shape change —
  re-review skipped per writing-plans §Amending a PASS plan; proposal
  expiry (constraint 2 second half) rides T4's SKILL.md protocol text.

## Task 1 — Generic verdict CLI (extract + parameterize)
- Description: Extract `improve_loop_verdict.py`'s compare/confirm/
  budget-cap/plateau verbs into a target-agnostic
  `goal_loop_verdict.py` (adapter-parameterized: pass-rule, budget kind,
  plateau window; consumes only case-id/pass tuples + grader exit codes;
  no principles vocabulary). Define the adapter-config JSON schema
  (executor prompt path+model, grader command array + pass rule,
  case source, edit-surface dir + allow-list, budgets, criteria file).
- Module: dev-workflow/skills/goal-loop
- Files touched: dev-workflow/skills/goal-loop/scripts/goal_loop_verdict.py,
  dev-workflow/skills/goal-loop/scripts/test_goal_loop_verdict.py,
  dev-workflow/skills/goal-loop/scripts/adapter_schema.json
- Context paths:
  - loom-product-principles/scripts/improve_loop_verdict.py
  - .claude/workflows/principles-improve-loop.js
- Acceptance:
  - RED: test_goal_loop_verdict.py::test_compare_win_and_plateau_on_toy_adapter
    fails (module absent)
  - GREEN: pytest passes — toy adapter fixture exercises compare-win,
    no-win, plateau exit, budget-cap exit; all verdicts via exit codes,
    zero LLM text parsed
- External surfaces: none (stdlib only, mirrors source CLI)
- Dependencies: none
- Independent: false
- Brief item covered: "Adapter contract (per target): executor…grader…
  seed/case source, edit surface…budget caps" (Decision 1 / Current
  State Evidence) + "keep verdict logic mechanical (exit codes)"
  (Decision 3)

## Task 2 — Stuck-fingerprint brakes + escape-hatch verdict
- Description: Add change-course detection to `goal_loop_verdict.py`:
  (a) same-failure-signature seen 3x across rounds (hash of failing
  case-ids + grader exit pattern), (b) no-new-information round (round
  delta empty vs previous), (c) regression (pass count decreased) —
  each yields a distinct STUCK exit code the harness must translate
  into stop-and-report (blockers report), not retry.
- Module: dev-workflow/skills/goal-loop
- Files touched: dev-workflow/skills/goal-loop/scripts/goal_loop_verdict.py,
  dev-workflow/skills/goal-loop/scripts/test_goal_loop_verdict.py
- Context paths:
  - dev-workflow/skills/goal-loop/scripts/goal_loop_verdict.py (T1 output)
- Acceptance:
  - RED: test_goal_loop_verdict.py::test_stuck_fingerprint_three_strikes fails
  - GREEN: three-strikes, no-new-info, and regression fixtures each
    return their STUCK exit; healthy-progress fixture does not
- External surfaces: none
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "port OpenHands-style stuck rules (same-grader-
  failure 3x, no-new-info rounds) into the generic verdict CLI" (Decision 4)

## Task 3 — Generic goal-loop Workflow skeleton
- Description: Author `.claude/workflows/goal-loop.js`: reads an
  adapter-config JSON (T1 schema), runs criteria-freeze preflight
  (criteria file must exist + hash recorded before round 1; mid-loop
  criteria edit → hard stop requiring human ratification), then rounds
  of one-change-per-round executor dispatch → grader courier (exit codes
  only, transcript persisted) → goal_loop_verdict.py verdicts →
  ledger append; exits = win-confirmed / plateau / budget / STUCK
  (emit blockers report per escape-hatch contract); proposal-branch
  discipline (local commit only, never push/merge); edit-surface
  allow-list guard. Proposal close-out emits a STRUCTURAL scorecard
  (diff lines/files, touched-protected-files flag, grader exit trail —
  brief §Design constraints 1) and enforces a size circuit-breaker
  (over-threshold diff → stop, request split; §Design constraints 2).
- Module: .claude/workflows
- Files touched: .claude/workflows/goal-loop.js,
  dev-workflow/skills/goal-loop/scripts/test_goal_loop_workflow.py
- Context paths:
  - .claude/workflows/principles-improve-loop.js
  - .claude/workflows/principles-replay-matrix.js
  - loom-product-principles/scripts/ (existing workflow test style)
- Acceptance:
  - RED: test_goal_loop_workflow.py::test_skeleton_parses_and_guards fails
  - GREEN: `node --check` clean; marker asserts for criteria-freeze
    preflight, one-change schema, STUCK→blockers-report path,
    never-push guard, allow-list guard; guard functions extracted and
    exercised via `node -e` (same technique as
    test_improve_loop_workflow.py)
- External surfaces: Claude Code Workflow runtime (agent()/pipeline();
  no Date.now/Math.random — resume-safe, per existing workflows)
- Dependencies: Tasks 1, 2 complete first
- Independent: false
- Brief item covered: "ONE target-agnostic loop harness…generic Workflow
  skeleton + adapter contract" + "criteria compiled to a frozen criteria
  file BEFORE round 1…criteria edits mid-loop require human
  ratification" + "escape-hatch clause" (Decision 1/2/4) + "grade
  transcript persisted" courier-transport mitigation (Decision 3)

## Task 4 — goal-loop SKILL.md front-end + CI wiring + version bump
- Description: Author `dev-workflow/skills/goal-loop/SKILL.md`
  (adapter contract spec, criteria-freeze protocol incl. the
  hidden/held-out criteria rule, escape-hatch contract, when-NOT-to-use:
  no mechanical oracle → no loop); add a pytest step for
  `dev-workflow/skills/goal-loop/scripts/` to dev-workflow-ci.yml
  (runnable-capability rule: new test suite declared in CI command
  surface); bump dev-workflow 2.25.0→2.26.0 + CHANGELOG + codex
  manifest sync.
- Module: dev-workflow
- Files touched: dev-workflow/skills/goal-loop/SKILL.md,
  .github/workflows/dev-workflow-ci.yml,
  dev-workflow/.claude-plugin/plugin.json,
  dev-workflow/.codex-plugin/plugin.json, dev-workflow/CHANGELOG.md
- Context paths:
  - dev-workflow/skills/goal-loop/scripts/ (T1-T3 outputs)
  - docs/loom/specs/2026-07-23-goal-loop-harness.md
- Acceptance:
  - RED: dev-workflow-ci has no pytest step (grep fails);
    goal-loop/SKILL.md absent
  - GREEN: CI yml runs the new suite; SKILL.md present, folder-structure
    hook clean; manifests synced at 2.26.0
- External surfaces: GitHub Actions yml (mirror existing loom-code-ci
  pytest step shape)
- Dependencies: Task 3 completes first
- Independent: true
- Brief item covered: "Build ONE target-agnostic loop harness" surface
  layer; runnable-capability rule (plan-format §External surfaces)

## Task 5 — Adapter #1 (workflows half): refactor principles pair onto the skeleton
- Description: Refactor `principles-improve-loop.js` +
  `principles-replay-matrix.js` into an adapter config + thin wrappers
  consuming the T3 skeleton; delete the duplicated skeleton logic from
  both files (extraction = deletion; net LOC decrease).
- Module: .claude/workflows
- Files touched: .claude/workflows/principles-improve-loop.js,
  .claude/workflows/principles-replay-matrix.js
- Context paths:
  - .claude/workflows/goal-loop.js (T3 output)
  - dev-workflow/skills/goal-loop/scripts/adapter_schema.json (T1)
- Acceptance:
  - RED: `node -e` guard-extraction check against the refactored files
    fails while monolith logic remains (duplicated skeleton markers
    still present)
  - GREEN: both files `node --check` clean, consume the skeleton, and
    net LOC across the pair decreases; no skeleton-logic duplication
    markers remain
- External surfaces: none new
- Dependencies: Task 3 completes first
- Independent: false
- Brief item covered: "that workflow becomes adapter #1 (extraction =
  deletion)" (Decision 1) + "What Becomes Obsolete"

## Task 8 — Adapter #1 (principles half): lockstep tests + version bump
- Description: Update the 5 loom-product-principles pytest suites in
  lockstep with T5's refactor (text/marker asserts move to the skeleton
  test where logic moved; adapter tests keep principles-specific
  asserts); slim `improve_loop_verdict.py` to a thin import/wrapper of
  the generic CLI where duplicated; bump loom-product-principles
  version + CHANGELOG.
- Module: loom-product-principles
- Files touched: loom-product-principles/scripts/improve_loop_verdict.py,
  loom-product-principles/scripts/test_improve_loop_workflow.py,
  loom-product-principles/scripts/test_replay_matrix_workflow.py,
  loom-product-principles/scripts/test_improve_loop_verdict.py,
  loom-product-principles/.claude-plugin/plugin.json,
  loom-product-principles/CHANGELOG.md
- Context paths:
  - .claude/workflows/principles-improve-loop.js (T5 output)
  - .claude/workflows/principles-replay-matrix.js (T5 output)
  - dev-workflow/skills/goal-loop/scripts/goal_loop_verdict.py (T1)
- Acceptance:
  - RED: test_improve_loop_workflow.py fails against the T5-refactored
    workflows (old monolith asserts)
  - GREEN: all 5 suites pass against the refactored pair + slimmed
    verdict wrapper
- External surfaces: none new
- Dependencies: Task 5 completes first
- Independent: true
- Brief item covered: "its 5 pytest suites keep the refactor honest"
  (Decision 1) + "tests updated in lockstep, not duplicated" (What
  Becomes Obsolete)

## Task 6 — wiki-lint mechanical validator (error-severity subset)
- Description: Author `obsidian/skills/wiki-lint/scripts/wiki_lint_check.py`
  implementing the deterministic error-severity checks — L01 frontmatter
  completeness, L02 summary length, L03 required sections, L04 wikilink
  format, L07 broken intra-wiki wikilinks, L14 source-wikilink format —
  per `references/lint-checks.md` (SSOT; script carries a lockstep
  header comment naming it). Output: violations as JSON lines + count;
  exit 0 = clean, 1 = violations. Also emits conservation counters
  (per-file word/link/heading counts) for the T7 ratchet
  (brief §Design constraints 4). LLM-judged checks (L05/L06/L08-L13/
  L15) explicitly out of scope, listed in --help.
- Module: obsidian/skills/wiki-lint
- Files touched: obsidian/skills/wiki-lint/scripts/wiki_lint_check.py,
  obsidian/skills/wiki-lint/scripts/test_wiki_lint_check.py,
  obsidian/skills/wiki-lint/SKILL.md (one pointer line: mechanical
  subset available via script), obsidian/.claude-plugin/plugin.json,
  obsidian/CHANGELOG.md
- Context paths:
  - obsidian/skills/wiki-lint/references/lint-checks.md
  - obsidian/skills/wiki-lint/references/language-policy.md
- Acceptance:
  - RED: test_wiki_lint_check.py::test_detects_seeded_violations fails
    (script absent)
  - GREEN: fixture mini-wiki with seeded violations of each covered
    check yields exactly those violations; clean fixture exits 0
- External surfaces: none (stdlib + pathlib; no Obsidian API)
- Dependencies: none
- Independent: true
- Brief item covered: "adapter #2 = a new cheap target with a fully
  mechanical oracle" (Smallest End State) — oracle construction half
- Note: obsidian plugin CI (test-obsidian.yml) must pick up the new
  pytest file; verify and wire if absent (runnable-capability rule).

## Task 7 — Adapter #2: wiki-lint fix-loop config + sandbox smoke
- Description: Author the wiki-lint adapter config (executor prompt:
  fix ONE violation class per round within wiki/ allow-list, actions
  pre-tiered safe/unsafe — retarget link / add alias = safe auto-run,
  ANY deletion = unsafe proposal-only (brief §Design constraints 3);
  grader = `wiki_lint_check.py`; pass rule = violation count strictly
  decreasing AND conservation ratchet holds (content counters may not
  net-decrease unflagged, §Design constraints 4); win = 0; budgets +
  plateau per T1 schema) and run one sandboxed
  smoke: fixture mini-wiki with seeded violations → loop converges to 0
  or stops honestly (STUCK/plateau) with blockers report; record run
  under docs/loom/dogfood/2026-07-23-goal-loop-wiki-lint-smoke/.
- Module: dev-workflow/skills/goal-loop (adapter config home:
  dev-workflow/skills/goal-loop/assets/wiki-lint-adapter.json)
- Files touched: dev-workflow/skills/goal-loop/assets/wiki-lint-adapter.json,
  docs/loom/dogfood/2026-07-23-goal-loop-wiki-lint-smoke/ (run artifacts)
- Context paths:
  - .claude/workflows/goal-loop.js (T3)
  - obsidian/skills/wiki-lint/scripts/wiki_lint_check.py (T6)
- Acceptance:
  - RED: smoke run attempted before adapter config exists → skeleton
    refuses (schema validation fail)
  - GREEN: smoke run completes on the fixture wiki: violations
    monotonically non-increasing across rounds, terminal state ∈
    {win-0, plateau, STUCK-with-blockers-report}; ledger + grade
    transcripts persisted
- External surfaces: Claude Code Workflow runtime (headless executor
  dispatches; CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0 if headless —
  known 600s trap)
- Dependencies: Tasks 3, 6 complete first
- Independent: true
- Brief item covered: "adapter #2…proving generality" (Smallest End
  State) + "wiki-lint auto-fix loop over the obsidian vault's wiki/"
  (Open Questions 1 RESOLVED)

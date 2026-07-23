# Plan: wiki-update — one-verb maintenance with mechanical fix loop

Source brief: docs/loom/specs/2026-07-23-wiki-update-maintenance-loop.md
Total tasks: 9
Critical-path depth: 5 (≤5) — T1→T2→T3→T4→T7; wide shallow tail
(T5/T6/T8/T9 fan out at their levels)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-23, round 2, 14/14 checks)

Progress (all DONE, 2026-07-24):
- T1 ea1c866c+d9f2aeb5 (R2: parse robustness + NFC) — spec PASS / quality PASS(R2)
- T2 38433af1+0aeca54a (R2: converging-not-stuck + loader validation) — spec PASS / quality PASS(R2)
- T3 96cc5bcd+b38c58b3 (R2: git -C assertions + honest commit-failure) — spec PASS / quality PASS(R2)
- T4 a260f621+0fd5b7e3 (R2: cold-read gap patches) — cold-read 6/6 correct
- T5 6d2c7e86 / T6 2b59fb1d / T7 09d4a23d (obsidian 3.20.0) / T8 018e5461 — light lane, whole-branch review covers
- T9 9a45166b+690fe7e0 — GREEN; smoke: 2 classes converged on proposal branch, ratchet honest-stop exercised; Finding #1 (words-ratchet vs retarget) → next-touch

Notes:
- Change-folder binding: N/A, loudly — the two non-archived
  `docs/loom/<change-id>/` folders belong to shipped investing arcs;
  input is the brainstorming brief only.
- Supersedes `2026-07-23-goal-loop-harness.md` plan (never dispatched).
- Bounded duplication disclosure: T2's loop_verdict.py is an adapted
  copy of loom-product-principles/scripts/improve_loop_verdict.py
  (origin header note required); extraction to a shared skeleton is
  parked in BACKLOG with a Rule-of-Three re-trigger (T8 writes the
  entry).
- Repo memory honored: never `git add -A`; unrelated working-tree
  files stay out; obsidian plugin version bump rides T7.

## Task 1 — Mechanical validator with conservation counters
- Description: Author `wiki_lint_check.py` implementing the
  deterministic error-severity checks L01 (frontmatter completeness
  per page-type), L02 (summary length), L03 (required body sections),
  L04 (wikilink format), L07 (broken intra-wiki wikilinks, alias-aware,
  `## Source` exemption), L14 (source-wikilink format) per
  `references/lint-checks.md` (SSOT; lockstep header comment naming
  it). Output: violations as JSONL (check id, file, line, detail) +
  per-file conservation counters (word/link/heading counts) + summary
  counts; exit 0 clean / 1 violations. Stdlib-only; a test asserts no
  non-stdlib and no repo-level imports (plugin self-containment).
  LLM-lane checks listed as out-of-scope in --help.
- Module: obsidian/skills/wiki-lint
- Files touched: obsidian/skills/wiki-lint/scripts/wiki_lint_check.py,
  obsidian/skills/wiki-lint/scripts/test_wiki_lint_check.py
- Context paths:
  - obsidian/skills/wiki-lint/references/lint-checks.md
  - obsidian/skills/wiki-lint/references/language-policy.md
- Acceptance:
  - RED: test_wiki_lint_check.py::test_detects_seeded_violations fails
    (script absent)
  - GREEN: fixture mini-wiki with seeded violations of each covered
    check yields exactly those violations (JSONL shape asserted);
    clean fixture exits 0; conservation counters correct on fixtures;
    stdlib-only import test passes
- External surfaces: none (stdlib + pathlib)
- Dependencies: none
- Independent: false
- Brief item covered: "Mechanical validator wiki_lint_check.py in
  wiki-lint/scripts/ — deterministic error-severity subset…violations
  as JSONL + conservation counters" (Decision 1)

## Task 2 — Loop verdict CLI (brakes + ratchet)
- Description: Author `loop_verdict.py` in wiki-update/scripts/:
  verbs compare (round N vs N-1 violation counts), plateau (K rounds
  no improvement), budget (round/token caps), stuck (same-failure-
  signature 3×, no-new-info round, regression), ratchet (conservation
  counters may not net-decrease without a flagged justification file).
  All verdicts via distinct exit codes; consumes T1's JSONL +
  counters; adapted copy of improve_loop_verdict.py with origin
  header note (bounded-duplication disclosure per plan Notes).
- Module: obsidian/skills/wiki-update
- Files touched: obsidian/skills/wiki-update/scripts/loop_verdict.py,
  obsidian/skills/wiki-update/scripts/test_loop_verdict.py
- Context paths:
  - loom-product-principles/scripts/improve_loop_verdict.py
  - obsidian/skills/wiki-lint/scripts/wiki_lint_check.py (T1 output)
- Acceptance:
  - RED: test_loop_verdict.py::test_stuck_three_strikes_and_ratchet
    fails (module absent)
  - GREEN: fixtures exercise win/no-win/plateau/budget/stuck(3 kinds)/
    ratchet-breach — each returns its distinct exit code; healthy-
    progress fixture returns none
- External surfaces: none
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "Loop verdict CLI…compare/plateau/budget verbs +
  stuck fingerprints + conservation-ratchet check; exit-code verdicts
  only" (Decision 2)

## Task 3 — Loop engine workflow
- Description: Author `wiki_fix_loop.js` in wiki-update/scripts/:
  criteria-freeze preflight (violations snapshot + check-config hash
  recorded before round 1; config change mid-loop → hard stop),
  one-violation-class-per-round executor dispatch with safe-tier
  action allow-list (retarget wikilink / add alias / fill derivable
  field; deletions structurally excluded from the executor contract),
  grader = T1 validator run, verdicts = T2 CLI, per-round ledger
  append, structural scorecard (diff lines/files, violation delta,
  rounds), size circuit-breaker (over-threshold → stop requesting
  split), proposal exit (vault git branch, local commits only, never
  merge/push), STUCK → blockers report. Resume-safe (no
  Date.now/Math.random; timestamps via args), mirroring existing
  workflow discipline.
- Module: obsidian/skills/wiki-update
- Files touched: obsidian/skills/wiki-update/scripts/wiki_fix_loop.js,
  obsidian/skills/wiki-update/scripts/test_wiki_fix_loop.py
- Context paths:
  - .claude/workflows/principles-improve-loop.js (structure prior art)
  - obsidian/skills/wiki-update/scripts/loop_verdict.py (T2 output)
- Acceptance:
  - RED: test_wiki_fix_loop.py::test_engine_parses_and_guards fails
  - GREEN: `node --check` clean; marker asserts for freeze preflight,
    safe-tier allow-list, never-merge/push guard, circuit-breaker,
    STUCK→blockers path; guard functions extracted and exercised via
    `node -e` (same technique as test_improve_loop_workflow.py)
- External surfaces: Claude Code Workflow runtime (scriptPath
  invocation; resume-safe constraints per existing workflows)
- Dependencies: Task 2 completes first
- Independent: false
- Brief item covered: "Loop engine wiki_fix_loop.js…criteria freeze,
  one-violation-class-per-round, safe-tier enforcement, ledger,
  structural scorecard, size circuit-breaker, proposal-branch exit,
  escape hatch" (Decision 3)

## Task 4 — wiki-update SKILL.md (orchestrator front-end)
- Description: Author `obsidian/skills/wiki-update/SKILL.md` — the
  5-step verb (delegate wiki-ingest → delegate wiki-cross-linker →
  run fix loop via Workflow scriptPath `${CLAUDE_SKILL_DIR}/scripts/
  wiki_fix_loop.js` → work-order triage (page-creation → ingest list,
  near-dup → wiki-merge candidates, LLM-lane findings → wiki-lint
  report) → close-out scorecard in conversation language); freeze
  protocol; `/goal` routing line (in-session one-sentence goal →
  /goal; this pipeline → wiki-update); when-NOT-to-use; trigger
  description with zh/ja keywords per family convention.
- Module: obsidian/skills/wiki-update
- Files touched: obsidian/skills/wiki-update/SKILL.md
- Context paths:
  - obsidian/skills/wiki-update/scripts/ (T1-T3 outputs)
  - docs/loom/specs/2026-07-23-wiki-update-maintenance-loop.md
  - obsidian/skills/wiki-ingest/SKILL.md (delegation surface)
- Acceptance:
  - RED: obsidian/skills/wiki-update/SKILL.md absent
  - GREEN: SKILL.md present, folder-structure hook clean, contains the
    5-step list, freeze protocol, /goal routing line, scriptPath
    invocation, work-order triage table
- External surfaces: none (prose contract)
- Dependencies: Task 3 completes first
- Independent: false
- Brief item covered: "Orchestrator SKILL.md obsidian:wiki-update —
  the 5-step verb…freeze protocol; /goal routing line; report
  language" (Decision 4)

## Task 5 — wiki-lint pointer line
- Description: Add one line to wiki-lint SKILL.md noting the
  mechanical error-severity subset is runnable via
  `scripts/wiki_lint_check.py` (read-only charter unchanged).
- Module: obsidian/skills/wiki-lint
- Files touched: obsidian/skills/wiki-lint/SKILL.md
- Context paths:
  - obsidian/skills/wiki-lint/scripts/wiki_lint_check.py (T1 output)
- Acceptance:
  - RED: grep for wiki_lint_check.py in wiki-lint/SKILL.md fails
  - GREEN: pointer line present; no other behavioral text changed
    (diff limited to the one line)
- External surfaces: none
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "wiki-lint gains a script + one pointer line
  only" (Out of Scope guardrail, Decision 1 surface)

## Task 6 — obsidian CI pytest wiring
- Description: Wire a pytest step for `obsidian/skills/*/scripts/`
  into test-obsidian.yml (runnable-capability rule: new test suites
  declared in the CI command surface), mirroring loom-code-ci's
  pytest step shape.
- Module: .github/workflows
- Files touched: .github/workflows/test-obsidian.yml
- Context paths:
  - .github/workflows/loom-code-ci.yml (step shape prior art)
  - obsidian/skills/wiki-lint/scripts/test_wiki_lint_check.py (T1)
- Acceptance:
  - RED: grep for a pytest invocation over obsidian skills scripts in
    test-obsidian.yml fails
  - GREEN: yml step present and lists the correct path glob; yml
    parses (actionlint or python yaml load)
- External surfaces: GitHub Actions yml
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: runnable-capability rule (plan-format §External
  surfaces) for Decision 1/2 test suites

## Task 7 — obsidian plugin ship surface
- Description: Bump obsidian plugin version, add CHANGELOG entry
  (validator + wiki-update skill + loop engine), run codex manifest
  sync.
- Module: obsidian
- Files touched: obsidian/.claude-plugin/plugin.json,
  obsidian/.codex-plugin/plugin.json, obsidian/CHANGELOG.md
- Context paths:
  - obsidian/CHANGELOG.md (entry format)
  - scripts/sync_codex_manifests.py
- Acceptance:
  - RED: plugin.json version unchanged from current (diff empty)
  - GREEN: both manifests bumped in sync (sync script exits 0 in
    --check mode); CHANGELOG entry describes all three surfaces
- External surfaces: none
- Dependencies: Task 4 completes first
- Independent: true
- Brief item covered: "obsidian version bump" (Decision 4 ship surface)

## Task 8 — BACKLOG park entry
- Description: Append BACKLOG entry per its header format: general
  goal-loop harness extraction PARKED; re-trigger = a third real
  convergence-loop target appears (Rule of Three — extract the shared
  skeleton from wiki_fix_loop.js + principles-improve-loop.js then);
  origin = this arc's superseded brief.
- Module: docs/loom
- Files touched: docs/loom/BACKLOG.md
- Context paths:
  - docs/loom/BACKLOG.md (entry format, header)
  - docs/loom/specs/2026-07-23-goal-loop-harness.md (superseded brief)
- Acceptance:
  - RED: grep for "goal-loop" in docs/loom/BACKLOG.md fails
  - GREEN: entry present with Status/Start(re-trigger)/Origin/What
    fields per BACKLOG header convention
- External surfaces: none
- Dependencies: none
- Independent: true
- Brief item covered: "general adapter harness (parked, BACKLOG
  Rule-of-Three re-trigger)" (Smallest End State)

## Task 9 — Sandbox smoke dogfood
- Description: Run the loop end-to-end on a sandboxed fixture
  mini-wiki (copy with seeded violations of each covered class, its
  own git init): loop converges (violations monotonically
  non-increasing; terminal state ∈ {win-0, plateau, STUCK-with-
  blockers-report}), safe-tier holds (zero deletions in diff), ratchet
  holds, proposal branch + ledger + scorecard produced. Record run
  artifacts under docs/loom/dogfood/2026-07-23-wiki-update-loop-smoke/.
- Module: docs/loom/dogfood
- Files touched: docs/loom/dogfood/2026-07-23-wiki-update-loop-smoke/
  (run artifacts + report)
- Context paths:
  - obsidian/skills/wiki-update/scripts/wiki_fix_loop.js (T3 output)
  - obsidian/skills/wiki-lint/scripts/wiki_lint_check.py (T1 output)
- Acceptance:
  - RED: the seeded fixture initially FAILS the convergence assertion
    (validator reports N>0 violations and no ledger/proposal exists) —
    asserted in the smoke report's "before" section
  - GREEN: smoke report shows terminal state + monotone violation
    counts + zero-deletion diff assertion + ledger/scorecard/proposal
    artifacts present
- External surfaces: Claude Code Workflow runtime (headless executor
  dispatches; set CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0 if headless —
  known 600s trap)
- Dependencies: Task 3 completes first
- Independent: true
- Brief item covered: "converge-or-honest-stop" loop behavior
  (Smallest End State) — end-to-end proof on fixtures before the real
  vault

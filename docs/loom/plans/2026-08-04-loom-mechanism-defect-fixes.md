# Plan: loom mechanism defect fixes (D-A / D-D / D-C / E-3)

Source brief: docs/loom/specs/2026-08-04-loom-mechanism-defect-fixes.md
Total tasks: 11
Critical-path depth: 4 (T1 → T2 → T3 → T11)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-08-04, round 2, 15/15)

## Task 1 — branch_creation_sha helper

- Description: Add `branch_creation_sha(repo: Path) -> str | None` to
  `review_scope.py`: resolve the current branch name via
  `git symbolic-ref --short -q HEAD` (None on detached HEAD), then read the
  branch's reflog OLDEST entry via `git log -g --format=%H%x1f%gs
  refs/heads/<branch>` (last output line); return that entry's `%H` sha only
  when its `%gs` subject starts with `branch: Created from` (a pruned or
  rewritten reflog whose oldest entry is not the creation entry returns
  None). Any git failure returns None. Reuse the module's existing `_git`
  helper for all invocations.
- Module: loom-code/scripts/review_scope.py
- Files touched: loom-code/scripts/review_scope.py, loom-code/scripts/test_review_scope.py
- Context paths:
  - loom-code/scripts/review_scope.py
  - loom-code/scripts/test_review_scope.py (fixture helpers `_init_upstream` / `_clone` / `_git`)
- Acceptance:
  - RED: `test_branch_creation_sha_returns_fork_sha` — fixture clone, cut a
    branch from a known commit, add commits; helper returns the cut-point
    sha. Paired negative in the same test run:
    `test_branch_creation_sha_none_on_detached_head` — detached HEAD
    returns None. (Two test functions, one behavior: "creation sha or
    honest None"; both must fail before the helper exists — pair each
    absence/None assertion with a positive fact per
    `docs/loom/memory/subprocess-red-tests-go-false-green-before-the-script-exists.md`.)
  - GREEN: both tests pass; existing `test_review_scope*.py` suites stay green.
- Reuse-adequacy:
  - Observed: returns stripped stdout or None on any failure/timeout — read loom-code/scripts/review_scope.py:106
  - Intended: `_git` runs the three new git invocations (symbolic-ref, log -g, merge-base --is-ancestor in T2).
- Dependencies: none
- Independent: true
- Brief item covered: "The remedy prefers the branch's reflog creation sha as the printed old-base" (Decision 1)

## Task 2 — remedy old-base selection prefers a usable creation sha

- Description: In `main()`'s stale-base refusal branch, compute
  `creation = branch_creation_sha(repo)`; the printed remedy's old-base
  becomes `creation` when BOTH `git merge-base --is-ancestor <base_sha>
  <creation>` AND `git merge-base --is-ancestor <creation> HEAD` hold
  (equality with base_sha passes naturally and prints the same sha as
  today); otherwise keep `base_sha` (fallback path — caveat line is Task 3,
  not this task). TRAP: `_git` returns `""` (falsy) on a SUCCESSFUL
  `merge-base --is-ancestor` (the command emits no stdout) — test both
  ancestry conditions with `is not None`, never truthiness. Update the module docstring's remedy description
  (currently `git rebase --onto <remote_sha> <base_sha> HEAD`, lines 23-27)
  to state the old-base selection: creation sha when usable, merge-base
  otherwise, and WHY (squash-merge repos: merge-base..HEAD may contain
  already-squashed foreign commits whose replay conflicts).
- Module: loom-code/scripts/review_scope.py
- Files touched: loom-code/scripts/review_scope.py, loom-code/scripts/test_review_scope.py
- Context paths:
  - loom-code/scripts/review_scope.py (main() lines 246-255, docstring lines 14-39)
  - docs/loom/specs/2026-08-04-loom-mechanism-defect-fixes.md (§Verified root cause)
- Acceptance:
  - RED: `test_cli_stale_cut_remedy_uses_creation_sha_not_merge_base` —
    fixture reproducing the stale-cut state: clone at upstream tip M0;
    local branch `prev` on M0 with 2 commits P1,P2; upstream main gains a
    squash-style commit S (content overlapping P1/P2); cut branch `arc`
    from P2, add own commit O1; fetch; run CLI. Assert exit 1 AND the
    printed remedy old-base == sha(P2) (creation sha) AND != sha(M0)
    (merge-base) AND the positive fact that the remedy line itself is
    present on stderr.
  - GREEN: new test passes; `test_cli_refuses_stale_base_with_rebase_remedy`
    (plain stale base, creation == merge-base) still passes byte-identically.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "prefers the branch's reflog creation sha ... when that sha is a descendant-or-equal of the merge-base AND an ancestor of HEAD" (Decision 1)

## Task 3 — fallback caveat line when the creation sha is unusable

- Description: When the stale-base remedy falls back to the merge-base
  (creation sha is None or fails either ancestry condition), print ONE
  extra stderr line, pinned verbatim: `review-scope: if the rebase stops
  on commits that are not this branch's own work, run git rebase --abort
  and retry with the second sha replaced by the last-line sha of: git
  reflog show <branch>` — with `<branch>` substituted by the actual branch
  name when known, left as the literal placeholder `<branch>` when
  detached. No caveat is printed when the creation sha was used (the
  remedy is already correct there).
- Module: loom-code/scripts/review_scope.py
- Files touched: loom-code/scripts/review_scope.py, loom-code/scripts/test_review_scope.py
- Context paths:
  - loom-code/scripts/review_scope.py
- Acceptance:
  - RED: `test_cli_stale_base_without_reflog_prints_caveat` — stale-base
    fixture whose branch reflog file (`.git/logs/refs/heads/<branch>`) is
    deleted before the CLI run; assert the remedy old-base == merge-base
    AND the caveat line is present (positive substring `git rebase
    --abort`). Paired negative: `test_cli_creation_sha_path_prints_no_caveat`
    — Task 2's stale-cut fixture asserts the caveat is absent AND the
    remedy line is present (absence assertion paired with a positive fact,
    per the false-green memory entry).
  - GREEN: both tests pass; full `test_review_scope*.py` suite green.
- Dependencies: Task 2 completes first
- Independent: false
- Brief item covered: "falls back to the merge-base and prints one extra stderr caveat line pointing at a verifiable action" (Decision 1)

## Task 4 — AGENTS.md remedy-mirror update

- Description: In `AGENTS.md` (line 119 region), replace the literal
  `` `git rebase --onto <remote_sha> <base_sha> HEAD` remedy also on stderr. ``
  with
  `` `git rebase --onto <remote_sha> <old_base> HEAD` remedy also on stderr (`<old_base>` = the branch's reflog creation sha when usable, else the merge-base plus a recovery caveat line). ``
  Exact-spec edit; no other AGENTS.md content changes. (Copy-sweep
  partition: brief §Copy-sweep — this is the only operative mirror that
  must change.)
- Module: AGENTS.md
- Files touched: AGENTS.md
- Context paths:
  - AGENTS.md (lines 115-123)
  - docs/loom/specs/2026-08-04-loom-mechanism-defect-fixes.md (§Copy-sweep partition)
- Acceptance:
  - RED: grep diagnostic — `grep -n "<base_sha> HEAD" AGENTS.md` currently
    returns the line (positive pre-fact); after the edit it returns
    nothing AND `grep -c "<old_base>" AGENTS.md` returns ≥1.
  - GREEN: both grep conditions hold; no other AGENTS.md lines changed
    (`git diff --stat` shows 1 file, minimal hunk).
- Review-weight: mechanical
- Dependencies: Task 2 completes first
- Independent: false
- Brief item covered: "module docstring and the `AGENTS.md` mirror describe the new semantics" (Smallest End State 1)

## Task 5 — claim_copy_sweep scans .py module docstrings

- Description: Extend `claim_copy_sweep.py` to also walk `*.py` files
  (same root, same frozen-prefix rule) and match needles against each
  file's MODULE docstring ONLY — parse with `ast.parse`, take
  `ast.get_docstring`-equivalent from the first statement when it is a
  string constant; a file that fails to parse goes on the existing
  unreadable list. Reported line numbers must be the ACTUAL file lines of
  the matched text (offset from the docstring literal's `lineno`).
  Fence detection applies to the docstring text the same way it applies
  to markdown. Non-module docstrings, comments, and other string literals
  stay out of scope by construction.
- Module: scripts/claim_copy_sweep.py
- Files touched: scripts/claim_copy_sweep.py, scripts/test_claim_copy_sweep.py
- Context paths:
  - scripts/claim_copy_sweep.py
  - scripts/test_claim_copy_sweep.py
- Acceptance:
  - RED: `test_py_module_docstring_copy_is_reported` — tmp corpus with a
    `.md` copy and a `.py` whose module docstring carries the same claim
    (hard-wrapped across a line break, exercising normalize); assert both
    files appear as operative hits AND the `.py` hit's line number equals
    the actual file line. Paired negative in the same test:
    a `.py` with the claim only in a function docstring reports NO hit
    for that file (absence paired with the positive `.md` hit).
  - GREEN: new test passes; existing `test_claim_copy_sweep.py` suite green.
- Dependencies: none
- Independent: true
- Brief item covered: "additionally scans `.py` MODULE docstrings (top-of-file string only, never the full file)" (Decision 2)

## Task 6 — sweep output names the extended scope

- Description: Update the sweep's self-describing output for the new
  scope: (a) the summary line `swept N markdown files` becomes `swept N
  markdown files and M python module docstrings` (M = count of .py files
  whose module docstring was scanned); (b) in the `LEAKS` block, replace
  the line `- anything outside \`.md\` files — a copy living in a code
  comment, a test fixture, or a commit message is out of scope by
  construction.` with `- anything outside \`.md\` files and \`.py\` module
  docstrings — a copy living in a code comment, a function or class
  docstring, a non-docstring string literal, a test fixture, or a commit
  message is out of scope by construction.`
- Module: scripts/claim_copy_sweep.py
- Files touched: scripts/claim_copy_sweep.py, scripts/test_claim_copy_sweep.py
- Context paths:
  - scripts/claim_copy_sweep.py (render() and LEAKS)
- Acceptance:
  - RED: `test_output_names_python_docstring_scope` — run on a tmp corpus;
    assert stdout contains `python module docstrings` in the summary line
    AND the new leak line text AND NOT the old absolute claim `anything
    outside \`.md\` files —` (absence paired with the two positives).
  - GREEN: test passes; suite green.
- Dependencies: Task 5 completes first
- Independent: false
- Brief item covered: "updates both its summary line and its printed leak list to name the new scope honestly" (Decision 2)

## Task 7 — D-C per-check sweep obligation sentence

- Description: In
  `loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md`
  §Verdict mapping, NEEDS_REVISION bullet, immediately after the sentence
  `List EVERY failure, not just the first — writing-plans fixes them in
  one re-dispatch round.` insert this sentence verbatim: `Before
  returning, re-scan every task against each check that failed anywhere;
  a check reported on one task but left unreported on another task with
  the same defect is a contract violation.` Add a prose-pin pytest (new
  file `loom-code/scripts/test_plan_reviewer_sweep_obligation.py`)
  asserting the sentence is present as a contiguous substring after
  whitespace-normalizing the file (per
  `docs/loom/memory/verbatim-phrase-guards-break-on-hard-line-wrap.md`).
- Module: loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md
- Files touched: loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md, loom-code/scripts/test_plan_reviewer_sweep_obligation.py
- Context paths:
  - loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md (§Verdict mapping)
- Acceptance:
  - RED: the new pytest fails before the edit (assert the pinned sentence
    in `re.sub(r"\s+", " ", text)`; pair with the positive fact that the
    anchor sentence `List EVERY failure` is already present, so the test
    cannot pass vacuously on a wrong path).
  - GREEN: pytest passes; the sentence sits inside the NEEDS_REVISION
    bullet of §Verdict mapping.
- Review-weight: mechanical
- Dependencies: none
- Independent: true
- Brief item covered: "one pinned sentence added to `plan-document-reviewer-prompt.md` §Verdict mapping" (Decision 3)

## Task 8 — E-3 capacity-recovery pointer within the word cap

- Description: Two pinned edits to
  `loom-code/skills/requesting-code-review/SKILL.md`: (a) in Step 2,
  replace `; plugin-level agent, v0.6.0 / P15-12 Phase 2, at` with
  `; plugin-level agent at` (removes the unpinned version tag; verified
  not test-pinned this session); (b) in Step 3, immediately after
  `(a single-arm verdict is degraded evidence — G4 measured why).` insert
  ` Capacity-error recovery:
  [\`dispatch-hygiene-notes.md\`](../subagent-driven-development/references/dispatch-hygiene-notes.md)
  §Capacity-error recovery.` (target section verified to exist at that
  path, heading line 8). Net word delta = −5 + 5 = 0 against the 4498/4500
  CHK-SKL-010 budget. Add a prose-pin pytest (new file
  `loom-code/scripts/test_rcr_capacity_pointer.py`) asserting the pointer
  phrase contiguous-after-normalization AND that
  `python3 scripts/check-skill-structure.py` passes for the file's plugin
  (word cap respected).
- Module: loom-code/skills/requesting-code-review/SKILL.md
- Files touched: loom-code/skills/requesting-code-review/SKILL.md, loom-code/scripts/test_rcr_capacity_pointer.py
- Context paths:
  - loom-code/skills/requesting-code-review/SKILL.md (Steps 2-3, lines 104-110)
  - loom-code/skills/subagent-driven-development/references/dispatch-hygiene-notes.md (§Capacity-error recovery)
- Acceptance:
  - RED: the new pytest fails before the edits (pointer phrase absent;
    pair with the positive fact the dead-arm anchor sentence is present).
  - GREEN: pytest passes; `wc -w` on the SKILL.md ≤ 4500 and
    check-skill-structure reports no CHK-SKL-010 violation.
- Review-weight: mechanical
- Dependencies: none
- Independent: true
- Brief item covered: "one pinned pointer sentence ... paid for by trimming the unpinned version tag ... net ≤ +2 words" (Decision 4)

## Task 9 — correct the D-A backlog entry

- Description: In
  `docs/loom/backlog/2026-08-04-review-scope-stale-base-remedy-wrong-old-base.md`,
  replace the paragraph beginning `Root-cause hypothesis (verify in the
  source before fixing):` through the end of the file with this pinned
  text (frontmatter and the evidence paragraphs above it stay untouched):

  > Root cause (verified 2026-08-04 by git-history reconstruction —
  > OVERTURNS the original hypothesis, kept here honestly): the script
  > already computes `git merge-base HEAD <ref>` at refusal time and the
  > printed `099af0c9` WAS the true merge-base. The branch had been cut
  > from `f61837ed` — the tip of the previous arc's merged-but-squashed
  > local branch `docs-loom-close-out-backlog-and-memory` — so
  > merge-base..HEAD contained 7 foreign commits whose content was already
  > squash-merged into main; squash changes patch-ids, so rebase cannot
  > skip them and their replay is what conflicted. The remedy is unsafe
  > precisely in the stale-cut state it exists to heal (second occurrence
  > of that state; see
  > `docs/loom/memory/new-arc-branch-bases-on-origin-main-not-merged-tip.md`).
  >
  > Fix shipped this arc (user-approved Option A): the remedy prefers the
  > branch's reflog creation sha as the printed old-base when it is a
  > descendant-or-equal of the merge-base and an ancestor of HEAD;
  > otherwise it falls back to the merge-base and prints a
  > verifiable-action caveat line. RED coverage:
  > `loom-code/scripts/test_review_scope.py` (creation-sha selection,
  > fallback caveat, detached-HEAD None).

  Then run `python3 scripts/backlog_index.py --write` and include the
  regenerated `docs/loom/BACKLOG.md` if it changes (description field is
  unchanged, so no index drift is expected — verify with `--check`).
- Module: docs/loom/backlog/2026-08-04-review-scope-stale-base-remedy-wrong-old-base.md
- Files touched: docs/loom/backlog/2026-08-04-review-scope-stale-base-remedy-wrong-old-base.md
- Context paths:
  - docs/loom/backlog/2026-08-04-review-scope-stale-base-remedy-wrong-old-base.md
  - docs/loom/specs/2026-08-04-loom-mechanism-defect-fixes.md (§Verified root cause)
- Acceptance:
  - RED: grep diagnostic — `grep -c "Root-cause hypothesis" <entry>` is 1
    before, 0 after; `grep -c "OVERTURNS the original hypothesis" <entry>`
    is 0 before, 1 after. `python3 scripts/backlog_index.py --check` exits 0
    after.
  - GREEN: all three conditions hold.
- Review-weight: mechanical
- Dependencies: none
- Independent: true
- Brief item covered: "The D-A backlog entry's now-disproven hypothesis paragraph is corrected in-place" (Decision 6)

## Task 10 — loom-code 0.51.0 bump + CHANGELOG

- Description: Three exact-spec edits. (1) Set
  `loom-code/.claude-plugin/plugin.json` `"version"` to `"0.51.0"`.
  (2) Run `python3 scripts/sync_codex_manifests.py loom-code` — the sync
  script whose SSOT is `loom-code/.claude-plugin/plugin.json` — which
  updates `loom-code/.codex-plugin/plugin.json` deterministically.
  (3) Insert into `loom-code/CHANGELOG.md`, directly above the
  `## [0.50.0]` heading, this entry verbatim (named deliverable per
  `docs/loom/memory/version-bump-packets-must-name-changelog-entry.md`):

  ```markdown
  ## [0.51.0] — 2026-08-04 — the stale-base remedy stops prescribing a conflicting rebase

  ### Fixed

  - **The stale-base refusal's rebase remedy now prints an old-base that is
    safe to follow verbatim.** `review_scope.py` previously filled the
    remedy's old-base with the merge-base — textbook-correct, but in this
    squash-merge repo a branch cut from a previous arc's merged-but-squashed
    local tip carries already-merged foreign commits between the merge-base
    and its own work, and replaying them conflicts (observed live on the
    0.50.0 fix arc; backlog entry
    `2026-08-04-review-scope-stale-base-remedy-wrong-old-base`). The remedy
    now prefers the branch's reflog creation sha when it is a
    descendant-or-equal of the merge-base and an ancestor of HEAD; otherwise
    it falls back to the merge-base and prints a verifiable-action caveat
    line (abort + substitute the creation sha from `git reflog show
    <branch>`). The `AGENTS.md` mirror follows.

  ### Added

  - **The plan-document-reviewer's output contract now obliges a per-check
    full-task sweep** — a check that failed anywhere must be re-scanned
    against every task before the verdict returns (one sentence in §Verdict
    mapping; closes the round-costing partial sweep observed on the 0.50.0
    fix arc).
  - **`requesting-code-review`'s panel step points at SDD's capacity-error
    recovery** (`dispatch-hygiene-notes.md` §Capacity-error recovery), paid
    for inside the CHK-SKL-010 word cap by trimming an unpinned version tag.
  ```

  Verify `python3 scripts/check_version_bump.py --base origin/main --head
  HEAD` exits 0 and `python3 scripts/sync_codex_manifests.py --check
  loom-code` reports clean.
- Module: loom-code/.claude-plugin/plugin.json
- Files touched: loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md
- Context paths:
  - loom-code/CHANGELOG.md (top entries for format)
  - loom-code/.claude-plugin/plugin.json
- Acceptance:
  - RED: `python3 scripts/check_version_bump.py --base origin/main --head HEAD`
    fails (or reports missing bump) while loom-code content commits exist
    without the bump.
  - GREEN: the same command exits 0; CHANGELOG heading `## [0.51.0]` present.
- Review-weight: mechanical
- Dependencies: Tasks 3, 7, 8 complete first
- Independent: false
- Brief item covered: "version bump 0.50.0 → 0.51.0 with a named CHANGELOG entry" (Decision 7)

## Task 11 — weak-model dogfood probes + record

- Description: Post-implementation verification (user directive). Three
  probes, results recorded at
  `docs/loom/dogfood/2026-08-04-remedy-fix-weak-model-probe.md` (write to
  an alias filename then `mv` if the Write tool refuses the name — see
  auto-memory `feedback_write_tool_refuses_report_md_basename`; the chosen
  name is safe): (a) D-A live probe — build a sandbox repo in the
  scratchpad reproducing the stale-cut state (same shape as Task 2's
  fixture but on-disk), run the CLI to capture the refusal stderr, then
  dispatch ONE haiku agent given ONLY the sandbox path + the stderr text
  with the instruction "follow the printed remedy to un-wedge this
  branch"; success = rebase completes conflict-free and
  `git log --oneline <merge-base-of-result>..HEAD` lists only the
  branch's own commits. (b) D-C/E-3 cold-reader probe — one sonnet agent
  reads ONLY the edited §Verdict mapping section plus a fabricated
  4-task round-1 scenario where one check fails on tasks 2 and 4; success
  = its returned gap list names BOTH tasks. (c) D-D mechanical check —
  `python3 scripts/claim_copy_sweep.py --claim "so the sample of recorded
  findings is never biased"` now lists
  `loom-code/scripts/loom_gate_markers.py` as an operative hit. The
  record states each probe's verdict; any FAIL blocks finishing and
  routes back to the owning task.
- Module: docs/loom/dogfood/2026-08-04-remedy-fix-weak-model-probe.md
- Files touched: docs/loom/dogfood/2026-08-04-remedy-fix-weak-model-probe.md
- Context paths:
  - docs/loom/dogfood/2026-08-04-docs-review-0490-fix-trap-probe.md (record-format precedent)
- Acceptance:
  - RED: record file absent (diagnostic).
  - GREEN: record exists with three named probe verdicts, all CLEAN/PASS.
- Review-weight: prose
- Dependencies: Tasks 3, 6, 7, 8 complete first
- Independent: false
- Brief item covered: "Weak-model dogfood before finishing (user directive)" (Decision 5)

## Decision Log

- T3 gained a third test (`test_cli_divergent_creation_sha_falls_back_with_caveat`)
  beyond the plan's two: T2's quality reviewer proved by mutation that
  neither ancestry check was test-necessary; the divergent-creation case
  is a fallback case, so the mutation-killer landed in T3's scope.
  Two-way door, no product consequence — logged, not asked.
- T11 executed by the orchestrator, not an implementer: probe (a)
  dispatches a weak-model agent, and subagents cannot dispatch agents
  (recorded nesting gotcha). Reviewer verification unchanged.
- T11 probe (c)'s pinned exemplar ("never biased" docstring copy) was
  retired by the 0490 arc's own claim rewrite before the probe ran;
  substituted a live md↔py mirror pair (§Pinned refusal contract), with
  the substitution recorded in the dogfood record. Two-way door — logged.

## Notes

- Verdict stamped PASS (round 2) — stamping the reviewer's returned
  verdict, no re-review (amendment kind 1).
- Reviewer round-1 Check-15 advisory (T3/T4, T10/T11 unmarked parallel
  candidates) acknowledged: T4 stays sequential behind T2 (doc mirrors
  T2's final semantics); T11 is the final gate by design.
- Copy-sweep partition for the remedy claim is frozen in the brief
  (§Copy-sweep partition); Task 4 is the only operative mirror edit.
  Historical records (memory / backlog / plans / specs / CHANGELOG) must
  NOT be edited to the new semantics.
- `scripts/claim_copy_sweep.py` and its test are top-level (no plugin
  bump) — precedent #638/#643; Task 10 deliberately excludes them.
- Wave 1 parallel-eligible set: Tasks 1, 5, 7, 8, 9 (disjoint files, no
  shared symbols). Tasks 2→3 chain behind 1; Task 6 behind 5; Tasks 10-11
  behind their listed dependencies.
- Orchestrator-side trap-guards for every dispatch packet: Read before
  Edit; on modified-since-read re-Read; guard blocking twice → stop and
  report verbatim; no `name:` on Agent dispatches; conventional-commits
  type+scope per repo CI; commit trailers per dispatch instruction.

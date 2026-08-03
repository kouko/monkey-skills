# Plan: one resolver owns review scope, and it refuses a stale base

Source brief: docs/loom/specs/2026-08-03-review-scope-resolver.md
Total tasks: 7
Critical-path depth: 5 (≤5) — Task 1 → 2 → 3 → 4 → {5, 6, 7}, the last three
being one parallel level of independent leaves.
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-08-03, round 2; amendment re-review PASS 15/15)

## Notes

- **The review loop is closed here, deliberately, and this is the deviation.**
  The plan reached PASS 15/15 at round 2, and an amendment re-review returned
  PASS 15/15 again with two notes — both mine, both non-gating: Task 4's
  `Files touched` omitted `AGENTS.md` while its GREEN required editing it, and
  Task 1's GREEN stated a hit count that was short. Both are corrected above —
  the count by deleting the total rather than restating it, for the reason
  Task 1's GREEN now gives. A `Files touched` change normally
  re-reviews, and that round is **not** being run. Reasons, stated rather than
  hidden: the reviewer that raised both notes already adjudicated their
  substance in the same verdict (it verified `AGENTS.md:32` is the right
  surface and that the rename partition is correct); both corrections are
  mechanically verifiable and were verified — the grep returns eight hits
  outside this plan, which is the figure Task 1's GREEN acts on (no total
  including this file's own mentions is stated, here or there: see that
  section for why); and the same reviewer explicitly flagged the
  loop risk, which this arc has already paid for once (`docs/loom/backlog/2026-08-03-origin-arc-close-out-residue.md`
  records five rounds where each fix pass authored the next round's finding).
  The loop ends by declining the next edit, not by running one more round.

- **Task 1 amendment (2026-08-03) — the plan, not the artifact, was the defect.**
  Round 2 of Task 1's review produced contradicting arms on one artifact:
  code-quality returned PASS 7/7 and had itself REQUESTED the docstring in
  round 1; spec returned NEEDS_REVISION holding that the docstring is outside
  Task 1's authorised population and duplicates §Pinned local-ref rule a task
  early. Per
  `docs/loom/memory/contradicting-reviewer-verdicts-localize-the-defect-to-the-spec.md`,
  the blocking arm's spec sentence was read rather than the artifact re-judged.
  That sentence is this plan's own, in Task 1's GREEN, quoted as it stood:
  *"The rename's population is **enumerated, not described**"*. It enumerates
  **which occurrences of the string `_default_branch_ref` change** — it was
  never a list of every line Task 1 may touch, and it does not say so. Both
  readings were available, so the ambiguity is the defect and it is mine.
  **Amended authorisation**: Task 1 MAY document the contract of the symbol it
  promotes, at the definition site, because that is what makes a newly public
  surface honest. It may NOT state downstream policy: `default_branch_ref` has
  no notion of freshness, so the pin's sentence *"Local-only is a freshness
  FAILURE, never a fresh verdict"* does not belong in it — that sentence stays
  with Tasks 2 and 3, its only transcribers. The orchestrator applied the
  one-clause trim directly rather than re-dispatching, since re-dispatching an
  implementer on a contradiction undoes correct work.

- **Plan defect found during the Tasks 5-7 wave: `Files touched` under-declared
  the tests that pin the strings each task deletes.** All THREE tasks in the
  parallel wave had to edit a pre-existing test outside their declared list —
  Task 5 `test_docs_review_mode.py`, Task 6
  `test_requesting_docs_review_skill.py`, Task 7
  `test_docs_review_blocking_class.py` — and each flagged it rather than
  silently widening scope. In every case it was unavoidable by construction:
  the old test asserted the presence of the exact string the task's GREEN
  requires deleting, so "delete the line" and "keep the suite green" are jointly
  satisfiable only by updating that pin. Two of the three were narrow assertion
  swaps; Task 7's was the standing version pin that every bump rewrites.

  This is the same class the plan-document-reviewer caught once already (Task 4's
  GREEN required editing `AGENTS.md` while `Files touched` omitted it), and it
  survived into a wave where it matters more: **`Files touched` is the
  disjointness oracle for parallel dispatch**. Three undeclared files in one
  concurrent wave meant the oracle was answering from an incomplete set — the
  three happened not to collide, which is luck, not design. **Rule for future
  plans: when a task deletes or rewrites a string, every existing test that pins
  that string belongs in its `Files touched`.** Find them before dispatch with a
  grep for the string being retired, not after.

- **Second plan defect in the same wave: Task 5's Description narrowed a pin
  that is general.** The Description said the delegation to carry the resolved
  scope is "the docs-only delegation"; §Pinned pass-down contract, which the
  same task must transcribe VERBATIM, is unqualified — it says *the* delegating
  station hands *the* delegate the scope, with no path carve-out. The
  implementer followed the Description, left the mixed-branch bullet alone, and
  **said so in its report** — its reading was correct and the narrowing was
  mine.

  The cost was not cosmetic. Review traced it: a mixed branch dispatches its
  docs arm with no `resolved-scope`; `requesting-docs-review`'s Step 1 therefore
  takes its "resolve it yourself" branch; the resolver returns the FULL branch
  list rather than the `.md` subset; that station's own "any non-`.md` means not
  docs-only" check then fires — a mixed branch contains non-`.md` files by
  definition — and routes the dispatch back to `requesting-code-review`, which
  hands it back the same way. The mixed-branch split breaks outright.

  **Amended**: Task 5 also hands `resolved-scope` on the mixed-branch path, and
  the value there is the `.md` subset of the resolved list — that arm's actual
  scope. **Rule for future plans: when a task must transcribe a pin VERBATIM,
  the task Description may not describe a narrower obligation than the pin
  states.** A Description that narrows a pin produces an artifact whose stated
  contract contradicts its own behaviour, and nothing downstream is looking for
  that contradiction — both of this task's grep-window tests passed.

- **`file:line` citations in this plan and its brief are as-of-authoring.**
  Task 1 lengthened `default_branch_ref`'s docstring, which shifted every line
  below it in `loom_gate_markers.py` — so citations written before that task
  landed now point a few lines off, including this plan's Task 1 GREEN and
  Task 2 `Reuse-adequacy` markers and the brief's §Current State Evidence.
  They were accurate when written and are **not** being refreshed: chasing
  them means re-editing on every subsequent change, and this arc has already
  demonstrated what a treadmill of number-corrections produces. Stated once
  here rather than left for a reader to discover. This is this plan's own
  choice; `plan-format.md` records no refresh policy in either direction.

- **Kickoff sweep result: zero one-way-door decisions to brief.** The round's
  two genuinely irreversible choices — the resolver runs the fetch itself, and
  it refuses rather than warns — were both ratified by the user at brief stage
  (`docs/loom/specs/2026-08-03-review-scope-resolver.md` §Resolved Questions 1,
  §Decision). A documented decision beats re-asking. The "expect 1-3 hits" line
  in the briefing contract is a precedent, not a quota. What the sweep did find
  is four foreseeable implementation forks, pinned below; three are look-ups
  against existing convention, one is not.

Kickoff decision: resolver exit-code vocabulary → 0 emits the file list, every
refusal exits non-zero, and the codes are documented in `review_scope.py`'s
module docstring — mirroring the convention that `loom_gate_markers.py`
documents its exit semantics in its own docstring
(`read loom-code/scripts/loom_gate_markers.py:17`). Look-up, unbriefed.

Kickoff decision: file-list output format → newline-delimited paths, byte-identical
to `git diff --name-only`. Already forced by Task 4's GREEN; pinned so no
implementer re-opens it. Look-up, unbriefed.

Kickoff decision: how the new module runs git → it writes its own stdlib
subprocess helper rather than importing `loom_gate_markers._git`. Task 1
promotes exactly one symbol; reaching for a second private name would recommit
the dependency Task 1 exists to remove, and this repo already tolerates a
deliberate duplicate for the same reason (`read loom-code/hooks/git-guard.py:322`).
Look-up, unbriefed.

Kickoff decision: `git fetch` timeout → bounded, with expiry routed into the
pinned refusal path rather than a distinct failure mode. **No convention exists
to inherit**: measured, `loom_gate_markers.py`'s git helper runs
`subprocess.run` with no `timeout` argument at all
(`read loom-code/scripts/loom_gate_markers.py:204`), and the module contains no
`timeout=` anywhere. This matters because the fetch is the only network call on
the path: unbounded, a dead remote hangs a review indefinitely, which is worse
than failing it, and the refusal path already exists to absorb it. Two-way door
(a constant), so it is decided here rather than briefed — and it is
user-vetoable late.

- **Change-folder binding: none, by recorded decision — not by a fresh skip.**
  Detection layer (ii) finds the same two non-archived folders as the previous
  arc (`docs/loom/2026-07-12-us-sec-primary-source-layer/`,
  `docs/loom/2026-07-19-8k-prose-kpi-intake/`). The user's decision not to bind
  either is already recorded and independently corroborated by
  `docs/loom/backlog/2026-07-26-loom-docs-two-stale-change-folders-belong-to-shipped-arcs.md`,
  which records both as belonging to shipped arcs. A documented decision beats
  re-asking. `check_scenario_coverage.py` does not apply — the input is a
  brainstorming brief.

- **Round-1 correction — this plan asserted a false fact about its own repo.**
  The round-1 version justified Task 1 by claiming this repo has "no
  production-to-production import precedent — only test modules import
  production ones". That is false, and the counterexamples sit in the same
  directory the new module lands in: `check-living-spec-index.py` imports four
  production modules (`read loom-code/scripts/check-living-spec-index.py:62`)
  and `living_spec_collect.py` imports another
  (`read loom-code/scripts/living_spec_collect.py:23`). The two citations the
  claim rested on were accurate but supported only its positive half, never the
  negative universal. **The correction strengthens Task 1 rather than removing
  it**: the existing precedent imports **public** names, so promoting
  `_default_branch_ref` before depending on it follows the precedent instead of
  inventing a cost. Recorded rather than quietly edited, because a wrong,
  actionable, silent claim is this arc's own subject matter.

- **Why a new module rather than a new subcommand on `loom_gate_markers.py`.**
  Measured: that module is 1528 lines and its docstring states its
  responsibility as the gate-marker CLI plus a frozen marker contract
  (`read loom-code/scripts/loom_gate_markers.py:1`). Scope resolution is a
  different concern and would stretch both.

- **§Pinned refusal contract** — four tasks (3, 4, 5, 6) write this across
  three artifacts; Tasks 3 and 4 both write `review_scope.py`. Transcribe
  VERBATIM from this pin, never from a sibling task's copy:

  ```
  A stale base, or any failure to establish freshness, REFUSES.
  The resolver never returns a file list it cannot vouch for, and a
  station that receives a refusal STOPS before dispatching anything.
  ```

  "Failure to establish freshness" includes a failed or impossible fetch, an
  unresolvable default branch, and a default-branch ref that resolves only
  locally (see §Pinned local-ref rule). There is no degrade-to-unfetched-ref
  path: the brief records that a resolver reading an unfetched ref returns a
  false all-clear indistinguishable from a genuine pass.

- **§Pinned local-ref rule** — Tasks 2 and 3 transcribe this VERBATIM:

  ```
  default_branch_ref returns a revision NAME, not a fetch target: either
  `origin/<branch>` (origin/HEAD, prefix stripped) or a bare local `main`
  / `master`, or None. A return with no remote component is a LOCAL-ONLY
  ref: comparing against it answers "am I current with my own local main",
  which is a false all-clear. Local-only is a freshness FAILURE, never a
  fresh verdict.
  ```

- **§Pinned pass-down contract** — Tasks 5 and 6 write the two ends of one
  protocol and are dispatched in parallel; without a pin they can name the two
  ends differently and both grep-window tests still pass. Transcribe VERBATIM:

  ```
  The delegating station hands the delegate the resolved scope as
  `resolved-scope` in the dispatch packet. The delegate resolves scope
  itself ONLY when no `resolved-scope` was supplied.
  ```

- **Brief Open Questions — explicit disposition, not silence.**
  - Brief OQ1 (does `finishing-a-development-branch:100`'s display read route
    through the resolver?) — **deferred, no task.** It is a display read, not a
    decision input; converting it is not required for correctness and is
    recorded here so its absence reads as a decision rather than an oversight.
  - Brief OQ2 (detached HEAD / no resolvable default branch) — **half
    resolved.** The no-resolvable-default-branch half is decided: Task 3 refuses
    on it, per §Pinned refusal contract. The detached-HEAD half is **deferred**
    — no task, and no code path in this plan claims to handle it.

- **Task 7 carries no `Review-weight` field, deliberately.** Its Codex-manifest
  half would qualify as `mechanical` alone (an established deterministic sync
  script verified by an existing drift check), but the marker is per-task and
  the task also writes an authored CHANGELOG sentence. Fail closed: the full
  triad runs. The field is absent rather than set to a sentinel — `OMIT` is the
  schema template's meta-instruction, not a value.

- **Field labels are plain (`- Description:`), not the schema example's bold
  form.** Measured against this repo's shipped plans, which use the plain form
  throughout (`docs/loom/plans/2026-08-02-finding-origin-attribution.md`,
  `docs/loom/plans/2026-08-01-backlog-one-entry-per-file.md`). Matching the
  repo beats matching the template's rendering.

- **A fourth call site, not named in the brief, is folded into Task 5.**
  `requesting-code-review/SKILL.md:106` runs
  `grep -rn "LOOM-SIMPLIFY:" $(git diff --name-only main...HEAD)` — the same
  stale-base exposure, in the same file Task 5 already edits. The brief's
  §What Becomes Obsolete named only three invocations because this one was not
  found until plan review. Leaving it while shipping "one resolver owns review
  scope" would reproduce the exact half-applied-remedy pattern this arc exists
  to end, so it is in Task 5's scope.

## Task 1 — promote the default-branch helper to a public name

- Description: Rename `_default_branch_ref` to `default_branch_ref` in
  `loom_gate_markers.py` and update its internal call site and tests. Behaviour
  unchanged — a visibility change so a sibling production module can depend on
  a public surface, matching the existing cross-module import precedent.
- Module: `loom-code/scripts/loom_gate_markers.py`
- Files touched: `loom-code/scripts/loom_gate_markers.py`, `loom-code/scripts/test_loom_gate_markers.py`, `loom-code/hooks/git-guard.py`
- Context paths:
  - `loom-code/scripts/loom_gate_markers.py`
  - `loom-code/scripts/check-living-spec-index.py`
- Acceptance:
  - RED: a new test asserting `from loom_gate_markers import default_branch_ref`
    succeeds — fails today with ImportError.
  - GREEN: that import resolves and the full `test_loom_gate_markers.py` suite
    stays green. The rename's population is **enumerated, not described** — a
    repo-wide grep for `_default_branch_ref` returns **eight hits outside this
    plan**, and only three of the eight are this symbol. (No total including
    this plan's own mentions is stated here, deliberately: every edit to this
    paragraph changes that total, and the two previous attempts to state it
    were both wrong for exactly that reason. The eight-hit partition below is
    the actionable claim and is stable.)
    - **Rename** — the definition (`read loom-code/scripts/loom_gate_markers.py:341`)
      and its one call site (`read loom-code/scripts/loom_gate_markers.py:368`).
    - **Update the citation only** — `read loom-code/hooks/git-guard.py:324`, a
      docstring naming this symbol.
    - **Do NOT rename** — `loom-code/hooks/git-guard.py:322` and `:343` are a
      DIFFERENT symbol that merely shares the name: a deliberate stdlib-only
      duplicate, private by design because the hook is dependency-free.
      Renaming it is out of scope and would break that independence.
    - **Out of scope** — the three occurrences in
      `docs/loom/specs/2026-08-03-review-scope-resolver.md`. The brief records
      the design as authored; it is not refreshed by implementation work.
- External surfaces: none — pure internal rename, stdlib only.
- Dependencies: none
- Independent: false
- Brief item covered: "the machinery this brief needs — default-branch resolution and merge-base computation — exists, is fail-closed, and is under test"

## Task 2 — a freshness verdict that detects a stale base

- Description: Create `loom-code/scripts/review_scope.py` with a function that
  derives a fetch target from the default-branch revision name, fetches that
  ref narrowly, and reports whether the branch's merge-base is the current
  remote tip. Transcribe §Pinned local-ref rule. It reports; refusal wiring is
  Tasks 3 and 4.
- Module: `loom-code/scripts/review_scope.py`
- Files touched: `loom-code/scripts/review_scope.py`, `loom-code/scripts/test_review_scope.py`
- Context paths:
  - `loom-code/scripts/loom_gate_markers.py`
  - `loom-code/scripts/test_loom_gate_markers.py`
- Acceptance:
  - RED: a test building a repo whose branch base predates a commit already on
    the default branch, asserting the verdict is not-fresh — fails today
    (the module does not exist).
  - GREEN: that test passes, AND a named regression assertion that a branch
    whose base IS the current remote tip reports fresh. The fetch names a
    remote and a branch derived by splitting the `origin/<branch>` revision
    name — never the revision name itself, which is not a valid refspec.
- Reuse-adequacy:
  - Observed: `default_branch_ref` returns a revision NAME — `origin/<branch>`
    from `origin/HEAD` with `refs/remotes/` stripped, else a bare local `main`
    or `master`, else `None` — `read loom-code/scripts/loom_gate_markers.py:341`
  - Intended: the new call path uses that return for the **comparison
    revision** only, and derives the fetch target separately by splitting the
    remote component off it. Two of the helper's three return shapes are NOT
    usable as-is on this path and are handled rather than assumed: `None` and a
    local-only name both mean freshness cannot be established, which Task 3
    turns into a refusal. The prior caller `compute_patch_id`
    (`read loom-code/scripts/loom_gate_markers.py:360`) uses the return purely
    as a merge-base revision argument, where `origin/main` and `main` are
    interchangeably valid — which is why those semantics were adequate there
    and are not here.
- External surfaces: `[BOUNDARY]` invokes `git fetch` — a network call. Stdlib
  `subprocess` only; no new dependency.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "the resolver runs the fetch itself" (§Resolved Questions 1)

## Task 3 — every way freshness can fail refuses, none falls back

- Description: Make a failed fetch, an unresolvable default branch, and a
  local-only default-branch ref each produce a refusal rather than a verdict
  computed from whatever is on disk. Transcribe §Pinned refusal contract and
  §Pinned local-ref rule.
- Module: `loom-code/scripts/review_scope.py`
- Files touched: `loom-code/scripts/review_scope.py`, `loom-code/scripts/test_review_scope.py`
- Context paths:
  - `loom-code/scripts/loom_gate_markers.py`
- Acceptance:
  - RED: a test where the fetch subprocess fails, asserting the result is a
    refusal — fails today because Task 2's happy path computes a verdict from
    whatever ref is on disk.
  - GREEN: that test passes, plus two named assertions covering the other two
    failure shapes — `default_branch_ref` returning `None`, and returning a
    local-only name with no remote component. No code path returns a freshness
    verdict unless a fetch of a remote-qualified ref succeeded.
- External surfaces: `[BOUNDARY]` same `git fetch` surface as Task 2; this task
  adds its failure handling.
- Dependencies: Task 2 completes first
- Independent: false
- Brief item covered: "Fetch failure (offline, auth prompt, timeout) must fail closed" (§Resolved Questions 1)

## Task 4 — the resolver returns a scope, or refuses with the rebase remedy

- Description: Add the changed-file-list resolution and the CLI entry point.
  On a fresh base it returns the same list the stations compute today; on any
  refusal it exits non-zero and prints the concrete `git rebase --onto`
  invocation with the resolved shas filled in. Transcribe §Pinned refusal
  contract.
- Module: `loom-code/scripts/review_scope.py`
- Files touched: `loom-code/scripts/review_scope.py`, `loom-code/scripts/test_review_scope.py`, `AGENTS.md`
- Context paths:
  - `loom-code/scripts/loom_gate_markers.py`
- Acceptance:
  - RED: TWO failing tests, both failing today for the same reason (no CLI
    exists) — (a) a CLI run against a stale-base repo exits non-zero and its
    output contains the `git rebase --onto` remedy with both shas; (b) a CLI
    run against a fresh-base repo emits a file list byte-identical to
    `git diff <default-branch>...HEAD --name-only` on the same repo. Neither is
    a GREEN-only assertion: (b) drives the list-resolution logic that (a) never
    reaches, since a refusal returns no list.
  - GREEN: both tests pass. Three-dot semantics are unchanged, per the brief's
    §Decision. The new runnable verb is declared in this repo's command surface
    — the `## Commands` section of `read AGENTS.md:32` — and verified to run
    from there.
- External surfaces: `[BOUNDARY]` inherits Task 2's `git fetch`; adds no new
  external surface.
- Dependencies: Task 3 completes first
- Independent: false
- Brief item covered: "One resolver call returns the branch's changed-file list and a base-freshness verdict"

## Task 5 — `requesting-code-review` calls the resolver, halts on refusal, passes scope down

- Description: Replace every branch-diff invocation in the file with the
  resolver call, make the docs-only delegation carry the resolved scope, and
  state that a refusal stops the station before any dispatch. Transcribe
  §Pinned refusal contract and §Pinned pass-down contract. Delete the replaced
  invocations in this same task.
- Module: `loom-code/skills/requesting-code-review/SKILL.md`
- Files touched: `loom-code/skills/requesting-code-review/SKILL.md`, `loom-code/scripts/test_review_scope_stations.py`
- Context paths:
  - `loom-code/skills/requesting-code-review/SKILL.md`
  - `loom-code/skills/requesting-docs-review/SKILL.md`
- Acceptance:
  - RED: a grep-window test asserting (i) the file names the resolver at the
    direct-entry step, the routing step and the marker-sweep step, (ii) the
    delegation step names `resolved-scope` verbatim from §Pinned pass-down
    contract, and (iii) the file states that a refusal stops the station before
    dispatching — fails today.
  - GREEN: that test passes, AND no line matching
    `git diff( --name-only)? main\.\.\.HEAD` or
    `git diff --name-only main\.\.\.HEAD` survives anywhere in the file. The
    oracle must match all three shapes present today — `:85` carries
    `git diff main...HEAD` with NO `--name-only`, `:96` carries the flag, and
    `:106` carries it in reversed order — so a `--name-only`-only oracle would
    pass while an old computation survives.
- External surfaces: none.
- Dependencies: Task 4 completes first
- Independent: true
- Brief item covered: "the three stations that currently compute scope call it instead of running their own `git diff`"

## Task 6 — `requesting-docs-review` accepts a passed-down scope and halts on refusal

- Description: Make Step 1 resolve scope only when it was not handed one, and
  state that a refusal stops the station before any dispatch. Transcribe
  §Pinned refusal contract and §Pinned pass-down contract. Delete the
  unconditional branch-diff invocation.
- Module: `loom-code/skills/requesting-docs-review/SKILL.md`
- Files touched: `loom-code/skills/requesting-docs-review/SKILL.md`, `loom-code/scripts/test_review_scope_docs_station.py`
- Context paths:
  - `loom-code/skills/requesting-docs-review/SKILL.md`
- Acceptance:
  - RED: a grep-window test asserting Step 1 resolves only when no
    `resolved-scope` was supplied — naming that token verbatim from §Pinned
    pass-down contract — and that the file states a refusal stops the station
    before dispatching. Fails today (`:53` resolves unconditionally).
  - GREEN: that test passes, and no line matching
    `git diff( --name-only)? main\.\.\.HEAD` survives in the file.
- External surfaces: none.
- Dependencies: Task 4 completes first
- Independent: true
- Brief item covered: "the delegating station passes its resolved scope down; the delegate resolves only when it was not given one" (§Resolved Questions 2)

## Task 7 — CHANGELOG entry and plugin version bump

- Description: Record the resolver in `loom-code/CHANGELOG.md`, bump the Claude
  manifest (the SSOT) from 0.45.0 to 0.46.0, then regenerate the Codex manifest
  by running the established sync engine — never by hand-editing it.
  Marketplace publishes by version: an unbumped manifest makes the skill
  changes a silent no-op for installed users
  (`read scripts/check_version_bump.py:1`).
- Module: `loom-code/.claude-plugin/plugin.json`
- Files touched: `loom-code/CHANGELOG.md`, `loom-code/.claude-plugin/plugin.json`, `loom-code/.codex-plugin/plugin.json`
- Context paths:
  - `loom-code/CHANGELOG.md`
  - `scripts/sync_codex_manifests.py`
- Acceptance:
  - RED: after bumping ONLY the Claude manifest, the sync engine's check mode
    exits non-zero on drift — the shape asserted by
    `read scripts/test_sync_codex_manifests.py:138`
    (`test_check_exits_nonzero_after_mutating_one_shared_field`). Run it and
    observe the non-zero exit before syncing.
  - GREEN: the sync engine's check mode exits 0, both manifests read 0.46.0,
    and the CHANGELOG entry states the refusal contract without restating the
    pin's wording as a new absolute.
- External surfaces: none.
- Dependencies: Task 4 completes first
- Independent: true
- Brief item covered: "one implementation replaces three that can drift apart" (§Decision — the shipped surface needs a released version to reach installed users)

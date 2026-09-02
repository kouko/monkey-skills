# Audit — Declared-vs-actual `Files touched` check: measurement

- **Date**: 2026-08-01
- **Branch**: `docs-declared-vs-actual-measurement` (base `f22e9aa1`)
- **Source brief**: `docs/loom/specs/2026-08-01-declared-vs-actual-files-touched-check.md`
- **Plan**: `docs/loom/plans/2026-08-01-declared-vs-actual-files-touched-check.md`
- **Freeze provenance**: this answer key was frozen BEFORE the comparator
  existed. Verified at freeze time (2026-08-01, Task 1):
  `test -f scripts/check_files_touched.py` exits 1 — the comparator's
  planned path was absent. Same discipline as the 8-cell
  Reuse-adequacy measurement
  (`docs/loom/dogfood/2026-07-27-plan-fact-grounding-coldread.md`).

## Rule variants under measurement

Restated from the brief §Rule variants (set-membership made explicit per
plan Task 3) so the key is self-contained:

| variant | flags | notes |
|---|---|---|
| R1 strict | any set difference, both directions | simplest possible rule |
| R2 under-only | `actual − declared ≠ ∅` only | the dangerous direction is under-declaration; OVER may be legitimate drift during a fix round |
| R3 = R2 + standing excludes | R2 after removing from the *actual* set: the plan file itself, and any path containing `__pycache__/` | measures whether excludes are even needed |

Comparator conventions bound by the plan (Notes, Kickoff decision):

- Actual set comes from `git show --name-only --no-renames --format= <sha>`,
  so a rename contributes BOTH the old and the new path (probed 2026-08-01
  in a sandbox repo: default rename detection prints only the new path,
  but the old path's deletion still collides with a sibling task touching
  it — the disjointness oracle needs both).
- `NEW: <path>` declarations normalize to the proposed path
  (`loom-code/skills/writing-plans/references/plan-format.md:79`).
- A task with no `Status: done(<sha>)` (the ledger field is optional,
  `plan-format.md:68-71,106`) yields `NO_JOIN` under every variant —
  never `OK` — and the comparator fails LOUD (exit 2 per plan Task 4,
  naming what was empty) when a whole plan parses to 0 tasks or 0 join
  keys (the loud-failure duty is brief §Decision; the exit code is the
  plan's convention; the citation-checker empty-pass lesson).

## Frozen answer key

Exactly 10 independent cells, shapes chosen to break the selection effect
(brief §Fixture cells). Construction specs are the SSOT for Task 4's
sandbox commits: each names the declared list and the actual commit
contents; Task 4 builds them with real `git init/add/commit` (never
hand-typed diffs). Fixture plan documents must not embed fenced blocks
containing `## Task` lines (parser section-boundary limitation carried
over from `loom-code/scripts/check_scenario_coverage.py:58-68`).
Each cell is its own fixture plan document unless the cell says
otherwise (cell 9 alone hosts two tasks in one plan); the plan-file
standing exclude always refers to the plan document under check.

| # | cell | construction spec (declared → actual commit) | ground truth (flag-worthy? why) | R1 | R2 | R3 |
|---|---|---|---|---|---|---|
| 1 | clean exact match | Declared: `src/a.py`, `tests/test_a.py`. Commit edits exactly `src/a.py` + `tests/test_a.py`, nothing else. | **No** — declaration equals reality; the oracle is correct. | OK | OK | OK |
| 2 | under-declaration, guard-test shape | Declared: `src/limits.py`. Commit edits `src/limits.py` AND `tests/test_limits_guard.py` (a guard test pinning the max value the change alters — the T3 shape in `docs/loom/memory/files-touched-misses-machinery-coupled-files.md`). | **Yes** — the undeclared guard test is mechanically coupled state a sibling task could collide on. | UNDER | UNDER | UNDER |
| 3 | under-declaration, SSOT-functional-copy shape | Declared: `canonical/checklists/spec.md` (the SSOT). Commit edits `canonical/checklists/spec.md` AND the regenerated functional copy `mirror/checklists/spec.md` (same-commit regeneration is mandated, `loom-code/scripts/distribute.py:24-26`). | **Yes** — regenerated copies are under-declaration TARGETS, never excludes (brief §Current State Evidence, Boundary bullet); the copy is a real collision surface. | UNDER | UNDER | UNDER |
| 4 | under-declaration, manifest-mirror shape | Declared: `plugin/plugin.json`. Commit edits `plugin/plugin.json` AND `plugin/.codex-plugin/plugin.json` (hook-enforced mirror, `.claude/settings.json:13` — the T6 shape). | **Yes** — same Boundary bullet: codex-mirror manifests land in the same commit by mandate and are the under-declaration target, not noise. | UNDER | UNDER | UNDER |
| 5 | over-declaration | Declared: `src/b.py`, `src/never_touched.py`. Commit edits only `src/b.py`; `src/never_touched.py` exists in the repo but is not in the commit. | **No** (in the dangerous direction) — nothing undeclared entered the diff; OVER may be legitimate drift during a fix round (brief §Rule variants, R2 rationale). Asymmetry recorded: R1's flag here is pure strictness cost — a false alarm against this ground truth; R2/R3 accept it by design. A shape absent from the known corpus. | OVER | OK | OK |
| 6 | `NEW: <path>` token | Declared: `NEW: src/new_module.py` (`plan-format.md:79`). Commit CREATES `src/new_module.py` (git add of a new file), nothing else. | **No** — after normalizing `NEW: src/new_module.py` → `src/new_module.py`, declaration equals reality. | OK | OK | OK |
| 7 | missing `done(<sha>)` | Declared: `src/c.py`; the task block carries NO `Status: done(<sha>)` line (field is optional, `plan-format.md:68-71`). A commit touching `src/c.py` exists but nothing joins the task to it. | **Yes, as a loud non-verdict** — no join key means no comparison; `NO_JOIN` under every variant, NEVER `OK`. Loud-report duty: a plan whose every task lacks the ledger must never render as all-clear (comparator exits 2 on 0 join keys; `docs/loom/memory/a-silently-skipped-edit-reports-as-a-completed-one.md`). | NO_JOIN | NO_JOIN | NO_JOIN |
| 8 | rename in the commit | Declared: `src/new_name.py` only. Commit performs `git mv src/old_name.py src/new_name.py` (plus an edit to the moved file). Under `--no-renames` the actual set is {`src/old_name.py`, `src/new_name.py`} — both paths (plan Notes, Kickoff decision). | **Yes** — declaring only the new path is UNDER on the old path: a sibling task touching `src/old_name.py` would collide with this task's deletion of it; the oracle needs both sides of the rename. | UNDER | UNDER | UNDER |
| 9 | field-form variance | One fixture plan, two tasks, both clean matches: task A uses bolded `- **Files touched**: src/d.py` (schema form, `plan-format.md:49`), task B uses plain `- Files touched: src/e.py` (the form real plans use, `loom-code/skills/writing-plans/SKILL.md:145`). Commits edit exactly `src/d.py` and `src/e.py` respectively. | **No** — both tasks' declarations equal reality; the cell measures that the parser treats both field forms identically (`check_scenario_coverage.py:62-68` bold-optional idiom). A parser missing one form would surface as a spurious verdict or a parse error, not as ground truth. | OK | OK | OK |
| 10 | path normalization + standing excludes | Declared: `./src/f.py` (leading `./`), `` `src/g.py` `` (backticked), `src/h.py` followed by a trailing space, all in one comma-separated list. Commit edits `src/f.py`, `src/g.py`, `src/h.py` AND additionally contains `src/__pycache__/f.cpython-312.pyc` plus the fixture plan file itself (the two standing-exclude classes). | **No** — institutional noise the excludes exist for: after normalization the three declared paths match reality, and the `__pycache__/` artifact + plan file are exactly what R3's fixed exclude list is designed to absorb. Amended 2026-08-01 (comparator still absent, re-verified) — the original cell 10 left R3 ≡ R2 corpus-wide (`docs/loom/memory/a-test-can-be-correct-and-still-unable-to-fail.md`). | UNDER | UNDER | OK |

Row count: 10. Flag-worthy cells: 2, 3, 4, 8 (UNDER) and 7 (NO_JOIN, loud).
Not flag-worthy: 1, 5, 6, 9, 10 — cell 5 discriminates R1 from R2/R3 by
construction (R1 flags, R2/R3 do not), and cell 10 is the R2↔R3
discriminating cell by construction (R2 flags the exclude-class paths,
R3 removes them and returns OK) — without it R3 ≡ R2 across the whole
corpus and the measurement could not tell the two variants apart.

## Results

**The run** (2026-08-01, Task 5): the parametrized cell matrix IS the
measurement — each of the 30 tests builds its cell with real
`git init/add/commit` in a sandbox repo and asserts that variant's
comparator verdict equals the frozen column above.

```
$ PYTHONDONTWRITEBYTECODE=1 python3 -m pytest scripts/test_check_files_touched.py -q -k cells
30 passed, 25 deselected in 3.90s
```

Node IDs `test_cells_match_frozen_answer_key[<cell>-<variant>]` cover all
10 cells × 3 variants; 30/30 passing means the comparator's output per
cell per variant is EXACTLY the R1/R2/R3 columns of the frozen key —
no cell deviated, so the tables below classify the frozen columns as
measured output.

Per-cell classification (flag-worthy = the key's ground-truth column;
`hit` = flag-worthy flagged, `FA` = false alarm = not-flag-worthy
flagged, `ok` = not-flag-worthy passed, `miss` = flag-worthy passed;
NO_JOIN counts as neither, reported separately):

| cell | flag-worthy? | R1 → class | R2 → class | R3 → class |
|---|---|---|---|---|
| 1 | no | OK → ok | OK → ok | OK → ok |
| 2 | yes | UNDER → hit | UNDER → hit | UNDER → hit |
| 3 | yes | UNDER → hit | UNDER → hit | UNDER → hit |
| 4 | yes | UNDER → hit | UNDER → hit | UNDER → hit |
| 5 | no | OVER → **FA** | OK → ok | OK → ok |
| 6 | no | OK → ok | OK → ok | OK → ok |
| 7 | loud non-verdict | NO_JOIN (neither) | NO_JOIN (neither) | NO_JOIN (neither) |
| 8 | yes | UNDER → hit | UNDER → hit | UNDER → hit |
| 9 | no | OK → ok | OK → ok | OK → ok |
| 10 | no | UNDER → **FA** | UNDER → **FA** | OK → ok |

Per-variant confusion tables over the 9 verdict-bearing cells (cell 7 is
the NO_JOIN cell in every variant — 1 loud non-verdict each, correct per
the key, outside the 2×2):

| R1 | flagged | passed |
|---|---|---|
| flag-worthy (2,3,4,8) | 4 hits | 0 misses |
| not flag-worthy (1,5,6,9,10) | 2 FA (cells 5, 10) | 3 ok |

| R2 | flagged | passed |
|---|---|---|
| flag-worthy (2,3,4,8) | 4 hits | 0 misses |
| not flag-worthy (1,5,6,9,10) | 1 FA (cell 10) | 4 ok |

| R3 | flagged | passed |
|---|---|---|
| flag-worthy (2,3,4,8) | 4 hits | 0 misses |
| not flag-worthy (1,5,6,9,10) | 0 FA | 5 ok |

Recount arithmetic: 4 + 0 + 2 + 3 = 9 (R1), 4 + 0 + 1 + 4 = 9 (R2),
4 + 0 + 0 + 5 = 9 (R3); 9 verdict cells + cell 7 = 10 rows. Summary —
**false alarms: R1 = 2, R2 = 1, R3 = 0; misses: 0 under every variant.**
This matches the expectation the frozen key's construction encoded
(cells 5 and 10 are the discriminators by design); the measurement
confirms rather than contradicts it.

## Retro-fit

Selection-bias label (standing, applies to everything in this section):
the three known real instances (reuse-adequacy branch T3 `c82c93cd`-family,
T4 `0c03c0e8`, T6 manifest commit — machine-local shas, branch was
squash-merged) are on this list BECAUSE they were found; retro-fit results
never enter the headline numbers.

**Provenance and harness work** (2026-08-01):

- Original plan recovered with `git show 293d446c:docs/loom/plans/2026-07-31-reuse-adequacy-declaration-hardening.md`
  into a scratchpad copy — the ORIGINAL declarations, not the corrected
  ones that `2c7e7f17` ("correct the plan's declarations…") later wrote
  into the committed plan.
- The original plan predates the Status ledger: it carries zero
  `Status:` lines (verified by grep over the recovered copy). Join keys
  were therefore injected manually into the scratchpad copy —
  three `- **Status**: done(<sha>)` lines: T3 → `c82c93cd`,
  T4 → `0c03c0e8`, T6 → `e8194146`. T6 was identified from
  `git log --oneline docs-reuse-adequacy-brief-and-backlog` as the
  version-bump commit and verified:
  `git show --name-only --no-renames --format= e8194146` lists
  `loom-code/.codex-plugin/plugin.json`. This sha-injection is harness
  work on a scratchpad copy only; no repo file was patched.
- All these shas are **machine-local**: the branch was squash-merged, so
  they resolve only in this machine's local clone (local branch
  `docs-reuse-adequacy-brief-and-backlog`), not on origin/main.

**The run** — `python3 scripts/check_files_touched.py <scratchpad-copy> --repo /Users/kouko/GitHub/monkey-skills`,
exit 1. Verdict lines for the three joined tasks, verbatim:

```
Task 3 [R1] UNDER  under: loom-code/scripts/test_plan_obligation_sweep.py, loom-code/scripts/test_sdd_review_weight_marker.py
Task 3 [R2] UNDER  under: loom-code/scripts/test_plan_obligation_sweep.py, loom-code/scripts/test_sdd_review_weight_marker.py
Task 3 [R3] UNDER  under: loom-code/scripts/test_plan_obligation_sweep.py, loom-code/scripts/test_sdd_review_weight_marker.py
Task 4 [R1] UNDER  under: domain-teams/skills/code-team/checklists/spec-consistency.md
Task 4 [R2] UNDER  under: domain-teams/skills/code-team/checklists/spec-consistency.md
Task 4 [R3] UNDER  under: domain-teams/skills/code-team/checklists/spec-consistency.md
Task 6 [R1] UNDER  under: loom-code/.codex-plugin/plugin.json
Task 6 [R2] UNDER  under: loom-code/.codex-plugin/plugin.json
Task 6 [R3] UNDER  under: loom-code/.codex-plugin/plugin.json
```

All three real instances flag UNDER under every variant — including R3:
the guard tests (T3), the domain-teams functional copy (T4) and the
codex-manifest mirror (T6) are under-declaration TARGETS that the
standing excludes correctly do NOT absorb (they are the live shapes of
frozen-key cells 2, 3 and 4 respectively). The unjoined tasks (1, 2, 5)
each printed the loud non-verdict, e.g. verbatim:
`Task 1 [R1] NO_JOIN  (no done(<sha>) join key — never OK)`.

## Limitations

- **One sha per task.** The parser keeps a single join key per task
  (multiple `done(<sha>)` lines are a reported parse error, last one
  kept). A task resolved across several commits — the normal fix-round
  pattern — compares only the joined commit. Live example from the
  retro-fit branch: follow-up commits `0c3e809b`, `5505c26f`, `e8934767`
  touched the same surfaces after the joined commits and enter no
  comparison at all. The check under-measures multi-commit tasks by
  construction.
- **The ledger is optional, so the check can only be as loud as its
  non-verdicts.** Measured behavior, not hoped-for behavior: a plan with
  tasks but zero join keys exits 2 with (verbatim, from a sha-less
  fixture run on 2026-08-01)
  `EMPTY: 0 join keys — no task in <plan-path> carries Status: done(<sha>); nothing joins the plan to commits`
  — pinned at CLI level by
  `test_cli_exit_2_on_zero_join_keys_names_what_was_empty` (frozen-key
  cell 7). A partially-ledgered plan prints a per-task
  `NO_JOIN  (no done(<sha>) join key — never OK)` line but does NOT gate
  on it while ≥1 join key exists (EXIT_CONTRACT's documented decision —
  gating would fail every plan mid-flight). Consequence: a team that
  never stamps the ledger gets a loud refusal, but a team that stamps it
  selectively gets verdicts only on what it stamped.
- **Retro-fit provenance is machine-local.** The three instances join to
  shas that exist only in this clone (squash-merged branch); nobody else
  can re-run that half of this audit. The 10-cell fixture half is fully
  reproducible (`scripts/test_check_files_touched.py` builds it from
  scratch).
- **Hit during the runs:** (a) the recovered plan lives in a scratchpad
  outside `--repo`, so the R3 plan-file exclude keeps the given spelling
  and can never match a committed path — harmless here (the joined
  commits don't touch the plan document) but it means the retro-fit run
  never exercised that exclude; the fixture's
  `test_cli_absolute_plan_path_still_hits_r3_plan_file_exclude` covers
  it. (b) The injected bolded `- **Status**:` form parsed identically to
  the plain form, as cell 9 predicts. (c) Corpus size is 10 cells,
  authored inside the same arc that built the comparator — frozen before
  implementation, but still one author's threat model.

## Recommendation

Argued strictly from the tables above (the measurement matched the
key's constructed expectation; nothing below rests on the expectation
alone).

- **R1 — no-ship.** 2 false alarms out of 5 not-flag-worthy cells, and
  its extra strictness buys zero recall: misses are 0 for all three
  variants, so R1's OVER direction (cell 5) and exclude-blindness
  (cell 10) are pure noise cost on this corpus.
- **R2 — no-ship as the default, R3's excludes cost nothing.** 1 false
  alarm (cell 10) with recall identical to R3. Honesty note (docs-review
  correction): cell 10's noise classes are CONSTRUCTED, not observed —
  this repo's history carries zero committed `__pycache__` paths and the
  measured branch's task commits never contain the plan file (ledger
  updates land as separate commits; a same-commit `done(<sha>)` stamp is
  mechanically impossible — the sha is unknown pre-commit). So R2's
  false alarm is a hypothetical cost, not a recurring one. The ranking
  is unchanged on the corpus numbers alone: R3 dominates R2 (equal
  recall, ≤ false alarms) and its two fixed excludes carry no observed
  miss risk (cells 3/4 stay flagged).
- **R3 — ship candidate.** 0 false alarms, 0 misses on the corpus, and
  in the retro-fit it flags all three known real instances with the
  offending paths named. The excludes are exactly two fixed classes;
  nothing shape-specific leaked into them (cells 3/4 stay flagged).
- **Placement options** (either consumes R3's output; not mutually
  exclusive):
  - *SDD per-task step* — run right after the implementer's commit,
    when the ledger sha is freshest. Catches under-declaration while the
    fix is one commit away and while sibling-task disjointness still
    matters (the oracle this exists to protect). Cost: one comparator
    run per task and a hard dependency on stamping `done(<sha>)` at
    task-close time.
  - *Finishing-branch batch* — one run over the whole plan at
    finishing time. Cheaper, tolerates mid-flight NO_JOIN rows
    naturally, and gives a single report; but it discovers collisions
    only after the parallel waves that could have collided already ran,
    so it protects the record, not the dispatch decision.
- **Ship-arc obligations** (restated from the brief — whichever
  placement is chosen): absorb or delete the prose subset rule at
  `loom-code/skills/subagent-driven-development/SKILL.md:86` (its
  "MUST be a subset of the task's declared `Files touched`" is R2-shaped
  prose with no excludes and no tooling — two sources of truth
  otherwise); and supersede the manual-diff advice in
  `docs/loom/memory/files-touched-misses-machinery-coupled-files.md`
  §How-to-apply ("diff `git show --stat <sha>` against the declared
  field") by pointing it at the comparator.

The decision — which variant (if any) to ship, and where to place it —
is explicitly left to the user.

---

Citation check (2026-08-01):
`python3 loom-code/scripts/check_doc_citations.py docs/loom/audits/2026-08-01-declared-vs-actual-check-measurement.md`
→ `checked 10 / unchecked 0 / findings 0` / `OK: all citations resolve.`
(exit 0).

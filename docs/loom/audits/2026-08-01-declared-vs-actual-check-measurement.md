# Audit — Declared-vs-actual `Files touched` check: measurement

- **Date**: 2026-08-01
- **Branch**: `docs-declared-vs-actual-measurement` (base `f22e9aa1`)
- **Source brief**: `docs/loom/specs/2026-08-01-declared-vs-actual-files-touched-check.md`
- **Plan**: `docs/loom/plans/2026-08-01-declared-vs-actual-files-touched-check.md`
- **Freeze provenance**: this answer key was frozen BEFORE the comparator
  existed. Verified at freeze time (2026-08-01, Task 1):
  `test -f scripts/check_files_touched.py` exits 1 — the path does not
  exist anywhere in the working tree. Same discipline as the 8-cell
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

RESULTS-PENDING — frozen before implementation; results land in Task 5.

## Retro-fit

RESULTS-PENDING — frozen before implementation; results land in Task 5.

Selection-bias label (standing, applies to everything in this section):
the three known real instances (reuse-adequacy branch T3 `c82c93cd`-family,
T4 `0c03c0e8`, T6 manifest commit — machine-local shas, branch was
squash-merged) are on this list BECAUSE they were found; retro-fit results
never enter the headline numbers.

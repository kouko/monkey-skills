# Whole-suite timing and diff scope — W2-01

Machine: this host, 16 cores. Command: the repo's own declared package-test
command from `docs/loom/KICKOFF-DEFAULTS.md`, driven group by group by a
scratch harness that wraps `scripts/run_package_tests.py`'s own
`loom_family_commands()` so each group is timed separately. The harness is
not committed; it only measures, and the commands it runs are the runner's.

## Totals

| run | tree | wall clock | assertions passed | any group non-zero exit |
|---|---|---:|---:|---|
| baseline | `89cf5d224` (branch base) | 154.58s | 2148 | no |
| after, run 1 | this branch HEAD | 68.70s | 2148 | no |
| after, run 2 | this branch HEAD | 64.83s | 2148 | no |

Both post-change runs sit under the intent's 95s Acceptance bound, and the
pass count is unchanged at 2148. An earlier baseline measurement of the same
tree read 144.90s; 154.58s is the figure taken in the same sitting as the two
post-change runs, so the three numbers above are directly comparable and the
earlier one is reported only to show the spread.

## Per group, slowest six

| group | baseline | run 1 | run 2 | passed |
|---|---:|---:|---:|---:|
| `loom-workflow/tests/test-memory-grep-perf.sh` | 77.25s | 4.75s | 4.58s | 12 → 12 |
| `loom-workflow/skills/git-memory/scripts` | 28.63s | 11.82s | 12.39s | 64 → 64 |
| loom-code group (`-n auto`) | 22.15s | 24.70s | 22.23s | 1174 → 1174 |
| `loom-workflow/skills/decision-map/scripts` | 9.03s | 9.38s | 8.98s | 244 → 244 |
| `loom-workflow/tests/test_cot_explain_scripts.py` | 6.39s | 3.85s | 3.83s | 48 → 48 |
| `loom-design/scripts` | 2.15s | 4.88s | 3.86s | 204 → 204 |
| all 21 remaining commands | 8.98s | 9.31s | — | unchanged |

Only the first two rows are this change's work. The other four move by a few
seconds in both directions between runs of identical code, which is the
measurement noise floor on this machine; nothing in this branch touches them.

## Acceptance 5 — what the diff touches

`git diff --name-only 89cf5d224..HEAD`:

```
docs/loom/2026-09-12-fast-test-fixtures/plan.md
docs/loom/intent/2026-09-12-fast-test-fixtures.md
loom-workflow/skills/git-memory/scripts/conftest.py
loom-workflow/skills/git-memory/scripts/test_probes_memory_grep_render.py
loom-workflow/skills/git-memory/scripts/test_probes_memory_grep_single_pass.py
loom-workflow/tests/test-memory-grep-perf.sh
```

Two loom records, one pytest conftest, and three test files. No script under
test appears. `git diff --exit-code 89cf5d224 HEAD --` exits 0 for
`memory-grep.sh`, `test_probe_store_failure_fails_loud.py` and
`test_probes_memory_grep_no_trailers_support.py`.

## Fixture equivalence, verified independently of the implementers

Each task's implementer claimed byte-equivalence; both claims were re-run here
from a separate process, building each fixture once with the pre-change builder
and once with the post-change builder and comparing commit object ids. Equal
ids can only hold when every message byte, tree, identity, date and parent link
matches.

| fixture | size | result |
|---|---|---|
| `build_perf_repo` (shell) | 2000 commits, 300 memory-worthy, 20 superseded | same HEAD id `6ee5166a1f445bdf9708c3adbb6825bf806fb011`, 2000 reachable, clean worktree |
| `_build_perf_repo` (pytest) | 200 commits | all 200 commit ids identical, in order |
| `_build_records_repo` (pytest) | 20 commits | all 20 commit ids identical, in order |
| `_build_records_repo` (pytest) | 200 commits | all 200 commit ids identical, in order |

## Negative cases

- A2, a dropped test must be visible in the count: running the git-memory
  group with one test deselected reports `63 passed, 1 deselected`, against
  `64 passed` for the same command without the deselection. The count
  comparison above therefore binds.
- A3 and A4 negative cases were run by their own tasks; each perturbed its
  rebuilt fixture's shape and observed the matching assertion go red. The
  verbatim failures are in those tasks' commits and reports.

## Note for the reader, not a finding of this change

An unmatched `--deselect <nodeid>` is silently ignored by the pytest version
in the locked requirements: the first attempt at the A2 negative case passed a
node id that did not resolve and still reported `64 passed`. The case above
uses `-k` instead. Nothing in this branch depends on `--deselect`.

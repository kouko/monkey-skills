# Whole-suite timing and diff scope — W2-01

Machine: this host, 16 cores. Command: the repo's own declared package-test
command from `docs/loom/KICKOFF-DEFAULTS.md`, driven group by group by a
scratch harness that wraps `scripts/run_package_tests.py`'s own
`loom_family_commands()` so each group is timed separately. The harness is not
committed; it only measures, and every command it runs is the runner's own. The
runner is fail-fast (`scripts/run_package_tests.py:63` returns on the first
non-zero group), so a whole-suite figure is only meaningful when no group fails.

## Measured at

Runs 1 and 2 below were taken at `670ef7913`, after the round-2 fix batch. Three
paths landed after it — this file, `plan.md` and `loom-workflow/CHANGELOG.md` —
and the changelog is **not** inert: the git-memory group binds its top heading to
the plugin version at
`loom-workflow/skills/git-memory/scripts/test_memory_grep_version.py:51`, which
is how the missing entry turned the suite red earlier on this branch. So the
declared suite was run again over the tree that contains the final changelog and
plan — `d00bc970a` — and exited 0 in 60.69s with the same 2148 assertions. The
only path landing after that run is this evidence file, and `grep` over every
`test_*.py` and `test-*.sh` in the repo finds no reference to it.

A first revision of this file reported runs taken at `992fab34f`, before the
version bump, and presented them as the branch HEAD. Both branch-end reviewers
caught that independently: at the sha those numbers were labelled with, the suite
was red — the bump had moved `loom-workflow`'s manifests to 4.3.1 and left the
root README's version cell at 4.3.0, which
`loom-workflow/scripts/test_independent_advisor_plugin_readmes.py:54` binds. Both
also caught the first attempt at this very section, which claimed the changelog
was executed by nothing.

## Totals

| run | tree | wall clock | assertions passed | any group non-zero exit |
|---|---|---:|---:|---|
| baseline | `89cf5d224` (branch base) | 154.58s | 2148 | no |
| after, run 1 | `670ef7913` | 63.00s | 2148 | no |
| after, run 2 | `670ef7913` | 58.48s | 2148 | no |
| after, run 3 | `d00bc970a` | 60.69s | 2148 | no |

The baseline row was measured in this change's first sitting, against the same
base tree; runs 1 through 3 are fresh measurements of the fixed tree. A reviewer
who tried to re-measure the baseline reported that the base tree does not
complete in a fresh clone — two `loom-memory` tests unrelated to this branch fail
there — so that row stands on its original sitting alone.

All three post-change runs sit under the intent's 95s Acceptance bound, and the pass count is
unchanged at 2148. The adversarial probe file this change also commits is not
part of that count: `scripts/run_package_tests.py` declares no group under
`docs/loom/**`, so `finalize-review` is what executes it.

## Per group, slowest six

| group | baseline | run 1 | run 2 | passed |
|---|---:|---:|---:|---:|
| `loom-workflow/tests/test-memory-grep-perf.sh` | 77.25s | 4.39s | 4.31s | 12 → 12 |
| `loom-workflow/skills/git-memory/scripts` | 28.63s | 11.54s | 10.41s | 64 → 64 |
| loom-code group (`-n auto`) | 22.15s | 20.97s | 20.92s | 1174 → 1174 |
| `loom-workflow/skills/decision-map/scripts` | 9.03s | 8.65s | 7.87s | 244 → 244 |
| `loom-workflow/tests/test_cot_explain_scripts.py` | 6.39s | 7.04s | 5.18s | 48 → 48 |
| `loom-design/scripts` | 2.15s | 1.84s | 1.71s | 204 → 204 |
| all 21 remaining commands | 8.98s | 8.55s | 8.07s | unchanged |

Only the first two rows are this change's work. The others move by a second or
two in both directions between runs of identical code; that spread is the
measurement noise floor on this machine, and nothing in this branch touches
them.

## Acceptance 5 — what the diff touches

`git diff --name-only 89cf5d224..HEAD`, fourteen paths:

```
README.md
docs/loom/2026-09-12-fast-test-fixtures/evidence/probes/test_abuse_fast_import_fixtures.py
docs/loom/2026-09-12-fast-test-fixtures/evidence/suite-timing.md
docs/loom/2026-09-12-fast-test-fixtures/plan.md
docs/loom/intent/2026-09-12-fast-test-fixtures.md
docs/loom/memory/a-count-probe-does-not-bind-its-fixtures-shape.md
docs/loom/memory/index.md
loom-workflow/.claude-plugin/plugin.json
loom-workflow/.codex-plugin/plugin.json
loom-workflow/CHANGELOG.md
loom-workflow/skills/git-memory/scripts/conftest.py
loom-workflow/skills/git-memory/scripts/test_probes_memory_grep_render.py
loom-workflow/skills/git-memory/scripts/test_probes_memory_grep_single_pass.py
loom-workflow/tests/test-memory-grep-perf.sh
```

Four loom records, one index, three test files, one pytest conftest, two plugin
manifests, one changelog and one README version cell. No script under test
appears. `git diff --exit-code 89cf5d224 HEAD --` exits 0 for `memory-grep.sh`,
`test_probe_store_failure_fails_loud.py` and
`test_probes_memory_grep_no_trailers_support.py`.

The manifests, the changelog and the README cell are not the intent's
"被測的程式碼": the version gate
(`scripts/check_version_bump.py`) treats any change under a plugin's `skills/`
tree as skill content and obliges the bump, the plugin's own test binds the
changelog's top entry and the README cell to that version, and none of the four
is read by anything under test.

## Fixture equivalence, verified three times independently

The claim is that each rebuilt fixture is byte-identical to what the per-commit
builder produced. It was checked by each task's implementer, re-checked by the
build orchestrator from separate processes, and re-checked again by a branch-end
reviewer, each building the fixture once with the base builder and once with the
HEAD builder and comparing commit object ids. Equal ids can only hold when
every message byte, the tree, both identities and both dates match.

| fixture | size | result |
|---|---|---|
| `build_perf_repo` (shell) | 2000 commits, 300 memory-worthy, 20 superseded | same HEAD id `6ee5166a1f445bdf9708c3adbb6825bf806fb011`, 2000 reachable, clean worktree |
| `build_perf_repo` (shell) | 20 commits, 5 memory-worthy, 1 superseded | same HEAD id `50a9c9e567a0f817a122c16b002882df537d7a40` — the second call site, raised by a reviewer and re-measured here |
| `_build_perf_repo` (pytest) | 200 commits | all 200 ids identical, in order |
| `_build_records_repo` (pytest) | 20 commits | all 20 ids identical, in order |
| `_build_records_repo` (pytest) | 200 commits | all 200 ids identical, in order |

`test_abuse_fast_import_fixtures.py` freezes the first of those ids as
`PINNED_PERF_HEAD`, so the comparison now runs on every probe execution rather
than once by hand.

### What a commit-id comparison does not cover

Storage layout. `fast-import` writes a packfile where 2,000 `git commit` calls
wrote loose objects, and that difference is invisible to commit ids. A
branch-end reviewer measured it instead of assuming, and the measurement was
then reproduced. To redo it: build the fixture from a checkout of each sha with
`bash loom-workflow/tests/test-memory-grep-perf.sh` — run it from inside that
checkout, since the extracted builder cannot find `memory-grep.sh` from
elsewhere and silently produces a nonsense timing — and read the script's own
timed line, expecting `12 PASS / 0 FAIL`. The reviewer's pair, 0.218s loose
against 0.148s packed, is two single runs in different cache states (a cold
fresh clone against a warm worktree), so neither is an average. Driving
`memory-grep.sh` directly against both fixtures in the same warm tree gives
0.208 / 0.212 / 0.212s over the loose build and 0.132 / 0.136 / 0.139s over the
packed one, with 6000 loose objects and no packfile on one side and no loose
objects and two packfiles on the other. So the 2.0s bound keeps roughly 15x
headroom where it had about 10x. The perf assertion still means what it meant,
and the script reads nothing layout-sensitive — no reflog, `for-each-ref`,
`count-objects` or `cat-file --batch-all-objects`. Index and worktree state, the
other output outside the object graph, is restored by the builders' final
`reset --hard` and asserted by the probe's `status --porcelain` and
`content.txt` checks.

## Negative cases

- **The adversarial pass found a real defect.** `fast_import_commits` reached
  its final hard reset with no ref written, so an empty spec list died on
  `fatal: ambiguous argument 'refs/heads/main'` instead of doing nothing.
  `test_empty_spec_list_leaves_head_unborn` caught it; `e68adc34f` fixed it with
  an early return.
- **Two claims in the first round were overstated, and the probes could not see
  either.** `_cleanup_whitespace` reimplements git's `--cleanup=whitespace`;
  a reviewer differential-fuzzed it against real `git commit -F -` over 2019
  bodies and found it stripped `\v` (0x0b) and `\f` (0x0c), which git does not.
  The probe case that exists to catch exactly this had seven bodies containing
  only spaces and newlines. Three cases carrying those bytes were added, seen
  red against the pre-fix code, and are green now. Separately, the rebuilt
  builders' shape read-back compared output against the builder's own
  parameters, so four perturbations of 200/40/5 — including the one its own
  comment named as the worked example — built with nothing firing. The
  read-back is now absolute.
- **A dropped test must be visible in the count.** Running the git-memory group
  with one test deselected reports `63 passed, 1 deselected` against `64 passed`
  for the same command without it, so the count comparison in the Totals table
  binds.
- The A3 and A4 negative cases were run by their own tasks, each perturbing its
  rebuilt fixture's shape and observing the matching assertion go red. The
  verbatim failures are in those tasks' commits.

## Note for the reader, not a finding of this change

An unmatched `--deselect <nodeid>` is silently ignored by the pytest version in
the locked requirements: the first attempt at the deselection case above passed
a node id that did not resolve and still reported `64 passed`. The case uses
`-k` instead. Nothing in this branch depends on `--deselect`.

# W0-02 adversarial RED evidence

Target: `4e9074e3beed2fbc644a8b45a37cf85ff143ed7e`.
Artifact: `test_w002_mutation_boundary.py` beside this note.
All mutations run inside temporary fixture repositories; production files and
permanent test files are untouched. No declared mutation/fuzz tool was found in
the package requirements or package CI workflow; these are executable abuse cases.

Re-run from the repository root:

```sh
uv run --isolated --with pytest --with pyyaml python -m pytest docs/loom/2026-09-06-reuse-branch-end-suite-result/evidence/probes/test_w002_mutation_boundary.py -q --tb=line
```

Observed outcome: **10 failed, 9 passed**, process exit **1**. The failures
are intended RED assertions of missing W0-02 behavior, not fixture failures.
Every mutation case asserts that its mutation actually happened before checking
the gate verdict. This is a pre-implementation attack result, not approval.

| Cases | Observed behavior | Result |
|---|---|---|
| Hook, absolute `git -C`, unrelated caller directory | Selected repository HEAD moves; hook exits 0; unrelated directory stays empty | RED |
| Package command makes an empty commit | HEAD moves, porcelain stays clean, push checker exits 0 | RED |
| Last adversarial command changes tracked, staged, or untracked content | Each command exits 0 and push checker exits 0 with changed porcelain | 3 RED |
| Last adversarial command advances HEAD | Push checker exits 0 after HEAD moves | RED |
| Last adversarial command starts a separate writer process | Writer changes tracked content and exits 0; checker exits 0 | RED |
| First adversarial command changes tracked content | Later probes were already prevalidated; checker exits 0 | RED |
| Build package execution before review | Affirmative package-run instruction remains in section 6 | RED, static contract |
| Ship pre-hook package execution | Full pytest command remains in Push checklist | RED, static contract |
| Package command changes tracked content | Existing later adversarial prechecks reject the dirty tree | held |
| Repeated unchanged checkpoint | Both executions release, same HEAD and clean tree | pass |
| Forged passing result for failing command | Actual nonzero execution blocks | held |
| Edited command, stale SHA, dirty input | Each is rejected | 3 held |
| Missing executable, malformed argv | Each is rejected | 2 held |
| Sentence oracle self-test | Affirmative example accepted, negated and cross-sentence examples rejected | pass |

Representative actual RED output, omitting machine-local traceback paths:

```text
AssertionError: hook rc=0
package-tests `python3 evidence/package.py`: observed exit code 0 (recorded result: 'pass')
adversarial evidence/abuse_empty.py: observed exit code 0 (recorded command: 'python3 evidence/abuse_empty.py', recorded result: 'pass'), referenced by 1 records
adversarial evidence/abuse_boundary.py: observed exit code 0 (recorded command: 'python3 evidence/abuse_boundary.py', recorded result: 'pass'), referenced by 1 records
adversarial evidence/abuse_hostile.py: observed exit code 0 (recorded command: 'python3 evidence/abuse_hostile.py', recorded result: 'pass'), referenced by 1 records
AssertionError: rc=0
AssertionError: Build still executes the complete suite before review
AssertionError: Ship still runs the package suite before its hook
```

## Findings

- **Important — `loom-code/scripts/loom_checker.py:_cmd_push`**: successful
  package and adversarial processes invalidate the validated repository state
  without blocking release. Capture the selected repository's validated HEAD
  and clean porcelain before execution and reject changed state afterward.
  Cover both HEAD-only changes and the final adversarial process.
- **Important — `loom-code/skills/build/SKILL.md:6`**: Build still requires
  running the complete package command before branch-end review. Remove that
  execution obligation while retaining task and integration verification.
- **Important — `loom-code/skills/ship/SKILL.md:4`**: Ship's Push checklist
  invokes the complete pytest command before the hook. Remove this residual
  package execution while retaining the deterministic checklist commands.

## Attack-catalogue interpretation and limits

- Forged artifact: held for recorded pass paired with a failing real command.
- Edited gate input: held for a record whose command differs from declaration.
- Stale artifact: held for a package record pointing at the base SHA.
- Repository/process boundary: reproduced for a HEAD mutation in the absolute
  `-C` target while the hook caller stands in a different directory.
- Concurrent writer: the separate-process write between validation and return
  is reproduced. This is deterministic interleaving, not a two-writer lost-update
  claim and not a proof about a writer acting after the checker exits.
- Prose exemption: no claimed live-agent reproduction. The exact temptation
  "the diff is one line, proceed?" does not justify skipping deterministic
  checks; this probe only exercises static Build/Ship instruction contracts.
  It does not claim a cold-agent behavioral run or complete class coverage.

The suite intentionally asserts behavior at the full checker/hook boundary,
so an implementation can place the final snapshot check centrally. Existing
package dirty-tree rejection is recorded as held, not presented as a new hole.
Ignored files and transient changes restored before return are outside these
cases. Each test name uses the `test_<unit>_<state>_<expected>` convention.

## Commit privacy

The exact commit carrier passed the deterministic privacy scan (exit 0, `[]`)
and a fresh-context judge (`verdict: PASS`, `findings: []`). No machine-local
paths or raw environment dumps are included in that carrier.

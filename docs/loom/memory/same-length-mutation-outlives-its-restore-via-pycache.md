---
name: same-length-mutation-outlives-its-restore-via-pycache
description: CPython validates a `.pyc` by (source mtime SECONDS, source size), so a length-preserving mutation restored within the same second leaves the mutant's bytecode valid — the next case in a mutation run then executes against it, which turned a real survivor into a reported "5 of 5 killed"
type: gotcha
origin: 2026-07-27 mutation-testing arc (PR #623) — the false kill was caught only by re-running with bytecode writing disabled
---

A mutation harness that writes a mutant, runs pytest, and restores the
original in a `finally` looks airtight — `git status` comes back clean. It is
not, when two things coincide:

- the mutation is **length-preserving** (`// 3` → `// 4`, `!=` → `==`,
  `-` → `+`, `12` → `13`), so the source size is unchanged; and
- the restore lands in the **same wall-clock second** as the mutated write.

CPython's `.pyc` validity check is `(source mtime seconds, source size)`.
Neither changed, so the mutant's compiled bytecode is still considered
current. The restored source is never recompiled, and the NEXT case in the
run imports the mutant.

Observed cost: a five-case run reported "5 of 5 killed". Re-run with
`PYTHONDONTWRITEBYTECODE=1` set **in the subprocess env**, one case was
SURVIVED — a test that could not fail, which would otherwise have shipped as
a closed gap.

**Why:** the parent process having `PYTHONDONTWRITEBYTECODE=1` is not enough;
pytest runs in a child, and `subprocess.run(..., env={...})` without merging
`os.environ` — or with a hand-built env — silently drops it. The harness's own
restore-and-verify step cannot see the problem either, because the SOURCE is
genuinely restored; only the bytecode is stale.

**How to apply:** in any mutation or patch-and-revert harness, set
`PYTHONDONTWRITEBYTECODE=1` in the CHILD process environment
(`env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}`), and unlink the
mutated module's `.pyc` before each run as a belt-and-braces second measure.
When a whole batch reports a perfect score, treat that as a prompt to
re-verify rather than as a result. Restoring the source is not the same as
restoring the program. Related:
[[reviewers-rerun-mutations-before-accepting-fix]] — an independent re-run is
what surfaced this, and it is why the reviewer's own harness must not reuse
the author's.

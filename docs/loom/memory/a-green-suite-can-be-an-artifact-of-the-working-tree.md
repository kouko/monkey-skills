---
name: a-green-suite-can-be-an-artifact-of-the-working-tree
description: A test that reads a real repo artifact reads the WORKING-TREE copy, so an uncommitted edit can keep it green for an entire session while the same test fails at HEAD — a real-artifact test must read the committed content (git show HEAD:<path>) or the suite is reporting on the author's desk, not on the branch
type: gotcha
origin: PR #693 (feat/open-question-dispatch-gate, merged 2026-08-14) — the arc's own gate test; recorded 2026-08-18 in the arc's residue pass
---

A test that exercises a checker against a real document in the repo
opens that document from the filesystem. The filesystem holds the
working tree, not the branch. So an edit that has not been committed —
or has been staged but not committed, or belongs to a neighbouring
task's uncommitted work — makes the test pass, and it keeps passing on
every re-run for as long as the edit sits there.

Observed: the test running `check_open_questions.py` against the arc's
own plan asserted exit 0 and was green all session. The plan's
`## Open Questions` section existed only as an uncommitted edit. Run
against HEAD, the same test failed. Nothing in the suite output
distinguished the two situations.

**Why:** "the suite is green" is the sentence every close-out is built
on, and this failure mode makes it locally true and globally false. It
survives full-suite runs, per-task review, and re-runs, because every
one of those reads the same working tree. It is caught only by someone
who thinks to compare against the committed content — and it is most
likely to bite precisely at close-out, when several tasks' edits are in
flight at once and it is least obvious which of them is committed.
Distinct from [[grep-tests-scope-to-measured-neighborhood]]: there the
assertion is too loose; here the assertion is fine and the *input* is
wrong.

**How to apply:** any test whose input is a real repo artifact (not a
fixture it writes itself) must read the committed content —
`git show HEAD:<path>` — rather than opening the path. If reading HEAD
is impractical, the test must be written against a fixture it creates,
and the real-artifact check moved to a separate, explicitly
HEAD-reading guard. And when reporting a green suite for a branch that
has uncommitted work in it, say so: "green with N uncommitted files"
is a different claim from "green", and only the second one is about
the branch.

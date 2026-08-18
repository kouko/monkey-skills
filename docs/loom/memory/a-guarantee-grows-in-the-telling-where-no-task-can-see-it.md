---
name: a-guarantee-grows-in-the-telling-where-no-task-can-see-it
description: When several tasks each ship a correctly-scoped mechanism, the prose written AROUND them — a protocol rule, release notes, a test's docstring — tends to describe the union as unconditional; every per-task review passes because every task scoped its own mechanism right, and only a cumulative read catches the guarantee that grew
type: gotcha
origin: 2026-08-18 stale-render arc (loom-code 0.88.0) — the same overclaim recurred four times in one branch across two different axes, caught once in a test docstring, once in the CHANGELOG, and twice by whole-branch review
---

Four legs shipped in one arc: a version stamp (scoped to the two HTML
outputs by design), a fallback, a path pin, and a fail-loud postcondition
(scoped to one output mode's rendition regions by design). Every task was
correct. The prose written around them was not:

- a test docstring claimed its fixture reproduced the stale-copy failure —
  it could not, that copy emits a different wrapper element entirely;
- the release notes implied the postcondition is what makes the reported
  incidents visible — the stamp is;
- the delivery rule said "the produced page", which by its own words
  refused an output that carries no stamp BY CONSTRUCTION;
- the same rule described the postcondition without the mode limit that
  makes it inert on two of three output paths.

Each per-task reviewer read one task and its own scope, and each was right.
Nobody was assigned the sentence that spanned them.

**Why:** scoping decisions live in the task; guarantees live in the prose
around the tasks. Review is organised by task. So the one artifact that
generalizes is the one artifact no reviewer owns — and a guarantee stated
too broadly is not a wording problem, it is a false claim about what the
software does, aimed at whoever reads the contract next.

**How to apply:** on any multi-task arc, run one cumulative pass whose
explicit question is *does the contract prose claim more than the union of
what the tasks shipped?* — sweeping protocol text, release notes, docstrings
and briefs together, including softened forms ("helps detect", "makes
visible") that imply the claim without stating it. When one such overclaim
IS found, sweep for the same shape on other axes before declaring it fixed:
this arc's first three catches were all on the staleness axis, and the
fourth, on the output-mode axis, was still live.
Related: [[a-per-task-triad-cannot-see-cross-plugin-guard-tests]].

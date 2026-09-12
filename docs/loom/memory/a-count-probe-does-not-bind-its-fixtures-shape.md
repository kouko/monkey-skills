---
name: a-count-probe-does-not-bind-its-fixtures-shape
description: A probe that counts subprocess or tool invocations says nothing about the shape of the fixture it counts them over, so a fixture can silently drift to the wrong record shape with every such probe still green — before rewriting a fixture, perturb the OLD one and require something to go red; when nothing does, the rewrite owes a shape assertion, not just an output oracle
type: practice
sources:
  - resource: 2026-09-12 fast-test-fixtures (loom-workflow 4.3.1) — the W1-02 implementer perturbed the pre-change builder's memory_count from 40 to 39 and both git-memory perf probes stayed green
---

Two probes in `loom-workflow/skills/git-memory/scripts/` pin
`memory-grep.sh`'s cost contract: the number of `git` invocations it makes
and the number of `jq` invocations its renderers make must be a small
constant regardless of repository size. Both build a fixture repository of
a stated shape — 200 commits, 40 of them memory-worthy, 5 of those
superseded — and both assert only on the counts.

Neither asserts the shape. The implementer rewriting those builders tested
this against the code as it stood, before touching it: dropping
`memory_count` from 40 to 39 left both probes passing. So a fixture that
quietly produced no memory-worthy commits at all would have left the
probes green while the contract they exist to defend went unmeasured —
the same class of hole an earlier change in this family found in its own
golden files.

**Why:** a count assertion is orthogonal to the content it counts over.
"Four git calls on a 2,000-commit repo" and "four git calls on a repo with
nothing to find" are the same number. The fixture is an input the probe
never reads back, which makes it the one part of a perf probe with no
guard on it at all — and a fixture rewrite is precisely the moment that
absence pays out.

**How to apply:** before changing how a fixture is built, perturb the
existing builder's stated shape by one element and run the suite. Something
must go red. When nothing does, the rewrite owes two artifacts rather than
one: an output oracle proving the new builder reproduces the old bytes —
commit object ids are the cheapest form when the fixture is a repository,
since one id covers every message byte, the tree, both identities and both
dates — and a read-back assertion inside the builder itself, so a later
drift fails at build time instead of relaxing whatever the probe was meant
to bind. Keep the read-back absolute where it can be: a check comparing
output against the builder's own parameters moves with them and proves
nothing. Related:
[[a-rewrite-that-promises-byte-identical-output-needs-an-oracle-built-from-the-old-code-first]],
[[a-mutation-test-must-run-the-production-assertion]],
[[assertion-must-encode-the-property-it-claims]].

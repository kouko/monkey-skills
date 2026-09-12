---
name: a-count-probe-does-not-bind-its-fixtures-shape
description: A probe that counts subprocess or tool invocations says nothing about the shape of the fixture it counts them over, so a fixture can silently drift to the wrong record shape with every such probe still green — before rewriting a fixture, perturb the OLD one and require something to go red; when nothing does, the rewrite owes a shape assertion, not just an output oracle
type: practice
sources:
  - resource: 2026-09-12 fast-test-fixtures (loom-workflow 4.3.1) — the W1-02 implementer perturbed the pre-change `_build_perf_repo`'s memory_count from 40 to 39 and its git-call probe stayed green; the jq-call probe's own builder was never perturbed, and a branch-end reviewer then perturbed the shipped builder four ways with no assertion firing
---

Two probes in `loom-workflow/skills/git-memory/scripts/` pin
`memory-grep.sh`'s cost contract: the number of `git` invocations it makes
and the number of `jq` invocations its renderers make must each be a small
constant regardless of repository size. Each builds its own fixture of a
stated shape — the git-call probe 200 commits with 40 memory-worthy and 5
of those superseded, the jq-call probe 20 and then 200 commits with every
one memory-worthy and no supersession — and each asserts only on the
counts.

Neither asserted its shape. The implementer rewriting those builders
tested this against the code as it stood, before touching it: dropping
`memory_count` from 40 to 39 in the git-call probe's builder left it
passing. A branch-end reviewer went further on the rebuilt builder and
found four perturbations — memory_count 39, memory_count 20, n_commits
150, and n_commits 60 with memory_count 12 — every one of which built with
no assertion firing, because the read-back compared the output against the
builder's own parameters. So a fixture that quietly produced almost no
memory-worthy commits would have left the probes green while the contract
they exist to defend went unmeasured — the same class of hole an earlier
change in this family found in its own golden files.

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

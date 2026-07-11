---
name: static-text-pins-blind-to-courier-runtime-holes
description: Static text-pin tests on Workflow JS are structurally blind to runtime security holes in courier surfaces — a green 240+-test suite coexisted with a live path-traversal bypass and a dcg-blocked revert command; security-critical courier code needs an adversarial reviewer that EXECUTES probes (standalone node eval, in-repo guard-doc grep), plus an executable pin mirroring the repro once fixed
type: practice
origin: branch feat-principles-replay-l3-loop (2026-07-11) — T4 quality review, 2 🔴 found live behind a fully green suite
---

On the L3 improve-loop branch, the workflow test suite (static regex/marker
pins + node --check, the house convention for `.claude/workflows/*.js`) was
fully green while two real defects sat in the fixer stage: (1) the
per-segment path allow-list `^[A-Za-z0-9._-]+$` admits whole `..` segments,
so a traversal payload passed the ONLY guard between an agent-proposed edit
and an arbitrary-file write — reproduced live by the reviewer with a
standalone `node -e` eval of the committed function; (2) the revert courier
used `git checkout -- <path>`, which this repo's dangerous-command-guard
blocks (documented at `environment-gotchas.md:36-38` — "Undo with stash,
not checkout"), meaning every post-rejection round would have silently
aborted. Both were caught only by an adversarial code-quality reviewer that
executed probes and grepped in-repo guard documentation, not by the 240+
green tests.

**Why:** static text pins assert what the source SAYS, not what it DOES;
Workflow courier surfaces (Bash/Edit authority driven by agent-produced
content) fail exactly where text and runtime semantics diverge — regex
character classes, guard-blocked commands, quoting. A green suite on this
artifact type is necessary but provides zero evidence on those axes.

**How to apply:** when reviewing or shipping security-critical courier code
in a Workflow script, (1) require the reviewer to EXECUTE adversarial
probes (extract the guard function into a standalone node eval with
traversal/quote payloads) and to grep the repo's guard docs
(environment-gotchas, dcg patterns) for every shell command the courier
issues; (2) once a hole is fixed, pin it with an EXECUTABLE test mirroring
the repro (node -e via subprocess), not only a marker regex; (3) treat
"suite is green" as a non-statement about courier runtime security.

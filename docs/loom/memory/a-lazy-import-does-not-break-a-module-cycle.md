---
name: a-lazy-import-does-not-break-a-module-cycle
description: Moving one edge of a circular module dependency into a function delays when the cycle executes but does not make the dependency graph one-way; remove or invert the edge, then assert the import graph directly
type: gotcha
origin: Outcome Map v3 whole-branch review, 2026-08-30
---

A function-local import can make a circular dependency appear harmless because
module initialization succeeds. The architecture is still circular: either
module can require the other to provide its public operation, and later edits
can turn the deferred edge back into an initialization or ownership failure.

**Why:** Review of the Outcome Map v3 writer boundary found that moving
`map_transaction` behavior into `map_lifecycle` only renamed the cycle while
`map_store` still imported the orchestration module from wrapper functions.
Tests passed, but ownership remained bidirectional.

**How to apply:** Draw or inspect the actual module import graph, including
imports inside functions. Put shared primitives below both consumers, move
orchestration above persistence, migrate callers to the authoritative facade,
and add an AST-level regression assertion that the lower layer never imports
either orchestration module.

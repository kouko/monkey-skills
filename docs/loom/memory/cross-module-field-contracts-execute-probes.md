---
name: cross-module-field-contracts-execute-probes
description: In build-assembled programs, cross-module field contracts are the systemic risk — review by concatenating the modules and executing behavioral probes, not by grep
type: practice
origin: PR #479 (loom-pipeline conductor v0.1, 17-task build, 2026-07-04)
---

In a build-assembled program — separate source modules concatenated
by a build step into one shipped artifact — the systemic risk is
cross-module FIELD contracts: one module writes an object with one
field name/shape, another module reads a different one, and no
single-module test or grep-style review notices. On PR #479, review
that concatenated the modules and EXECUTED behavioral probes
(`node -e` snippets driving the assembled code) caught all 8
serious-class defects, including three producer/consumer field-shape
mismatches (`judge`/`role`, `bucket`/`text`, `station` vs `name`);
grep-style review caught none of them.

**Why:** each module is internally consistent, so per-module tests
and text search stay green; only running data across the module seam
exposes that the two sides disagree about the field.

**How to apply:** when reviewing or testing build-assembled code,
make behavioral execution the default — assemble the artifact and
run small probes that push real data across module boundaries,
asserting on the values that come out.

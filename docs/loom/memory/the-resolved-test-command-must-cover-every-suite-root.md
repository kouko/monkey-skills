---
name: the-resolved-test-command-must-cover-every-suite-root
description: this repo runs two pytest suites (repo-root scripts/ and loom-code/scripts, ~310 + ~1870 tests) — a "suite green" claim resolved from only the root suite let two version-pin failures and a compaction-pin failure ride three tasks undetected until a reviewer independently ran both; resolve the package test command as BOTH invocations, and treat any single-suite green claim as unverified
---

The SDD orchestrator resolved the package test command once as
`python3 -m pytest scripts/ -q` (declared-first, verified by a live run)
and passed it into every implementer dispatch of the 2026-08-28
review-loop-convergence arc. Three tasks reported "suite green" against
that command while `loom-code/scripts`' 1,800+ tests were never run;
the 0.102.0 version bump then reddened two version-pin tests and a
contract-compaction pin there, caught only when the task-4
code-quality-reviewer ran the second suite independently. The two
suites are visible in `AGENTS.md` and in CI, but the resolution step
stopped at the first suite that ran and emitted a count.

**Why:** a test-command resolution that stops at one passing invocation
silently narrows every downstream "green" claim to that suite; the gap
compounds because each task inherits the same resolved command.

**How to apply:** when resolving this repo's package test command,
resolve it as both `python3 -m pytest scripts/ -q` AND
`python3 -m pytest loom-code/scripts -q`, and require both tails in any
green claim; generalized — enumerate every pytest root before caching a
resolved command, and re-verify the enumeration when a new suite root
appears in CI config.

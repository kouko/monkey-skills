---
name: a-user-declared-lane-is-the-small-lane-with-its-floor-waived-never-a-third-shape
description: The first draft of gate-only listed what it forbade (checker, hooks, agent contracts, SKILL.md) and let ordinary code through with zero readers; the adversary showed the recompute settles a pure small-class delta as small before any declaration is read, so the only coherent shape was "the small lane with the reader floor waived, when the user says so" — PRINCIPLES.md non-negotiable 2 now names exactly that, and a declaration counts only when its commit states the line and the delta recomputes small
type: practice
origin: 2026-09-05 user-declared-express-lane (loom-code 1.6.0) — two reader rounds, one ratification; iCHEF-dbt-pipeline's 62 of 63 PRs that skipped loom entirely were the evidence for wanting a recorded way to skip
---

A lighter lane is a user's decision about verification cost, and loom
records it as a dated `lane:` line the user's commit states. But "lighter"
has to be defined against the recompute the checker already does, not
against a list of forbidden paths: the recompute classifies a delta as
`small` (tests, docs, CI/config, version sync, clean revert, one plugin,
no gate/skill/contract/standing/interface path) or `full`, and every
declaration is a floor on top of that classification. `express` is full
with one reader and no mid checkpoint; `gate-only` is small with zero
readers and no blind run. A delta the recompute calls full for any reason
keeps a gate-only declaration ignored, with the path in the reason.

**Why the first draft was wrong:** forbidding gate, skill and agent paths
felt like the right boundary, but it allowed ordinary code with zero
readers and it never met the recompute — a pure-docs delta reached the
small branch first and gate-only never applied at all. Two independent
readers found the two halves of that; the constitution decided it.

**How to apply:** when adding a switch the user can flip, express it as a
parameter of an existing recompute (a floor, a skipped step), not as a
new branch with its own eligibility list.

Related: [[a-graduated-probe-that-pins-a-fact-of-the-moment-goes-red-at-the-next-change]].

---
name: execute-cheap-loom-simplify-upgrades-at-review
description: When a LOOM-SIMPLIFY marker's recorded upgrade turns out one-line-cheap at review time, execute it on the spot instead of leaving the marker
type: practice
origin: PR #479 (loom-pipeline conductor v0.1, 2026-07-04)
---

`LOOM-SIMPLIFY:` is loom-code's in-code marker for a deliberate,
scope-bounded shortcut; each marker records the shortcut, a
checkable ceiling, the upgrade path, and a reference
(`loom-code/skills/subagent-driven-development/standards/deliberate-simplification.md`).
When review reaches such a marker and the recorded upgrade turns out
to be one-line-cheap, execute the upgrade right there instead of
leaving the marker for later. On PR #479 three such upgrades were
executed at review time — a hardcoded personal checkout path became
a `skillsRoot` argument, hardcoded station names were generalized,
and a probe budget was parameterized — and all three paid off
immediately.

**Why:** a marker whose upgrade costs less than re-reading the
marker later is pure debt; deferring it buys nothing and risks the
shortcut outliving its ceiling unnoticed.

**How to apply:** at review time, price each LOOM-SIMPLIFY upgrade
you encounter; if it is roughly one line (or comparably trivial), do
it now and delete the marker. Keep the marker only when the upgrade
is genuinely non-trivial.

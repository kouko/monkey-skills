---
name: a-successful-gate-command-can-mutate-the-reviewed-tree
description: An executable quality gate that exits zero can still move HEAD or change tracked, staged, or untracked state, so release safety requires recomputing the selected repository's revision and porcelain after the final executable finishes rather than trusting exit codes or per-command prechecks
type: gotcha
origin: 2026-09-06-reuse-branch-end-suite-result — W0-02 adversarial probes
---

A package suite or adversarial probe is an executable program, not a passive
observation. It can return success after writing a tracked file, staging a
change, creating an untracked file, or committing and moving HEAD. A clean-tree
check before each command misses mutation performed by the final command in the
sequence, and checking only porcelain misses a clean HEAD move.

**Why:** a release gate that validates one revision but lets its own executable
checks replace that revision can release bytes no reviewer assessed. Exit zero
proves only the program's reported outcome; it says nothing about whether the
subject under review stayed fixed during execution.

**How to apply:** resolve the repository selected by the intercepted operation,
snapshot both its live HEAD and `git status --porcelain` immediately before the
first untrusted executable, and recompute both after the last one. Block when
either differs, even when every command returned zero. Keep per-command input
checks as defence in depth, but never treat them as the final-state check.

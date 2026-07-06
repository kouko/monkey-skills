---
name: python-path-parent-resolve-gotcha
description: Python pathlib — Path(".").parent is still ".", so resolve() before any parent-directory lookup on a relative path
type: gotcha
origin: PR #472 (ui-flows per-change folder validator, 2026-07-02)
---

In Python's `pathlib`, `Path(".").parent` evaluates to `Path(".")` —
a relative path does not know its absolute location, so walking up
`.parent` from a relative path silently goes nowhere instead of
climbing the real directory tree.

**Why:** code that climbs parents to find a repo root or config file
appears to work in tests run from the right directory, then silently
loops or mis-resolves when handed a bare relative path.

**How to apply:** call `.resolve()` on the path first, then do
parent lookups: `Path(p).resolve().parent`.

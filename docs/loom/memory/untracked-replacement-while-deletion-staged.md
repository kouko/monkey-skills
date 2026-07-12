---
name: untracked-replacement-while-deletion-staged
description: During a file relocation, a replacement created with Write stays UNTRACKED while the deletion of the file it replaces is already staged — committing the index as-is ships the deletion without the replacement, and git diff cannot reveal it because untracked files never appear in a diff
type: gotcha
origin: PR #556 Axis-B relocation (2026-07-13) — whole-branch review caught it pre-commit
---

Relocating `X/foo.py` → `Y/foo.py` by **`git rm X/foo.py` (or a `git mv`
that staged only the source deletion) + `Write Y/foo.py`** leaves an
asymmetric index: the **deletion is staged**, the **replacement is
untracked** (`??`). A `git commit` of that index ships the deletion
*without* the replacement. Real case: a test file relocated across
plugins — the deletion of the old `test_surface_canon.py` was staged,
the new one was created with the Write tool and never `git add`ed, so
the relocated canon would have shipped **completely unguarded**.

**Why it survives review:** `git diff <base>` — the command a reviewer
runs to see the change — **does not show untracked files at all**. The
missing replacement is invisible in every diff-based check; it only
appears in `git status` as a `??` line sitting next to the `D`. A
whole-branch reviewer reading `git status` (not just the diff) is what
caught it; no per-task reviewer could, because each task's own suite was
green in the working tree where the untracked file DID exist.

**How to apply:** on any relocation, before committing run
`git status --short` and pair every `D` (staged deletion) with its
intended replacement. `git add` the replacement **by name** (never
`git add -A` in this repo) — git then re-reads the index and collapses
the `D` + `A` into a single `R` (rename), which is the signal the pair
is complete. If a `D` has no matching `R`/`A`, the replacement is still
untracked.

This is the **under-inclusion** twin of
[[git-mv-sweeps-untracked-files]] (that one is *over*-inclusion — `git mv`
of a directory drags untracked passengers IN). Both stem from the same
blind spot: **untracked files are invisible in `git diff` during a
relocation** — trust `git status`, not the diff, for the tracked/untracked
boundary. See also [[parallel-wave-commit-discipline]] (the orchestrator
commits; implementers leave the working tree, so the orchestrator owns
exactly this staging check).

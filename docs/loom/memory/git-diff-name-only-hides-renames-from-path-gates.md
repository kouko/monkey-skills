---
name: git-diff-name-only-hides-renames-from-path-gates
description: git diff --name-only silently collapses a rename to its NEW path only, so any gate that classifies changed files by path can be bypassed by renaming a guarded file into an exempt directory — enumerate with --no-renames (or parse --name-status both sides)
type: gotcha
origin: 2026-08-11 review-cost-reduction arc — record-only exemption 🔴, reproduced end-to-end pre-fix (loom_gate_markers.py, fixed in the same arc with a rename-fixture test)
---

Git's rename detection is ON by default: `git mv guarded/file.md
exempt/notes.md` plus a small edit shows up in `git diff --name-only`
as ONLY the new path. A path-classification gate reading that list
never sees the guarded old path — the record-only push exemption minted
successfully for a branch that had moved a contract-class agent file
into `docs/`, reproduced end-to-end against the real CLI before the fix.

**Why:** the bypass needs no adversary — file reorganizations and doc
moves trigger rename detection naturally, so the gate silently weakens
on exactly the operations a repo performs routinely.

**How to apply:** any code that enumerates changed files to make a
policy decision passes `--no-renames` (or parses `--name-status` and
treats BOTH sides of an `R` line as changed). Pair the fix with a
fixture that first proves rename detection fired (`--name-status`
starts with `R`) before asserting the refusal — otherwise the test can
pass on a plain add/delete without exercising the bypass.

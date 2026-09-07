---
name: a-successful-gate-command-can-mutate-the-reviewed-tree
description: An executable quality gate can mutate the reviewed tree synchronously or after its process exits, so a safe release boundary needs final state recomputation plus an immutable published object and a shell-stable canonical command
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
either differs, even when every command returned zero. That closes synchronous
mutation only: a successful process can leave a detached child that changes a
branch after the hook returns. Bind the later network operation to the exact
full object ID that passed validation instead of a mutable branch name.

The command text is another boundary. Parsing one safe-looking refspec is not
enough when shell expansion, aliases, wrappers, or Git configuration can add
runtime arguments, tags, or submodule pushes. Accept one canonical quote-all
command using the trusted absolute Git executable, a literal remote, the exact
object-to-branch refspec, and fixed flags that disable implicit tag and
submodule publication plus repository-configured pre-push hooks. A quoted absolute executable can still be shadowed by
an inherited shell function with the same name, so the canonical command starts
with the supported shell's standard `command` builtin; that builtin is the
explicit trust root. Reject every other form before running the expensive
suite. This guarantees which object is published under that supported-shell
boundary; it does not claim to contain hostile descendants, protect a shell
whose `command` builtin is itself replaced, or stop later local-file mutation.

---
name: bash-matched-git-guard-is-the-only-cross-host-enforcement-surface
description: A mechanical gate that must hold on BOTH Claude Code and Codex has exactly one place to live — a Bash-matched PreToolUse guard (loom-code's git-guard.py, forwarded on Codex by .codex/hooks/git-guard-shim.sh) plus portable scripts and SessionStart-injected text — because Codex 0.139 fires PreToolUse for Bash only (Skill/Write/Edit hooks never fire there); and inside that guard, list staged paths with `git diff --cached -z` (NUL split) — the default `core.quotepath` octal-escapes non-ASCII filenames so a `docs/loom/plans/計画.md` fails a `startswith`/`endswith` filter and is silently allowed
type: gotcha
origin: branch onramp-explicit-choice-gate (2026-08-18) — on-ramp explicit-choice gate arc; Codex facts docs/loom/codex-verification.md:102-116 + loom-code/skills/using-loom-code/references/codex-tools.md:64-83; quotepath bypass caught by the whole-branch review panel (round 1) and fixed in loom-code/hooks/git-guard.py (`-z`) with a CJK-name regression test
---

Designing the on-ramp choice gate, the "door" candidates were a
PreToolUse hook on `Skill` (block brainstorming), a hook on
`Write`/`Edit`, a script the skill text tells the model to run, and the
existing Bash-matched git-guard. Only the last is enforced on Codex:
its hooks engine fires PreToolUse for Bash alone (upstream issue), while
SessionStart context injection works on both hosts. So the portable
shape is: SessionStart text (both hosts) + a plain-stdlib checker script
the skill invokes (any host, prose-invoked) + the Bash-matched guard as
the real door (both hosts via the shim, which forwards unconditionally
once the payload shape checks out).

Inside such a guard, never filter `git diff --cached --name-only` output
by prefix/suffix without `-z`: under the default `core.quotepath` a
non-ASCII path arrives as `"docs/loom/plans/\350\250\210\347\224\273.md"`
(quoted, escaped) and silently misses the filter — for a 中/日-working
user that is a plausible input, and it is exactly the silent-bypass
class the gate exists to close. `-z` both NUL-terminates and disables
the quoting.

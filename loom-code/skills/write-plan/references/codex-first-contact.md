# Codex first contact

Codex uses the installed `loom-code` plugin's `PreToolUse` publication hook.
There is no repository-local checker scaffold, copied contract, or firing
ledger to approve and synchronize.

Creating another worktree does not create another installed Loom hook identity:
Codex keys that definition to the installed plugin, not the repository path.
Repository-local hooks are separate host identities and may require their own
review for each absolute worktree path; name them separately rather than
attributing their prompt to Loom.

At the start of a change:

1. Resolve the injected plugin root and run
   `python3 <plugin-root>/scripts/loom_checker.py contract --require 2.0`.
2. Confirm `python3 <plugin-root>/scripts/loom_checker.py --list-rules`
   includes `push.attestation`.
3. If Codex presents a trust prompt for a new or modified installed definition,
   ask the user to review that single installed definition. Never edit Codex
   trust state, use `--dangerously-bypass-hook-trust`, or write hook files into
   the adopting repository to suppress the host decision.

The hook activates only for publication-shaped Bash commands. Normal shell
commands pass through without running repository verification. Canonical push
validation pins the selected repository, HEAD, remote, and refspec before the
fast attestation check.

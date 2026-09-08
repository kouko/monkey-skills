# Codex first contact

Codex uses the installed `loom-code` plugin's `PreToolUse` publication hook.
There is no repository-local checker scaffold, copied contract, or firing
ledger to approve and synchronize.

At the start of a change:

1. Resolve the injected plugin root and run
   `python3 <plugin-root>/scripts/loom_checker.py contract --require 1.0`.
2. Confirm `python3 <plugin-root>/scripts/loom_checker.py --list-rules`
   includes `push.attestation`.
3. If Codex presents a trust prompt for the installed plugin hook, ask the
   user to approve that single installed definition once. Do not write hook
   files into the adopting repository.

The hook activates only for publication-shaped Bash commands. Normal shell
commands pass through without running repository verification. Canonical push
validation pins the selected repository, HEAD, remote, and refspec before the
fast attestation check.

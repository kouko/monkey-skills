# Resolve plugin hook worktrees without repeated Loom trust — spec
intent: 2026-09-08-fix-plugin-hook-worktree-resolution@147d13a3e
pre-build-review: required — this changes the installed publication hook's repository selection and documents the Codex host trust boundary

## Requirements
REQ-1 — Use the executor-selected worktree
  WHEN a supported Bash tool call supplies an absolute `workdir`, the installed publication hook shall use that directory as the fallback repository for a publication command that carries no explicit repository selector, rather than the task's top-level `cwd` → Acceptance #1

REQ-2 — Preserve explicit repository selection
  WHEN a publication command selects a repository with an absolute `cd` or the supported canonical Git `-C` form, the publication hook shall keep that explicit selection authoritative over both `tool_input.workdir` and the top-level hook `cwd`; ambiguous, relative, missing, invalid, or conflicting selectors shall remain blocked → Acceptance #2

REQ-3 — Reproduce the Desktop mismatch permanently
  WHEN the regression test supplies a main-checkout top-level `cwd`, a feature-worktree `tool_input.workdir`, and a publication command without an embedded directory change, the hook shall validate the feature worktree and shall not report the main branch's empty diff → Acceptance #3

REQ-4 — Keep Loom trust plugin-scoped
  WHERE Codex loads the installed `loom-code` publication hook, creating another worktree for the same repository shall not create a repository-local Loom hook definition, checker copy, trust probe, or firing ledger and shall not require a separate Loom approval solely because the worktree path is new → Acceptance #4

REQ-5 — Report the host trust boundary honestly
  IF Codex classifies an installed hook as new or modified and requires review, THEN Loom shall direct the user to review that installed definition once and shall not edit private trust state, disable hooks, invoke a dangerous trust bypass, or claim that plugin code can suppress the host decision; repository-local non-Loom hooks shall be identified separately → Acceptance #5

REQ-6 — Retain publication safety and ordinary-command behavior
  WHEN the hook receives a non-publication Bash command, it shall continue without repository verification; when it receives a publication command, attestation, selected repository, immutable HEAD, destination, and exact-refspec protections shall remain enforced → Acceptance #6

## Design decision
- agent-decided — Add one hook-payload fallback resolver with precedence `command-explicit repository > absolute tool_input.workdir > top-level cwd`, because the command is the closest executable statement of intent and the executor workdir is more specific than the task root.
- agent-decided — Accept `tool_input.workdir` only when it is a non-empty absolute path naming an existing directory; invalid or relative executor metadata does not fall through silently for a publication-shaped command because doing so could validate the wrong checkout.
- agent-decided — Apply the resolved fallback to both canonical Git push validation and conservative GitHub publication parsing, while leaving canonical PR-create repository selection authoritative, so every publication route follows the same repository identity rule.
- agent-decided — Keep explicit `cd` and canonical Git `-C` parsing unchanged and fail closed on multiple or conflicting repository selections; this change fixes host metadata precedence, not the shell parser's safety model.
- agent-decided — Treat installed-plugin trust and repository-local hook trust as separate host identities. Loom owns only its installed hook; this repository's two PostToolUse definitions remain outside Loom and may independently require host review.
- agent-decided — Do not automate Codex's `--dangerously-bypass-hook-trust` option. Its own CLI labels it dangerous and intended for externally vetted automation, which does not satisfy the intent's safety constraints.
- agent-decided — Update the first-contact guidance to say that new or modified installed definitions may require one host review, while a new worktree alone must not generate Loom trust work.
- user-decided — Use Claude Code as the second-vendor reader for the pre-build spec review and closing review.

## Alternatives considered
- Require every agent command to begin with `cd <worktree>` — rejected because it pushes a host integration defect onto prompt compliance and recreates the same failure whenever a caller uses the tool's native workdir field.
- Always trust top-level hook `cwd` — rejected because the reproduced Desktop call shows it can name the task root while the executor runs in another worktree.
- Infer the worktree from branch names, PR numbers, or all registered worktrees — rejected because more than one candidate may exist and guessing would weaken fail-closed publication safety.
- Silently approve hooks by editing Codex state or using `--dangerously-bypass-hook-trust` — rejected because trust is host-owned, the bypass is explicitly dangerous, and both violate the confirmed constraints.
- Restore one repository-local Loom hook per checkout — rejected because it reintroduces copied code, per-worktree approval, synchronization, and firing-ledger costs removed by the installed-plugin design.
- Remove this repository's unrelated PostToolUse hooks — rejected as out of scope; they must be named separately so their prompts are not attributed to Loom.

## Current state evidence
- Forward: `loom-code/hooks/hooks.json` registers the installed `PreToolUse` Bash handler as `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/loom_checker.py" push --hook`.
- Reverse: `loom-code/scripts/loom_checker.py` function `cmd_push` reads `tool_input.command`, but derives its fallback only from `payload.get("cwd")`; canonical Git push and GitHub actions both receive that fallback.
- Error: `loom-code/scripts/loom_checker.py` function `git_dash_c_push_cwd` correctly honors explicit `cd` and Git `-C`, but its host-reported fallback cannot distinguish a Desktop task root from a Bash executor workdir; the reproduced PR-merge payload therefore validates main and reports an empty branch diff.
- Data: Codex CLI 0.153.4's local hook schema exposes `tool_input` and top-level `cwd`, while the Bash executor call carries `workdir`; its hook UI locally labels new and modified definitions as requiring review. `.codex/hooks.json` in this repository separately defines two non-Loom PostToolUse commands.
- Boundary: `loom-code/skills/write-plan/references/codex-first-contact.md` already forbids a repository-local Loom checker, scaffold, or firing ledger; attestation generation, privacy, review convergence, package execution, the repository's unrelated PostToolUse hooks, and Codex's private trust storage remain unchanged.

## UI flows
N/A — this is an engineering correction to hook repository identity and host-trust guidance; it adds no product surface or user-entered command.

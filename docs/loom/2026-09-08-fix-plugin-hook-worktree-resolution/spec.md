# Resolve plugin hook worktrees without repeated Loom trust — spec
intent: 2026-09-08-fix-plugin-hook-worktree-resolution@147d13a3e
pre-build-review: required — this changes the installed publication hook's repository selection and documents the Codex host trust boundary

## Requirements
REQ-1 — Make the selected worktree explicit
  WHEN Loom issues an authorized direct PR-merge command, Loom shall always render an absolute `cd` to the selected repository root in the same command because the hook's top-level `cwd` is not observable when the command is rendered, so the installed hook validates the executor-selected worktree without relying on unavailable executor metadata → Acceptance #1

REQ-2 — Preserve explicit repository selection
  WHEN a publication command selects a repository with an absolute `cd` or the supported canonical Git `-C` form, the publication hook shall keep that explicit selection authoritative over the top-level hook `cwd`; a direct PR merge with no absolute selection, a `-C` without a directory argument, a nonexistent selected directory, or ambiguous, relative, or conflicting selectors shall remain blocked, while other supported commands with no selector shall use top-level `cwd` as today → Acceptance #2

REQ-3 — Reproduce the Desktop mismatch permanently
  WHEN the regression test reuses the observed Codex payload shape with a main-checkout top-level `cwd`, no executor-workdir field, and a Loom-rendered publication command selecting a feature worktree, the hook shall validate the feature worktree and shall not report the main branch's empty diff → Acceptance #3

REQ-4 — Keep Loom trust plugin-scoped
  WHERE Codex loads the installed `loom-code` publication hook, Loom shall use the observed path-independent `loom-code@` identity, shall not create a repository-local Loom hook definition, checker copy, trust probe, or firing ledger for a new worktree, and shall identify an absolute-path trust identity as repository-local rather than Loom → Acceptance #4

REQ-5 — Report the host trust boundary honestly
  IF Codex classifies an installed hook as new or modified and requires review, THEN Loom shall direct the user to review that installed definition once and shall not edit private trust state, disable hooks, invoke a dangerous trust bypass, or claim that plugin code can suppress the host decision; repository-local non-Loom hooks shall be identified separately → Acceptance #5

REQ-6 — Retain publication safety and ordinary-command behavior
  WHEN the hook receives a non-publication Bash command, it shall continue without repository verification; when it receives a publication command, attestation, selected repository, immutable HEAD, destination, and exact-refspec protections shall remain enforced → Acceptance #6

## Design decision
- agent-decided — Do not add a hook-payload workdir resolver: the captured Codex 0.153.4 PreToolUse payload contains only `tool_input.command`, so treating an imagined field as authority would make tests pass without fixing production.
- agent-decided — Make Ship's user-authorized direct PR-merge command render `cd <absolute-repository> && gh pr merge ...` in one shell command; the host executes the command in its selected workdir, but only the rendered selector is visible and therefore verifiable by the hook. Existing push and PR creation continue through `cmd_publish`, which validates from its actual process working directory and does not need this repair.
- agent-decided — Keep top-level `cwd` as the fallback for supported commands other than a direct PR merge with no selector, preserving ordinary same-directory behavior; the hook must never search registered worktrees or guess from branch and PR names.
- agent-decided — Keep explicit `cd` and canonical Git `-C` behavior and fail closed on multiple or conflicting repository selections; this change makes repository identity visible rather than guessing from unavailable host metadata.
- agent-decided — Tighten the existing `push.attestation` implementation so a raw direct PR merge without an absolute command-visible repository is blocked; this enforces the Ship rendering rule without admitting a second prose-gate mechanism.
- agent-decided — Treat installed-plugin trust and repository-local hook trust as separate host identities. Loom owns only its installed hook; this repository's two PostToolUse definitions remain outside Loom and may independently require host review.
- agent-decided — Do not automate Codex's `--dangerously-bypass-hook-trust` option. Its own CLI labels it dangerous and intended for externally vetted automation, which does not satisfy the intent's safety constraints.
- agent-decided — Update the first-contact guidance to say that new or modified installed definitions may require one host review, while a new worktree alone must not generate Loom trust work; a repository-local hook in that worktree is a separate host identity and must be named as such.
- user-decided — Use Claude Code as the second-vendor reader for the pre-build spec review and closing review.

## Alternatives considered
- Ask the user to prepend `cd <worktree>` manually — rejected because Loom can render an absolute repository selector itself and the user should not repair agent command construction.
- Always trust top-level hook `cwd` — rejected because the reproduced Desktop call shows it can name the task root while the executor runs in another worktree.
- Infer the worktree from branch names, PR numbers, or all registered worktrees — rejected because more than one candidate may exist and guessing would weaken fail-closed publication safety.
- Silently approve hooks by editing Codex state or using `--dangerously-bypass-hook-trust` — rejected because trust is host-owned, the bypass is explicitly dangerous, and both violate the confirmed constraints.
- Restore one repository-local Loom hook per checkout — rejected because it reintroduces copied code, per-worktree approval, synchronization, and firing-ledger costs removed by the installed-plugin design.
- Remove this repository's unrelated PostToolUse hooks — rejected as out of scope; they must be named separately so their prompts are not attributed to Loom.

## Current state evidence
- Forward: `loom-code/hooks/hooks.json` registers the installed `PreToolUse` Bash handler as `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/loom_checker.py" push --hook`; `loom-code/scripts/loom_checker.py` function `cmd_publish` is the existing wrapper that executes push and PR creation from its actual process working directory.
- Reverse: `loom-code/scripts/loom_checker.py` function `cmd_push` reads `tool_input.command`, but derives its fallback only from `payload.get("cwd")`; canonical Git push and GitHub actions both receive that fallback.
- Error: `loom-code/scripts/loom_checker.py` function `git_dash_c_push_cwd` correctly honors explicit `cd` and Git `-C`, but its host-reported fallback cannot distinguish a Desktop task root from a Bash executor workdir; the reproduced PR-merge payload therefore validates main and reports an empty branch diff.
- Data: `docs/loom/2026-09-08-fix-plugin-hook-worktree-resolution/evidence/codex-hook-input-and-trust.md` records the real Codex CLI 0.153.4 payload: `tool_input` contains only `command`, while top-level `cwd` remains main. It also records the path-independent `loom-code@...` installed-hook trust key, the absolute-path repository-local keys, and their `trusted_hash` change boundary. `.codex/hooks.json` separately defines two non-Loom PostToolUse commands.
- Boundary: `loom-code/skills/write-plan/references/codex-first-contact.md` already forbids a repository-local Loom checker, scaffold, or firing ledger; attestation generation, privacy, review convergence, package execution, the repository's unrelated PostToolUse hooks, and Codex's private trust storage remain unchanged.

## UI flows
N/A — this is an engineering correction to hook repository identity and host-trust guidance; it adds no product surface or user-entered command.

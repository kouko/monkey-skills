# Brief: loom advances by default and asks only at genuine authority boundaries

Date: 2026-08-22
Author: kouko (session)

## Design-side on-ramp

not fired — this changes loom's internal workflow contract, not a new
product or interaction surface

## Queue relation

unqueued — user-directed corrective change after observing unnecessary
stops; the backlog has no live `bet` entry

## Problem

Loom currently has three independent ways to stop for a user: its router
defaults to human-pumped stage transitions, its close-out flow requires a
next-bet prompt when the queue is empty, and git-memory asks again before a
commit or PR. The first is an old default; the other two contradict loom's
own rule that a close-out request authorizes push and PR creation once.

The result is that a user who asks an agent to finish a bounded change can be
interrupted for administration or a duplicate confirmation, even though no
new product decision is being made.

## Users

The immediate users are people running loom through Codex or Claude Code.
They need a bounded engineering request to keep moving through checks,
review, commit, push, and PR preparation without repeatedly supervising the
same already-authorized work. They must still retain control over product
scope, privacy failures, destructive actions, deployment, and merge.

## Smallest End State

BI-1 — loom's standard execution posture becomes autonomy-by-default: after
the user has approved a brief/spec, it advances through plan, execution,
review, verification, and close-out unless a defined authority boundary
fires. `一站一站來` remains an explicit per-session override.

BI-2 — one cross-skill ask policy defines four outcomes: auto-resolve,
notify, ask, and halt. A checkable/reversible in-scope action auto-resolves;
an advisory state notifies; user-only preference or unapproved scope asks;
privacy, merge, deploy, delete, or a failed safety gate halts.

BI-3 — a close-out with zero live bets reports that the queue is empty but
does not prompt for a new bet. Agents still never auto-promote a bet.

BI-4 — when loom delegates git-memory during a close-out whose request
already named commit/push/PR, git-memory drafts memory and runs privacy
checks without duplicate confirmation. Privacy BLOCK remains a stop.

BI-5 — distill-sessions ingests Codex session JSONL in addition to Claude
sessions, normalizes the events into its existing model, and reports which
policy caused each user-facing stop.

BI-6 — executable tests and a weak-model dogfood scenario prove both sides:
routine close-out proceeds without an unnecessary prompt, while the retained
authority boundaries still stop.

## Current State Evidence

- **Forward** — `loom-code/skills/using-loom-code/SKILL.md` says continuous
  mode is opt-in and the default is human-pumped; a request without a publish
  endpoint therefore waits at every stage.
- **Reverse** — `loom-code/skills/using-loom-code/references/continuous-mode.md`
  owns the full stop contract. Its table already names the safety boundaries
  that must remain: scope outside the plan, failed bounded loops, review
  failure, and PR-open as the never-auto-merge terminal.
- **Error** — `finishing-a-development-branch/SKILL.md` says zero live
  `bet` entries must surface a betting prompt, while the same file's `ASK =`
  clause says happy-path close-out is autonomous except for worktree removal
  and privacy failure. The prior session exercised this contradiction.
- **Data** — `dev-workflow/skills/git-memory/protocols/compose-commit.md`
  and `compose-pr.md` require confirmation before finalizing, while loom's
  close-out rule says PR authorization arrived with the request.
- **Boundary** — `dev-workflow/skills/distill-sessions/scripts/main.py`
  imports `ingest_claude_jsonl` and its skill describes only
  `~/.claude/projects/**/*.jsonl`; the current session is stored under
  `~/.codex/sessions/`, so current telemetry cannot measure this host.

## Decision

Make autonomy the default only after a human-approved scope artifact exists;
do not silently invent product work. Consolidate the asking rules around the
existing reversibility and authority distinction, then make every delegated
skill honor the initiating loom request. Empty queues become a visible status,
not a request to decide the next direction.

The design deliberately does not auto-promote bets or auto-merge. Those are
directional or irreversible decisions rather than execution of an approved
scope. This follows the existing lane-level standing-bet decision, while
removing the unrelated need to answer a prompt during close-out.

## Alternatives Considered

- **Keep human-pumped as the global default and add a repo opt-in.** This
  preserves the old behavior but leaves every new loom repo with the reported
  friction. Rejected because the user identified it as a loom-wide defect.
- **Auto-promote the next ready bet.** This removes the prompt but changes
  product direction without a recorded authorization. Rejected; status-only
  reporting solves the interruption without weakening the direction boundary.
- **Delete all confirmation rules.** This would hide privacy, deployment,
  deletion, merge, and genuine scope decisions. Rejected; the outcome is
  fewer low-value questions, not fewer safety boundaries.

## Out of Scope

- Auto-merge, deployment, deletion, or automatic selection of a new backlog
  bet.
- Rewriting the existing backlog's standing-bet/lane design.
- Mining old session history beyond adding the Codex-compatible ingestion
  path and stop-reason fields.

## Open Questions

N/A — no unresolved question: the user explicitly selected loom-wide
autonomy-by-default, and the retained authority boundaries are fixed by the
current safety contract.

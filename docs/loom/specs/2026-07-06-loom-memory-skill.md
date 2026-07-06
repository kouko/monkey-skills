# Brief: loom-memory — management skill for the practice-memory store

- **Date**: 2026-07-06
- **Status**: user-approved scope (this session); follows on the store built
  in specs/2026-07-06-loom-memory-store.md (same branch, PR #500)
- **Origin**: post-ship gap analysis + industry sweep (this session):
  every serious industry memory implementation carries an ACTIVE
  management layer; ours shipped passive (charter + hook only).

## Design-side on-ramp

Axis 0 N/A — meta-tooling increment on an existing artifact set; axes
walked in-conversation (gap analysis = Axes 1/3; EN+JA industry research
2026-07-06 = Axis 4, sources cited in session log + below).

## Problem

(Axis 1) The store shipped write-guarded but read-orphaned: no skill or
hook ever PULLS from `docs/loom/memory/`, no verb guides writing INTO it
outside the machine-local-memory hook path, and pruning has a charter
warning but no mechanism. Risk: write-only graveyard — memories exist
but sessions re-commit recorded mistakes.

## Users

(Axis 2) Same as the store: solo maintainer across hosts + headless
agents. New emphasis: the RECALL consumer is any session starting loom
work in a repo with a docs/loom/ tree.

## Alternatives Considered

(Axis 4 — EN+JA sweep 2026-07-06, second round)

1. **Heavy tool layer** (agentmemory: 53 MCP tools + 15 skills;
   Hindsight retain/recall/reflect MCP; Mem0/Cognee servers) — rejected:
   trades away zero-infra; team-scale lane.
2. **Mandatory read-all protocol** (Cline Memory Bank: "read ALL memory
   bank files at start of EVERY task") — rejected: the always-loaded
   anti-pattern our charter already refuses (ETH −3%/+20% evidence).
3. **Pure passive (status quo)** — rejected by industry consensus:
   recall verbs/protocols are universal; prune is a first-class ops
   discipline ("define expiry policies before accumulating").
4. **CHOSEN — minimal verb skill** (industry floor: /recall + /remember
   commands + prune cadence; index-pushed/body-pulled like Claude Code
   native + rac): one SKILL.md, three verbs, no new infra.

## Smallest End State

1. **`loom-pipeline/skills/loom-memory/SKILL.md`** — one skill, three
   verbs, host-portable, N/A-loud when the target repo has no
   `docs/loom/memory/` (same conditional pattern as using-loom-pipeline):
   - **record**: given a fact, execute the store charter — classify
     (practice/gotcha/process vs backlog-shaped→BACKLOG.md vs
     harness-friction→environment-gotchas.md, per the charter's
     jurisdiction table), write `<slug>.md` in the charter format,
     append the byte-identical index line. POINTS at the charter for
     format (SSOT — never copies the table/format spec).
   - **recall**: given a topic/task description, grep the store index +
     file bodies (pull-based), read only hits, surface the operative
     rules with file citations; report "no hits" honestly.
   - **prune**: review store files against expiry signals (origin age,
     superseded-by-repo-artifact, never-fired since N sessions),
     propose per-file keep/merge/retire with reasons; NEVER auto-delete
     — retire = user-approved deletion (git history archives).
2. **Reception hook pointer** — ONE line in
   `loom-pipeline/hooks/family-reception.md`: before starting loom work,
   recall from `docs/loom/memory/` (points at the skill). Pointer only —
   no content preloading (pull-not-push preserved).
3. **Plumbing**: loom-pipeline plugin version bump + CHANGELOG entry +
   codex manifest sync (drift hook enforces); skill description follows
   the repo's SKILL.md description standard (trigger phrases incl.
   中/日).
4. **Acceptance**: cheap-model dogfood, 2 consecutive clean rounds,
   disk/transcript-verified (standing rule from the store build):
   recall scenario (seeded hit must surface), record scenario
   (format-valid file + index), prune scenario (honest per-file verdicts
   on a synthetic aged store).

## Current State Evidence

- Forward: `loom-pipeline/hooks/family-reception.md:37-42` (on-ramp SSOT
  table — the pointer line lands beside it); `loom-pipeline/skills/`
  currently holds only `using-loom-pipeline`.
- Reverse (SSOT): `docs/loom/memory/README.md` owns charter + format —
  skill must point, never copy (anti-copy is test-pinned family
  convention per #488).
- Data: store = 20 files + index; plugin.json 0.4.0 both manifests.
- Boundary: skill folder must be flat (repo hook enforces); plugin.json
  edits trip check-codex-manifest-drift (sync script exists).

## What Becomes Obsolete

Nothing removed; the store's read path stops being undefined. The
BACKLOG "park a management skill" recommendation from earlier this
session is superseded before filing (never filed — no cleanup needed).

## Decision

Build the minimal three-verb skill in loom-pipeline + one reception-hook
pointer line + plumbing. Do NOT build: MCP serving, scheduled/cron
pruning, auto-delete, semantic search, mandatory read-all protocol,
scripts (grep suffices at 20 files — first script re-trigger: store >
~60 files or recall misses observed).

## Out of Scope

- MCP / vector / SQLite anything
- Cron or hook-driven automatic pruning (prune is invoked, not ambient)
- Changes to the store charter, the mirror hook, or git-memory
- Firing-test corpus for the new skill (dogfood covers v0.1; corpus
  re-trigger: first observed mis-fire)

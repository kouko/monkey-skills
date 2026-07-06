# Brief: docs/loom/memory/ — repo-native practice-memory store

- **Date**: 2026-07-06
- **Status**: DRAFT — awaiting user sign-off before writing-plans
- **Origin**: 3-turn evaluation (this session) — leaked backlog-shaped facts
  found in machine-local Claude memory; user chose option (b) build the store.

## Design-side on-ramp

Offered implicitly via Axis 0 — work is loom-family meta-tooling; prior family
work (#488, #481) established the docs/loom/specs brief path. User chose direct.

## Problem

(Axis 1) Project-shaped knowledge about loom-* — distilled practices, habits,
workflows, gotchas not bound to a single commit — accumulates in one machine's
Claude-side auto-memory and does not travel with the repo. Any other machine,
host (Codex CLI), headless/workflow agent, or future session without that
local memory silently loses it. Job story: *when I (or any agent) work on
loom-* from any host or machine, I want the family's learned practices to be
readable from the repo itself, so nothing load-bearing lives only on one
machine.*

Two concrete leak instances (2026-07-05 session): corpus-`expected`-narrower-
than-design (trap #6 residual) and sibling SKILL.md frontmatter 0.3.0 vs
plugin.json 0.4.0 — both lived only in
`~/.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/project_loom_family_connective_tissue.md`,
absent from `docs/loom/BACKLOG.md` despite its durable-truth charter (those
two are backlog-shaped → migrate to BACKLOG.md, not to the new store; they
are the *evidence*, not the residents).

## Users

(Axis 2) Solo maintainer (kouko) across Claude Code + Codex CLI + possible
second machine; SDD subagents and Workflow agents dispatched headlessly (no
access to user-level Claude memory); future-session Claude instances after
memory compaction/loss. Constraints: zero-infra preference (documented in
git-memory SKILL.md), pull-not-push retrieval (documented anti-preload
decision), repo conventions (BACKLOG.md charter, plugin README parks).

## Smallest End State

(Axis 3) A `docs/loom/memory/` folder that:

1. **Holds one fact per file** — same shape as Claude-side auto-memory so
   mirroring is a mechanical copy:

   ```markdown
   ---
   name: <kebab-slug>
   description: <one-line — used for relevance decisions at pull time>
   type: practice | gotcha | process
   origin: <PR / session / audit reference>
   ---

   <the fact; **Why:** and **How to apply:** lines>
   ```

2. **`docs/loom/memory/README.md`** = charter + index. Charter states the
   jurisdiction split (below) and the pull-not-push rule; index is one line
   per memory (MEMORY.md style — praised by the 2026-07-04 audit as good
   context economy).

3. **Jurisdiction split** (charter content, one table):

   | Knowledge shape | Home |
   |---|---|
   | Open item / debt / re-trigger | `docs/loom/BACKLOG.md` (cross-plugin) or plugin README §parked (local) |
   | Decision bound to a commit | git-memory trailers (`Decision:`) |
   | Distilled practice / habit / process / recurring gotcha | **`docs/loom/memory/`** (this store) |
   | One-off event artifact | `docs/loom/{specs,plans,audits,dogfood,research}/` |
   | Harness/dcg friction (plugin-shipped) | `loom-code/.../environment-gotchas.md` — stays, NOT migrated |

4. **Pull, not push**: nothing auto-loads the folder. Retrieval = read the
   index / grep on demand. This preserves the documented anti-preload
   decision (git-memory SKILL.md:193-197; the ETH Zurich −3%/+20% evidence
   lives one hop away in git-memory standards/memory-conventions.md §Pull
   retrieval).

5. **One-time migration**: sweep machine-local Claude memories for loom
   project-shaped facts; practice-shaped → new store; backlog-shaped → 
   BACKLOG.md (incl. the two known leaks); Claude-side files become pointers.

6. **Mirror reminder hook — dual-host**: ONE host-neutral hook script
   (reads event JSON from stdin; fires on Write/Edit targeting a machine-local
   memory dir with `type: project`; emits the mirror reminder), wired twice:
   `.claude/settings.json` (Claude Code PostToolUse) and `.codex/hooks.json`
   (Codex PostToolUse — hooks engine stable since Codex v0.124.0, 2026-04;
   repo-verified Codex 0.139.0 includes it; same event vocabulary incl.
   PostToolUse per developers.openai.com/codex/hooks). Payload field names
   may differ per host — the script must tolerate both shapes; Codex wiring
   gets a live-verify note per the `codex-verification.md` execution=truth
   precedent. Closes the prose-enforcement gap named by the 2026-07-04
   harness audit.

7. **Fix `docs/loom/README.md` staleness in the same change** (Axis 5): it
   claims the directory is a frozen 2026-05-30 archive and lists only
   specs/ + plans/; rewrite to describe the live directory incl. the new
   memory/ folder, BACKLOG.md, audits/, dogfood/, firing-corpus/.

## Current State Evidence

- **Forward** — `docs/loom/BACKLOG.md:8-11`: "Claude-side session memory
  keeps only a pointer here — this file is the durable truth"; charter exists,
  enforcement doesn't.
- **Reverse (SSOT direction)** — `dev-workflow/skills/git-memory/SKILL.md:180-197`:
  deliberate division (native memory = user prefs, git-memory = project
  decisions) + always-loaded MEMORY.md deliberately rejected;
  `:250-256`: "graduate to a Markdown + MCP store" documented as the explicit
  signal for when the repo outgrows trailers — this brief exercises the
  Markdown half of that graduation, defers MCP.
- **Error** — the two leaked facts (see §Problem) demonstrate the failure
  mode end-to-end.
- **Data** — trailer stock: `Learning:` ×146, `Gotcha:` ×139 (git log --grep
  counts, 2026-07-06); sole existing distilled-practice file is
  `loom-code/skills/using-loom-code/references/environment-gotchas.md`
  (harness friction only, pointed at by 8 skills).
- **Boundary** — `docs/loom/README.md:1-5` stale ("Frozen as historical
  archive (2026-05-30)"); `docs/loom/INDEX.md` name is taken by the
  living-spec index (do not reuse INDEX.md as the memory index name).

## Alternatives Considered

(Axis 4 — researched EN+JA 2026-07-06, see session log)

1. **Harden status quo only** (mirror discipline + hook, no new folder) —
   rejected by user after the gap analysis: practice-shaped knowledge has no
   non-commit-bound repo home at all; hardening alone leaves that class
   homeless.
2. **Typed Markdown + MCP serving + CI status** (Lore `rac` full form) —
   deferred: MCP trades away zero-infra; documented as team/org-scale lane.
   Re-trigger: multi-agent/team need becomes real.
3. **Always-loaded repo MEMORY.md** — rejected by documented prior decision
   (ETH Zurich study: −3% success, +20% cost).

Industry support: Letta Context Repositories (git-backed markdown memory),
Cline/Kilo Memory Bank (as cautionary always-loaded shape), JA consensus
(note.com 2026, Tolaria git-first vault): solo scale = markdown-in-repo,
compress before it noises up.

## What Becomes Obsolete

- Claude-side loom project memories → become pointer stubs (repo = SSOT).
- `docs/loom/README.md` current content → rewritten (stale archive framing).
- NOT obsolete: environment-gotchas.md (plugin-shipped, 8 inbound refs),
  BACKLOG.md, git-memory trailers — jurisdictions unchanged.

## Decision

Build `docs/loom/memory/` as a pull-based, one-fact-per-file practice-memory
store with a charter+index README; migrate existing machine-local loom
memories (practice→store, backlog→BACKLOG.md); add a mirror-reminder hook;
fix docs/loom/README.md in the same change. Do NOT build MCP serving, CI
status enforcement, auto-distillation from trailers, or any search infra.

## Out of Scope

- MCP read-only serving of the store (re-trigger: real multi-agent/team need)
- CI-enforced memory status / liveness checks
- Moving or restructuring environment-gotchas.md
- Any change to git-memory (dev-workflow plugin) jurisdiction or schema
- Auto-distilling the 285 Learning/Gotcha trailers into the store (manual,
  on-demand curation only — bulk import would recreate the noise problem)
- Vector/semantic search, SQLite index

## Open Questions

- ~~Hook parity on Codex hosts — accept Claude-Code-only enforcement for
  v0.1?~~ **RESOLVED 2026-07-06 (user request + web verification)**: Codex
  CLI has a stable hooks engine (v0.124.0+, PostToolUse supported,
  `.codex/hooks.json` / config.toml inline — developers.openai.com/codex/hooks).
  v0.1 ships dual-host wiring; Codex side carries a live-verify-pending note.

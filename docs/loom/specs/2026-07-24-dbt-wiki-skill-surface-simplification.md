# Brief: dbt-wiki skill-surface simplification — router + one maintenance verb

> Status: brainstorming output (Axis 0-5 walked; Axis 4 research-grounded,
> 1 bilingual sweep + 1 current-state recon, 2026-07-24). Awaiting user
> sign-off on the maintenance-verb fork before `writing-plans`.

## Design-side on-ramp

dbt-wiki is developer tooling (a skill/command surface), not a GUI
product; no `docs/loom/PRINCIPLES.md`. The "interface" here is the
command surface — loom-code brainstorm's own jurisdiction. Proceeding
direct.

## Problem

(Axis 1, JTBD) "When I come back to my dbt-wiki after a while, I want
one obvious place to start and one obvious 'bring it up to date' action
— without holding 8 skills and their ordering in my head." The job is
**discoverability + a clear default path**, NOT fewer capabilities. The
user's framing ("too many skills") is a symptom; the diagnosis (recon)
is: no entry router + two skills that are already internal steps but
presented as top-level.

## Users

(Axis 2) kouko as an occasional dbt-wiki maintainer (init'd once, returns
periodically), and any dbt-wiki plugin user meeting 8 parallel skills
with no entry point. Condition: faces `init/ingest/rescan/redistill/
review/sync/query/pack` and must self-route from scattered `→` hints.

## Smallest End State

(Axis 3) A `using-dbt-wiki` router (lightweight, obsidian-style routing
table + Quick Start sequence + primary-vs-advanced grouping) that gives
one starting point and names the default maintenance path. This ALONE
resolves most of the discoverability pain at near-zero cost/risk. The
maintenance-verb question (below) is an enhancement layered on top, not
required for the smallest end state.

## Current State Evidence

- Forward: 8 parallel skills, no `using-dbt-wiki` entry (unlike
  obsidian's `using-obsidian`, obsidian/skills/using-obsidian/SKILL.md,
  and every `using-loom-*`). First-time users self-route from each
  description's trailing `→` hints (rescan/SKILL.md:4).
- Reverse (SSOT / orchestration): `sync` IS already the maintenance
  orchestrator — it delegates to rescan (Step 1, always) → redistill
  (gated) (sync/SKILL.md:15-21, 41, 51-165). rescan/redistill are
  therefore already sync's internal steps, yet still top-level
  user-facing skills. Only real runtime orchestration in the plugin is
  sync→rescan→redistill.
- Error: no router means the discoverability failure has no single fix
  surface today.
- Data: token sizes (soft cap ~4,500 w) — init 6,476 (ALREADY OVER),
  rescan 3,680 (near), pack 3,027, query 2,770, review 1,895, sync
  1,315, redistill 1,223, ingest 862. → merging SKILL.md files is
  mostly infeasible (init over cap; rescan+redistill ≈4,903 over).
- Boundary: dbt-wiki has NO CI — `.github/workflows/` has zero dbt-wiki
  entries; the 3 lint scripts have tests that never run. Any added
  surface (router, enriched verb) rots unguarded.
- Version: dbt-wiki 3.2.1 (dbt-wiki/.claude-plugin/plugin.json:3).

## Alternatives Considered (Axis 4 — research-grounded)

Industry pattern for "too many commands" (bilingual sweep):
- **dbt build** (the golden precedent) — added a "run everything in DAG
  order" verb while KEEPING run/test/seed/snapshot individually. build =
  production/CI default; run = dev-iteration/debug. Deleted nothing. EN:
  docs.getdbt.com/reference/commands/build, dagster.io/learn/dbt-build-vs-run;
  JA: future-architect.github.io/articles/20260706a/
- **git porcelain vs plumbing** — same tool, two layers (everyday
  commands surfaced first, plumbing scriptable underneath); solved by
  LAYERED PRESENTATION, not deletion. EN: clig.dev
- **make / npm scripts** — aggregate named entry over primitives that
  stay individually callable.
Convergent priority order: **progressive disclosure (router/layered
help) FIRST → integration verb SECOND → actually merging/deleting
commands LAST**, with red lines (clig.dev, Click #2590, CLI11): flag
explosion, single-responsibility collapse, muscle-memory breakage, and
— named explicitly — **avoid confusable `update`/`upgrade`-style
synonyms**. EN/JA agree; JA frames progressive disclosure additionally
as an agent-token-cost optimization (zenn/assign, zenn/chot).

Rejected: merging the 8 skills into fewer files (token caps make it
infeasible; research red-lines confirm — each skill has a distinct
responsibility).

## Decision

Two committed pieces + one fork for the user:

**Committed 1 — add `using-dbt-wiki` router** (obsidian-style, ~60-70
lines): a routing table grouping skills as Setup (init) / Input (ingest)
/ Maintain (the maintenance verb + rescan/redistill demoted as
"advanced / internal steps") / Read (query) / Certify (review) / Export
(pack), plus a Quick Start sequence. Additive, near-zero risk, matches
repo precedent. This is the smallest-end-state core and does the bulk of
the "I don't know what to use" fix.

**Committed 2 — do NOT merge/delete any of the 8 skills.** Token caps
forbid it and each has a distinct responsibility; simplification is
by ROUTING + PROGRESSIVE DISCLOSURE (demote rescan/redistill in the
router's presentation to "advanced — sync calls these for you"), not by
deletion.

**Maintenance verb — RESOLVED (user, 2026-07-24): rename `sync` → `update`
and enrich it.** This is Fork A (enrich the existing orchestrator — no
new competing command) PLUS a rename that makes the name advertise the
scope. The rename ELIMINATES sync rather than adding a competitor, so the
clig.dev `update`/`sync`-synonym red-line does not apply (no synonym pair
exists). It also corrects a mild misnomer: `sync` implies bidirectional,
but the operation is one-way dbt→wiki (sync/SKILL.md forbids touching
dbt) — `update` ("make current", one-way) is semantically more accurate.

Final shape:
- `dbt-wiki:update` = the renamed+enriched orchestrator: ingest-front
  (optional) → rescan → redistill → phantom-column lint gate →
  review-handoff → scorecard. Grows the ex-sync SKILL.md (1,315 w —
  ample headroom). Router presents it as THE maintenance verb.
- rescan/redistill stay callable but demoted to "advanced — update runs
  these for you" in the router.

Rename cost (must be paid in the same change): (a) `git mv
dbt-wiki/skills/sync → …/update` (preserve history); (b) plugin-wide
grep-sweep for the old `sync` name — cross-skill `→sync` hints
(rescan/SKILL.md:4 et al.), CHANGELOG, README(s), codex-mirror manifest,
marketplace entry — zero operative survivors of the old name (repo
convention: mine OLD names after a rename); (c) manifest/description
updates. Sub-decision below: hard rename vs one-version `sync`
deprecation alias.

**Prerequisite (both forks) — wire dbt-wiki into CI.** It has none; the
3 lint scripts have tests that never run. This can be a small first
step, valuable regardless of the rest.

## Out of Scope

- The convergence-fix-loop (assessed and rejected for dbt-wiki earlier
  this session — derived-artifact / two-repo mismatch; BACKLOG note).
- Fixing the actual .dbt-wiki artifact debt (11 phantom-columns / evidence
  gaps) — that's a run, not a plugin change.
- Reviving/deleting the dead `lint_schema_divergence` asset (separate
  call).
- Any evidence-gap → upstream-dbt writeback (dbt-wiki is dbt→wiki only).

## What Becomes Obsolete

- The scattered `→` self-routing hints across 8 descriptions (the router
  supersedes them as the discoverability surface — hints can stay as
  belt-and-braces).
- rescan/redistill as PRIMARY user-facing entries (demoted to advanced in
  the router; still callable — nothing deleted).
- Under Fork A: no skill deleted; under Fork B: nothing deleted either
  (dbt-build pattern keeps底層).

## Open Questions

(both RESOLVED by user 2026-07-24)
1. **Hard rename** `sync`→`update` — no deprecation alias (CHANGELOG
   marks the breaking rename; solo/early plugin). Plugin-wide grep-sweep
   must leave zero operative survivors of the old `sync` name.
2. **CI wire-up folded into this arc** (not a separate PR).

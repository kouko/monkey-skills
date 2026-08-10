# Brief: loom-init — scaffold the queue layer into any repo

Date: 2026-08-10
Origin: arc B of the user-directed two-arc goal「把 A 跟 B 都做完」. Grounded in (a) the live population: 7 local repos consume loom, only 2 have the queue layer, and the one external repo that wanted it (kumiko) hand-copied the whole structure — the init verb's job done manually, drift seeds included; (b) two-language industry research: `specify init` and `task-master init` both treat planning-layer scaffolding as table stakes, and both instantiate templates as STARTING POINTS owned by the target repo (no sync-back duty); (c) the placement adjudication this session: verb + templates live in loom-code (version lockstep with backlog_index.py/plan_card.py, the templates' contract partners), the family reception gains only a recommendation row.

## Problem

loom's queue layer (backlog store + charter README + DIRECTION.md) can
only be adopted by hand-copying monkey-skills' structure: no verb
creates it, so 5 of 7 consuming repos run the task layer alone, and
the one repo that wanted the queue layer hand-rolled it — the exact
hand-copy path that produced four progress-table drifts there. The
skills already fire conditionally on the store's presence
(brainstorming's ready check, finishing's backlog-close and betting
rows: "no store → skip silently"), so the machinery is opt-in-ready;
what is missing is the opt-in's front door.

## Users

kouko's 6 external loom repos (immediate); any future repo adopting
loom's queue layer.

## Smallest End State

1. **`loom-code/scripts/loom_init.py`** (plugin-shipped, cascade-
   resolvable like its siblings): creates `docs/loom/backlog/`
   (charter README instance), `docs/loom/DIRECTION.md` (skeleton with
   the generated-Now charter bullets), and `docs/loom/plans/` +
   `docs/loom/specs/` directories. Refuses (exit 1, loud) if
   `docs/loom/backlog/` already exists — never overwrites. Each
   instantiated file carries a one-line vintage stamp (template
   version = the shipping loom-code version) so future audits can date
   the instance. After writing, it runs `backlog_index.py --validate`
   + `--direction-check` on the fresh store and reports their exit
   codes — the scaffold proves itself against the real validators
   before declaring success.
2. **Templates are starting points, not synced copies** (industry
   pattern: specify init's constitution): once instantiated they are
   the target repo's own documents; no drift checker, no sync duty.
   The charter template is a generalized edition of this repo's
   `docs/loom/backlog/README.md` (two-tier tooling paths per #680/#681
   wording; monkey-skills-specific references removed).
3. **No new skill.** The verb is offered at two existing touchpoints:
   brainstorming Axis 0's ready check gains an offer branch — when the
   target repo has NO `docs/loom/backlog/`, offer loom-init ONCE
   (recommend-once rule, recorded like the design-side on-ramp),
   proceed either way; and `loom-pipeline/hooks/family-reception.md`'s
   on-ramp criteria table gains one row (no queue layer → suggest
   loom-init once). Deletion-first: two prose touchpoints + one
   script, zero new SKILL.md (no README-table/i18n/description-budget
   surface).
4. Versions: loom-code 0.72.0 → 0.73.0 (assumes #682 merged — hard
   dependency recorded in the plan), loom-pipeline 0.16.0 → 0.17.0,
   codex manifests synced, version pin migrated.

## Current State Evidence

- Forward: brainstorming SKILL.md:72-77 — ready check with cascade,
  N/A = "no store … skip silently"; family-reception on-ramp table
  rows 1-4 + negative guard (loom-pipeline/hooks/family-reception.md).
- Reverse: `backlog_index.py --validate/--direction-check` are the
  correctness oracles the scaffold must satisfy; both plugin-shipped
  since #680. The charter README is the store's format SSOT
  (docs/loom/backlog/README.md:1-30 field contract).
- Error: creating a store without its charter would produce entries no
  agent can validate against intent; creating over an existing store
  would destroy live state — hence instantiate-charter-always +
  refuse-if-exists.
- Data: population count verified live this session (7 repos with
  docs/loom/, 2 with backlog stores, kumiko's hand-rolled).
- Boundary: memory store (`docs/loom/memory/`) is OUT of v1 — its
  integrity gate (`check_loom_memory_integrity.py`) ships in no
  plugin, so scaffolding external memory stores would mint stores
  without their gate (the documented-fallback-legitimizes-a-gap class).

## Alternatives Considered

1. **Script + two offer rows, no new skill** (chosen) — deletion-first;
   the reception and Axis 0 already own the "recommend once" UX shape.
2. A new `loom-init` SKILL.md — rejected for v1: costs a README-table
   row ×3 languages, description budget, and routing surface for a verb
   that fires roughly once per repo lifetime; the offer rows route to
   the script fine. Revisit if usage shows discovery failure.
3. Synced charter copies with a drift checker — rejected: industry
   precedent (spec-kit constitution, task-master store) treats
   instances as repo-owned starting points; a cross-repo sync duty has
   no enforcement surface anyway.
4. Scaffolding the memory store too — rejected for v1 (Boundary above).

## Decision

Ship the script + templates in loom-code, the offer branch in
brainstorming, the recommendation row in loom-pipeline's reception;
templates instantiate as vintage-stamped repo-owned documents; the
scaffold self-verifies against the live validators.

We will NOT: create a new skill, scaffold the memory store, add any
sync/drift machinery, or auto-run init anywhere (offer once, user
decides — same posture as betting promotion).

## Out of Scope

- Memory-store scaffolding (needs its integrity gate shipped first).
- The milestone layer (separate OPEN backlog entry; its design may
  later extend what init casts).
- Backfilling the 5 external repos (each repo's user runs init when
  they want the layer; this arc ships the verb, not the migration).

## Design-side on-ramp

Negative guard: tooling increment on existing machinery — upstream-
artifact walk skipped silently. Backlog ready check: run this session
(`## Now` empty; the two-arc /goal is the direction call).

## Open Questions

None blocking.

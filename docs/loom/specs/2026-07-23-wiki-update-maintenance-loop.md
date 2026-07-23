# Brief: wiki-update — one-verb wiki maintenance with a mechanical fix loop

> Status: brainstorming output, user-ratified 2026-07-23 ("OK 開工").
> Research substrate: `2026-07-23-goal-loop-harness.md` (superseded
> sibling) — its 6 bilingual Axis-4 sweeps, §Design constraints 1-5,
> and §loom-* integration map apply here BY REFERENCE; this brief does
> not restate them.

## Design-side on-ramp

Offered across prior loom arcs; user pattern is direct-to-code for
internal tooling. Proceeding direct.

## Problem

(Axis 1) The user's actual job is one verb — "bring my wiki up to date
and clean" — but the wiki subsystem exposes seven implementation-sliced
skills (setup/ingest/cross-linker/lint/merge/query/auto-research) with
ordering knowledge the user must carry. Result: activation friction;
ingest stalled 3 weeks; mechanical debt accumulated to ~1,900 violations
(991 pages missing required fields, ≈873 broken wikilinks upper-bound,
measured 2026-07-23) with checks that exist but never enforce.

## Users

(Axis 2) kouko, running "update my wiki" after note-taking sessions or
on a maintenance whim, on any machine with the obsidian plugin + vault.
Weak-model executors must be safe inside the loop (verdict paths
mechanical; judgment-shaped prose dies on weak tiers).

## Smallest End State

(Axis 3) One new thin-orchestrator skill `obsidian:wiki-update` +
mechanical machinery, such that `/wiki-update` runs:
ingest (delegated) → cross-linker (delegated) → mechanical fix loop
(new engine, safe-tier repairs only, converge-or-honest-stop) →
work-order triage (what the loop must NOT touch, routed to
ingest/merge/lint lanes) → close-out scorecard. Existing 7 skills
untouched. NOT building: general adapter harness (parked, BACKLOG
Rule-of-Three re-trigger), any principles-pair refactor, LLM-judged
oracle lanes.

## Current State Evidence

- Forward: maintenance today = manually invoking wiki-ingest →
  wiki-cross-linker → wiki-lint in the right order; wiki-lint SKILL.md
  is read-only by charter ("does not auto-fix", SKILL.md:5 description).
- Reverse (SSOT): page-format spec owned by wiki-ingest (its
  description: "owns page format spec"); check semantics owned by
  wiki-lint `references/lint-checks.md` (known second-drift-surface —
  repo memory); neither may be duplicated into the new skill.
- Error: no convergence mechanism exists — lint reports, nobody loops.
- Data: vault at `/Users/kouko/kouko-obsidian-vault`, wiki/ 4,977 pages
  (references 2,891 / concepts 1,645 / entities 424 / others 17);
  23,775 wikilinks; violations measured 2026-07-23: L01-missing-fields
  991 pages (mostly `domain`/`status`), L07-broken-links ≈873
  (upper bound; top target concentrated — one missing page cited 59×),
  orphans 0; last wiki activity 2026-07-01.
- Boundary: loop-engine prior art in-repo =
  `.claude/workflows/principles-improve-loop.js` (860 lines) +
  `loom-product-principles/scripts/improve_loop_verdict.py` (367,
  near-target-agnostic per dissection); verdict logic will be an
  adapted copy WITH origin header note (bounded duplication accepted
  pending Rule-of-Three extraction — BACKLOG entry).
- Jurisdiction boundaries (from family map): fix loop repairs ONLY
  safe-tier mechanical violations in place (retarget links, add
  aliases, fill derivable fields); page creation / re-distillation →
  ingest work-orders; near-duplicates → wiki-merge candidates; ANY
  deletion = unsafe tier, proposal-only, never auto.

## Alternatives Considered

By reference: superseded brief §Alternatives (6 sweeps). Scope-cut
history: general harness (option A) → wiki-specific standalone skill
(option B) → wiki-fix + sorter → thin orchestrator wiki-update (final;
user-driven, matches loom family's router pattern). Mega-merge of
ingest/lint/fix into one skill REJECTED (token cap, single-responsibility,
drift). Name `wiki-update` chosen over fix/heal/maintain — the
orchestrator covers intake + maintenance, so the broader verb is honest.

## Decision

Build:
1. **Mechanical validator** `wiki_lint_check.py` in wiki-lint/scripts/
   — deterministic error-severity subset (L01/L02/L03/L04/L07/L14) per
   lint-checks.md (SSOT, lockstep header note), violations as JSONL +
   conservation counters (word/link/heading per file), exit codes.
   Stdlib-only, zero repo-level imports (plugin self-containment).
2. **Loop verdict CLI** `loop_verdict.py` in wiki-update/scripts/ —
   compare/plateau/budget verbs + stuck fingerprints (same-failure 3×,
   no-new-info, regression) + conservation-ratchet check; exit-code
   verdicts only; adapted copy of improve_loop_verdict.py with origin
   note.
3. **Loop engine** `wiki_fix_loop.js` in wiki-update/scripts/ —
   criteria freeze (violations snapshot + check-config hash before
   round 1), one-violation-class-per-round, safe-tier enforcement
   (action allow-list; deletions structurally excluded), per-round
   ledger, structural scorecard (diff lines/files/violation delta),
   size circuit-breaker, proposal-branch exit (vault git branch,
   never merge), escape hatch (STUCK → blockers report).
4. **Orchestrator SKILL.md** `obsidian:wiki-update` — the 5-step verb
   (delegate ingest → delegate cross-linker → run loop → work-order
   triage → scorecard report); freeze protocol; `/goal` routing line;
   report language = conversation language; obsidian version bump.

## Out of Scope

- General adapter harness + principles-pair refactor (BACKLOG, parked).
- LLM-judged checks (L05/L06/L08-L13/L15 stay wiki-lint's LLM lane).
- Any edit to the existing 7 skills' behavior (wiki-lint gains a
  script + one pointer line only).
- Auto-merge of proposal branches; vault-side scheduling.

## What Becomes Obsolete

- The manual "remember to run ingest → cross-linker → lint" ordering
  knowledge (absorbed into wiki-update's step list).
- Nothing else deleted; existing skills keep their direct-invocation
  paths for surgical use.

## Open Questions

(none — both forks resolved: adapter #2 → superseded by this re-cut;
judge-family diversity deferred with the general harness.)

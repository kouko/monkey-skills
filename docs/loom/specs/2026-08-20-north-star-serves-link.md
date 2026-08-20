# Brief: purpose layer + serves link

## Design-side on-ramp

not fired — negative guard: a test-covered tooling increment to existing
loom-code skill text and scripts, not product-shaped new work. Backlog ready
check ran: 25 OPEN entries surfaced, none overlaps this seed.
`docs/loom/DIRECTION.md` `## Now` is empty; `## Next` names two lane themes,
neither overlapping. Queue layer already exists — loom-init not offered.

## Problem

A project's long-horizon purpose has no home of its own, and nothing forces
it back into view. When it is achieved, nothing requires the next one to be
written, so the project keeps shipping short-horizon tasks against a purpose
that is already satisfied — and circles.

Measured instance: `loom-code/PRODUCT-SPEC.md:74` still states
`### 3.1 Goals (MVP v0.1.0)` with G1-G6, all six demonstrably green today,
while the shipped version is `0.90.0`. Roughly 89 minor versions have run
with no stated long-horizon purpose — only a schedule and a completed
milestone.

Second measured instance: of seven repos on this machine using loom, five
have plans and specs but nothing anywhere stating why the project exists.
`reading-list-summarize-scraper` has five plans and no such line.

## Users

The solo developer running loom across seven repos of very different
adoption depth. They bet at branch close-out, promoting a backlog entry to
COMMITTED-NEXT by hand — the only actor who may promote, so the betting
moment is already a forced human stop.

The standing design posture, stated by the user on 2026-08-20: loom assumes
the user does NOT understand its internal mechanisms. The agent guides,
reminds, and where warranted forces. A missing artifact is never silently
skipped.

## Smallest End State

Three legs.

**Leg C — the purpose layer** (new; Leg A depends on it).

1. A `PURPOSE.md` artifact: one line of why the product exists (`Why:`) and
   one checkable condition that means it is met (`Done when:`). Format
   contract, loom-init template, and scaffold.
2. `## North Star` moves OUT of loom-design's `PRINCIPLES.md` contract.
   PRINCIPLES.md keeps only product / design / engineering principles.
   Touches `validate_principles_output.py`, `principles-rules.md`, and the
   `product-principles` SKILL.md.

**Leg A — the serves link** (retargeted onto `PURPOSE.md`).

3. Backlog entries gain a `serves:` frontmatter field, REQUIRED when
   `status: COMMITTED-NEXT`. Closed two-form grammar:
   `serves: <how this serves the purpose>` or `serves: unrelated — <reason>`.
4. `loom-code/scripts/check_north_star_link.py` — exit 0 resolved, exit 1
   unreadable path, exit 2 unresolved (prints the question; STOP and ask).
5. The betting prompt prints `PURPOSE.md` before listing candidates, then
   runs the checker. When `PURPOSE.md` is ABSENT it prompts for one — it
   does not silently exempt the repo.

**Leg B — the DIRECTION.md move.**

6. The 18-line charter header moves to `loom-code/hooks/family-reception.md`
   (SHIPPED on this branch); `## Later`'s three entries become backlog
   entries and the section is removed.

## Current State Evidence

- **Forward**: `loom-code/skills/finishing-a-development-branch/SKILL.md:188`
  — the Backlog-close row fires the betting prompt when COMMITTED-NEXT is
  empty; the USER promotes by editing `status:`, agents never auto-promote.
- **Reverse**: `scripts/backlog_index.py:1-9` is an exec shim; the real
  implementation is `loom-code/scripts/backlog_index.py`. Schema changes
  land in the plugin copy, never the repo-root shim.
- **Error**: shipping Leg A against the wrong probe target was reproduced
  live — the committed `1fe7b2c1` run against kumiko's store returns
  `FAIL — COMMITTED-NEXT entry missing required 'serves' field` for both of
  its entries. Leg A cannot ship until its target file exists.
- **Data**: seven repos use loom. Adoption is layered, not all-or-nothing:
  7 have `plans/`; 2 have `backlog/` + `DIRECTION.md` (monkey-skills,
  kumiko); 1 has `PRINCIPLES.md` (kumiko); 0 have `PURPOSE.md`.
- **Boundary**: `loom-design/scripts/principles/validate_principles_output.py:73`
  pins `_NORTH_STAR = "## North Star"`, but its only requirement is >=1
  non-empty body line (`:11-13`). The `**Goal:**` / `**Success:**`
  sub-structure appears ONLY in error-message text at `:168` and `:175` —
  advisory, never enforced. Nothing may parse for those labels.

Evidence paths: `loom-code/skills/finishing-a-development-branch/SKILL.md`,
`loom-code/scripts/backlog_index.py`, `scripts/backlog_index.py`,
`loom-design/scripts/principles/validate_principles_output.py`,
`loom-design/skills/product-principles/`, `docs/loom/DIRECTION.md`,
`loom-code/PRODUCT-SPEC.md`,
`/Users/kouko/GitHub/kumiko-zaiku-app-icons/docs/loom/PRINCIPLES.md`.

## Alternatives Considered

Two research rounds ran, each EN + JA per the Axis-4 protocol.

**Round 1 — the mechanism.** Three arms (traditional SE / shipped coding
agents / Japanese practice).

**My take: Recommend** traceability-at-promotion. **Why**: it is the only
mechanism whose underlying practice has academic grounding rather than blog
consensus, and it reuses a forced human stop that already exists.
**Conditional reversal**: if `serves: unrelated` is the answer on most bets,
the link carries no information and should be withdrawn, not tightened.

1. **Re-inject the purpose into context every turn.** REJECTED on evidence.
   Laban et al. (2025, ICLR 2026 best paper, arXiv:2505.06120) measured a
   39% accuracy drop and 112% higher variance multi-turn vs single-turn,
   with poor recovery after an early wrong turn. Liu et al.
   (arXiv:2307.03172) shows mid-context content is under-retrieved.
   Leviathan et al. (Google, arXiv:2512.14982) DOES show prompt duplication
   helps — but tests same-turn single duplication, a different mechanism.
   No published study tests re-injecting a static goal across a long agentic
   session; that gap is real, not a search failure.
2. **Render it on the progress card.** REJECTED — display, not forced
   consultation, and it would sit mid-context.
3. **A status field checked at betting** ("is it met?"). REJECTED — fires
   once per lifetime, and catches only achievement, not a purpose that was
   wrong from the start.
4. **A monitored metric.** REJECTED — these are developer tools with no
   natural continuous metric.
5. **CHOSEN: traceability at promotion time.** Basili's Goal-Question-Metric
   (Univ. Maryland TAME) was the only practice found with empirical
   grounding; Adzic's Impact Mapping applies the same shape. Japanese
   sources converge independently: the countermeasure to 形骸化 is to make
   the document load-bearing inside an existing workflow — the
   ADR-in-PR-review pattern (zenn.dev/henry; KAKEHASHI Tech Blog).

**Round 2 — the name.** Two arms (EN, JA) on what PMs and product designers
actually call this artifact.

- `NORTH-STAR` REJECTED by both arms: dominant usage is North Star METRIC,
  a single quantified KPI (Amplitude, 2023; 電通デジタル). JA sources are
  categorical — 「たった1つの指標」with countable examples. A file holding a
  sentence would read as a category error.
- `VISION` REJECTED: SVPG defines vision as deliberately aspirational and
  explicitly NOT checkable, which clashes with the `Done when:` requirement.
- `PRODUCT-GOAL` REJECTED: a DEFINED Scrum Guide 2020 term, and it collides
  with Claude Code's own `/goal`.
- `PURPOSE` CHOSEN, over a real EN/JA disagreement recorded here rather than
  resolved silently. The EN arm recommends it as the plainest uncontested
  noun, pairing with SCOPE / PRINCIPLES / DIRECTION. The JA arm objects:
  パーパス is 2020-21 corporate-governance vocabulary (パーパス経営,
  パーパス・ウォッシュ) and appears in no JA engineering blog as a product-doc
  filename. The user chose `PURPOSE` with that objection stated.
- Both arms independently report that NO canonical filename exists for this
  artifact in either language — this position is a genuine gap, so the name
  is coined, not adopted.

## Decision

Ship the purpose layer and the serves link together, because the link has no
target without the layer — proven live: the already-committed `1fe7b2c1`
fails kumiko's store today.

`PURPOSE.md` is a FOUNDATIONAL artifact, not an optional one. A repo without
one is not silently exempt; the betting prompt asks for one.

The forcing is on the ANSWER, not on the CONTENT. A user who cannot yet
articulate a purpose records that, exactly as the on-ramp gate's three-state
grammar records a declined detour. Forcing content at a moment when the
answer is unknowable produces a filled-in template — the first step of the
形骸化 chain the research documents, and worse than an absent file because
it passes every later check.

Timing follows whether the answer is KNOWABLE, not whether the file exists:
prompt at betting (a commitment is being made), offer once during ordinary
work, never block a fresh repo with nothing in it yet.

The drift signal falls out of the `serves:` field rather than needing its own
mechanism: when every candidate can only be written `serves: unrelated`, the
purpose is stale — whether achieved or wrong from the start.

NOT building: a status/achievement field, any progress-card change, any
per-lane purpose layer.

## Out of Scope

- **Renaming the plan schema's `Goal:` field to `End-state:`** — decided
  2026-08-20, deferred to its own arc. 51 plan files across two repos;
  `plan_card.py:334` raises on a missing `Goal:`, so a rename needs a
  migration window where the parser accepts both names, and a cross-repo
  ordering table. Independent of this arc.
- **Migrating kumiko's `PRINCIPLES.md`** — a different repo; must happen
  there, after the plugin ships.
- **`PRODUCT-SPEC.md` §3 pointing at `PURPOSE.md`** — the loom-code fossil
  at `PRODUCT-SPEC.md:74` is evidence for this arc, not its target.
- Commit-time enforcement of `serves:` via `git-guard.py` — resolved OQ-1.
- Retrofitting `serves:` onto historical entries. New promotions only.

## What Becomes Obsolete

- `## North Star` inside `PRINCIPLES.md` — moves to `PURPOSE.md`; the
  loom-design contract, validator, and skill text all drop it.
- `docs/loom/DIRECTION.md`'s 18-line charter header (moved, not deleted).
- `## Later` as a section (its three entries become backlog entries).

## Queue relation

unqueued — `docs/loom/DIRECTION.md` `## Now` is empty (`_(queue empty —
bet at the next close-out)_`); this arc arrives from a live design
discussion, not from a promoted backlog entry.

## Open Questions

- OQ-1 [RESOLVED] Should a malformed `serves:` BLOCK at commit time via
  `git-guard.py`, or surface at betting? RESOLVED 2026-08-20, user chose
  ask-at-betting-only. The gate belongs where the decision is made, and
  backlog entry `2026-07-04-mechanical-gates-v2-candidates-loom-code-0-23-0-follow-ups`
  is already OPEN awaiting gate-fatigue evidence.
- OQ-2 [RESOLVED] Where do `## Later`'s three entries go? RESOLVED
  2026-08-20, user chose converting each into an OPEN backlog entry.
- OQ-3 [RESOLVED] Is `PURPOSE.md` optional or foundational? RESOLVED
  2026-08-20, user chose foundational, citing the standing posture that loom
  guides rather than waits.

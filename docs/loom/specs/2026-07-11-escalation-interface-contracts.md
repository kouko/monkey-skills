# Brief: escalation interface / decision log / acceptance-surface / appetite — four behavioral contracts

- Date: 2026-07-11
- Source: BACKLOG `## Designer/PM loop — escalation interface, decision log,
  acceptance-surface contracts (OPEN)` (docs/loom/BACKLOG.md:111-149); design
  SSOT = `docs/loom/design/2026-07-10-designer-pm-loop-architecture.md`
  §1-§2 (inversions #2-#4, two-axis rubric), §5 (KEEP list + merge decisions),
  §6 (user decisions). Design decisions are RECORDED there and not relitigated
  here; this brief cuts scope + fixes landing spots + defines acceptance.
- Design-side on-ramp: N/A — loom-internal skill-behavior work, no product
  on-ramp row fires (repo has no PRINCIPLES.md; not product-shaped).

## Problem

When loom-code implements, engineering decisions carry hidden product
consequences (local vs cloud inference is also a privacy promise). Today the
agent silently guesses (architecture doc §1 #3: "no protocol for translating
an implementation-discovered product question back into product language"),
the guesses are unauditable, and the user's only "done" surface is test
counts — which a non-engineer cannot adjudicate (§1 #4). Job-to-be-done: when
an engineering choice has product stakes, let the product-role user decide at
the right moment in product language; for everything the agent decides alone,
leave a product-language record that is auditable and late-vetoable.

## Users

The product/PM-role operator of the loom pipeline (kouko today; designed for
non-engineer users) — reads plans and briefs, cannot read diffs/test output.
Secondary: the (often weak-model) agents executing the skills, who need
mechanical decision points, not judgment prose.

## Smallest End State

All four contracts land as BEHAVIORAL TEXT in existing skills plus one
lightweight record format — no new tooling, no new scripts:

1. **Escalation interface** (loom-code): `writing-plans` gains a §Kickoff
   briefing step — after the plan draft, collect the round's one-way-door
   engineering decisions (two-axis test: product consequence × reversal
   cost; the invisible×one-way-door bottom-right cell IS included, user
   decision 2026-07-10) and batch the 1-3 of them into ONE product-stakes
   briefing (per decision: plain-language stakes → 2-3 options with product
   consequences → recommendation; derivation-for-confirmation framing when
   PRINCIPLES.md already locks the choice). `subagent-driven-development`'s
   mid-implementation ask paths (NEEDS_CONTEXT / §Asking the user) point at
   the SAME two-axis test as the exception firing point — one interface,
   two firing points (architecture doc merge decision :227). Composition,
   not duplication: the kickoff briefing is a batched
   `dev-workflow:brief-before-asking`; the two-axis test refines SDD
   §Asking-the-user gate ① for product-consequence decisions — both wired
   as pointers to the existing SSOTs.
2. **Decision log** (loom-code): a `## Decision Log` section in the PLAN
   document, maintained by the SDD orchestrator during execution (same
   pattern as the Status ledger); one entry per agent-decided engineering
   choice, record shape shared with the deviation ledger ("chose X because
   Y; the day you want Z, this choice costs W" — one format, two views,
   architecture doc :228). Commit trailers stay the engineer-facing
   greppable index; the plan section is the product-language narrative
   (two-tier, research-grounded). Reviewed at close-out with the plan.
3. **Acceptance-surface promotion** (loom-code): `ui-verification` promoted
   from side gate to the user's main acceptance stage in
   `finishing-a-development-branch` (running product + ui-verification
   results + product-language completion report = what the user judges
   "done" by); NEEDS_REVISION review loops digest silently inside SDD /
   finishing rather than surfacing to the user.
4. **Per-project escalation appetite** (loom-product-principles): an
   optional appetite declaration slot in the Engineering Principles section
   (rules + question-set + validator tolerance as needed), read once by the
   escalation interface, never re-asked (judgment-rubrics §3(c)). Appetite
   PRESETS stay DEFERRED (architecture doc :208-210 — extract from ≥2 real
   projects, don't invent upfront).

Ship gate: cold-reader behavioral dogfood on the contracts (fresh-context
agent + realistic case per contract — the repo's proven
process-mechanism-dogfood pattern), plus each touched SKILL.md under its
word cap.

## Current State Evidence

- **Forward** (where the contracts fire): plan kickoff = `writing-plans`
  SKILL.md pipeline (brief → plan → reviewer → SDD); mid-implementation ask
  = `subagent-driven-development` SKILL.md §Asking the user (three gates,
  Horvitz) + NEEDS_CONTEXT status handling; acceptance = `finishing-a-development-branch`
  Phase 2b ui-verification (side gate today) + Step 13 report.
- **Reverse** (SSOT directions): brief-before-asking owns the 6-block
  briefing format (dev-workflow); SDD §Asking the user owns gates ①②③;
  deviation-ledger record shape owned by
  loom-product-principles/references/principles-rules.md:224-227 (its prose
  explicitly names the engineering decision log as the same-shape sibling).
  loom-code knowledge layer is a distribute.py functional copy of
  domain-teams:code-team — check whether touched loom-code files are in the
  sync set before editing (edit canonical side if so).
- **Error** (failure modes designed against): silent agent guessing (no
  record, no ask); over-asking (confirmation fatigue — the two-axis test +
  appetite declaration bound it); briefing buried mid-turn (existing
  machine-local lesson: end turn with briefing as final text).
- **Data**: zero implementation today — greps for escalation / decision log
  / acceptance-surface / appetite return no hits in any station skill
  (recon 2026-07-11); the only sibling is the deviation ledger.
- **Boundary**: product-principles SKILL.md word budget 2,351/4,500 (~2,149
  headroom); loom-code skill files each carry their own budget — check
  `scripts/check-skill-structure.py` per touched plugin at implementation.

Evidence paths: docs/loom/BACKLOG.md:111-149; docs/loom/design/2026-07-10-designer-pm-loop-architecture.md:33-97,194-237;
docs/loom/specs/2026-07-10-designer-pm-loop-implementation.md:199-202;
loom-product-principles/skills/product-principles/references/principles-rules.md:224-227.

## Alternatives Considered

- Design-level alternatives: recorded in the architecture doc §5 (KEEP /
  DROP / DEFER — e.g. standalone gradient-enforcement table DROPPED as a
  second source of truth) and §6 (user decisions) — not relitigated.
- Decision-log placement (researched 2026-07-11, EN+JA, 5 shipped
  approaches: Nygard/MADR standalone ADR dirs, embedded design-doc decision
  sections, wiki logs, agent audit trails — no clean precedent for
  agent-authored/PM-read logs, honestly noted): **plan-embedded section
  chosen** (decision lives next to its reasoning; plan doc is already the
  per-arc artifact the user reads; composes with trailers as the
  engineer-facing index). **Reversal conditions (recorded, user-approved)**:
  switch to standalone `docs/loom/decisions/` if (a) >15-20 decisions in
  one arc, or (b) cross-arc lookup need emerges ("did we already decide
  this?").

## Decision

Build all four contracts in ONE arc as behavioral text + one record format,
landing in: writing-plans (kickoff briefing + two-axis test), SDD (exception
firing point + decision-log maintenance), finishing-a-development-branch +
ui-verification (acceptance-surface promotion), loom-product-principles
(appetite slot). Wire by POINTERS to existing SSOTs (brief-before-asking,
§Asking the user, deviation-ledger shape) — no duplicated doctrine. Do NOT
build: appetite presets (DEFERRED), any new script/tool, a standalone
decisions directory (reversal conditions recorded above).

## Out of Scope

- Appetite presets (architecture doc DEFER — needs ≥2 real projects).
- Cross-station generalization of the escalation interface beyond loom-code
  (the interface fires in loom-code stages; other stations unaffected).
- L3 autonomous improvement loop (separate BACKLOG item).
- Any change to the two-axis test or the recorded user decisions (design
  SSOT is the architecture doc).
- Conductor (loom-pipeline) wiring — follows after the station contracts
  exist.

## Open Questions

1. Whether the loom-code files to be touched are inside the
   distribute.py/code-team sync set (affects WHERE edits land) — resolve at
   plan recon, before task split. — re-trigger: writing-plans recon.

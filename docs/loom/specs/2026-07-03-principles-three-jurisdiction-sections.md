# PRINCIPLES.md three-jurisdiction sections (Product / Design / Engineering) — brief

> **Phase**: brainstorming output (`brainstorming` → `writing-plans` handoff)
> **Date**: 2026-07-03
> **Author**: agent (kouko-approved fork decisions, this session)
> **Supersedes**: the earlier single-section draft
> `2026-07-03-engineering-principles-section.md` (removed same day —
> scope grew from one Engineering section to the three-jurisdiction
> heading scheme after a rename-cost re-estimate; see Alternatives #2)

## Problem

When an implementer or pipeline station hits a per-project ENGINEERING
fork (tech stack, dependency posture, conservative↔aggressive style
dial, test-rigor level above the TDD iron-law floor), there is no
constitution-level home that auto-answers it — those decisions live
scattered in per-change briefs, LOOM-SIMPLIFY markers, and AGENTS.md, so
the same engineering questions resurface as bucket-B interruptions on
every change. A second, quieter symptom: the constitution's single
`## Principles` section is jurisdiction-blind — its own ✅ examples
("no blocking modal", "≤3 steps") are design-natured by industry
taxonomy (NN/g: design principles are value statements resolving
interface trade-offs), so design and product clauses land unsorted in
one list and future consumers cannot tell which lens should enforce
which clause.

## Users

- **kouko (solo operator)** — wants day-time discussion / hands-off
  implementation; every recurring engineering question a station must
  ask back is an interruption the constitution should have absorbed.
- **loom-pipeline station agents & loom-code implementers** — need a
  supreme, checkable file to consult instead of guessing engineering
  posture mid-task.
- **loom-code code-reviewer (D8)** — needs an unambiguous statement
  that engineering clauses fall under its existing
  principles-conformance jurisdiction.
- **loom-interface-design design-critic** — its conditional PRINCIPLES
  lens already enforces the constitution against design artifacts; a
  labeled Design jurisdiction tells it exactly which clauses are its to
  judge.
- **loom-product-principles generator skill** — the authoring path that
  must emit the new sections without breaking its validator.

## Smallest End State

`PRINCIPLES.md` (filename unchanged — every cross-plugin consumer
hardcodes it) becomes a three-jurisdiction constitution:

1. **`## Principles` → `## Product Principles`** — hard rename, same
   rules (3–7 top-level ordered entries, each with the literal
   `— check:` marker). The validator detects the legacy `## Principles`
   heading and emits a targeted migration message ("rename to
   `## Product Principles`") so old files self-explain their fix.
2. **`## Design Principles`** and **`## Engineering Principles`** —
   OPTIONAL sections, 1–7 entries each (1 as the floor: clauses are
   minted from real committed decisions, so a young project
   legitimately has one or two), same ordered-list + `— check:` lexeme.
   A present-but-empty section is invalid; a section with no clauses is
   simply omitted (an empty heading invites platitude-filling).
3. The authoring contract (`principles-rules.md`) gains a jurisdiction
   table — Product = what/for whom/success trade-offs; Design = how the
   interface behaves and feels (interaction posture, feedback/error
   stance, density, accessibility floor, tone where checkable);
   Engineering = how it is built (stack, dependency posture, style
   dial, test-rigor CEILING above the iron-law floor, explicit negative
   decisions) — with the existing ✅/❌ examples re-sorted per
   jurisdiction, new synthetic examples for the two new sections, and
   its "Validator contract (summary)" section updated to mirror the new
   validator checks (rename, migration message, optional-section
   rules) one-for-one.
4. Generator SKILL.md: elicitation extends to BOTH engineering posture
   and design posture (kouko decision 2026-07-03, after the industry
   research round: the enforcement lens already exists and
   elicitation-only preserves the guardrail); only clauses the user
   actually commits to are emitted — nothing imagined upfront; a
   jurisdiction with no committed clauses emits no section.
5. loom-code D8: one-line jurisdiction note — clauses in ALL three
   sections are judged under the existing subject-matter severity rule
   (a supply-chain clause violation is 🔴, a dependency-count clause
   violation is 🟡); no new severity tier.
6. docs/loom/BACKLOG.md: the shipped ENGINEERING entry is deleted (per
   convention) and the v1.1 batch-mode start condition updated.
7. docs/loom/INDEX.md regenerated: this brief and its plan are new
   docs under docs/loom/, and the living-spec index CI gate
   (loom-code/scripts/check-living-spec-index.py) requires lockstep
   registration of new spec/plan files.

**Success criteria**: (a) validator exits 0 on a file with any valid
combination of the three sections and exits 1 with the migration
message on a legacy `## Principles` file; (b) validator exits 1 when
any present section has an entry missing `— check:`; (c) loom-pipeline
seg1 adopt-if-valid tests stay green with zero driver changes (the
adopt gate regexes north-star + `— check:` over the whole text — it
never keyed on the section heading). **Non-criteria**: we do NOT
measure whether bucket-B engineering interruptions actually drop (that
needs future ledger data — G2-style metric, observed later, not gated
here).

## Current State Evidence

- **Forward** (what runs when the touched contract changes):
  - Validator keys on literal heading constants and the `— check:`
    lexeme: `loom-product-principles/scripts/validate_principles_output.py:40-54`
    (`_NORTH_STAR` / `_PRINCIPLES` constants, `^\d+\.\s` entry regex,
    `— check:` marker), `:106-118` (per-entry marker check).
    `_section_body` cuts each section at the next `##` (`:57-66`), so
    additional H2 sections do not corrupt per-section entry counts.
  - D8 judges "the falsifiable `— check:` clauses already written in
    that file" — heading-agnostic:
    `loom-code/agents/code-reviewer.md:401-421` (conditional dimension;
    🔴 only when the violated principle is safety/security/
    privacy-bearing, `:410-415`; statically-verifiable portion only,
    `:417-421`).
  - seg1 adopt-if-valid gate regexes the WHOLE text for north-star +
    one `— check:` — section-agnostic:
    `loom-pipeline/scripts/driver_30_seg1.js:38-43`
    (`isPrinciplesStructurallyValid`), `:93-108` (stable preamble),
    `:130-145` (`reconcilePrinciplesAdoption` downgrade path).
- **Reverse** (who consumes the touched artifacts):
  - The literal `## Principles` heading is hardcoded ONLY inside
    loom-product-principles (grep sweep this session, all 6 files):
    `scripts/validate_principles_output.py:41`,
    `scripts/test_validate_principles_output.py`,
    `scripts/test_product_principles_skill.py:116`,
    `skills/product-principles/SKILL.md`,
    `skills/product-principles/references/principles-rules.md`,
    `README.md`. Zero cross-plugin heading hardcodes — the rename is
    contained in one plugin.
  - `principles-rules.md` is consumed by BOTH the validator and the
    generator SKILL.md
    (`loom-product-principles/skills/product-principles/references/principles-rules.md:7-11`)
    — contract edits must keep the two consumers in sync.
  - The filename `docs/loom/PRINCIPLES.md` is hardcoded by:
    `loom-code/skills/requesting-code-review/SKILL.md:134` (D8
    discovery), `loom-pipeline/scripts/driver_40_seg2.js:132`
    (seg1Paths.principles), `loom-interface-design` design-system /
    interaction-flows / design-critic intake sections, `loom-spec`
    spec-expansion / completeness-critic lens 6 (recon report, this
    session). Keeping ONE file means none of these change.
  - The bundled driver asset
    (`loom-pipeline/skills/using-loom-pipeline/assets/loom-pipeline.js`)
    is GENERATED from `loom-pipeline/scripts/driver_*.js` via
    `build_driver.py` (drift-tested byte-identical) — driver sources
    are SSOT and are NOT touched by this change, so no rebuild.
- **Error**: validator exits 1 with agent-actionable messages
  (`validate_principles_output.py:155-159`) — preserved; the new
  conditional checks and the legacy-heading migration message use the
  same message style. The seg1 adopt-downgrade path
  (`driver_30_seg1.js:130-145`) is preserved unchanged.
- **Data**: PRINCIPLES.md text flows generator → file → validator (path
  argument, `SKILL.md:110`) → station `principles_text_head` (first ~80
  lines, `driver_30_seg1.js:71`). The adopt structural rule needs only
  north-star + one `— check:`, both in the head regardless of appended
  sections — no head-window issue.
- **Boundary**: `[FRAGILE]` the literal `— check:` lexeme (em dash
  U+2014, single space, lowercase, same line;
  `principles-rules.md:144-151`) is the load-bearing token every
  consumer keys on — all three sections reuse it verbatim, no second
  lexeme. `[FRAGILE]` the section headings become a second set of
  load-bearing literals (validator constants ↔ contract ↔ generator ↔
  test fixtures — all in one plugin, drift-testable). No network / DB /
  external API touched.
- **Evidence paths**:
  - `loom-product-principles/scripts/validate_principles_output.py:40-66,91-118,155-159`
  - `loom-product-principles/scripts/test_product_principles_skill.py:116`
  - `loom-product-principles/skills/product-principles/SKILL.md:16,30-37,46-49,60-117`
  - `loom-product-principles/skills/product-principles/references/principles-rules.md:7-15,80-103,133-156`
  - `loom-pipeline/scripts/driver_30_seg1.js:38-43,71,93-108,130-145`
  - `loom-pipeline/scripts/driver_40_seg2.js:132`
  - `loom-code/agents/code-reviewer.md:341,386,401-421`
  - `loom-code/skills/requesting-code-review/SKILL.md:134,174`
  - `docs/loom/BACKLOG.md:13-28`
  - `docs/loom/specs/2026-06-17-principles-conformance-lens.md:115,133`
    (prior decisions: machine parser rejected; conformance = LLM
    judgment)

## Decision

Extend the single-constitution model with three named jurisdictions
instead of adding files: the filename `PRINCIPLES.md` stays (that is
the expensive 8-consumer literal), while the section headings become
`## Product Principles` (hard rename of `## Principles`, required,
3–7 entries) plus optional `## Design Principles` and
`## Engineering Principles` (1–7 entries each). The rename was
originally rejected in this brief's first draft on validator-breakage
grounds; re-costed with kouko on 2026-07-03 after a grep sweep showed
the heading literal is confined to loom-product-principles itself, and
chosen now while the ecosystem is young (few existing files; seg1
adopt gate never keyed on the heading, so deployed pipelines do not
break — legacy files fail only on explicit re-validation, with a
self-explaining migration message). The generator
(loom-product-principles) owns all three sections — one file, one
owner; its "product-level" framing prose widens to "project
constitution", with per-jurisdiction content guidance grounded in the
industry pattern (NN/g value-statements-resolving-trade-offs; Kiro
product/tech steering split; SmartHR-style design principles as design
review 判断軸 — which is exactly design-critic's existing PRINCIPLES
lens). D8 keeps its existing severity rule with a one-line
jurisdiction note. We will NOT build: separate per-jurisdiction files,
ledger-harvest automation, or any change to the TDD iron-law floor.
Trade-off accepted: spec/design consumers read clauses outside their
jurisdiction — the existing "unexercised principles produce no
finding" rule keeps that inert, and labeled sections make the
jurisdiction split explicit rather than implicit.

## Out of Scope

- **Separate ENGINEERING.md / DESIGN.md constitution files** — rejected
  alternative; revisit only if a jurisdiction develops a different
  lifecycle or owner (sectioned content splits cheaply later).
- **Automated clause harvesting from pipeline ledgers** (bucket-B →
  proposed clause) — future work once ≥2 real-change ledgers exist.
- **Changes to loom-interface-design / loom-spec intake prose** — they
  read the whole file already; the design-critic lens needs no code
  change to benefit from labeled sections.
- **Any change to the TDD iron-law floor or loom-code's 12-rule
  baseline** — sections set per-project CEILINGS only.
- **loom-pipeline driver changes** — seg1 adopt gate is
  heading-agnostic (verified); no rebuild of the bundled asset.
- **G4 severity A/B for engineering clauses** — folds into the existing
  G4 backlog item when it runs.
- **Backfilling Design/Engineering sections into existing toy-project
  files** — legacy files migrate their Product heading when next
  re-validated; new sections appear only when their owners commit
  clauses.

## Alternatives Considered

1. **Separate `docs/loom/ENGINEERING.md` (and/or DESIGN.md)** —
   rejected: every consumer hardcodes the single path (8 intake points
   would need wiring); Kiro splits steering files but its harness
   auto-loads ALL of them — ours is path-hardwired, so the split costs
   real wiring; Spec Kit ships one constitution covering both.
2. **Keep `## Principles` heading untouched, append Engineering only**
   (this brief's own first draft) — superseded: rejected the rename on
   breakage grounds before the grep sweep showed the literal is
   confined to one plugin; kouko chose the symmetric three-heading
   scheme once the true cost (one plugin + a migration message) was on
   the table. Recorded here because the reversal is decision history.
3. **Three fully-populated sections from day one** — rejected: no
   ledger evidence of recurring design forks yet (live-verify design
   station + critic panel ran clean); sections appear only when real
   committed clauses exist; a present-but-empty heading is invalid by
   contract.
4. **Machine parser for engineering/design conformance** — already
   rejected by the D8 originating brief (2026-06-17): conformance is
   LLM judgment against `— check:` clauses; the validator checks
   structure only.
5. **CAPS headings (`## PRODUCT-PRINCIPLES`)** — rejected for house
   style consistency with `## North Star` (Title Case) and general
   markdown convention.

## What Becomes Obsolete

- The BACKLOG "ENGINEERING.md" entry (docs/loom/BACKLOG.md:13-28) —
  deleted (not archived) in the shipping PR; the v1.1 batch-mode
  entry's "(after ENGINEERING.md)" start condition updates to reflect
  completion. The planned "Design Principles parked" BACKLOG entry is
  dropped entirely — Design ships in this change (kouko decision
  2026-07-03).
- The unqualified "product-level" claims in loom-product-principles
  SKILL.md / principles-rules.md / README that would contradict the new
  sections — updated in the same PR (widened to project-constitution
  framing; product jurisdiction retained for `## Product Principles`).
- The jurisdiction-blind ✅/❌ example list in `principles-rules.md` —
  re-sorted per jurisdiction in the same PR.
- The earlier draft brief `2026-07-03-engineering-principles-section.md`
  — removed in the same change (this file supersedes it).

## Open Questions

(none — Design-posture elicitation timing resolved 2026-07-03: elicit
now, alongside Engineering; all fork decisions in this brief are
kouko-approved in-session)

> **⛔ SUPERSEDED 2026-06-14 (session 2).** This single-plugin brief was split into TWO plugins after deciding
> (a) `product-principles` is a cross-cutting product constitution (not a design sub-task), and (b) kouko's
> projects span headless/CLI/TUI/GUI so principles must be usable without visual design. Replaced by:
> - `docs/product-principles-toolkit/specs/2026-06-14-product-principles-toolkit-mvp.md`
> - `docs/interface-design-toolkit/specs/2026-06-14-interface-design-toolkit-mvp.md`
> Kept for the decision trail; do NOT build from this file. Its plan (`docs/product-design-toolkit/plans/…`) is likewise superseded.

# Brief — product-design-toolkit MVP (GENERATE front-end: design docs → spec-toolkit)

> Date: 2026-06-14 · Stage: brainstorming → (next) writing-plans
> Pipeline position: **Station 0 (DESIGN) → spec-toolkit (SPEC) → code-toolkit (BUILD)**

> **Revision 2 (2026-06-14, session 2) — output shape corrected after schema research + an external reference review.**
> The MVP is **one skill** but **NOT one file**. Research showed Google's `DESIGN.md` is scoped to the
> **design *system*** (8 token sections only — colors/typography/layout/elevation/shapes/components/do-don't),
> NOT UX flows or screens. An external reference implementation (kept out of this repo) independently splits
> the **visual system** from the **UX flow** into separate artifacts. And kouko added a **supreme
> product-principles layer**. So the one skill now emits a
> **design change-folder of three artifacts** (mirroring spec-toolkit's `proposal.md`+`specs/spec.md` shape):
> 1. **`PRINCIPLES.md`** — supreme, first-produced, slowest-changing: product north-star + non-negotiable,
>    *falsifiable* principles (= Spec Kit `constitution.md` / Kiro `product.md` steering pattern).
> 2. **`DESIGN.md`** — the visual *system* (adopt Google's open 8-section Apache-2.0 format).
> 3. **`ui-flows.md`** — the UX *flow* (screen inventory + navigation + transitions; a 7-dimension UX-flow checklist).
> B/D is **resolved = D** (three peer toolkits, integrate via file-format contract + seams, not merge).
> The sections below are updated to this shape; build is still NOT started.

## Problem

(Axis 1 — JTBD) When kouko starts a software feature/product from an idea, he wants to
do the **front-end design planning and produce design documents** (product direction,
UX flows, UI structure) in a form that **flows directly into `spec-toolkit:spec-expansion`
as a rich seed** — so the product/design intent is captured up front and seeds the
spec→build pipeline, instead of jumping straight to spec/code and discovering UX/UI gaps
late. Sub-job: **discuss design visually** (mermaid flows / ascii layout, optionally real
UI mockups) rather than purely in prose. The capability gap is real because the existing
`domain-teams:design-team` is **audit/consultant-only** (never used as a generator) — there
is no *active GENERATE* design layer, exactly the asymmetry `spec-toolkit` fixed for specs
vs `code-team`.

## Users

(Axis 2) kouko — solo dev, macOS, Claude Code + Codex hosts, public `monkey-skills`
marketplace, **key-free / portable** ethos. Builds via the toolkit pipeline. Today jumps
straight to `spec-expansion`; `design-team` exists but is passive/audit and unused. Wants a
GENERATE front-end he actually uses, with visual design communication.

## Smallest End State

(Axis 3 — **minimal core**, user-chosen) **One skill** (`product-design` / working name)
that takes a sparse product-or-feature idea and, **principles-first**, emits a **design
change-folder** of three key-free, in-repo, git-diffable artifacts:

```
<design-output-dir>/
  PRINCIPLES.md   # supreme layer — product north-star + non-negotiable principles
  DESIGN.md       # visual SYSTEM (Google 8-section open format)
  ui-flows.md     # UX FLOW (screen inventory + navigation; 7-dim UX-flow checklist)
```

**1. `PRINCIPLES.md` (supreme, produced first).** Two sections:
- `## North Star` — the product's original goal + what "success" means.
- `## Principles` — 3–7 **non-negotiable** rules, each carrying a **falsifiable check**
  (e.g. "primary task ≤3 steps", "never block the primary flow with a modal", "offline-readable")
  — NOT platitudes ("be delightful"). DESIGN.md + ui-flows.md are *derived from and accountable
  to* PRINCIPLES.md. (Pattern = Spec Kit `constitution.md` / Kiro steering `product.md`.)

**2. `DESIGN.md` (visual system).** Adopt Google's open Apache-2.0 **8-section** shape —
Overview/Brand · Colors · Typography · Layout · Elevation & Depth · Shapes · Components ·
Do's & Don'ts (YAML token front-matter + markdown rationale; lint-able via `npx @google/design.md`).
**Scope = the visual system only** (tokens/rules), NOT flows or screens.

**3. `ui-flows.md` (UX flow).** The screen-and-journey layer, sections from a 7-dimension
UX-flow checklist: **screen inventory** (each screen + a *flag* of which render
variants exist — empty/loading/error/success), **user flows** (mermaid flowchart/state/journey,
reusing `obsidian:obsidian-mermaid-visualizer`), **UI structure** (ascii layout blocks — mermaid
has no native wireframe, issue #1184), **transitions** (instant/guided/deliberate), **entry/exit
points** (kill dead-ends), **information density**, **mobile flow**.

**Two downstream paths (corrected seam — see Current State Evidence):**
- `ui-flows.md` (screen inventory + nav + render-variant flags) is the **rich seed** to
  `spec-toolkit:spec-expansion` — it names the objects / starting states / journey; spec-expansion
  then does the **behavioral fan-out** (full state machines, edge cases, `#### Scenario:`) — NOT
  duplicated here.
- `DESIGN.md` tokens are a **side-channel** straight to code-toolkit's frontend implementation
  (styling/lint), bypassing spec.

Ship this portable, key-free core first, exactly like `spec-toolkit` shipped OpenSpec-shape
before any tooling. Still **one skill** — three outputs, not three skills.

## Current State Evidence

- **Forward (the downstream seam — CORRECTED):** `spec-toolkit/skills/spec-expansion/SKILL.md:3,9-12,32`
  — spec-expansion consumes a **"sparse seed (a few lines of feature intent)"**; "the seed sets the
  ceiling." The seed is **`ui-flows.md`** (screen inventory + nav + render-variant flags) — NOT
  `DESIGN.md`. DESIGN.md is visual tokens (spec has zero visual concern), so it rides a **side-channel**
  to frontend implementation. Seam-1 = **`ui-flows.md` → spec-expansion seed** (analogous to the
  spec→plan seam, one station earlier).
- **Design↔spec boundary (the clean cut):** design owns the **surface** — decisions a human makes that
  spec can't derive (visual system, screen set, navigation graph). spec owns the **depth** — the
  systematic high-recall fan-out from those decisions (object state machines, edge cases, acceptance
  scenarios). Overlap on "states" is resolved by axis: design lists **render variants per screen** as a
  *flag* (presentational completeness); spec-expansion owns the full **domain-object lifecycle + transition
  rules** (behavioral). Design deliberately **stops at the surface** — doing spec's fan-out would duplicate
  spec-toolkit and bloat the design skill (breaks the three-peer symmetry).
- **Supreme-principles layer (prior art, not invented):** `PRINCIPLES.md` = the **constitution / steering**
  pattern. Spec Kit `constitution.md` = "immutable principles that govern how specifications become code …
  the first thing you do … every subsequent command reads it automatically." Kiro steering `product.md`
  (purpose/objectives) with `inclusion: always` = the mechanism for loading it at every downstream station.
  Load-bearing constraint: principles must be **falsifiable / checkable** or they are dead text (echoes the
  repo's "executable guards, not prose platitudes" lesson). Single source, **referenced (path-passed) not
  copied** downstream — no drift.
- **External corroboration (a reference implementation reviewed privately — PATTERNS ONLY, kept out of this
  repo):** a larger product-development skill suite treats "feature design" as behavioral spec (= our
  spec-toolkit, NOT visual), and puts its **visual layer in a separate alignment step, split into two
  artifacts** — a *visual-system* one (palette/typography/spacing/layout/components = DESIGN.md's territory)
  and a *UX-flow* one (journey/pages/transitions/entry-exit/density/mobile = ui-flows.md's territory). This
  independently validates: (a) separate visual-system from UX-flow; (b) the 7-dimension UX-flow checklist;
  (c) defer external visual tools to a reference tier. Differences we keep: we *generate* (the reference
  *captures* decisions post-hoc — we invert its capture-questions into generation prompts); we use Google
  `DESIGN.md` (the reference uses bespoke yaml); MVP = visual + UX-flow only (the reference's full
  multi-dimension alignment suite is team-scale, out of scope).
- **Reverse (the audit complement / SSOT):** `domain-teams/skills/design-team/SKILL.md:1-11`
  — design-team is "**Design with accessibility and quality review … auditing accessibility …
  Delivers UI specs, wireframes**" but is used as a **passive gate** (kouko: never used,
  consultant/checker by intent). Relationship: product-design-toolkit = **active GENERATE**,
  design-team = **audit** — symmetric to `code-toolkit`↔`code-team`. **MVP does NOT set up a
  knowledge-sync (distribute.py) between them** — keep lean; reference design-team as the
  audit complement, defer any byte-sync. (Avoids premature drift machinery.)
- **Error / boundary (overlap to NOT cross):** `planning-team` owns `PRODUCT-SPEC.md`
  (business + design + tech direction, per CLAUDE.md §Two-Layer Spec). MVP scopes the toolkit to
  the **design layer (principles/UX/UI/screens)** only — NOT business strategy (planning-team's turf)
  and NOT state/edge spec fan-out (spec-expansion's turf). Specifically, `PRINCIPLES.md`'s north-star
  is the **product goal as a design-decision filter** (lightweight, governs look + flow), NOT a full
  market/business-model/strategy document (that stays planning-team's `PRODUCT-SPEC.md`). Distinct
  artifacts, clear seams.
- **Data (reuse):** `obsidian/skills/obsidian-mermaid-visualizer/SKILL.md` — mature mermaid
  generation to reuse for the UX-flow visuals (reference the pattern; do not re-author mermaid
  rules).
- **Plugin scaffold convention:** a new plugin = `.claude-plugin/plugin.json` + `skills/` +
  `scripts/` + `README.md` + a `marketplace.json` entry (`name`/`description`/`source`).
  `spec-toolkit/` is the template.

### Evidence paths appendix
- `spec-toolkit/skills/spec-expansion/SKILL.md`, `domain-teams/skills/design-team/SKILL.md`
- `obsidian/skills/obsidian-mermaid-visualizer/SKILL.md`
- `spec-toolkit/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`
- Research (session 2): Google open-sourced `DESIGN.md` (Apache-2.0, 2026-04), **8 canonical token
  sections, visual-system scope only** — designmd.app/what-is-design-md, howaiworks.ai/blog/google-design-md-standard-ai-agents,
  anthropics/skills#1008. Supreme-layer prior art: Spec Kit `constitution.md`
  (github/spec-kit/blob/main/memory/constitution.md), Kiro steering (kiro.dev/blog/teaching-kiro-new-tricks),
  Martin Fowler "SDD: Kiro, spec-kit, Tessl". External reference: visual-system/UX-flow split — kept out of this repo, patterns only.

## Decision

Build a **new, separate `product-design-toolkit` plugin** (a thin active-GENERATE front-end),
MVP = **one skill** that turns a sparse idea, **principles-first**, into a **design change-folder**
(`PRINCIPLES.md` + `DESIGN.md` + `ui-flows.md`), **key-free**, whose `ui-flows.md` **seeds
`spec-toolkit:spec-expansion`**. Separate plugin (not merged into spec-toolkit) keeps the pipeline
modular + portable — **B/D resolved = D** (kouko, 2026-06-14): three peer toolkits (design/spec/code)
integrate via **file-format contract + seams**, not merge. Decisive arg: product-design-toolkit being
its own plugin makes the three-station granularity consistent; merging spec into code would break the
symmetry. (Also: portability, code-toolkit router identity, plus a larger external lifecycle suite that itself chose modular-not-merged.)

We adopt the **Google `DESIGN.md` 8-section format** (portable, like we adopted OpenSpec-shape) and the
**constitution/steering pattern** for `PRINCIPLES.md`, but **not**: the Stitch/Figma MCP integration yet,
a knowledge-sync with design-team, a multi-skill product-lifecycle suite (a team-scale shape —
anti-Bitter-Lesson to copy now), nor the **downstream principles-conformance gate** (that's P2 seam — see
Out of Scope).

## Out of Scope (MVP)

- Stitch / Figma / v0 MCP integration (tier-2; wire later via official MCP with graceful
  degradation — re-trigger: kouko builds real UI apps, not just tooling).
- Multi-skill decomposition (product-framing / ux / ui as separate skills — a team-scale lifecycle
  shape). Re-trigger: the single skill proves too coarse on a real multi-screen product.
- Knowledge-sync (distribute.py) between product-design-toolkit and design-team.
- Business/product strategy framing (planning-team's PRODUCT-SPEC turf).
- State/edge/path fan-out (spec-expansion's turf — DESIGN.md seeds it, doesn't do it).
- Generator/evaluator design-critic (code-toolkit reviewers + completeness-critic already exist;
  a design-specific critic is a later question).
- product-design → spec-toolkit **automated** hand-off seam (MVP hands the change-folder over manually,
  same posture as the spec→plan seam; automate when manual proves painful).
- **Downstream principles-conformance check (P2 seam).** `PRINCIPLES.md` flows downstream two ways:
  (A) **steering** — passed as always-on context to spec/code stations (this much MAY ride in MVP, it's
  just one more file path on the seam); (B) **conformance gate** — a writer≠judge check "does this
  scenario / this code violate a principle?". B is **out of MVP scope** and, when built, is added as a
  **lens to the existing critics** (`completeness-critic` at spec, `requesting-code-review` at code) —
  NOT a new gate engine, and NOT by modifying spec-toolkit/code-toolkit now. Re-trigger: a real run where
  drift from the stated principles actually bites.

## Alternatives Considered

(Axis 4 — research-grounded, EN+JP via WebSearch)
- **DESIGN.md (Google open Apache-2.0 format)** — *chosen for the visual-system artifact.* Portable,
  Claude-Code-consumable, git-diffable, key-free, lint-able (`npx @google/design.md`); the design-layer
  analog of OpenSpec. **Scope confirmed by research = 8 token sections only** (Overview · Colors ·
  Typography · Layout · Elevation & Depth · Shapes · Components · Do's & Don'ts) — design *system*, NOT
  UX flows/screens → hence the separate `ui-flows.md`. Source: Google open-sourced DESIGN.md 2026-04 (EN).
  Con: newer ecosystem.
- **Constitution / steering for `PRINCIPLES.md`** — *chosen for the supreme layer.* Direct prior art:
  Spec Kit `constitution.md` (immutable governing principles, auto-read by every command) + Kiro steering
  `product.md` (`inclusion: always`). Adopted as pattern, not a dependency. Con: only valuable if
  principles are falsifiable — enforced by the per-principle check rule.
- **External visual-system + UX-flow split** — *corroborating pattern (reference kept out of this repo,
  patterns-only).* Independently validates separating the visual system from the UX flow and the UX-flow
  dimension checklist.
- **Stitch / Figma via official MCP** — *deferred to tier-2.* Produces real UI mockups + exports
  React/Tailwind; has an official Claude Code Skills/MCP path (EN+JP confirm). Con: account/service-
  bound, breaks key-free purity, non-production code (JP: needs eng refinement). Good as optional.
- **mermaid + ascii (diagrams-as-code)** — *chosen for core visuals.* Agent-generatable, key-free,
  in-repo, reuse existing skill. Con: mermaid has no native wireframe (issue #1184) → ascii for layout.
- **Reuse domain-teams:design-team as-is** — *rejected for the generate role.* It's audit/consultant,
  not an active generator (the gap this toolkit fills); kept as the audit complement.
- **Extend spec-expansion with a design phase** — *rejected.* Bloats spec-toolkit's scope + conflates
  design framing with state fan-out; cleaner as a separate Station 0.

## What Becomes Obsolete

(Axis 5) Closes the "jump straight to spec with no design front-end" gap **and** the "no stated product
principles governing design + downstream implementation" gap. Nothing is deleted —
design-team stays as audit, planning-team stays for product strategy, spec-expansion stays for fan-out.
Purely additive → YAGNI risk acknowledged, but justified by (a) the real generate-gap (design-team
audit-only) and (b) kouko's explicit pipeline-front-end scenario. Re-baseline if the single skill goes
unused after a real product run.

## Open Questions

- **`DESIGN.md` schema** — *now known* (8 sections above); still fetch the authoritative Google spec at
  build time to lock the exact YAML token keys + adopt the shape with a `validate_*` script mirroring
  `validate_spec_output.py` (validates the **whole change-folder**: PRINCIPLES + DESIGN + ui-flows present
  and well-formed).
- **File names** — `PRINCIPLES.md` vs `CONSTITUTION.md` (Spec-Kit-precedented); `ui-flows.md` vs
  `UX-FLOW.md`. Decide in writing-plans. (`DESIGN.md` is fixed by the Google format.)
- **Skill name**: `product-design` vs `design-framing` vs `design-doc` — decide in writing-plans.
- **Codex 1024-char description guardrail** applies (the new skill's description must be ≤1024 — the
  lesson from the code-toolkit Codex-compat work).
- **Principles falsifiability enforcement** — does the skill *require* each principle to carry a check, or
  just prompt for it? (Lean: require — a principle with no check is rejected at generation.)
- Does the `ui-flows.md` → spec-expansion seam want a tiny adapter eventually, or stay manual (likely
  manual for single-feature, like the spec→plan seam)? Does `PRINCIPLES.md` ride the seam as steering
  context in MVP, or wait for the P2 conformance lens?

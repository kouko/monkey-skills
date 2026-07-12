# Brief — enrich product-principles' visual-style movement anchoring (canon split + Axis-B expansion + 3-5/divergent candidates)

Date: 2026-07-12
Station: loom-product-principles (design-section flow + visual canon reference files). Light optional follow-on in loom-interface-design.
Type: enrichment of EXISTING machinery (not a new feature / not a new station)

## Design-side on-ramp

N/A — this edits the product-principles STATION itself (the machinery that
recommends design canon and writes PRINCIPLES.md), not a consumer product.
On-ramp table governs consumer repos; it does not fire for editing the generator.
Routed directly through loom-code.

## Problem

(Axis 1 — JTBD) When a user drives the principles station's Design section, they
want to **commit a named visual-style direction early, chosen from a rich,
grounded set of candidates**, so downstream design derives details from a
coherent anchor instead of improvising. Three sub-jobs:

1. **Richer candidate set.** The Design section recommends 2-3 visual-canon
   candidates; the user wants **3-5**, including some that **deliberately
   deviate** from their stated stance to surface possibilities they had not
   considered.
2. **Axis separation without cross-contamination.** The visual-style space has
   two different KINDS of entry — (A) cultural / graphic-design movements
   (Bauhaus, Swiss, Memphis…) and (B) UI surface treatments (skeuomorphism,
   flat, neumorphism, glassmorphism, Spatial/Liquid Glass). Today both live in
   ONE file and the surface treatments are collapsed into a single row. The user
   wants Axis B **expanded into individual grounded entries** AND the two axes
   **split into separate files** — so that when the agent reasons about Axis A it
   is not context-polluted by Axis-B entries (a risk that GROWS as Axis B gets
   richer).
3. **The named anchor travels downstream.** The chosen movement(s) land in
   PRINCIPLES.md `## Anchors` (already version-pinned) and interface-design's
   design-system elaborates them into tokens.

Origin: a runtime-improvised style menu once offered a technical STANDARD as if
it were an aesthetic option (investigated — plugin text was clean; the conflation
was agent improvisation). The durable fix is to make the principled candidate
flow richer and axis-typed so improvisation has no room.

## Users

(Axis 2) The user (designer/PM) driving `loom-product-principles:product-principles`
through its Design section, stating a design stance in their own words and
choosing a visual direction from agent-recommended candidates. Job story: *"When
I commit my product's visual direction, I want a rich set of grounded candidates —
including a couple that stretch beyond what I asked — organized so a cultural
movement and a surface treatment are chosen as separate, non-contaminating
decisions."*

## Current State Evidence

**This is mostly already built — the change is enrichment, not creation.**

- **Forward** (candidate flow exists): `product-principles/SKILL.md:102-137`
  (Step 3-4) — agent proposes 2-3 same-axis canon candidates with fit/tension
  notes from ≥2 traditions, surfaces 1-2 considered-but-rejected, user decides;
  `question-sets.md:49-56` (Design section) — "state your design stance … agent
  maps onto canon (lists 2 + 3: interaction + visual, **separately**), returns
  **2-3 candidates per lens**".
- **Data** (the library exists with our entry structure): `references/canon-design-visual.md`
  — a table `Entry (originator, era) | Fits when… | Stability | Source` (~19
  entries: Bauhaus, De Stijl, Swiss, Memphis, Vignelli Canon, Kenya Hara/MUJI,
  etc.). The `Stability` column already distinguishes `Canon` (stable) from
  `Trend cycle, not canon`. Surface treatments are collapsed into ONE row:
  "Flat → skeuo → neumorphic → glassmorphic cycle (2007-) | … must name which
  era". Grounded in `docs/loom/research/2026-07-10-principles-canon-base-lists.md §3`.
  Header: "**never shown raw to the user** … agent-facing recall insurance"
  (the source-not-menu principle already holds).
- **Reverse** (SSOT / downstream carry): the chosen canon lands version-pinned in
  PRINCIPLES.md `## Anchors` (`SKILL.md:156-158`, "canon drifts too — Material
  2→3, HIG yearly"); complementary canons (different questions) pin as SEPARATE
  Anchors rows, "never … one exclusive pick-one menu" (`SKILL.md:113-120`) —
  Axis A vs Axis B ARE complementary, so this rule already sanctions two rows /
  two rounds. `PRINCIPLES.md` is read downstream by design-system
  (`product-principles/SKILL.md:305-320`).
- **Error / Boundary**: the "same-axis alternatives in one round" rule
  (`SKILL.md:113-120`) is the guardrail that keeps a cultural movement and a
  surface treatment from being offered as one pick-one menu — the change extends
  it (two typed rounds), it does not fight it.

Evidence paths: `loom-product-principles/skills/product-principles/SKILL.md`,
`.../references/question-sets.md`, `.../references/canon-design-visual.md`,
`.../references/principles-rules.md`,
`docs/loom/research/2026-07-10-principles-canon-base-lists.md`.

## Smallest End State

(Axis 3) Reference-file split + expansion + small flow-text tweaks in
product-principles. NO new skill/module, NO validator-logic change.

- **Split the visual canon into two files** (contamination prevention, scales
  with enrichment):
  - `references/canon-design-visual.md` → keep as **Axis A: cultural / graphic
    movements** (the existing cultural entries; remove the surface-cycle row).
  - NEW `references/canon-design-surface.md` → **Axis B: UI surface treatments**,
    the collapsed cycle **expanded into a Phase-1 minimal seed of individual
    grounded entries** (~5-6: skeuomorphism / flat / material-as-surface /
    neumorphism / glassmorphism / spatial-Liquid-Glass), same table shape PLUS a
    currency stamp and risk flags (e.g. neumorphism's low-contrast WCAG risk).
    Grounded to time-stamped current sources (NN/g + platform release docs) via a
    dated companion research doc. **Axis A ships its existing ~18 entries as-is**
    (content already rich — only the surface row is removed). See §Phasing.
- **Design-section flow tweaks** (`SKILL.md` Step 3 + `question-sets.md:49-56`):
  - The visual lens runs as **two separate candidate rounds** — Axis A (reads
    canon-design-visual.md) then Axis B (reads canon-design-surface.md) — each
    round Reads only its own file (the contamination guard). Each lands as its
    own version-pinned `## Anchors` row (Axis B optional-blank).
  - Bump the visual-lens candidate count from 2-3 to **3-5**.
  - Add the **divergent-candidate** concept: of the 3-5, deliberately include
    1-2 that **deviate from the user's stated stance** to expand the space —
    TRANSPARENTLY labeled as exploratory, and still **defensible against the
    Product Principles values** (deviate on aesthetic expression, never on the
    non-negotiable values; a low-stimulus constitution still excludes Memphis).
  - Update the canon-audit reference list (`SKILL.md:122-124`) to name both files.
- **plugin.json** — loom-product-principles version bump at close-out.

Deferred to Out of Scope / Open Questions: design-system Overview/Brand
discoverability + style/quality guardrail (tiny, optional follow-on); the
interaction-quality-floor expansion (keyboard/focus/touch/motion/i18n) is a
SEPARATE design-system concern, not this brief.

## Phasing

- **Phase 1 (this brief / SDD)** — the MECHANISM + a runnable seed: two-file
  split, two-round Design flow (A then B, each reads only its own file), 3-5
  candidate count, divergent-candidate logic, currency/risk columns, two-row
  Anchors landing. Content: Axis A ships its existing ~18 entries (surface row
  removed); Axis B ships a ~5-6 entry minimal seed (a round cannot be empty).
  This is the behavioral change — full TDD/SDD + review.
- **Phase 2 (later, additive — BACKLOG)** — expand BOTH catalogs (more Axis-A
  movements, more Axis-B treatments). Purely additive entries to the reference
  files; NO flow change, lighter process (per-entry grounding research). Add a
  BACKLOG item at close-out; re-trigger = "want richer candidates" OR "a real
  product needs a treatment not in the seed". Expectation: the divergent-candidate
  feature's surprise value grows with catalog richness — Phase 1's thin Axis B
  makes the surface round's exploratory options limited by design, not a defect.

## Alternatives Considered

(Axis 4 — EN+JP WebSearch, sources tagged by language; full findings in the
session research pass)

1. **Weave a11y into the color foundation vs a dedicated section** — Apple HIG /
   Material 3 / デジタル庁 weave contrast INTO color ([EN] m3.material.io/foundations;
   [JA] design.digital.go.jp/dads/foundations/color/accessibility/); IBM Carbon
   keeps a separate top-level accessibility tree ([EN] carbondesignsystem.com).
   EN/JA divergence: EN leans separate-section, JA leans interwoven. → informs the
   deferred quality-floor item, not this brief's core.
2. **Movement taxonomy = genealogy, not orthogonal axes** — the field frames
   cultural movements as ROOTS feeding surface trends ([EN] IxDF Design Movements,
   NN/g "Flat Design: Its Origins"; [JA] unprinted.design / sungrove.co.jp —
   源流はスイス/バウハウス). A rigid two-axis grid is a **novel synthesis**;
   keep the axes typed but frame them combinable/genealogy-aware, not pure
   orthogonal. The existing canon file's `Stability` column already encodes this
   (Canon vs Trend cycle).
3. **Movement-first anchoring is only an informal prompt convention** — v0 /
   Galileo prompt a named aesthetic then emit token files ([EN] designcode.io,
   hackdesign.org); no tool derives tokens from a movement's principles. The
   design's novelty = the real derivation; its risk = costume-over-function.

**My take (given the brief):** enrich the EXISTING product-principles Design flow
rather than build anything new (grep proved ~80% exists). Keep style
principle-derived (with the grain of every mature system). Keep the two axes
TYPED and in SEPARATE files (user's contamination guard, reinforced by the
existing same-axis rule). Ship the divergent-candidate concept with the
values-defensibility guard to fight genericness.

**Conditional reversal:** if two candidate rounds (A then B) prove too heavy in
real runs, collapse to one visual round that reads both files but keeps the
entries axis-tagged — the file split (contamination guard) stays regardless.

**Red flags carried in (from research):** costume-over-function (best-documented;
→ divergent candidates must stay values-defensible + derivation-must-be-real);
genericness/dating (→ Axis-B currency stamps + popularity-head crowd-out note,
already present); category conflation (→ two typed files/rounds).

## What Becomes Obsolete

(Axis 5) The collapsed "Flat → skeuo → neumorphic → glassmorphic cycle" single
row in `canon-design-visual.md` is superseded by the expanded
`canon-design-surface.md` entries — remove the row in the same change (don't
leave both). The "2-3 candidates per lens" wording for the visual lens is
superseded by "3-5" — replace, not duplicate.

## Out of Scope

- No new skill or module; no validator-logic change.
- Interaction-quality-floor expansion (keyboard/focus/touch-target/motion/i18n)
  in design-system schema — a separate, later item.
- design-system Overview/Brand discoverability rename + runtime-improvisation
  guardrail — optional tiny follow-on; not required for this brief's value.
- No global change to the Product / Engineering sections' 2-3 candidate count —
  the 3-5 bump is scoped to the VISUAL lens only.
- No change to the `## Anchors` / `— check:` contract in principles-rules.md
  (the two-row landing is already supported).

## Open Questions

1. Axis-B starter size: how many surface-treatment entries ship in v1? (Recommend
   ~6: skeuomorphism, flat, material, neumorphism, glassmorphism, spatial/Liquid
   Glass — each currency-stamped.)
2. Divergent-candidate ratio at 3-5: fixed "1-2 exploratory" or agent-judged?
   (Recommend 1-2, agent labels which are on-brief vs exploratory.)
3. `Excluded when` note on Axis-A entries — only on entries that cross common
   values (e.g. Memphis vs low-stimulus), or on every entry? (Recommend
   only-when-crossing, to keep the file light and not over-prescribe values.)
4. Does the §3 research doc get extended in-place, or a dated Axis-B companion
   added? (Recommend a dated companion for the time-sensitive surface entries.)

# Brief — Visual anchoring realignment: tone & manner primary anchor + Axis A reframing (P2 Step 1)

> **Type**: brainstorming brief (loom-code Stage 1 output)
> **Date**: 2026-07-12
> **Origin**: BACKLOG "Visual-style canon catalog expansion — Phase 2" (PR #551),
> re-scoped after industry research. Supersedes the naive "just grow both
> catalogs" reading of that entry.
> **Target plugin**: loom-product-principles (0.7.0 → 0.8.0)

## Problem

At the principles stage the agent currently proposes art-movement candidates
(Axis A) and UI surface-treatment candidates (Axis B) as two parallel
candidate rounds, and the user anchors on them. Industry research (see
§Research below) shows this is **structurally misaligned** with how digital
products actually anchor visual direction:

- The industry's real primary anchor is **brand/product values → 3-5
  tone & manner adjectives** (Aaker brand personality; NN/g mood boards;
  the JA トンマナ pipeline). Our flow **skips this step entirely**.
- **Art movements are stage-3 mood/creative-direction INPUT** (downstream of
  values), not a formal selection criterion. Presenting them as a pick-one
  candidate menu over-claims convention — and is the shape of the original
  bug the user reported (styles appearing as a menu mixed with standards).
- **Surface treatments (Axis B) are a stage-4 design-language sub-decision**
  (the surface/depth convention components inherit), i.e. they belong to the
  DESIGN station, not the PRINCIPLES station. They are frequently *derived*
  from platform/era/tech constraints rather than user-anchored.

JTBD: *When defining a product's constitution, I want the visual direction
anchored the way the industry actually anchors it — values first, adjectives
as the anchor, art movements as constrained inspiration — so the downstream
DESIGN stage inherits a defensible direction instead of a costume pick.*

## Users

The agent operating `loom-product-principles:product-principles` for a user
defining a new product's constitution, and (downstream) the
`loom-interface-design` station that consumes the resulting Anchors.

## Smallest End State

Three deliverables, all inside loom-product-principles:

1. **Tone & manner primary anchor (NEW, lightweight)**: the Design lane's
   visual flow first derives **3-5 tone & manner adjectives** from the
   product's values/principles. These adjectives are the primary visual
   anchor. Implemented as flow text + derivation instruction in SKILL.md and
   question-sets.md — no new machinery.
2. **Axis A reframed as value-constrained mood inspiration**: the
   `canon-design-visual.md` framing states Axis A is stage-3 mood/creative
   direction *downstream of the adjective anchor*, never a pick-one menu;
   strengthen the anti-costume rule (a movement may enrich candidates but
   NEVER overrides a PRINCIPLES value — the existing Memphis-vs-low-stimulus
   discipline, now stated as the general law).
3. **Axis A cultural-blindspot expansion (16 entries, all URL-live-verified)**:
   grow `canon-design-visual.md` with the researched entries below.

## Current State Evidence

- **Forward**: `loom-product-principles/skills/product-principles/SKILL.md`
  Step 3 runs the visual lens as two axis-typed candidate rounds (Axis A =
  `references/canon-design-visual.md`, Axis B = `references/canon-design-surface.md`),
  each round reading only its own file, 3-5 candidates incl. 1-2 divergent.
- **Reverse**: `references/canon-design-visual.md:1-16` — the canon file is
  agent-facing recall insurance ("never shown raw to the user"), carrying
  name + fits-when + stability + source; ~19 rows today, all Western
  professional-graphic-design history except two Japan rows.
- **Data**: `references/question-sets.md` Design lane carries the same
  two-round + 3-5/divergent wording (interaction lens stays 2-3).
- **Boundary**: `loom-product-principles/scripts/test_canon_references.py`
  enforces the CANON_FILES contract (≥14 rows for canon-design-visual.md);
  `test_surface_canon.py` guards canon-design-surface.md (≥5 rows + Currency).
  Adding rows keeps both contracts satisfied (additive only).
- **Error**: no error path — these are reference/flow-text changes.

## Decision

**Build**: the tone & manner primary anchor (lightweight, flow-text only),
the Axis A reframing (mood inspiration downstream of the anchor, hard
anti-costume law), and the 16-entry Axis A cultural expansion. Bump
loom-product-principles 0.7.0 → 0.8.0 (new capability).

**Do NOT build** (deferred to Step 2, a separate BACKLOG entry): moving
Axis B to loom-interface-design's DESIGN stage, and the Axis B catalog
expansion (12 researched candidates). This step adds only a **forward-note**
in `canon-design-surface.md` recording that this axis's correct home is the
design-language stage — no move, no expansion.

**Why split**: the Axis B move is cross-plugin (product-principles →
interface-design) and touches a different pipeline station; it is genuinely
a different stage's concern (industry stage 4 vs stage 3). Shipping the
principles-side realignment first is the smallest end state that fixes the
structural misalignment where it originates.

## Axis A expansion — the 16 entries (user-approved, all live-verified)

Chronological within region. Every source URL was WebFetch-verified live
during research (the #550 fabricated-URL lesson).

**Euro-American** (6):
1. Art Deco (1920s-30s) — Canon — https://www.vam.ac.uk/articles/an-introduction-to-art-deco
2. Pop Art (1950s-60s) — Canon — https://www.tate.org.uk/art/art-terms/p/pop-art
3. Psychedelic poster art (1966-70) — Canon (niche) — https://posterhouse.org/event/psychedelic-posters-an-introduction/
4. Pixel Art (late 1970s-80s) — Canon — https://en.wikipedia.org/wiki/Pixel_art
5. Cyberpunk (1980s) — Trend/genre — https://en.wikipedia.org/wiki/Cyberpunk
6. Vaporwave (early 2010s) — Trend — https://en.wikipedia.org/wiki/Vaporwave

**Japan** (4):
7. Ukiyo-e (Edo, 17th-19th c.) — Canon (regional) — https://en.wikipedia.org/wiki/Ukiyo-e
8. Kawaii (1970s-) — Canon (regional) — https://en.wikipedia.org/wiki/Kawaii
9. City Pop visual / Hiroshi Nagai (1980s) — Trend/revival — https://en.wikipedia.org/wiki/Hiroshi_Nagai
10. Superflat (Murakami, 2000) — Canon (regional) — https://www.theartstory.org/movement/superflat/

**Soviet** (1) — added after the user spotted the gap; see §Lineage note below:
11. Soviet Socialist Realism poster art (Stalin-era state doctrine, 1932/34-1980s) — Canon (propaganda-origin) — https://www.tate.org.uk/art/art-terms/s/socialist-realism

**Greater China** (5):
12. Dunhuang / Mogao mural aesthetic (4th-14th c.) — Canon (regional) — https://www.getty.edu/research/exhibitions_events/exhibitions/cave_temples_dunhuang/gallery.html
13. Shanghai calendar poster / 月份牌 (1920s-30s) — Canon (regional) — https://www.thecollector.com/yuefenpai-facts-chinese-calendar-advertisements/
14. Cultural-Revolution poster style (1949-76) — Canon (regional) — https://chineseposters.net/themes/mao-cult
15. Hong Kong neon / Kowloon streetscape (mid-late 20th c.) — Canon (regional) — https://www.mplus.org.hk/en/magazine/collecting-neon-signs-from-hong-kongs-streets/
16. Guochao / 国潮 (contemporary) — Trend — https://en.wikipedia.org/wiki/Guochao

### Lineage note (Soviet ↔ Cultural-Revolution) — evidence-bounded

The canon already carries **Russian Constructivism (1920s)**, the Soviet
avant-garde. It was MISSING the style that *displaced* Constructivism (the
1932 decree / 1934 congress) and that stands upstream of the Chinese
Cultural-Revolution look — i.e. the canon held the ancestor and the
grandchild but not the parent. Entry 11 closes that gap.

**The transmission claim was researched and came back SUPPORTED but weaker
than first assumed** — the evidence licenses *descent-then-divergence*, NOT
"the Chinese regional variant". Landsberger's collection records that in
1949-57 Chinese painters trained in Soviet academies (and Soviet professors
taught in Chinese institutions), and that Mao was depicted "in the vein of the
statues of Lenin"; but the same sources record the doctrinal BREAK — Socialist
Realism was replaced by "revolutionary realism + revolutionary romanticism",
producing the distinct 紅光亮 (red / bright / shining) leader-cult register.

**Paste-ready, source-licensed wording for the Cultural-Revolution row's
cross-reference** (do NOT strengthen it to a bare "variant" — that overstates
continuity against the sources):

> descended from Soviet Socialist Realism (Chinese painters trained in Soviet
> academies, 1949-57), then diverged into its own "red, bright and shining"
> (紅光亮) leader-cult register

**A fabricated-URL near-miss was caught during this research**:
`chineseposters.net/themes/socialist-realism` is a plausible-looking 404 that
does not exist. Same shape as the #550 fabricated source. Every URL above was
WebFetch-verified live.

**High-costume-risk rows** (Cyberpunk, Vaporwave, City Pop, **Soviet Socialist
Realism**, Cultural-Revolution poster, Guochao) carry an explicit per-row
anti-costume caveat. The two propaganda-origin rows (Socialist Realism,
Cultural-Revolution) additionally state: **formal visual vocabulary only, never
the propaganda freight**. Including these RAISES the load on the anti-costume
law — which deliverable 2 exists to carry.

## Research (Axis 4) — why this realignment

Industry stage map (EN+JA corroborated, all sources live-verified):

| Stage | Layer | Decides |
|---|---|---|
| 1 Strategy & values | strategy | what/for whom |
| 2 Brand personality → 3-5 adjectives (tone & manner) | strategy | **the primary visual anchor (words)** |
| 3 Art/creative direction + mood board | strategy | mood, emotional tone ← **Axis A** |
| 4 Visual design language (color/type/shape/**surface-depth**/motion) | design-language | the concrete look ← **Axis B** |
| 5 Design system / tokens | execution | reusable variables |
| 6 Components / screens | execution | the UI |

- Aaker, "Dimensions of Brand Personality," JMR 34(3) 1997 — https://journals.sagepub.com/doi/abs/10.1177/002224379703400304
- NN/g, "Mood Boards in UX" — https://www.nngroup.com/articles/mood-boards/ (named method; keyword-seeded, NOT movement-seeded)
- Norman's three levels (IxDF) — https://ixdf.org/literature/article/norman-s-three-levels-of-design (aesthetics anchor to intended feeling)
- Material Design — https://en.wikipedia.org/wiki/Material_Design (anchors on a paper/ink metaphor + principles, not an art movement)
- Swiss Style — https://en.wikipedia.org/wiki/Swiss_Style_(design) (art-movement influence operates as retrospective lineage at two layers — closest prior art for the two-axis split)
- JA トーン&マナー pipeline — https://chibico.co.jp/blog/branding-design/tone-and-manner-026/ (brand concept → keywords → key color/font)

**Key findings**: (a) No mature design system anchors on an art movement —
all anchor on brand values + a functional metaphor. (b) Art movements are
mood-board input / retrospective lineage, not a formal selection criterion.
(c) Axis A (stage 3) and Axis B (stage 4) sit in **different layers**; A may
feed B but never determines it (same mood → several possible surface
treatments; B is also platform/era/tech-driven). (d) EN/JA divergence is
emphasis only: JA is more operationally explicit about the adjective
pipeline; EN supplies the art-movement narrative.

## Alternatives Considered

- **Grow both catalogs as originally scoped** (Axis A → ~34, Axis B → ~18):
  rejected — doubling Axis A without the reframing amplifies the
  costume-menu failure mode the user originally reported; and it leaves the
  real industry anchor (adjectives) still missing.
- **Move Axis B to interface-design in the same change**: rejected for THIS
  step — cross-plugin, different pipeline station; would bloat the change and
  couple two stations' releases. Deferred to Step 2 (BACKLOG).
- **Only add the adjective anchor, no Axis A expansion**: rejected — the user
  explicitly wants the richer divergent-candidate fuel now, and the reframing
  is what makes the risky rows safe to add.

## What Becomes Obsolete

- Nothing is removed. The `canon-design-surface.md` two-round machinery stays
  functional as-is (it merely gains a forward-note about its eventual home).
- The framing "the visual lens runs as two parallel axis-typed candidate
  rounds, both anchoring" is superseded in spirit: Axis A becomes explicitly
  downstream of the adjective anchor. The two-file contamination guard from
  #550 is UNCHANGED and still load-bearing.

## Out of Scope

- Moving Axis B to `loom-interface-design` (Step 2).
- Axis B catalog expansion — the 12 researched surface-treatment candidates
  (Step 2). Research is preserved in
  `scratchpad/p2-research-axisB-surface{,-round2}.md` and will be re-grounded
  into a dated research doc when Step 2 runs.
- Any change to the interaction lens (stays 2-3 candidates).
- Any change to the CANON_FILES ≥14 contract or the surface-canon ≥5 contract.

## Resolved decisions

- **The tone & manner adjectives land as their own version-pinned `## Anchors`
  row in PRINCIPLES.md** (user-decided 2026-07-12) — NOT as Design-section
  prose. Rationale: it IS the primary visual anchor, so it must be mechanically
  readable by the downstream DESIGN station (loom-interface-design); prose-only
  would leave the movement nouns as the only machine-readable signal, which is
  exactly the misalignment this change exists to fix. Same shape as the existing
  canon Anchors rows (name + version pin), so the Anchors-row machinery is
  reused, not extended.

## Open Questions

- None outstanding. (The Anchors-row question above was the last one; resolved
  by the user before writing-plans.)

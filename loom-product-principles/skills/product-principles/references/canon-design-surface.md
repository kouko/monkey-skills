# Canon: UI surface treatment (Axis B)

Agent-facing recall insurance, consulted at the propose-candidates step as a
completeness audit — never shown raw to the user.

Including but not limited to the entries below; doctrine content stays in
the model (this list carries name + fits-when hint + stability note +
currency note + source only). Kept as a SEPARATE file from
`canon-design-visual.md` (Axis A: cultural/graphic-design movements) so
reasoning about Axis-A movements is not context-polluted by Axis-B surface
entries — the two axes answer different questions ("which design
tradition" vs "which screen-surface treatment era").

Grounded in `docs/loom/research/2026-07-12-ui-surface-treatments-canon.md`.

**Forward-note — this axis's correct home is the DESIGN stage.** Industry
practice places surface/depth treatment at **stage 4, the visual
design-language step** (the concrete look components inherit), downstream of
the stage-3 tone & manner anchor — not at the PRINCIPLES stage where this
file currently lives. Surface treatments are typically *derived* from
platform / era / tech constraints rather than user-anchored, so their proper
owner is `loom-interface-design`, not `loom-product-principles`. **Relocating
this axis to `loom-interface-design` is deferred to Step 2** (cross-plugin
move; out of scope for this change). Until then the entries below stay here
and stay usable — the mis-placement is recorded, not hidden.

| Entry (originator, era) | Fits when… | Stability | Currency | Source |
|---|---|---|---|---|
| Skeuomorphism (Apple iOS, 2007-13) | Novice users need physical-object intuition transferred to the screen | Historical reference | Retired 2013 (WWDC iOS 7) | [NN/g](https://www.nngroup.com/articles/flat-material-design/) |
| Flat design (Apple iOS 7 / Microsoft Metro, 2010-13) | Legibility and minimalism over realism; typography-led hierarchy | Live baseline | Mainstream default since 2013, still tempered-live | [Apple Newsroom](https://www.apple.com/newsroom/2013/06/10Apple-Announces-iOS-7/) |
| Material-as-surface (Google Material Design elevation/shadow, 2014-) | Need selective physicality — elevation shadow + motion communicating spatial relationship, not full skeuomorphic literalism | Live, evolving | Launched 2014, current iteration "Material 3 Expressive" (2025) | [design.google](https://design.google/library/material-design-eras) |
| Neumorphism / soft UI (neumorphism.io generator, 2019-20) | Monochromatic soft-extruded look is explicitly requested — flag the WCAG risk before proposing | Trend, cautionary | Viral peak 2019-2020, never shipped as a platform default | [Axess Lab](https://axesslab.com/neumorphism/) |
| Glassmorphism (Apple macOS Big Sur / Microsoft Fluent Acrylic, 2017-20) | Translucent, layered-glass-pane depth cue over content is wanted | Recognizable, still-used | macOS Big Sur shipped Nov 2020, term entered mainstream same year | [Apple Newsroom](https://www.apple.com/newsroom/2020/11/macos-big-sur-available-today/) |
| Spatial design / Liquid Glass (Apple, 2025-) | Interface chrome must unify across 2D screens and spatial/mixed-reality contexts | Live, newest in cycle | Announced WWDC June 2025, current design language 2025-26 | [Apple Newsroom](https://www.apple.com/newsroom/2025/06/apple-introduces-a-delightful-and-elegant-new-software-design/) |

**Risk flag**: neumorphism's signature low-contrast, same-hue
shadow-on-background technique routinely fails **WCAG** 2.x contrast-ratio
minimums for text and interactive elements — treat it as a cautionary
paradigm, not a recommended default, unless the requester explicitly
accepts the accessibility trade-off.

**Popularity head**: flat design and Material Design crowd out the rest of
this list — an LLM defaults to one of these two without prompting. If a
draft's candidate set only names "flat" or "Material," re-check the full
cycle above (especially glassmorphism and spatial/Liquid Glass for a
current-era ask, or skeuomorphism/neumorphism when the ask is historical
or explicitly nostalgic) before proposing.

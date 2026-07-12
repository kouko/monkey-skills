# UI surface-treatment paradigms — grounding note

> **Type**: research note (web-grounded, per-paradigm sourcing)
> **Date**: 2026-07-12
> **Consumer**: the Axis-B visual-style canon entry (a later task) in
> `loom-product-principles/skills/product-principles/references/`, mirroring
> how `canon-design-visual.md` cites
> `docs/loom/research/2026-07-10-principles-canon-base-lists.md` §3.
> **Method**: single research pass, well-established public facts per
> paradigm; each entry carries a citable source URL and an era/currency note
> (house discipline: "ground in sources before cataloging").
> **Scope**: this is a grounding reference, not an essay — one-line
> characterization + adjective cluster + exemplar + era + source per
> paradigm. Doctrine/decision content stays out of this file.

## 1. Skeuomorphism

**Characterization**: UI elements mimic real-world material/texture/depth
(leather stitching, paper grain, chrome knobs) so novice users transfer
physical-object intuition to the screen.

**Adjectives**: textured, ornamental, realistic, tactile, literal.

**Exemplar**: Apple's original iOS (2007-2013) — Notes app's yellow legal-pad
texture, Game Center's felt-and-wood-grain shelving, Calendar's leather
stitching.

**Era / currency**: dominant iOS design language 2007-2013; formally retired
at WWDC 2013 with iOS 7's flat redesign. Now a historical reference point,
not a live default.

**Source**: [NN/g — "Flat, Skeuomorphic, and 'Material' Design"](https://www.nngroup.com/articles/flat-material-design/)

## 2. Flat design

**Characterization**: strips ornamental depth cues (shadows, gradients,
textures) down to solid color, geometric shape, and typography-led
hierarchy; legibility and minimalism over realism.

**Adjectives**: minimal, geometric, high-contrast, typographic, austere.

**Exemplar**: Apple iOS 7 (2013) — the flagship break from skeuomorphism;
also Microsoft's Metro/Modern UI (Windows Phone 7, 2010) as an earlier
mover.

**Era / currency**: iOS 7 shipped September 2013; flat design became the
mainstream default through the mid-2010s and remains a live baseline
(tempered since by Material's subtle elevation shadows).

**Source**: [Apple Newsroom — "Apple Announces iOS 7"](https://www.apple.com/newsroom/2013/06/10Apple-Announces-iOS-7/)

## 3. Material Design (as a surface treatment)

**Characterization**: reintroduces physicality selectively — paper-like
surfaces with printed-ink color, cast shadows keyed to elevation (z-axis),
and motion that communicates spatial relationships — a middle path between
flat's austerity and skeuomorphism's literalism.

**Adjectives**: layered, elevation-shadowed, motion-coherent, printed-ink,
grid-disciplined.

**Exemplar**: Google's Material Design, introduced 2014; evolved into
Material You / Material 3 (2021) and Material 3 Expressive (2025).

**Era / currency**: launched June 2014 (Google I/O); current live iteration
is "Material 3 Expressive" as of 2025-26.

**Source**: [design.google — "Material Design"](https://design.google/library/material-design-eras)

## 4. Neumorphism (soft UI)

**Characterization**: monochromatic surfaces with soft dual light/shadow
casts making elements look extruded from or inset into the background —
"soft" skeuomorphism without color or texture.

**Adjectives**: soft-shadowed, monochromatic, low-contrast, extruded,
minimal-but-tactile.

**Exemplar**: the neumorphism.io generator and its viral Dribbble
concept shots (2019-2020) — never broadly shipped as a production OS
language.

**Era / currency**: viral design-trend peak late 2019 into 2020; quickly
flagged as an accessibility anti-pattern and did not graduate to a shipping
platform default. **WCAG risk**: its signature low-contrast, same-hue
shadow-on-background technique routinely fails WCAG 2.x contrast-ratio
minimums for text and interactive elements, making it a cautionary rather
than a recommended paradigm.

**Source**: [Axess Lab — "Neumorphism – the accessible and inclusive way"](https://axesslab.com/neumorphism/)

## 5. Glassmorphism

**Characterization**: frosted, translucent panels with background blur
(backdrop-filter) and subtle borders/highlights, giving a sense of
layered glass panes floating above content.

**Adjectives**: translucent, blurred, frosted, layered, luminous.

**Exemplar**: Apple macOS Big Sur (2020) redesign — translucent menu bar,
Control Center, and sidebar panels; also Microsoft's earlier Fluent
Design "Acrylic" material (2017).

**Era / currency**: macOS Big Sur shipped November 2020; the term
"glassmorphism" entered mainstream design vocabulary the same year and
remains a recognizable, still-used treatment.

**Source**: [Apple Newsroom — "macOS Big Sur available today"](https://www.apple.com/newsroom/2020/11/macos-big-sur-available-today/)

## 6. Spatial design / Liquid Glass

**Characterization**: a translucent, refractive material that dynamically
reflects and bends surrounding content/light, unifying interface chrome
across 2D screens and spatial (3D/mixed-reality) contexts — glassmorphism's
successor, built for a world where interfaces also live in physical space.

**Adjectives**: refractive, dynamic, spatial, adaptive, unifying.

**Exemplar**: Apple's "Liquid Glass" material, introduced at WWDC 2025
across iOS 26/macOS 26/visionOS, spanning phone, desktop, and headset UI.

**Era / currency**: announced WWDC June 2025; current/live design language
as of 2025-26 — the newest entry in the cycle, superseding flat-era chrome
on Apple platforms.

**Source**: [Apple Newsroom — "Apple introduces a delightful and elegant new software design"](https://www.apple.com/newsroom/2025/06/apple-introduces-a-delightful-and-elegant-new-software-design/)

## Summary cycle

skeuomorphism (2007) → flat (2013) → material-as-elevation (2014) →
neumorphism (2019-20, WCAG-risky detour) → glassmorphism (2020) →
spatial / Liquid Glass (2025). Each entry above names its own era so a
consumer cites "which era," never the bare genre name — the same
discipline `canon-design-visual.md` row 18 already states for this cycle.

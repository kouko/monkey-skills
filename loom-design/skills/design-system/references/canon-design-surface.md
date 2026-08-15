# Canon: UI surface treatment (Axis B)

Agent-facing recall insurance, consulted at the propose-candidates step as a
completeness audit — never shown raw to the user.

Including but not limited to the entries below; doctrine content stays in
the model (this list carries name + fits-when hint + stability note +
currency note + source only). It stays SEPARATE from the Axis-A canon of
cultural/graphic-design movements (`canon-design-visual.md`, owned by
`loom-product-principles`) — the two axes answer different questions
("which design tradition" vs "which screen-surface treatment era"), and
they now live in different stations, so an Axis-A round cannot be
context-polluted by these Axis-B entries by construction.

Grounded in `docs/loom/research/2026-07-12-ui-surface-treatments-canon.md`.

**This canon is consulted at the DESIGN stage.** Industry practice places
surface/depth treatment at **stage 4, the visual design-language step** (the
concrete look components inherit) — a design-language sub-decision, not a
PRINCIPLES one. Surface treatments are typically *derived* from platform /
era / tech constraints rather than user-anchored, which is why this axis is
owned by `loom-interface-design` (the DESIGN station) rather than by
`loom-product-principles`. It is **downstream of the tone & manner anchor**:
the stage-3 adjectives carried in the PRINCIPLES.md `## Anchors` section are
the governing mood, and they constrain which treatments below are even
proposable — a treatment may enrich the mood, never override it.

| Entry (originator, era) | Fits when… | Stability | Currency | Source |
|---|---|---|---|---|
| Web 1.0 / GeoCities maximalism (amateur homepage web, ~1994-2001) | Deliberately retro "old web" — tiled backgrounds, animated GIFs, under-construction banners, no grid | Historical reference | Retired ~2001-04; nostalgic revival (Neocities) live | [Wikipedia](https://en.wikipedia.org/wiki/GeoCities) |
| Web 2.0 gloss / gel (mid-2000s web, ~2004-2010) | Glossy reflective badge/button chrome — beveled edges, "gel" highlights, starbursts, vibrant gradients | Historical reference | Retired ~2012 (flat turn); shares its era with Frutiger Aero but distinct (chrome vs nature imagery) | [Smashing Magazine](https://www.smashingmagazine.com/2012/03/symptoms-of-epidemic-web-design-trends/) |
| Frutiger Aero / Aero Glass (Microsoft Windows Vista/7, ~2006-2012) | Glossy wet-look translucent surface with nature/lens-flare motifs and beveled 3D chrome — distinct from Apple's leather/felt skeuomorphism | Historical reference, revived nostalgically | Retired ~2012 (Windows 8 flat); Gen-Z nostalgia revival 2023- | [Wikipedia](https://en.wikipedia.org/wiki/Frutiger_Aero) |
| Skeuomorphism (Apple iOS, 2007-13) | Novice users need physical-object intuition transferred to the screen | Historical reference | Retired 2013 (WWDC iOS 7) | [NN/g](https://www.nngroup.com/articles/flat-material-design/) |
| Flat design (Apple iOS 7 / Microsoft Metro, 2010-13) | Legibility and minimalism over realism; typography-led hierarchy | Live baseline | Mainstream default since 2013, still tempered-live | [Apple Newsroom](https://www.apple.com/newsroom/2013/06/10Apple-Announces-iOS-7/) |
| Long-shadow / Flat 2.0 / almost-flat (community correction to pure flat, 2013-15) | Pure flat removed too many affordance cues — want "mostly flat" plus subtle shadows/highlights/layers so users still see what is clickable | Live (absorbed into baseline) | Transitional 2013-15; long-shadow motif dated, "flat 2.0" restraint now the live default | [NN/g](https://www.nngroup.com/articles/flat-design/) |
| Material-as-surface (Google Material Design elevation/shadow, 2014-) | Need selective physicality — elevation shadow + motion communicating spatial relationship, not full skeuomorphic literalism | Live, evolving | Launched 2014, current iteration "Material 3 Expressive" (2025) | [design.google](https://design.google/library/material-design-eras) |
| Dark mode as a surface treatment (macOS Mojave 2018 / iOS 13 + Android 10, 2019) | A deliberate dark-surface SYSTEM is wanted — dark-grey (not pure-black) base, elevation via lighter translucent overlays, semantic (not inverted) colors — **WCAG risk**: pure-black/over-dimmed surfaces fail contrast in BOTH directions (halation; grey-on-grey), so it is a designed system, never a free color inversion | Live baseline | System-wide since 2018-19; a standing expectation, not a trend | [Material 3](https://m3.material.io/blog/android-dark-theme-tutorial) |
| Neumorphism / soft UI (neumorphism.io generator, 2019-20) | Monochromatic soft-extruded look is explicitly requested — flag the WCAG risk before proposing | Trend, cautionary | Viral peak 2019-2020, never shipped as a platform default | [Axess Lab](https://axesslab.com/neumorphism/) |
| Glassmorphism (Apple macOS Big Sur / Microsoft Fluent Acrylic, 2017-20) | Translucent, layered-glass-pane depth cue over content is wanted | Recognizable, still-used | macOS Big Sur shipped Nov 2020, term entered mainstream same year | [Apple Newsroom](https://www.apple.com/newsroom/2020/11/macos-big-sur-available-today/) |
| Aurora UI / mesh-gradient backdrop (Michał Malewicz, 2021-) | Soft blurred organic multi-color "glow" as a decorative backdrop (the "Stripe look") — the surface is the atmosphere, not the controls — **WCAG risk**: keep it decorative; never place text or controls on the gradient (contrast fail) | Trend, still-used as backdrop | 2021 trend; persists as SaaS hero-section baseline | [UX Collective](https://uxdesign.cc/aurora-ui-new-visual-trend-for-2021-c763a7daa7e2) |
| Claymorphism / soft-clay 3D (Michał Malewicz, coined 2021) | Friendly "inflated clay" tactile surface — puffy rounded elements, double inner shadow + floating drop shadow (kids / onboarding / friendly fintech) — **WCAG risk**: milder than neumorphism, but pastel-on-pastel still risks a contrast failure | Trend, settled to niche | Viral 2021-22; niche since | [Smashing Magazine](https://www.smashingmagazine.com/2022/03/claymorphism-css-ui-design-trend/) |
| Material You / dynamic color (Google, Android 12, 2021-) | A user-personalized color SYSTEM is wanted — palette (5 tonal ramps, 65 tokens) extracted from the wallpaper; distinct from static 2014 Material — **WCAG risk**: auto-generated palettes can land on failing text/background contrast; the tonal-role mapping is what keeps it compliant | Live, evolving | Live baseline on Android 12+ | [AOSP](https://source.android.com/docs/core/display/material) |
| Neubrutalism / brutalist UI (Gumroad redesign 2021 → Malewicz names it 2022) | Raw in-your-face chrome — thick black borders, hard offset (non-blurred) drop-shadows, clashing saturated blocks, oversized type — **WCAG risk**: hard shadows + clashing saturated blocks can hurt focus-order clarity if applied carelessly (NN/g notes it is usually usability-friendly) | Trend, live | Viral 2022-; current on startup/marketing sites | [NN/g](https://www.nngroup.com/articles/neobrutalism/) |
| Bento-box grid (Apple keynotes, 2022-23) — scope tag `layout`, NOT a surface treatment | Content compressed into a tiled composition of differently-sized rounded cards, one idea per cell; propose it as a layout companion to a surface pick, never as the surface pick itself | Trend, live | Viral 2022-23; now a default marketing-page layout | [Muzli](https://muz.li/blog/bento-ui-grids/) |
| Spatial design / Liquid Glass (Apple, 2025-) | Interface chrome must unify across 2D screens and spatial/mixed-reality contexts | Live, newest in cycle | Announced WWDC June 2025, current design language 2025-26 | [Apple Newsroom](https://www.apple.com/newsroom/2025/06/apple-introduces-a-delightful-and-elegant-new-software-design/) |
| Retro-terminal / CRT / monospace-tech UI (dev-culture revival, ongoing) | Signaling competence, directness, zero decoration — green/amber phosphor on black, monospace grid, scanline/glow overlay | Niche, recurring | Perennial; live in dev-tool / hacker-brand contexts | [CSS-Tricks](https://css-tricks.com/old-timey-terminal-styling/) |
| Anti-design / "new ugly" (design-fringe, 2016-17-) | Intentional rebellion against slick usability — broken grids, clashing colors, harsh type, deliberate dissonance for expressive/brand edge — **WCAG risk**: deliberately anti-usability by definition; only fits expressive/brand-art contexts, never a task-completion product | Fringe, persistent | 2016-; recurs in fashion / art / portfolio work | [NN/g](https://www.nngroup.com/articles/brutalism-antidesign/) |

**Risk flag**: neumorphism's signature low-contrast, same-hue
shadow-on-background technique routinely fails **WCAG** 2.x contrast-ratio
minimums for text and interactive elements — treat it as a cautionary
paradigm, not a recommended default, unless the requester explicitly
accepts the accessibility trade-off. Six further entries carry a **WCAG**
risk **in their own row** (dark mode, Aurora, claymorphism, Material You,
neubrutalism, anti-design) — read the row, not just this note.

**Not the Axis-A movement**: the *neubrutalism* row above is a datable
screen-surface treatment (thick borders, hard offset shadows, clashing
blocks). It is NOT the cultural/graphic neo-brutalism movement catalogued
in the Axis-A `canon-design-visual.md`. They share a name and nothing
else — do not merge or substitute them.

**Popularity head**: flat design and Material Design crowd out the rest of
this list — an LLM defaults to one of these two without prompting. If a
draft's candidate set only names "flat" or "Material," re-check the full
cycle above (especially glassmorphism and spatial/Liquid Glass for a
current-era ask, or skeuomorphism/neumorphism when the ask is historical
or explicitly nostalgic) before proposing.
